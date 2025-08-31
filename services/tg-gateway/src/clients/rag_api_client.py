# file: services/tg-gateway/src/clients/rag_api_client.py

"""
Asynchronous HTTP client for interacting with the A-RAG API service.

This module provides a dedicated client class to encapsulate all communication
logic with the backend `a-rag-api`. It handles request construction, error
handling, and connection management using the `httpx` library.
"""

import logging
import json
from typing import Optional, TypedDict

import httpx
from src.core.config import settings

# --- Type for the dual response for clarity ---
class DualRagResponse(TypedDict):
    """
    Represents the expected structure of the dual response from the a-rag API.
    """
    rag_answer: str
    llm_answer: str
    original_query: str


class RagApiClient:
    """A client for making asynchronous requests to the A-RAG backend API."""

    def __init__(self, timeout: Optional[int] = None):
        """
        Initializes the RagApiClient.
        
        [MODIFIED] Increased the default timeout to handle long-running RAG processes.
        """
        headers = {"Authorization": f"Bearer {settings.INTERNAL_SERVICE_API_KEY}"}

        # --- [FIX] Set a much longer timeout ---
        # The advanced RAG pipeline can take a long time to run on local hardware.
        # We are setting a 3-minute (180 seconds) timeout as a safe margin.
        # This should be configured via `settings` for production.
        #request_timeout = timeout or 180.0 

        self.client = httpx.AsyncClient(
            base_url=settings.RAG_API_BASE_URL,
            timeout=timeout or settings.RAG_API_TIMEOUT,
            headers=headers,
        )
        logging.info(f"RagApiClient initialized with a timeout of {timeout} seconds.")

    async def get_rag_response(self, user_query: str, user_id: int) -> Optional[DualRagResponse]:
        """
        Sends a user query to the a-rag-api and returns the dual response.
        """
        endpoint_path = f"{settings.RAG_API_VERSION_PREFIX}{settings.RAG_API_CHAT_ENDPOINT}"
        payload = {"user_query": user_query, "user_id": str(user_id)}

        logging.info(f"Sending request to A-RAG API at {endpoint_path} for user {user_id}")

        try:
            response = await self.client.post(url=endpoint_path, json=payload)
            response.raise_for_status()
            data = response.json()
            
            if "rag_answer" in data and "llm_answer" in data:
                return data
            else:
                logging.error(f"A-RAG API response is missing required fields: {data}")
                return None

        except httpx.TimeoutException:
            logging.error(f"Request to A-RAG API timed out after {self.client.timeout.read} seconds.")
            return None
        except httpx.HTTPStatusError as e:
            logging.error(f"A-RAG API returned a non-2xx status: {e.response.status_code} - {e.response.text}")
            return None
        except httpx.RequestError as e:
            logging.error(f"Failed to connect to A-RAG API: {e}")
            return None
        except json.JSONDecodeError:
            logging.error("Failed to decode JSON response from A-RAG API.")
            return None

    async def clear_user_memory(self, user_id: int) -> bool:
        """
        Sends a request to the a-rag-api to clear a user's memory.
        """
        endpoint_path = f"{settings.RAG_API_VERSION_PREFIX}{settings.RAG_API_CLEAR_CHAT_HISTORY_ENDPOINT}{user_id}"
        logging.info(f"Sending request to clear memory for user {user_id} at {endpoint_path}")
        try:
            response = await self.client.delete(url=endpoint_path)
            response.raise_for_status()
            return True
        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            logging.error(f"API request for memory clear failed: {e}")
            return False

    async def close(self):
        """Closes the HTTP client sessions."""
        if not self.client.is_closed:
            await self.client.aclose()