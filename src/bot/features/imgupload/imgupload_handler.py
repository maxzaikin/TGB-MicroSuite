"""
tgrambuddy/src/bot/features/imgupload/imgupload_handler.py

...

TgramBuddy - A solution for building and managing Telegram bots.
Copyright (c) 2025 Maks V. Zaikin
Released by 01-May-2025 under the MIT License.
"""
import os
import logging
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import Message
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from src.database.models import (
    Client,
    Photo
)
from src.bot.core.localization import (
    load_locale,
    localize_message
)

async def save_compressed_image(message: Message,
                                session: AsyncSession,):
    """
    save_uploaded_photo
    """
    locale = load_locale(Path(__file__))
    PVOL_FOLDER = os.getenv("DATA_DIR", "./data")
    
    #TODO: move client to separate object
    tg_user = message.from_user
    tg_user_id = tg_user.id
    tg_user_name = tg_user.full_name or "Unknown"
    root_folder = Path(PVOL_FOLDER) / 'clients' /str(tg_user_id)  

    largest_photo = message.photo[-1]
    file = await message.bot.get_file(largest_photo.file_id)
    file_path = file.file_path
    filename = f"{message.from_user.id}_{file.file_id}.jpg"
    full_path = root_folder / 'originals' / filename

    await message.bot.download_file(file_path, destination=full_path)
    await message.reply(localize_message(locale, "upload_compressed_image_message"))

    logging.info('-----------> Image: %s successfully upload.',full_path)

    result = await session.execute(
        select(Client).where(Client.t_id == tg_user_id)
    )
    client = result.scalar_one_or_none()

    if client is None:
        raise ValueError(f"Client with tg_user_id={tg_user_id} not found")

    photo = Photo(client_id=client.id, path=str(full_path))
    session.add(photo)
    await session.commit()

    logging.info('-----------> Info: %s successfully added to database.', photo.path)

    await message.answer(
        localize_message(locale, "image_process_options_message"),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=localize_message(locale, 
                                                        "convert_to_bw_button_text"), 
                                  callback_data="process_bw")],
            [InlineKeyboardButton(text=localize_message(locale, 
                                                        "improve_img_button_text"), 
                                  callback_data="process_improve")]
        ])
    )

async def save_raw_image(message: Message):
    """
    handle_image_file
    """
    locale = load_locale(Path(__file__))

    allowed_types = ["image/jpeg", 
                     "image/png", 
                     "image/heic"]

    if message.document.mime_type not in allowed_types:
        await message.reply(localize_message(locale, "unsupported_file_type_message"))
        return

    UPLOAD_DIR = os.getenv('CLIENTS_FOLDER')
    filename = f"{message.from_user.id}_{message.document.file_name}"
    full_path = os.path.join(UPLOAD_DIR, filename)

    await message.bot.download(message.document.file_id, destination=full_path)
    await message.reply(localize_message(locale, "upload_raw_image_message"))

    await message.answer(
        localize_message(locale, "image_process_options_message"),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=localize_message(locale, 
                                                        "convert_to_bw_button_text"), 
                                  callback_data="process_bw")],
            [InlineKeyboardButton(text=localize_message(locale, 
                                                        "improve_img_button_text"), 
                                  callback_data="process_improve")]
        ])
    )