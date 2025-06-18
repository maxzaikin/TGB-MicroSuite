"""
file: TGB-MicroSuite/services/tg-gateway/src/clients/rag_api_client.py

Asynchronous HTTP client for interacting with the A-RAG API service.

This module provides a dedicated client class to encapsulate all communication
logic with the backend `a-rag-api`. It handles request construction, error
handling, and connection management using the `httpx` library.
"""

import logging
from typing import Optional

import httpx
from src.core.config import settings


class RagApiClient:
    """A client for making asynchronous requests to the A-RAG backend API."""

    def __init__(self, timeout: Optional[int] = None):
        """Initializes the RagApiClient."""
        headers = {"Authorization": f"Bearer {settings.INTERNAL_SERVICE_API_KEY}"}

        self.client = httpx.AsyncClient(
            base_url=settings.RAG_API_BASE_URL,
            timeout=timeout or settings.RAG_API_TIMEOUT,
            headers=headers,
        )

    async def get_rag_response(self, user_query: str, user_id: int) -> str:
        """
        Sends a user query to the a-rag-api and returns the generated answer.

        Args:
            user_query: The user's raw text message.
            user_id: The Telegram ID of the user.

        Returns:
            The generated answer from the RAG service, or a user-friendly error message.
        """
        # The endpoint path is now composed from configuration variables
        endpoint_path = (
            f"{settings.RAG_API_VERSION_PREFIX}{settings.RAG_API_CHAT_ENDPOINT}"
        )

        # The payload now matches the new `RAGRequest` schema
        # payload = {"user_query": user_query, "user_id": user_id}
        payload = {"user_query": user_query, "user_id": str(user_id)}

        logging.info(
            f"Sending request to A-RAG API at {endpoint_path} for user {user_id}"
        )

        try:
            response = await self.client.post(url=endpoint_path, json=payload)
            response.raise_for_status()

            data = response.json()
            # The response schema now has an "answer" field
            return data.get("answer", "No valid answer received.")

        except httpx.HTTPStatusError as e:
            logging.error(
                f"A-RAG API returned a non-2xx status: {e.response.status_code}"
            )
            return "Sorry, an error occurred while processing your request."

        except httpx.RequestError as e:
            logging.error(f"Failed to connect to A-RAG API: {e}")
            return "I'm having trouble connecting to my knowledge base right now."
        
    async def clear_user_memory(self, user_id: int) -> bool:
        """
        Sends a request to the a-rag-api to clear a user's memory.

        Args:
            user_id: The Telegram ID of the user.

        Returns:
            True if the operation was successful, False otherwise.
        """
        # The endpoint for clearing memory.
        endpoint_path = (
            f"{settings.RAG_API_VERSION_PREFIX}{settings.RAG_API_CLEAR_CHAT_HISTORY_ENDPOINT}{user_id}"
        )        
        
        logging.info(f"Sending request to clear memory for user {user_id} at {endpoint_path}")
        
        try:
            # We use the DELETE HTTP method here as it's semantically correct.
            response = await self.client.delete(url=endpoint_path)
            response.raise_for_status() # Will raise for 4xx/5xx status codes
            # A 204 No Content response is a success signal.
            return True
        except httpx.HTTPStatusError as e:
            logging.error(f"API returned an error on memory clear: {e.response.status_code}")
            return False
        except httpx.RequestError as e:
            logging.error(f"Failed to connect to A-RAG API for memory clear: {e}")
            return False

    async def close(self):
        """Closes the HTTP client sessions."""
        if not self.client.is_closed:
            await self.client.aclose()
