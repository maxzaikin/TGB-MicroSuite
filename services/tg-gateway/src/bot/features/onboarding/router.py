"""
file: TGB-MicroSuite/services/tg-gateway/src/bot/features/onboarding/router.py

Router for the user onboarding feature.

This module defines the router that handles the entry-point commands for new
users, such as /start. It maps the command to its corresponding handler
function from the same feature slice.
"""

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

# Import the handler from the same feature slice
from .handler import handle_start_command

onboarding_router = Router(name="onboarding_router")


@onboarding_router.message(CommandStart())
async def on_start_command(message: Message, session: AsyncSession):
    """
    Handles the /start command.

    This function acts as the entry point for the command. It receives the
    update from Aiogram and passes it, along with any injected dependencies
    like the database session, to the core handler function.

    Args:
        message (Message): The message object from the user.
        session (AsyncSession): The database session, injected by middleware.
    """
    await handle_start_command(message, session)
