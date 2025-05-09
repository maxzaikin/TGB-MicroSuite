import os
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

@media_router.callback_query(F.data == "upload_photo")
async def upload_photo_callback(callback: CallbackQuery,
                                #client_context: TelegramClientContext
                                ):
    await callback.message.answer("📤 Please upload photo.")
    await callback.answer()

@media_router.message(F.photo)
async def save_uploaded_photo(message: Message,
                              session: AsyncSession,):
    # TODO: move client to separate object
    tg_user = message.from_user
    tg_user_id = tg_user.id
    tg_user_name = tg_user.full_name or "Unknown"
    root_folder = Path(os.getenv('PVOL_FOLDER')) / 'clients' /str(tg_user_id)  

    largest_photo = message.photo[-1]
    file = await message.bot.get_file(largest_photo.file_id)
    file_path = file.file_path
    filename = f"{message.from_user.id}_{file.file_id}.jpg"
    full_path = root_folder / 'originals' / filename

    await message.bot.download_file(file_path, destination=full_path)
    await message.reply("✅ Compressed image file has been successfully uploaded.")
    logging.info(f'-----------> Image: {full_path} successfully upload.')
    
    result = await session.execute(
        select(Client).where(Client.t_id == tg_user_id)
    )
    client = result.scalar_one_or_none()

    if client is None:
        raise ValueError(f"Client with tg_user_id={tg_user_id} not found")

    photo = Photo(client_id=client.id, path=str(full_path))
    session.add(photo)
    await session.commit()    
    
    logging.info(f'-----------> Info: {photo.path} successfully added to database.')
    
    await message.answer(
        "📸 Choose how to process the image:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🖤 Convert to B&W", callback_data="process_bw")],
            [InlineKeyboardButton(text="✨ Improve quality", callback_data="process_improve")]
        ])
    )
    
@media_router.message(F.document)
async def handle_image_file(message: Message):
    allowed_types = ["image/jpeg", "image/png", "image/heic"]
    if message.document.mime_type not in allowed_types:
        await message.reply("❌ Unsupported file type. Our application support only JPG, PNG or HEIC.")
        return

    UPLOAD_DIR = os.getenv('CLIENTS_FOLDER')
    filename = f"{message.from_user.id}_{message.document.file_name}"
    full_path = os.path.join(UPLOAD_DIR, filename)

    await message.bot.download(message.document.file_id, destination=full_path)
    await message.reply("✅ Uncompressed image file has been successfully uploaded.")
    
    await message.answer(
        "📸 Choose how to process the image:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🖤 Convert to B&W", callback_data="process_bw")],
            [InlineKeyboardButton(text="✨ Improve quality", callback_data="process_improve")]
        ])
    )

@media_router.callback_query(F.data == "process_improve")
async def process_improve(callback: CallbackQuery):
    await callback.message.answer("⚙️ Enhancing image quality...")
    # TODO: Добавить  обработку
    await callback.answer()