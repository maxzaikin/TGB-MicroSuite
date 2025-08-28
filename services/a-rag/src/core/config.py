# file: services/a-rag/src/core/config.py
"""
Configuration module for application settings.

Defines the Settings class which loads all configuration from environment
variables or a .env file using Pydantic. It also computes absolute paths for
critical resources like the ML model to ensure path robustness.
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration settings loaded from environment variables.

    This class centralizes all configuration, provides default values, and
    performs validation. It also includes computed properties for derived
    settings like absolute file paths.
    """

    # --- Application Configuration ---
    PROJECT_NAME: str = "A-RAG API Service"
    API_V1_STR: str = "/api/v1"

    # --- Security & JWT Configuration ---
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # --- Default User Credentials ---
    DEFAULT_USER_EMAIL: str
    DEFAULT_USER_PASSWORD: str

    # --- Database Configuration ---
    DATABASE_URL: str

    # --- Model Configuration ---
    # --- [DEPRECATED] ---
    # MODEL_PATH: str
    
    # --- [NEW] LLM Inference Server Configuration ---
    LLM_SERVER_BASE_URL: str
    LLM_MODEL_NAME: str


    # --- Redis Configuration ---
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    # --- [ISSUE-28] Start of changes: Vector DB Migration ---

    # --- Vector Database Type Switch ---
    # Determines which vector database implementation to use.
    # Default is 'qdrant', 'chroma' is the fallback.
    VECTOR_DATABASE_TYPE: Literal["qdrant", "chroma"] = "qdrant"

    # --- ChromaDB Configuration (Fallback) ---
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8000 # Changed to int for type safety

    # --- Qdrant Configuration ---
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333 # Default gRPC port for Qdrant

    # --- [ISSUE-28] End of changes: Vector DB Migration ---
    
    
    # --- Embedding Model Configuration ---
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DEVICE: str = "auto"
    
    # --- [NEW] Reranker Model Configuration ---
    RERANKER_MODEL_NAME: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    
    # Сompute the embedding dimension dynamically later,
    @property
    def EMBEDDING_DIMENSION(self) -> int:
        # This is a simple way to manage dimensions for known models.
        if "all-MiniLM-L6-v2" in self.EMBEDDING_MODEL_NAME:
            return 384
        elif "bge-large-en-v1.5" in self.EMBEDDING_MODEL_NAME:
            return 1024
        # Default or fallback dimension
        return 384

    # --- Pydantic Model Configuration ---
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
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