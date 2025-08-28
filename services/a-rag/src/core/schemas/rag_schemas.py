# file: services/a-rag/src/core/schemas/rag_schemas.py

"""
Pydantic models for representing data artifacts within the RAG system.

These models provide strict typing and a clear data contract for objects
used during ingestion (e.g., EmbeddedChunk) and retrieval (e.g., LoadedDocument).
"""

from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ChunkMetadata(BaseModel):
    """
    A structured model for chunk metadata to ensure consistency.
    This is what gets stored in the 'payload' of the vector database.
    """
    source: str
    page_number: Optional[int] = None
    chunk_index: int
    document_id: str
    title: Optional[str] = None
    section: Optional[str] = None
    date_created: Optional[str] = None
    author: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    language: Optional[str] = "en"
    source_type: str
    confidence_score: Optional[float] = None
    score_override: Optional[float] = None
    document_type: Optional[str] = None
    embedding_model: Optional[str] = None
    timestamp: Optional[str] = None
    user_id: Optional[str] = None # Added for chat history filtering

    # --- [NEW] Add fields for hybrid search observability ---
    bm25_score: Optional[float] = Field(default=None, description="Score from BM25 keyword search.")
    rrf_score: Optional[float] = Field(default=None, description="Fused score from Reciprocal Rank Fusion.")
    # --- End of new fields ---


class EmbeddedChunk(BaseModel):
    """
    Represents a chunk with its embedding, ready for the vector DB.
    This is the object created by the 'embed' step.
    """
    id: str = Field(default_factory=lambda: str(uuid4()))
    content: str
    embedding: List[float]
    metadata: ChunkMetadata


class LoadedDocument(BaseModel):
    """
    Represents a document retrieved from a vector store search.
    It's a combination of the chunk's content, its metadata, and scores.
    """
    id: Union[str, int, UUID] # Allow different ID types from various DBs
    content: str
    score: float # The original vector similarity score from the vector DB
    metadata: ChunkMetadata
    
    rerank_score: Optional[float] = Field(default=None, description="Score from the final CrossEncoder reranker.")


class RAGQuery(BaseModel):
    """
    Represents a user query as it passes through the RAG pipeline.
    It gets enriched with additional data at each step.
    """
    original_query: str

    expanded_queries: List[str] = Field(
        default_factory=list,
        description="List of queries including the original and generated variations."
    )

    filters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Metadata filters extracted from the original query."
    )

    def get_queries_for_search(self) -> List[str]:
        """
        Returns the definitive list of queries to be used for vector search.
        """
        if self.expanded_queries:
            return self.expanded_queries
        return [self.original_query]


class ExtractedFilters(BaseModel):
    """
    Structured model for metadata filters extracted by the Self-Querying step.
    """
    author: Optional[str] = None
    document_type: Optional[str] = None