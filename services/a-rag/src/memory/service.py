"""
file: services/a-rag/src/memory/service.rc.py

Service for managing both short-term (Redis) and long-term (ChromaDB)
conversational memory.

This module provides a MemoryService class that encapsulates all logic for
dialogue history. It performs a "dual-write" operation for long-term associative
memory and implements an intelligent summarization strategy for short-term
context preservation.
"""
import json
import logging
from typing import Callable, List, Optional

from llama_index.core import VectorStoreIndex
from llama_index.core.llms import ChatMessage as LlamaChatMessage, MessageRole
from llama_index.core.schema import Document
from llama_index.llms.llama_cpp import LlamaCPP

from core.schemas.chat_schemas import ChatMessage, Role
from storage.redis_client import redis_client

# --- Constants for Memory Management ---
MEMORY_KEY_PREFIX = "memory:chat:"
# --- [ISSUE-22]
# Memory limit in TOKENS(not in number of messages)
# Maximum number of tokens for the Redis history before any pruning/summarization.
MAX_HISTORY_TOKENS = 2048

# --- [ISSUE-24] Start of changes: Summarization Memory ---
# Number of messages that triggers the summarization process.
SUMMARY_THRESHOLD = 8
# How many of the OLDEST messages to compress into a single summary.
MESSAGES_TO_SUMMARIZE = 4
# The specialized prompt for the summarization task.
SUMMARY_PROMPT_TEMPLATE = """Concisely summarize the following conversation.
Focus on key facts, names, and user intentions mentioned.

--- CONVERSATION TO SUMMARIZE ---
{conversation_text}
--- END OF CONVERSATION ---

CONCISE SUMMARY:"""
# --- [ISSUE-24] End of changes: Summarization Memory ---

# --- [ISSUE-23] Start of changes: Long-Term Memory ---
CHAT_HISTORY_COLLECTION = "chat_history"
# --- [ISSUE-23] End of changes: Long-Term Memory ---


class MemoryService:
    """Handles multi-layered conversational memory."""

    def __init__(
        self,
        tokenizer: Callable[[str], List[int]],
        # --- [ISSUE-24] Start of changes: Summarization Memory ---
        llm_adapter: Optional[LlamaCPP] = None,
        # --- [ISSUE-24] End of changes: Summarization Memory ---
        # --- [ISSUE-23] Start of changes: Long-Term Memory ---
        chat_history_index: Optional[VectorStoreIndex] = None,
        # --- [ISSUE-23] End of changes: Long-Term Memory ---
    ):
        """Initializes the MemoryService."""
        if not callable(tokenizer):
            raise TypeError("Tokenizer must be a callable function.")
        
        self.tokenizer = tokenizer
        # --- [ISSUE-24] Start of changes: Summarization Memory ---
        self.llm_adapter = llm_adapter
        # --- [ISSUE-24] End of changes: Summarization Memory ---
        # --- [ISSUE-23] Start of changes: Long-Term Memory ---
        self.chat_history_index = chat_history_index
        # --- [ISSUE-23] End of changes: Long-Term Memory ---

        logging.info("MemoryService initialized.")
        if not self.llm_adapter:
            logging.warning("MemoryService initialized WITHOUT an LLM adapter. Summarization will be disabled.")
        if not self.chat_history_index:
            logging.warning("MemoryService initialized WITHOUT a chat history index. Long-term memory will be disabled.")

    def _get_user_memory_key(self, user_id: str | int) -> str:
        """Constructs the Redis key for a user's short-term memory."""
        return f"{MEMORY_KEY_PREFIX}{user_id}"

    async def get_history(self, user_id: str | int) -> List[ChatMessage]:
        """Retrieves the short-term conversation history for a user from Redis."""
        key = self._get_user_memory_key(user_id)
        history_json_strings = await redis_client.lrange(key, 0, -1)
        if not history_json_strings:
            return []
        return [ChatMessage.model_validate_json(item) for item in history_json_strings]

    async def add_message_to_history(
        self, user_id: str | int, role: Role, content: str
    ) -> None:
        """Adds a new message to all memory layers and prunes/summarizes if needed."""
        # --- [ISSUE-23] Start of changes: Long-Term Memory ---
        # 1. Add to Long-Term Memory (ChromaDB)
        if self.chat_history_index:
            try:
                # Create a LlamaIndex Document object. The text is formatted
                # to include the role for better semantic meaning.
                # Metadata helps us filter by user_id during retrieval.
                doc = Document(
                    text=f"{role.capitalize()}: {content}",
                    metadata={"user_id": str(user_id)}
                )
                await self.chat_history_index.ainsert_nodes([doc])
                logging.info(f"[MEMORY-LTM] Ingested message for user '{user_id}' into ChromaDB.")
            except Exception:
                logging.exception(f"[MEMORY-LTM] Failed to ingest message for user '{user_id}' into ChromaDB.")
        # --- [ISSUE-23] End of changes: Long-Term Memory ---

        # 2. Add to Short-Term Memory (Redis)
        key = self._get_user_memory_key(user_id)
        message = ChatMessage(role=role, content=content)
        
        logging.info(f"[MEMORY-STM] Caching for user '{user_id}': role='{message.role}', content='{message.content[:100]}...'")
        
        # Add the new message to the end of the list
        await redis_client.rpush(key, message.model_dump_json())
        logging.info(f"[MEMORY-STM] Cached for user '{user_id}': role='{message.role}'")

        # Prune short-term memory based on token count
        await self._prune_and_summarize_history(key)

    async def _prune_and_summarize_history(self, redis_key: str) -> None:
        """Internal method to manage the size of the Redis history via summarization and token pruning."""
        history = await self.get_history(redis_key.split(":")[-1])
        
        # --- [ISSUE-24] Start of changes: Summarization Memory ---
        if self.llm_adapter and len(history) > SUMMARY_THRESHOLD:
            logging.warning(f"[MEMORY-STM] History length ({len(history)}) exceeds threshold ({SUMMARY_THRESHOLD}). Triggering summarization.")
            
            messages_to_summarize = history[:MESSAGES_TO_SUMMARIZE]
            conversation_text = "\n".join([f"{msg.role}: {msg.content}" for msg in messages_to_summarize])
            
            prompt = SUMMARY_PROMPT_TEMPLATE.format(conversation_text=conversation_text)
            
            try:
                response = await self.llm_adapter.acomplete(prompt)
                summary_text = f"Summary of earlier conversation: {response.text.strip()}"
                summary_message = ChatMessage(role="system", content=summary_text)

                async with redis_client.pipeline() as pipe:
                    pipe.ltrim(redis_key, MESSAGES_TO_SUMMARIZE, -1)
                    pipe.lpush(redis_key, summary_message.model_dump_json())
                    await pipe.execute()

                logging.info(f"[MEMORY-STM] Summarization complete. New history length: {await redis_client.llen(redis_key)}")
                history = await self.get_history(redis_key.split(":")[-1])
            except Exception:
                logging.exception("[MEMORY-STM] Failed to summarize chat history.")
        # --- [ISSUE-24] End of changes: Summarization Memory ---

        total_tokens = sum(len(self.tokenizer(msg.content.encode("utf-8"))) for msg in history)
        while total_tokens > MAX_HISTORY_TOKENS:
            removed_message_json = await redis_client.lpop(redis_key)
            if not removed_message_json: break
            
            removed_message = ChatMessage.model_validate_json(removed_message_json)
            logging.warning(f"[MEMORY-STM] Token limit still exceeded. Pruning oldest message from Redis...")
            total_tokens -= len(self.tokenizer(removed_message.content.encode("utf-8")))

        logging.info(f"[MEMORY-STM] Final short-term history for user '{redis_key.split(':')[-1]}' has {total_tokens} tokens.")

    async def clear_history(self, user_id: str | int) -> None:
        """Deletes a user's history from all memory layers."""
        # 1. Clear Short-Term Memory (Redis)
        redis_key = self._get_user_memory_key(user_id)
        deleted_count = await redis_client.delete(redis_key)
        if deleted_count > 0:
            logging.info(f"[MEMORY-STM] Successfully deleted Redis history for user '{user_id}'.")
        
        # --- [ISSUE-23] Start of changes: Long-Term Memory ---
        # 2. Clear Long-Term Memory (ChromaDB)
        # This is more complex as ChromaDB doesn't have a simple 'delete by user'.
        # We need to retrieve all node IDs for that user and then delete them.
        if self.chat_history_index:
            try:
                # This is a placeholder for the actual deletion logic,
                # which requires retrieving node IDs by metadata filter first.
                # For now, we just log the intent.
                # Proper implementation would be:
                # node_ids_to_delete = vector_store.delete_by_filter(...)
                logging.warning(f"[MEMORY-LTM] Deleting from ChromaDB for user '{user_id}' is not yet fully implemented, but the short term memory is cleared.")
            except Exception:
                logging.exception(f"[MEMORY-LTM] Error while trying to clear history from ChromaDB for user '{user_id}'.")
        # --- [ISSUE-23] End of changes: Long-Term Memory ---