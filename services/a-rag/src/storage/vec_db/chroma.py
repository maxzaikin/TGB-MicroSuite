# file: services/a-rag/src/storage/vec_db/chroma.py
"""
ChromaDB-specific implementation of the VectorStoreRepository interface.

This module provides the `ChromaRepository` class. It serves as a fallback
or alternative implementation, allowing the system to use ChromaDB as its
vector store. It uses the `chromadb` library under the hood.
"""

from typing import List

import chromadb
from chromadb.types import Collection

from src.core.config import settings
from src.core.schemas.rag_schemas import EmbeddedChunk, LoadedDocument
from storage.vec_db.legacy.base import VectorStoreRepository, VectorStoreQueryResult

class ChromaRepository(VectorStoreRepository):
    """Concrete implementation of the repository for ChromaDB."""

    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self.client = chromadb.HttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)
        self.collection: Collection = self.client.get_or_create_collection(name=self.collection_name)

    def add_documents(self, documents: List[EmbeddedChunk]) -> List[str]:
        if not documents:
            return []
            
        doc_ids = [str(doc.id) for doc in documents]
        # Filter out documents without embeddings, as Chroma requires them
        docs_with_embeddings = [doc for doc in documents if doc.embedding is not None]
        if not docs_with_embeddings:
            return []
            
        self.collection.add(
            ids=[str(d.id) for d in docs_with_embeddings],
            embeddings=[d.embedding for d in docs_with_embeddings],
            documents=[d.content for d in docs_with_embeddings],
            metadatas=[
                {"document_id": str(d.document_id), **d.metadata} for d in docs_with_embeddings
            ]
        )
        return doc_ids

    def search(self, query_embedding: List[float], top_k: int) -> VectorStoreQueryResult:
        query_results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["metadatas", "documents"]
        )
        
        # Unpack results from Chroma's nested list structure
        ids = query_results['ids'][0]
        contents = query_results['documents'][0]
        metadatas = query_results['metadatas'][0]

        return [
            LoadedDocument(id=doc_id, content=content, metadata=meta)
            for doc_id, content, meta in zip(ids, contents, metadatas)
        ]

    def clear_collection(self) -> bool:
        # Re-creating a collection is the simplest way to clear it in Chroma
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.get_or_create_collection(name=self.collection_name)
        return True