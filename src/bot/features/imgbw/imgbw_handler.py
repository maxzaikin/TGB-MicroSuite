"""
tgrambuddy/src/bot/features/imgbw/imgbw_handler.py

...

TgramBuddy - A solution for building and managing Telegram bots.
Copyright (c) 2025 Maks V. Zaikin
Released by 01-May-2025 under the MIT License.
"""
import logging
from pathlib import Path
import cv2
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    FSInputFile,
    Message
)
from src.database.models import (
    Client,
    Photo
)
from src.bot.core.localization import (
    load_locale,
    localize_message
)

async def process_bw_image(client: Client,
                           client_bw_folder: Path,
                           message: Message,
                           session: AsyncSession):
    """
    process_bw_image
    """
    locale = load_locale(Path(__file__))

    original_photo_path = Path(client.photos[0].path)
    img = cv2.imread(str(original_photo_path))
    bw_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    client_bw_folder.mkdir(parents=True, exist_ok=True)

    bw_photo_name = f"bw_{original_photo_path.name}"
    bw_photo_path = client_bw_folder / bw_photo_name

    cv2.imwrite(str(bw_photo_path), bw_img)

    new_photo = Photo(client_id=client.id, path=str(bw_photo_path))
    session.add(new_photo)
    await session.commit()

    await message.answer_photo(FSInputFile(path=bw_photo_path))

    logging.info('sent: %s', bw_photo_path)

    await message.answer(
        localize_message(locale, "image_processed_successfully"),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=localize_message(locale, "back_to_menu"), callback_data="main_menu")],
            [InlineKeyboardButton(text=localize_message(locale, "upload_another_image"), callback_data="upload_photo")]
        ])
    )
