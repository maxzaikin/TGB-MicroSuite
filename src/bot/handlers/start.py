""" Comming soon

    _extended_summary_
"""
# TgramBuddy - A solution for building and managing Telegram bots.
# Copyright (c) 2025 Maks V. Zaikin
# Released by 01-May-2025 under the MIT License.
#
from typing import Any
from aiogram.types import Message
from aiogram.handlers import BaseHandler

class StartHandler(BaseHandler[Message]):
    async def handle(self) -> Any:
         await self.event.reply("Hello!")
         
         
#class StartHandler(BaseHandler[Message]):
#    async def handle(self, event: Message, data: dict[str, Any]) -> Any:
#        await event.reply("Hello from OOP handler!")
