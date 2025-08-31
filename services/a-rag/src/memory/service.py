# file: services/a-rag/src/memory/service.py

"""
Service for managing both short-term (Redis) and long-term (Vector DB)
conversational memory.

[REFACTORED] This version is decoupled from specific database implementations
and uses an OpenAI-compatible client for LLM-based operations like summarization.
"""
import logging
from typing import Callable, List, Optional
from datetime import datetime, timezone

from openai import AsyncOpenAI

# Core application components and schemas
from src.core.schemas.chat_schemas import ChatMessage, Role
from src.core.schemas.rag_schemas import EmbeddedChunk, ChunkMetadata
from src.models.embedding_service import embedding_model_service
from src.storage.redis_client import redis_client
from src.storage.vec_db.base import VectorStoreRepository

# --- Constants ---
MEMORY_KEY_PREFIX = "memory:chat:"
MAX_HISTORY_TOKENS = 2048
SUMMARY_THRESHOLD = 8
MESSAGES_TO_SUMMARIZE = 4
SUMMARY_PROMPT_TEMPLATE = """Concisely summarize the following conversation.
Focus on key facts, names, and user intentions mentioned.

--- CONVERSATION TO SUMMARIZE ---
{conversation_text}
--- END OF CONVERSATION ---

CONCISE SUMMARY:"""

logger = logging.getLogger(__name__)


class MemoryService:
    """Handles multi-layered conversational memory."""

    def __init__(
        self,
        # --- [MODIFIED] Removed tokenizer and llm_adapter ---
        # tokenizer: Callable[[str], List[int]],
        llm_client: Optional[AsyncOpenAI] = None, # Now accepts the OpenAI client
        chat_history_store: Optional[VectorStoreRepository] = None,
    ):
        """Initializes the MemoryService with its dependencies."""
        # self.tokenizer = tokenizer # Tokenizer is now an implementation detail
        self.llm_client = llm_client
        self.chat_history_store = chat_history_store

        logging.info("MemoryService initialized.")
        if not self.llm_client:
            logging.warning("MemoryService initialized WITHOUT an LLM client. Summarization will be disabled.")
        if not self.chat_history_store:
            logging.warning("MemoryService initialized WITHOUT a chat history store. Long-term memory will be disabled.")

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
        # 1. Add to Long-Term Memory (Vector DB via Repository)
        if self.chat_history_store:
            try:
                text_to_embed = f"{role.capitalize()}: {content}"
                embedding = embedding_model_service.get_embedding(text_to_embed)
                
                metadata = ChunkMetadata(
                    source="chat_history",
                    document_id=str(user_id),
                    chunk_index=0,
                    source_type="chat",
                    user_id=str(user_id)
                )
                
                chunk = EmbeddedChunk(
                    content=text_to_embed,
                    embedding=embedding,
                    metadata=metadata
                )
                
                await self.chat_history_store.add_documents([chunk])
                logging.info(f"[MEMORY-LTM] Ingested message for user '{user_id}' into Vector DB.")
            except Exception:
                logging.exception(f"[MEMORY-LTM] Failed to ingest message for user '{user_id}' into Vector DB.")

        # 2. Add to Short-Term Memory (Redis)
        key = self._get_user_memory_key(user_id)
        message = ChatMessage(role=role, content=content)
        await redis_client.rpush(key, message.model_dump_json())
        logging.info(f"[MEMORY-STM] Cached for user '{user_id}': role='{message.role}'")

        # Pruning is now a conceptual placeholder, as we don't have the tokenizer
        # await self._prune_and_summarize_history(key)

    async def clear_history(self, user_id: str | int) -> None:
        """Deletes a user's history from all memory layers."""
        # Placeholder for your history clearing logic.
        pass