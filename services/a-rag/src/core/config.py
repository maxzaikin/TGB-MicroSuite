# file: services/a-rag/src/core/config.py
"""
Configuration module for application settings.

Defines the Settings class which loads all configuration from environment
variables or a .env file using Pydantic. It also computes absolute paths for
critical resources like the ML model to ensure path robustness.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration settings loaded from environment variables.

    This class centralizes all configuration, provides default values, and
    performs validation. It also includes computed properties for derived
    settings like absolute file paths.
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

    # --- Database Configuration ---
    DATABASE_URL: str

    # --- Model Configuration ---
    # This holds the RELATIVE path to the model from the monorepo root,
    # as defined in the .env file.
    MODEL_PATH: str

    # --- Redis Configuration ---
    REDIS_HOST: str
    REDIS_PORT: int
    
    # --- Chroma Configuration ---
    CHROMA_HOST: str
    CHROMA_PORT: str

    # --- Pydantic Model Configuration ---
    model_config = SettingsConfigDict(
        # Specifies the name of the file to load environment variables from.
        env_file=".env",
        env_file_encoding="utf-8",
        # Allows environment variables to be case-insensitive.
        case_sensitive=False,
        # Ignores any extra fields not defined in this model.
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached, singleton instance of the application settings.

    This uses the lru_cache decorator to ensure the Settings object is
    created and validated only once, the first time this function is called.
    """
    return Settings()


# Create a single, globally accessible instance of the settings for easy import.
settings = get_settings()
