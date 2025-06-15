"""
file: TGB-MicroSuite/services/tg-gateway/src/bot/features/rag_chat/handler.py

Core logic for handling general text messages for RAG processing.

This module is responsible for taking a user's text message, forwarding it
to the backend A-RAG API service for processing, and returning the
generated response to the user.
"""

import logging

from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from src.clients.rag_api_client import RagApiClient


async def handle_text_message(
    message: Message, session: AsyncSession, rag_client: RagApiClient
):
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

    user_id = message.from_user.id
    query_text = message.text

    logging.info(f"[TG-GW] Received message from user {user_id}: '{query_text}'")

    # 1. Provide immediate feedback to the user that the request is being processed.
    await message.bot.send_chat_action(message.chat.id, action="typing")

    response_text = await rag_client.get_rag_response(
        user_query=query_text, user_id=user_id
    )

    if not response_text:
        response_text = "Sorry, I couldn't get a response. Please try again."

    logging.info(
        f"[TG-GW] Sending response to user {user_id}: '{response_text[:100]}...'"
    )

    await message.reply(response_text)
