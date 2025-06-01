"""
tgrambuddy/src/bot/features/imgupload/__init__.py

TgramBuddy - A solution for building and managing Telegram bots.
Copyright (c) 2025 Maks V. Zaikin
Released by 01-May-2025 under the MIT License.
"""
from .imgupload_router import imgupload_router

def get_imgupload_router():
    """
    get_imgupload_router
    """
    
    return imgupload_router
