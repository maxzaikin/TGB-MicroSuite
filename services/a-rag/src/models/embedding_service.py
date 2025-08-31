# file: services/a-rag/src/models/embedding_service.py

"""
Singleton service for managing the embedding model.

This module ensures that the computationally expensive embedding model is
loaded into memory only once and provides a simple, consistent interface
for creating embeddings. It includes logic to auto-detect the best
available hardware (GPU/CPU).
"""

import logging
from typing import List

import torch  # <--- Import torch for hardware detection
from sentence_transformers import SentenceTransformer

from src.core.config import settings

logger = logging.getLogger(__name__)


# [NEW] Helper function to determine the best device
def get_best_device() -> str:
    """
    Automatically determines the best available device for PyTorch.
    Prioritizes CUDA (NVIDIA GPU), then MPS (Apple Silicon GPU), falls back to CPU.
    """
    if torch.cuda.is_available():
        logger.info("CUDA (NVIDIA GPU) is available. Using 'cuda'.")
        return "cuda"
    # Note: MPS support can sometimes be unstable. For full stability,
    # you might prefer to default to 'cpu' on Mac unless you've tested your setup.
    if torch.backends.mps.is_available():
        logger.info("MPS (Apple Silicon GPU) is available. Using 'mps'.")
        return "mps"
    logger.info("No specialized hardware detected. Using 'cpu'.")
    return "cpu"


class EmbeddingModelSingleton:
    """
    A singleton class to manage a SentenceTransformer model.

    Attributes:
        _instance: Stores the single instance of this class.
        model: The loaded SentenceTransformer model object.
    """
    _instance = None
    model: SentenceTransformer = None

    def __new__(cls):
        if cls._instance is None:
            logger.info("Creating new EmbeddingModelSingleton instance...")
            cls._instance = super(EmbeddingModelSingleton, cls).__new__(cls)
            try:
                # [FIX] Start of changes: Auto-detect device if configured
                device = settings.EMBEDDING_DEVICE
                if device == "auto":
                    # If config is 'auto', we determine the best device programmatically
                    device = get_best_device()
                # [FIX] End of changes

                # Load the model using settings from our centralized config
                logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL_NAME} on device: {device}")
                cls._instance.model = SentenceTransformer(
                    model_name_or_path=settings.EMBEDDING_MODEL_NAME,
                    device=device, # Pass the determined device (e.g., 'cuda' or 'cpu')
                )
                logger.info("Embedding model loaded successfully.")
            except Exception as e:
                logger.critical(f"Failed to load embedding model: {e}", exc_info=True)
                cls._instance.model = None
        return cls._instance

    def get_embedding(self, text: str) -> List[float]:
        """Generates an embedding for a single piece of text."""
        if self.model is None:
            raise RuntimeError("Embedding model is not available.")
        embedding = self.model.encode(text, convert_to_tensor=False)
        return embedding.tolist()

    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generates embeddings for a batch of texts. This is more efficient.
        """
        if self.model is None:
            raise RuntimeError("Embedding model is not available.")
        
        logger.info(f"Generating embeddings for a batch of {len(texts)} texts...")
        embeddings = self.model.encode(
            texts, 
            batch_size=32,
            show_progress_bar=True,
            convert_to_tensor=False
        )
        return embeddings.tolist()

# Create a single, globally accessible instance.
embedding_model_service = EmbeddingModelSingleton()