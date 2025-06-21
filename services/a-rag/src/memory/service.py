"""
file: services/a-rag/src/memory/service.py

Service for managing short-term conversational memory using Redis.

This module provides a MemoryService class that encapsulates all logic for
reading from and writing to a user's dialogue history.
As of 21-Jun-2025 Iit now includes token-based management to ensure the c
onversation context does not exceed a predefined size, preventing performance degradation.
"""
import json
import logging
from typing import Any, Callable, List

from core.schemas.chat_schemas import ChatMessage, Role
from storage.redis_client import redis_client

# --- Constants for Memory Management ---
MEMORY_KEY_PREFIX = "memory:chat:"
# Define the memory limit in TOKENS(not in number of messages)
MAX_CONTEXT_TOKENS = 2048


class MemoryService:
    """
    Handles token-aware reading from and writing to short-term memory.
    """

    def __init__(self, tokenizer: Callable[[str], List[int]]):
        """
        Initializes the MemoryService with a tokenizer function.

        Args:
            tokenizer: A function that takes a string and returns a list of
                       token IDs. This will be used to calculate the size
                       of the conversation history.
        """
        if not callable(tokenizer):
            raise TypeError("Tokenizer must be a callable function.")
        
        self.tokenizer = tokenizer
        logging.info("MemoryService initialized with a tokenizer.")

    def _get_user_memory_key(self, user_id: str | int) -> str:
        """Constructs the Redis key for a given user's memory."""
        return f"{MEMORY_KEY_PREFIX}{user_id}"

    async def get_history(self, user_id: str | int) -> List[ChatMessage]:
        """Retrieves and deserializes the conversation history for a user from Redis DB."""
        key = self._get_user_memory_key(user_id)
        history_json_strings = await redis_client.lrange(key, 0, -1)
        if not history_json_strings:
            return []
        return [ChatMessage.model_validate_json(item) for item in history_json_strings]

    async def add_message_to_history(
        self, user_id: str | int, role: Role, content: str
    ) -> None:
        """
        Adds a new message to history and prunes the history if it exceeds
        the token limit.
        """
        key = self._get_user_memory_key(user_id)
        message = ChatMessage(role=role, content=content)
        
        logging.info(f"[MEMORY] Caching for user '{user_id}': role='{message.role}', content='{message.content[:100]}...'")
        
        # Add the new message to the end of the list
        await redis_client.rpush(key, message.model_dump_json())

        # --- Token-based Pruning Logic ---
        # After adding, check the total token count and remove old messages if needed.
        current_history = await self.get_history(user_id)
        
        # Encode the string to bytes before tokenizing.
        total_tokens = sum(len(self.tokenizer(msg.content.encode("utf-8"))) for msg in current_history)
        logging.info(f"[MEMORY] History for user '{user_id}' now has {total_tokens} tokens.")

        while total_tokens > MAX_CONTEXT_TOKENS:
            removed_message_json = await redis_client.lpop(key)
            
            if removed_message_json:
                removed_message = ChatMessage.model_validate_json(removed_message_json)
                logging.warning(
                    f"[MEMORY] History limit exceeded. Pruning oldest message for user '{user_id}': "
                    f"role='{removed_message.role}', content='{removed_message.content[:50]}...'"
                )
                # Recalculate total tokens, also encoding the string.
                total_tokens -= len(self.tokenizer(removed_message.content.encode("utf-8")))
            else:
                break
        
        logging.info(f"[MEMORY] Final history for user '{user_id}' has {total_tokens} tokens.")
        
    async def clear_history(self, user_id: str | int) -> int:
        """
        Deletes the entire conversation history for a specific user from Redis.

        Args:
            user_id: The unique identifier for the user session.

        Returns:
            The number of keys that were removed (0 or 1).
        """
        key = self._get_user_memory_key(user_id)
        logging.info(f"[MEMORY] Clearing history for user '{user_id}' (key: {key}).")
        # The `delete` command in redis-py returns the number of keys deleted.
        deleted_count = await redis_client.delete(key)
        
        if deleted_count > 0:
            logging.info(f"[MEMORY] Successfully deleted history for user '{user_id}'.")
        else:
            logging.warning(f"[MEMORY] Attempted to clear history for user '{user_id}', but no history was found.")
            
        return deleted_count
        