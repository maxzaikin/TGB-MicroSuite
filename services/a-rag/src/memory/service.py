"""
# file: services/a-rag/src/memory/service.py
Service for managing both short-term (Redis) and long-term (ChromaDB)
conversational memory.

This module provides a MemoryService class that encapsulates all logic for
dialogue history. It performs a "dual-write" operation: recent messages
are kept in a token-capped Redis list for immediate context, while all
messages are also vectorized and stored in ChromaDB for long-term
associative retrieval.
"""
import json
import logging
from typing import Callable, List, Optional

from llama_index.core import VectorStoreIndex
from llama_index.core.schema import Document
from llama_index.vector_stores.chroma import ChromaVectorStore

from core.schemas.chat_schemas import ChatMessage, Role
from storage.redis_client import redis_client

# --- Constants for Memory Management ---
MEMORY_KEY_PREFIX = "memory:chat:"
# --- [ISSUE-22]
# Memory limit in TOKENS(not in number of messages)
MAX_CONTEXT_TOKENS = 2048
# --- [ISSUE-23] Start of changes: Long-Term Memory ---
# Name for the ChromaDB collection that will store chat history.
CHAT_HISTORY_COLLECTION = "chat_history"


class MemoryService:
    """
    Handles token-aware short-term memory and long-term associative memory.
    """

    # --- [ISSUE-23] Start of changes: Long-Term Memory ---
    def __init__(
        self,
        tokenizer: Callable[[str], List[int]],
        chat_history_index: Optional[VectorStoreIndex] = None,
    ):
        """
        Initializes the MemoryService.

        Args:
            tokenizer: A function to calculate token count for short-term memory.
            chat_history_index: A LlamaIndex VectorStoreIndex connected to the
                                 'chat_history' ChromaDB collection.
        """
        if not callable(tokenizer):
            raise TypeError("Tokenizer must be a callable function.")
        
        self.tokenizer = tokenizer
        self.chat_history_index = chat_history_index
        logging.info("MemoryService initialized.")
        if not chat_history_index:
            logging.warning("MemoryService initialized WITHOUT a chat history index. Long-term memory will be disabled.")
    # --- [ISSUE-23] End of changes: Long-Term Memory ---

    def _get_user_memory_key(self, user_id: str | int) -> str:
        """Constructs the Redis key for a given user's short-term memory."""
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
        """
        Adds a new message to both short-term (Redis) and long-term (ChromaDB) memory.
        """
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
                await self.chat_history_index.a_insert_nodes([doc])
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

        # Prune short-term memory based on token count
        await self._prune_history_by_tokens(key)

    async def _prune_history_by_tokens(self, redis_key: str) -> None:
        """Internal method to prune the Redis list to MAX_CONTEXT_TOKENS."""
        # This logic is extracted into a private method for clarity.
        current_history_json = await redis_client.lrange(redis_key, 0, -1)
        history_messages = [ChatMessage.model_validate_json(item) for item in current_history_json]
        
        total_tokens = sum(len(self.tokenizer(msg.content.encode("utf-8"))) for msg in history_messages)

        while total_tokens > MAX_CONTEXT_TOKENS:
            removed_message_json = await redis_client.lpop(redis_key)
            if removed_message_json:
                removed_message = ChatMessage.model_validate_json(removed_message_json)
                logging.warning(
                    f"[MEMORY-STM] History limit exceeded. Pruning oldest message from Redis..."
                )
                total_tokens -= len(self.tokenizer(removed_message.content.encode("utf-8")))
            else:
                break
        logging.info(f"[MEMORY-STM] Final short-term history has {total_tokens} tokens.")

    async def clear_history(self, user_id: str | int) -> None:
        """
        Deletes a user's history from both short-term and long-term memory.
        """
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