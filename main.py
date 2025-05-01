#
# TgramBuddy - A solution for building and managing Telegram bots.
# Copyright (c) 2025 Maks V. Zaikin
# Released by 01-May-2025 under the MIT License.
#
"""Main

"""
import asyncio
import logging

from src.bot.core.aiobot import AioBot


# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

async def main():
    """Запускает Telegram-бота."""
    bot_instance = AioBot(token="7753876174:AAEQGEUCQFCo0R-YVnMEZ2chf9OMqnGG0FA")  # Замените на свой токен
    await bot_instance.run()  # Теперь просто await, так как main уже async

if __name__ == "__main__":
    asyncio.run(main())