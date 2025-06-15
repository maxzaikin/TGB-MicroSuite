"""
file: TGB-MicroSuite/services/tg-gateway/src/bot/features/rag_chat/router.py

Router for the core RAG chat feature.

This module defines the router that captures general text messages from users,
ensuring they are not commands, and passes them to the appropriate handler
for processing by the A-RAG service.
"""

from aiogram import F, Router
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from src.clients.rag_api_client import RagApiClient

# Import the handler from the same feature slice.
from .handler import handle_text_message

rag_router = Router(name="rag_chat_router")


@rag_router.message(F.text, ~F.text.startswith("/"))
async def on_text_message(
    message: Message, session: AsyncSession, rag_client: RagApiClient
):
    """
    Handles any incoming text message that is not a command.

    This handler is the main entry point for user queries to the RAG system.
    It uses a combination of filters to capture the right type of message.

    Args:
        message (Message): The message object from the user.
        session (AsyncSession): The database session, injected by middleware.
                                (Even if not used now, it's good practice to have it ready).
    """
    # The router's job is simply to delegate the work to the handler.
    await handle_text_message(message, session, rag_client)
