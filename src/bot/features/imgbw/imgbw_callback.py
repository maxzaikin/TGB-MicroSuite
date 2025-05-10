"""
tgrambuddy/src/bot/features/imgbw/imgbw_callback.py

Handles callback queries for the image bw feature.

TgramBuddy - A solution for building and managing Telegram bots.
Copyright (c) 2025 Maks V. Zaikin
Released by 01-May-2025 under the MIT License.
"""
import os
from pathlib import Path
from aiogram.types import CallbackQuery
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from src.bot.features.imgbw.imgbw_handler import process_bw_image
from src.database.models import Client
from src.bot.core.localization import (
    load_locale,
    localize_message
)

async def imgbw_callback(callback: CallbackQuery,
                         session: AsyncSession):
    """
    imgbw_callback
    """
    locale = load_locale(Path(__file__))
    PVOL_FOLDER = os.getenv("DATA_DIR", "./data")
    tg_user = callback.from_user
    tg_user_id = tg_user.id

    root_folder = Path(PVOL_FOLDER) / 'clients' / str(tg_user_id) / 'bw'

    if callback.message:
        await callback.message.answer(localize_message(locale, "bw_convert_in_progress_message"))

    result = await session.execute(
        select(Client)
        .options(selectinload(Client.photos))
        .where(Client.t_id == tg_user_id)
    )
    client = result.scalar_one_or_none()

    if client is None:
        await callback.message.answer(localize_message(locale, "bw_client_not_found_message"))
        return

    await process_bw_image(client, 
                           root_folder, 
                           callback.message,
                           session)
    await callback.answer()
