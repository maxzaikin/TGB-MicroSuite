""" tgrambuddy/src/bot/core/aiobot.py

aiobot.py defines the AioBot class, which encapsulates the logic for
interacting with the Telegram Bot API using the aiogram library.
It handles initialization of the bot and dispatcher, registration of
message handlers, and the main event polling loop.

TgramBuddy - A solution for building and managing Telegram bots.
Copyright (c) 2025 Maks V. Zaikin
Released by 01-May-2025 under the MIT License.
"""
import asyncio
import logging
from aiogram import (
    Bot,
    Dispatcher
)
#from aiogram.filters import (
#    Command,
#    Filter
#)
#from aiogram.types import CallbackQuery
from ..features import (
    onboarding,
)
from ..middleware.db_middleware import DbAdapterMiddleware
from src.database.db_adapter import DBAdapter

class AioBot:

    def __init__(self, token: str, logging: logging, db_adapter:DBAdapter)->None:
        self.bot = Bot(token)
        self.dp = Dispatcher()
        self.logging= logging

        self.dp.message.middleware(DbAdapterMiddleware(db_adapter))
        self.dp.callback_query.middleware(DbAdapterMiddleware(db_adapter))
        
        #self.dp.message.middleware(ClientContextMiddleware())
        #self.dp.callback_query.middleware(ClientContextMiddleware( ))

    def register_handlers(self):
        self.dp.include_router(onboarding.get_start_command_router())
        #self.dp.include_router(media.get_media_router())
                
    async def run(self):
        self.register_handlers()

        try:
            await self.dp.start_polling(self.bot)
        except asyncio.CancelledError:
            self.logging.info("Bot shutdown triggered by keyboard interrupt (Ctrl+C)")
        finally:
             
            #shutdown storage if it supports wait_closed
            storage = self.dp.fsm.storage
            wait_closed = getattr(storage, "wait_closed", None)
            if callable(wait_closed):
                await wait_closed()

            await self.bot.session.close()
            logging.info("Bot and resources closed successfully.")