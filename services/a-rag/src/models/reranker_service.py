# file: services/a-rag/src/models/reranker_service.py

"""
Singleton service for managing the Cross-Encoder reranking model.

This module ensures that the reranker model is loaded into memory only once
and provides a simple, consistent interface for scoring query-document pairs.
This is crucial for the post-retrieval reranking step in the advanced RAG pipeline.
"""

import logging
from typing import List, Tuple
import torch


from sentence_transformers.cross_encoder import CrossEncoder

# Import settings to get model configuration
from src.core.config import settings

logger = logging.getLogger(__name__)

# Helper function to determine the best available device ---
def get_optimal_device() -> str:
    """Checks for available hardware and returns the best device."""
    if torch.cuda.is_available():
        logger.info("CUDA is available. Using GPU.")
        return "cuda"
    # Add other checks here if needed, e.g., for MPS on Apple Silicon
    logger.info("CUDA not available. Using CPU.")
    return "cpu"


class RerankerModelSingleton:
    """
    A singleton class to manage a CrossEncoder model.

    This pattern prevents the costly operation of loading the model from disk
    on every request.

    Attributes:
        _instance: Stores the single instance of this class.
        model: The loaded CrossEncoder model object.
    """
    _instance = None
    model: CrossEncoder = None

    def __new__(cls):
        if cls._instance is None:
            logger.info("Creating new RerankerModelSingleton instance...")
            cls._instance = super(RerankerModelSingleton, cls).__new__(cls)
            
            try:
                device = get_optimal_device()
                
                # Load the model using settings from our centralized config.
                # The device is shared with the embedding model for simplicity,
                # as they will likely run on the same hardware.
                logger.info(
                    f"Loading reranker model: '{settings.RERANKER_MODEL_NAME}' "
                    f"on device: '{device}'"
                )
                cls._instance.model = CrossEncoder(
                    model_name=settings.RERANKER_MODEL_NAME,
                    device=device,
                    # We can set a default activation function if needed, e.g., sigmoid
                    # default_activation_function=torch.nn.Sigmoid()
                )
                logger.info("Reranker model loaded successfully.")
            except Exception as e:
                logger.critical(f"Failed to load reranker model: {e}", exc_info=True)
                cls._instance.model = None
        return cls._instance

    def predict(self, pairs: List[Tuple[str, str]]) -> List[float]:
        """
        Scores a list of (query, document) pairs for relevance.

        Args:
            pairs: A list of tuples, where each tuple is (query, document_text).

        Returns:
            A list of float scores corresponding to each pair.
        """
        if self.model is None:
            raise RuntimeError("Reranker model is not available or failed to load.")
        
        if not pairs:
            return []
            
        logger.info(f"Reranking a batch of {len(pairs)} query-document pairs...")
        # The `predict` method of CrossEncoder is highly optimized for batch processing.
        scores = self.model.predict(pairs, show_progress_bar=True)
        return scores.tolist()

# Create a single, globally accessible instance for easy import across the application.
reranker_model_service = RerankerModelSingleton()
