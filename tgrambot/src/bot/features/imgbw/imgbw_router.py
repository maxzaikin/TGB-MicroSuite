"""
tgrambuddy/src/bot/features/imgbw/imgbw_router.py

This module defines router for convert image to b&w request handling using the Aiogram framework.

TgramBuddy - A solution for building and managing Telegram bots.
Copyright (c) 2025 Maks V. Zaikin
Released by 01-May-2025 under the MIT License.
"""
from aiogram import (
    Router,
    F
)
from aiogram.types import (
    CallbackQuery
)
from sqlalchemy.ext.asyncio import AsyncSession
from .imgbw_callback import imgbw_callback

imgbw_router = Router()

@imgbw_router.callback_query(F.data == "process_bw")
async def on_process_bw_click(callback: CallbackQuery, session: AsyncSession):
    """
    on_process_bw_click
    """
    await imgbw_callback(callback, session)
