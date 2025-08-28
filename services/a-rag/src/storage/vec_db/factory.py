# file: services/a-rag/src/storage/vec_db/factory.py

"""
Factory for creating vector store repository instances.

This module reads the application's configuration and instantiates the
correct vector database repository. Note that for async repositories,
the `.initialize()` method must be called after creation.
"""
import logging

from src.core.config import settings
from src.storage.vec_db.base import VectorStoreRepository
# from src.storage.vec_db.chroma import ChromaRepository # Would need an async version
from src.storage.vec_db.qdrant import QdrantRepository

logger = logging.getLogger(__name__)


def get_vector_store_repository(
    collection_name: str,
    embedding_dimension: int 
) -> VectorStoreRepository:
    """
    Factory function to get the configured vector store repository instance.

    Reads VECTOR_DATABASE_TYPE from settings and instantiates the correct
    repository with the appropriate settings.

    Args:
        collection_name: The name of the collection for the repository.
        embedding_dimension: The dimension of vectors that will be stored.

    Returns:
        An uninitialized instance of a class that adheres to the
        VectorStoreRepository interface.

    Raises:
        ValueError: If an unsupported vector database type is configured.
    """
    db_type = settings.VECTOR_DATABASE_TYPE.lower()
    
    logger.info(f"Creating vector store repository of type '{db_type}' for collection '{collection_name}'.")
    
    if db_type == 'qdrant':
        return QdrantRepository(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT,
            collection_name=collection_name,
            embedding_dimension=embedding_dimension
        )
    # elif db_type == 'chroma':
    #     return ChromaRepository(...)
    else:
        logger.error(f"Unsupported vector db type requested: {db_type}")
        raise ValueError(f"Unsupported vector db type: '{db_type}'")