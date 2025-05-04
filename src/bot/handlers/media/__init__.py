from aiogram import Dispatcher
from .upload_photo_callback import UploadPhotoCallbackHandler

def register_handlers(dp: Dispatcher):
    dp.callback_query.register(
        UploadPhotoCallbackHandler,
        lambda c: c.data == "upload_photo"
    )