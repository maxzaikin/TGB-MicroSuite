"""
file: TGB-Microsuite/services/tg-gateway/src/bot/features/onboarding/handler.py

Core logic for the user onboarding feature.

This module contains the handler function that is executed when a user
sends the /start command. Its primary responsibility is to greet the user,
and in the future, to ensure the user's profile is created in the database.
"""

from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession


async def handle_start_command(message: Message, session: AsyncSession):
    """
    Greets the user and ensures their profile exists.

    Args:
        message (Message): The incoming message object from Aiogram.
        session (AsyncSession): The database session injected by middleware.
    """
    # TODO: Implement user creation logic.
    # 1. Check if user already exists in the database by their telegram ID.
    #    user_id = message.from_user.id
    #    result = await session.execute(select(Client).where(Client.t_id == user_id))
    #    existing_client = result.scalar_one_or_none()
    #
    # 2. If not, create a new Client record and save it.
    #    if not existing_client:
    #        new_client = Client(...)
    #        session.add(new_client)
    #        await session.commit()

    welcome_text = (
        "Hello! I am your RAG-powered assistant. "
        "Just send me any question, and I'll do my best to answer."
    )
    await message.reply(welcome_text)
