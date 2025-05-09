"""
tgrambuddy/src/bot/features/start_router.py

This module defines router for /start command handler classusing the Aiogram framework. 

TgramBuddy - A solution for building and managing Telegram bots.
Copyright (c) 2025 Maks V. Zaikin
Released by 01-May-2025 under the MIT License.
"""
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from .start_handler import start_command_handler

start_command_router = Router()

@start_command_router.message(Command("start"))
async def start_command(message: Message, session: AsyncSession):
    """
    Handles the incoming /start command from a Telegram user.

    This function is called when a user sends the /start command to the bot.
    It invokes the `start_handler` function to process the command.

    Args:
        message (aiogram.types.Message): The message object that contains the data 
                                            about the received command.
        session (sqlalchemy.ext.asyncio.AsyncSession): Aiogram DI, - the async session used 
                                            for database interaction.
    
    Returns:
        None
    """
    await start_command_handler(message, session)
