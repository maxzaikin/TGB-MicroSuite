# file: services/tg-gateway/src/bot/features/session/handler.py
"""
Handler logic for session-related commands like /start and /clear.
"""
import logging
from aiogram.types import Message
from clients.rag_api_client import RagApiClient
from core.localization import Localize

async def clear_chat_history_handler(
    message: Message, 
    rag_client: RagApiClient,
    loc: Localize
):
    """
    Handles the logic for clearing a user's conversation history.
    ...
    Args:
        ...
        loc: The localization service, injected by the Dispatcher.
    """
    if not message.from_user:
        return

    user_id = message.from_user.id
    command_text = message.text or "/unknown"
    
    logging.info(
        f"[HANDLER] Received command '{command_text}' from user {user_id}. "
        "Initiating memory clear."
    )

    await message.answer(loc.get("session_clearing_memory"))

    success = await rag_client.clear_user_memory(user_id)

    if success:
        await message.answer(loc.get("session_clear_success"))
    else:
        await message.answer(loc.get("session_clear_error"))