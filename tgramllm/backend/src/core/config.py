"""
tgrambuddy/tgramllm/src/llm/core/config.py

Configuration module for application settings.

Defines the Settings class which loads configuration from environment variables
or a .env file using Pydantic BaseSettings. Supports resolving relative SQLite
database paths to absolute ones based on the project root directory.
"""

from pathlib import Path
import logging
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent  # <root>/tgramllm

class Settings(BaseSettings):
    """
    Application configuration settings loaded from environment variables or .env file.

    Attributes:
        PROJECT_NAME (str): The name of the project.
        API_V1_STR (str): The API version prefix string.
        SECRET_KEY (str): Secret key used for cryptographic operations (e.g., JWT).
        ALGORITHM (str): Algorithm used for token encoding.
        ACCESS_TOKEN_EXPIRE_MINUTES (int): Expiration time in minutes for access tokens.
        DEFAULT_USER_EMAIL (str): Default email for initial user setup.
        DEFAULT_USER_PASSWORD (str): Default password for initial user setup.
        MODEL_PATH_DUMMY (str): Path to a dummy or default ML model.
        ASYNCSQLITE_DB_URL (str): Database URL, typically for an SQLite database with aiosqlite driver.

    Configuration is loaded from the .env file located at the project root directory
    or from environment variables, with environment variables taking precedence.
    """
    PROJECT_NAME: str
    API_V1_STR: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    DEFAULT_USER_EMAIL: str
    DEFAULT_USER_PASSWORD: str

    MODEL_PATH_DUMMY: str
    ASYNCSQLITE_DB_URL: str

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent.parent / ".env",
        env_file_encoding='utf-8',
        extra='ignore'
    )

    def get_db_path(self) -> str:
        """
        Returns the database URL with an absolute path for SQLite databases.

        If the configured database URL uses SQLite with the aiosqlite driver
        and the path is relative, this method resolves it to an absolute path
        based on the project's base directory. For other database
        URLs, it returns the URL unchanged.

        Returns:
            str: The resolved database URL with an absolute path for SQLite,
                or the original URL for other database types.
        """
        if self.ASYNCSQLITE_DB_URL.startswith("sqlite+aiosqlite:///"):
            raw_path = self.ASYNCSQLITE_DB_URL.replace("sqlite+aiosqlite:///", "")
            resolved_path = BASE_DIR / raw_path

            return f"sqlite+aiosqlite:///{resolved_path.as_posix()}"
        return self.ASYNCSQLITE_DB_URL

settings = Settings()
