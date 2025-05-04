from aiogram.types import CallbackQuery
from aiogram.handlers import BaseHandler
from typing import Any

class UploadPhotoCallbackHandler(BaseHandler[CallbackQuery]):
    async def handle(self) -> Any:
        await self.event.answer("📸 Upload photo feature comming soon.")