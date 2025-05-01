""" tgrambuddy/main.py

main.py is a main entry point to tgrambuddy solution

TgramBuddy - A solution for building and managing Telegram bots.
Copyright (c) 2025 Maks V. Zaikin
Released by 01-May-2025 under the MIT License.
"""

import asyncio
import logging
import os
import sys
from dotenv import load_dotenv
from src.bot.core.aiobot import AioBot

load_dotenv()
bot_token: str|None = os.environ.get("BOT_TOKEN")
logging.basicConfig(level=logging.INFO, 
                    stream=sys.stderr,
                    format='%(asctime)s - %(levelname)s - %(message)s')

#logging.basicConfig(level=logging.ERROR, stream=sys.stderr,format='%(asctime)s - %(levelname)s - %(message)s')

if not bot_token:
    logging.error("The environment variable BOT_TOKEN hasn't been found. \
                  Make sure you are running your docker container as follows: \
                  docker run -e BOT_TOKEN=\"YOUR_BOT_TOKEN\" \
                  --name tgrambuddy-container -d tgrambuddy-app ")    
    exit(1)

async def main():
    logging.info(f"Runing bot with. BOT_TOKEN:{bot_token}")
    bot_instance = AioBot(token=bot_token)
    await bot_instance.run()

if __name__ == "__main__":
    asyncio.run(main())