"""
tgrambuddy/src/bot/features/onboarding/start_handler.py

This module defines /start command handler classusing the Aiogram framework. 
When a user initiates the bot with the `/start` command, 
the job of this handler is repond with welcome instructions.

TgramBuddy - A solution for building and managing Telegram bots.
Copyright (c) 2025 Maks V. Zaikin
Released by 01-May-2025 under the MIT License.
"""
import os
import shutil
import logging
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from src.database.models import Client
from src.bot.core.localization import (
    load_locale,
    localize_message
)

async def start_command_handler(message: Message,
                                session: AsyncSession,
                                ):
    """
    start_command_handler
    """
    locale = load_locale(Path(__file__))
    PVOL_FOLDER = os.getenv("DATA_DIR", "./data")

    #TODO: move client to separate object
    tg_user = message.from_user
    tg_user_id = tg_user.id
    tg_user_name = tg_user.full_name or "Unknown"
    root_folder = Path(PVOL_FOLDER) / 'clients' /str(tg_user_id)

    if root_folder.exists() and root_folder.is_dir():
        shutil.rmtree(root_folder)
        logging.info('-----------> Client: %s folder %s, has been succesfully deleted.',
                     tg_user_name,
                     root_folder)

        client = await session.scalar(select(Client).where(Client.t_id == tg_user_id))
        if client:
            await session.delete(client)
            await session.commit()

        logging.info('-----------> Client data has been deleted from database.')

    #TODO: 
    originals_folder = root_folder / 'originals'
    bw_folder = root_folder / 'bw'
    improved_folder = root_folder / 'improved'

    for folder in [root_folder, originals_folder, bw_folder, improved_folder]:
        folder.mkdir(parents=True, exist_ok=True)
        logging.info('-----------> Folder %s has been created.', folder)


    client = Client(t_id=tg_user_id, name=tg_user_name)
    session.add(client)
    await session.commit()

    logging.info('-----------> Client: telegram_id:%s, name:%s has been add to db',
                 tg_user_id,
                 tg_user_name)
    
    inline_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=localize_message(locale, 
                                                        "upload_photo_text"
                                                        ), callback_data="upload_photo")],
        ]
    )
    
    await message.reply(
        localize_message(locale, "start_message_text"),
        reply_markup=inline_keyboard
    )
