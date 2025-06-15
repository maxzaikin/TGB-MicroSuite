"""
file: TGB-MicroSuite/services/tg-gateway/src/bot/middleware/db_middleware.py

Database Middleware for Aiogram.

This module provides a middleware that handles the lifecycle of a database
session for each incoming update. It ensures that every handler that needs
database access receives an active session.
"""

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class DbSessionMiddleware(BaseMiddleware):
    """
    Middleware that injects a SQLAlchemy AsyncSession into handler data.

    This middleware is responsible for creating a new database session for each
    incoming event, making it available to the handler, and ensuring the session
    is properly closed after the handler has finished its work.
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        """
        Initializes the middleware with a SQLAlchemy session factory.

        Args:
            session_factory: An async_sessionmaker instance that creates
                             new database sessions.
        """
        super().__init__()
        self.session_factory = session_factory

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """
        Executes the middleware logic for each event.
        """
        # Create a new session from the factory for each update.
        async with self.session_factory() as session:
            # Add the active session to the workflow data. Aiogram's dispatcher
            # will then inject it into any handler that type-hints it.
            data["session"] = session

            # Call the next handler in the chain with the active session.
            return await handler(event, data)
