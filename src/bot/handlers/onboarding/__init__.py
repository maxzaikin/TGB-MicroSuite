from .start_command import StartHandler
from aiogram.filters import Command
from aiogram import Dispatcher

def register_handlers(dp: Dispatcher):
    dp.message.register(StartHandler, Command("start"))