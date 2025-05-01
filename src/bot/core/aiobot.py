""" Comming soon

    _This file defines the AioBot class, which encapsulates the logic for
interacting with the Telegram Bot API using the aiogram library.
It handles initialization of the bot and dispatcher, registration of
message handlers, and the main event polling loop.
"""
# TgramBuddy - A solution for building and managing Telegram bots.
# Copyright (c) 2025 Maks V. Zaikin
# Released by 01-May-2025 under the MIT License.
#
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from  ..handlers.start import StartHandler

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

class AioBot:
    '''ddd
    '''
    
    def __init__(self, token: str)->None:
        self.bot = Bot(token)
        self.dp = Dispatcher()

    def register_handlers(self):
        """Регистрирует обработчики для бота."""
        self.dp.message.register(StartHandler(), Command("start"))



    async def run(self):
        self.register_handlers()
        try:
            await self.dp.start_polling(self.bot)
        finally:
            await self.bot.session.close()

