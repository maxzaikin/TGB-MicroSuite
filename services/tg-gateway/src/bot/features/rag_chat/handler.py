"""
file: TGB-MicroSuite/services/tg-gateway/src/bot/features/rag_chat/handler.py

Core logic for handling general text messages for RAG processing.

This module is responsible for taking a user's text message, forwarding it
to the backend A-RAG API service for processing, and returning the
generated response to the user.
"""

import asyncio

from aiogram.types import Message

# In the future, you will import a service to handle the API call.
# from src.services.rag_api_client import RagApiClient


async def handle_text_message(message: Message):
    """
    Processes a non-command text message from the user.

    This function serves as the main handler for the chat functionality.
    It simulates an interaction with a backend RAG service.

    Args:
        message (Message): The incoming message object from Aiogram.
    """
    if not message.text:
        # A safeguard in case this handler is ever triggered by a non-text message.
        return

    # 1. Provide immediate feedback to the user that the request is being processed.
    await message.bot.send_chat_action(message.chat.id, action="typing")

    # 2. TODO: Implement the actual call to the a-rag-api service.
    #    This logic will be encapsulated in a dedicated service/client.
    #
    #    Example:
    #    rag_client = RagApiClient()
    #    try:
    #        response_text = await rag_client.get_response(
    #            user_id=message.from_user.id,
    #            text=message.text
    #        )
    #    except Exception as e:
    #        # Handle API errors gracefully
    #        response_text = "Sorry, I'm having trouble connecting to my brain right now."

    # Simulating the API call delay for now.
    await asyncio.sleep(2)
    response_text = (
        f"A-RAG mock response for: '{message.text[:50]}...'. "
        "The real answer will be here."
    )

    # 3. Send the final response back to the user.
    await message.reply(response_text)
