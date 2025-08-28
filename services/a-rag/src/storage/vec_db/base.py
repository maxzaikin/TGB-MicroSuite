# file: services/a-rag/src/storage/vec_db/base.py

"""
Defines the abstract interface for a vector store repository.

This module contains the `VectorStoreRepository` abstract base class (ABC),
which defines a common, asynchronous "contract" that all concrete vector
database implementations must adhere to. This allows the rest of the
application to work with any vector database without changing its code,
following the Dependency Inversion Principle.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from src.core.schemas.rag_schemas import EmbeddedChunk, LoadedDocument

VectorStoreQueryResult = List[LoadedDocument]


class VectorStoreRepository(ABC):
    """
    Abstract base class defining the async interface for a vector store.
    
    This ensures that any vector database implementation can be used
    interchangeably by the application.
    """

    @abstractmethod
    async def initialize(self):
        """
        Performs any necessary asynchronous setup, such as ensuring a
        collection exists in the database. Must be called after instantiation.
        """
        ...

    @abstractmethod
    async def add_documents(self, documents: List[EmbeddedChunk]) -> List[str]:
        """
        Asynchronously adds a list of embedded documents (chunks) to the store.

        Args:
            documents: A list of EmbeddedChunk objects.

        Returns:
            A list of IDs of the added documents.
        """
        ...

    @abstractmethod
    async def search(
        self,
        query_text: str,
        query_embedding: List[float],
        top_k: int,
        filters: Optional[Dict[str, Any]] = None,
    ) -> VectorStoreQueryResult:
        """
        Asynchronously performs a search against the vector store.
        Concrete implementations can use hybrid search (vector + keyword).

        Args:
            query_text: The original string query for keyword-based search.
            query_embedding: The vector representation of the query.
            top_k: The number of most similar results to return.
            filters: Optional dictionary of metadata filters to apply.

        Returns:
            A list of LoadedDocument objects representing the retrieved chunks.
        """
        ...

    @abstractmethod
    async def clear_collection(self) -> bool:
        """
        Asynchronously deletes all vectors from the primary collection.

        Returns:
            True if successful, False otherwise.
        """
        ...