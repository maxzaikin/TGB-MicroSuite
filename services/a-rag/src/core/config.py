# file: services/a-rag/src/core/config.py
"""
Configuration module for application settings.

Defines the Settings class which loads configuration from the .env file
in the project's root directory using Pydantic BaseSettings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration settings loaded from environment variables or .env file.

    Pydantic automatically reads variables from the .env file and environment variables.
    Environment variables will always override values from a .env file.
    """

    # --- Application Configuration ---
    PROJECT_NAME: str
    API_V1_STR: str

    # --- Security & JWT Configuration ---
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # --- Default User Credentials ---
    DEFAULT_USER_EMAIL: str
    DEFAULT_USER_PASSWORD: str

    # --- Model & Database Configuration ---
    MODEL_PATH: str
    DATABASE_URL: str

    # --- Pydantic Model Configuration ---
    # This tells Pydantic to look for a file named '.env' in the current
    # working directory and to load variables from it.
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


# Create a single, reusable instance of the settings.
settings = Settings()
