"""
file: TGB-MicroSuite/services/tg-gateway/src/core/config.py

Configuration module for the Telegram Gateway service.

Defines the Settings class which loads all configuration from environment
variables or a .env file using Pydantic's BaseSettings. This provides a single,
validated source of truth for all configuration parameters.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration settings loaded from environment variables.

    Pydantic automatically reads variables from the .env file found in the
    current working directory and from the system's environment variables.
    System environment variables will always override values from a .env file.
    """

    # --- Telegram Bot Configuration ---
    # The secret token for your Telegram Bot, obtained from @BotFather.
    BOT_TOKEN: str

    # --- Database Configuration ---
    # The connection string for the database.
    # e.g., "sqlite+aiosqlite:///local_gateway.db"
    DATABASE_URL: str

    # --- Data Storage Configuration ---
    # The root directory for storing persistent client data (e.g., uploaded images).
    # In a Docker environment, this path will point to a mounted volume.
    DATA_VOLUME_PATH: str = "data"  # A sensible default for local dev

    # --- Pydantic Model Configuration ---
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        # Allow case-insensitive matching for environment variables
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached instance of the application settings.

    The `lru_cache` decorator ensures that the Settings object is created
    only once, the first time this function is called. Subsequent calls
    will return the same cached instance, making it an efficient singleton.

    This pattern also resolves issues with static type checkers like Mypy
    that may complain about missing arguments during direct instantiation.
    """
    return Settings()


# Create a single, globally accessible instance of the settings.
# Any module in the service can now import it via `from core.config import settings`.
settings = get_settings()
