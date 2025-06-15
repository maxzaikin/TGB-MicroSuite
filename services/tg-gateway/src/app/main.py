"""
file: TGB-MicroSuite/services/tg-gateway/src/app/main.py

Main entry point for the Telegram Gateway service.

This module initializes the Aiogram Bot and Dispatcher, sets up logging,
configures middleware, registers all command and message handlers from their
respective feature slices, and launches the bot's polling loop.
"""

# --- Standard Library Imports ---
import asyncio
import logging
import sys

# --- Third-party Library Imports ---
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# --- Application-specific Imports ---
# Routers from feature slices
from src.bot.features.onboarding.router import onboarding_router
from src.bot.features.rag_chat.router import rag_router

# Middlewares
from src.bot.middleware.db_middleware import DbSessionMiddleware

# Core services and configuration
from src.core.config import settings
from src.core.localization import Localize
from src.storage.rel_db.db_adapter import DBAdapter


async def main() -> None:
    """
    Initializes and runs the Telegram bot.

    This function orchestrates the startup of the bot by:
    1. Setting up structured logging.
    2. Initializing shared services (DBAdapter, Localize).
    3. Creating the main Bot and Dispatcher instances.
    4. Passing shared services into the Dispatcher's workflow data.
    5. Registering essential middlewares.
    6. Including all feature routers.
    7. Starting the bot's polling process to receive updates from Telegram.
    """

    # 1. Initialize structured logging
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logging.info("Initializing bot...")

    # 2. Initialize shared services and adapters
    db_adapter = DBAdapter()
    localize_service = Localize(default_lang="en")

    # Create an object with default properties for the bot
    default_properties = DefaultBotProperties(parse_mode=ParseMode.HTML)

    # Pass the properties object to the Bot constructor
    bot = Bot(token=settings.BOT_TOKEN, default=default_properties)

    dp = Dispatcher()

    # 4. Inject shared services into the workflow data for access in handlers
    dp.workflow_data.update(
        {
            "db_adapter": db_adapter,
            "loc": localize_service,
        }
    )

    # 5. Register middlewares
    # The middleware now gets the session factory directly, not the whole adapter.
    dp.update.middleware(
        DbSessionMiddleware(session_factory=db_adapter.session_factory)
    )
    logging.info("Middlewares have been registered.")

    # 6. Register all feature routers
    dp.include_router(onboarding_router)
    dp.include_router(rag_router)
    logging.info("All routers have been included.")

    # 7. Start the bot's polling loop
    try:
        logging.info("Starting bot polling...")
        await dp.start_polling(bot)
    finally:
        # This block executes on graceful shutdown (e.g., Ctrl+C).
        logging.info("Shutting down bot and resources...")
        await bot.session.close()
        await db_adapter.close()
        logging.info("Shutdown complete.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot execution stopped by user.")
