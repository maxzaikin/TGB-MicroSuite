"""
tgrambuddy/src/bot/handlers/start.py

This module defines the StartHandler class for handling the `/start` command 
in a Telegram bot using the Aiogram framework. When a user initiates the bot 
with the `/start` command, this handler responds with a welcome message.

Classes:
    StartHandler -- Handles incoming /start messages and replies with a greeting.

TgramBuddy - A solution for building and managing Telegram bots.
Copyright (c) 2025 Maks V. Zaikin
Released by 01-May-2025 under the MIT License.
"""
from typing import Any
from aiogram.types import (
    Message, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton
)
from aiogram.handlers import BaseHandler

class StartHandler(BaseHandler[Message]):
    async def handle(self) -> Any:
        
        inline_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Загрузить фото", callback_data="upload_photo"),
                ],
                # template for other buttons
                # [
                #     InlineKeyboardButton(text="Другая кнопка", callback_data="other_action"),
                # ],
            ]
        )

        await self.event.reply(
            "👋 Hello Buddy from 🤖 Telegram Buddy 😊! Что вы хотите сделать?",
            reply_markup=inline_keyboard
        )
