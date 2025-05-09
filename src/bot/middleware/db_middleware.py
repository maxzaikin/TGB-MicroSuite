# src/bot/middleware/db_adapter.py
from typing import Callable, Awaitable, Dict, Any
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from src.database.db_adapter import DBAdapter

class DbAdapterMiddleware(BaseMiddleware):
    def __init__(self, db_adapter: DBAdapter):
        self.db_adapter = db_adapter

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        async with await self.db_adapter.get_session() as session:
            data["session"] = session

        data["db_adapter"] = self.db_adapter
        return await handler(event, data)