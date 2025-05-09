#convert_to_bw_callbakc.pyi
mport os
import logging
from aiogram import (
    Router, 
    F
)
from sqlalchemy import select
from aiogram.types import (
    CallbackQuery, 
    Message
)
from aiogram.types import (
    InlineKeyboardMarkup, 
    InlineKeyboardButton
)
from src.database.models import (
    Client, 
    Photo
)
from src.bot.core.t_cc import TelegramClientContext
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path

media_router = Router()

@media_router.callback_query(F.data == "process_bw")
async def process_bw(callback: CallbackQuery):
    tg_user = message.from_user
    tg_user_id = tg_user.id
    tg_user_name = tg_user.full_name or "Unknown"
    root_folder = Path(os.getenv('PVOL_FOLDER')) / 'clients' /str(tg_user_id) 
    await callback.message.answer("⚙️ Converting image to black & white...")
    stmt = (
            select(Photo)
            .where(Photo.client_id == client_id)
            .where(Photo.path.contains('/original/'))  # или просто 'original' если имя может быть в любом месте
        )
        result = await session.scalar(stmt)
    
    
    
    await callback.answer()
