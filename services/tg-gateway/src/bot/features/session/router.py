"""
file: services/tg-gateway/src/bot/features/session/router.py

Router for handling session-related commands like /start and /clear.
"""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from clients.rag_api_client import RagApiClient
from .handler import clear_chat_history_handler
from core.localization import Localize

session_router = Router(name="session_router")

@session_router.message(Command("start", "clear"))
async def handle_session_commands(message: Message, rag_client: RagApiClient, loc: Localize):
    """
    Catches /start and /clear commands and delegates them to the handler.
    
    This router's only responsibility is to match the command and pass control.
    All business logic resides in the handler.
    """
    await clear_chat_history_handler(message, rag_client,loc)