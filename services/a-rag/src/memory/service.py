"""
file: services/a-rag/src/memory/service.py

Service for managing short-term conversational memory using Redis.

This module provides a MemoryService class that encapsulates all logic for
reading from and writing to a user's dialogue history, stored as a capped
list in Redis. It uses a structured ChatML format for messages.
"""

import logging
from typing import List

from core.schemas.chat_schemas import ChatMessage, Role
from storage.redis_client import redis_client

# --- Constants for Memory Management ---

# A prefix for all Redis keys related to memory to avoid collisions.
MEMORY_KEY_PREFIX = "memory:chat:"
# The maximum number of individual messages (user + assistant) to retain.
# For example, 10 messages = 5 pairs of user/assistant turns.
MAX_HISTORY_LENGTH = 10


class MemoryService:
    """Handles reading from and writing to the short-term conversation memory."""

    def _get_user_memory_key(self, user_id: str | int) -> str:
        """
        Constructs the Redis key for a given user's memory.

        Args:
            user_id: The unique identifier for the user session.

        Returns:
            A formatted string to be used as a Redis key.
        """
        return f"{MEMORY_KEY_PREFIX}{user_id}"

    async def get_history(self, user_id: str | int) -> List[ChatMessage]:
        """
        Retrieves and deserializes the conversation history for a user from Redis.

        Args:
            user_id: The unique identifier for the user session.

        Returns:
            A list of ChatMessage Pydantic objects. Returns an empty list
            if no history is found.
        """
        key = self._get_user_memory_key(user_id)
        # lrange(key, 0, -1) fetches all elements from the list.
        history_json_strings = await redis_client.lrange(key, 0, -1)

        # The data in Redis is stored as JSON strings. We need to parse
        # them back into our strongly-typed ChatMessage objects.
        if not history_json_strings:
            return []
        return [ChatMessage.model_validate_json(item) for item in history_json_strings]

    async def add_message_to_history(
        self, user_id: str | int, role: Role, content: str
    ) -> None:
        """
        Adds a new message to a user's history and trims the history to size.

        This function appends the new message to the end of the list and then
        removes older messages from the beginning if the list exceeds
        MAX_HISTORY_LENGTH.

        Args:
            user_id: The unique identifier for the user session.
            role: The role of the message author ('user' or 'assistant').
            content: The text content of the message.
        """
        key = self._get_user_memory_key(user_id)
        message = ChatMessage(role=role, content=content)

        logging.info(
            f"[MEMORY] Caching for user '{user_id}': role='{message.role}', content='{message.content[:100]}...'"
        )

        # rpush: Pushes the new message (as a JSON string) to the right (end) of the list.
        await redis_client.rpush(key, message.model_dump_json())

        # ltrim: Trims the list, keeping only elements from index -MAX_HISTORY_LENGTH to the end.
        # This efficiently maintains a capped-size list.
        await redis_client.ltrim(key, -MAX_HISTORY_LENGTH, -1)
