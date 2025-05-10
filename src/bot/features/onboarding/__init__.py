"""
tgrambuddy/src/bot/features/onboarding/__init__.py

TgramBuddy - A solution for building and managing Telegram bots.
Copyright (c) 2025 Maks V. Zaikin
Released by 01-May-2025 under the MIT License.
"""
from .start_router import start_command_router

def get_start_command_router():
    return start_command_router
