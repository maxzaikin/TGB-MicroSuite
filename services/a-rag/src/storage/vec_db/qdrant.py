# file: services/a-rag/src/storage/vec_db/qdrant.py

"""
Qdrant-specific, async-first implementation of the VectorStoreRepository.

This module provides the `QdrantRepository` class, which handles all
asynchronous interactions with a Qdrant vector database and implements
a hybrid search strategy combining vector search with BM25 keyword search.
"""
import asyncio
import logging
from typing import Any, Coroutine, Dict, List, Optional

from qdrant_client import AsyncQdrantClient, models
from qdrant_client.http.models import Filter, FilterSelector, UpdateStatus
from rank_bm25 import BM25Okapi

from src.core.schemas.rag_schemas import ChunkMetadata, EmbeddedChunk, LoadedDocument
from src.storage.vec_db.base import VectorStoreRepository, VectorStoreQueryResult

logger = logging.getLogger(__name__)


class BM25Index:
    """A wrapper for in-memory BM25 indexing and searching."""
    def __init__(self, documents: List[LoadedDocument]):
        self.documents = {str(doc.id): doc for doc in documents}
        if documents:
            logger.info(f"Tokenizing corpus for BM25 with {len(documents)} documents...")
            tokenized_corpus = [doc.content.split() for doc in documents]
            self.bm25 = BM25Okapi(tokenized_corpus)
            logger.info("BM25 tokenization complete.")
        else:
            self.bm25 = None
        logger.info(f"BM25 index created for {len(documents)} documents.")

    def search(self, query: str, top_k: int) -> VectorStoreQueryResult:
        """Performs a BM25 search and returns results in a standard format."""
        if not self.bm25:
            return []
            
        tokenized_query = query.split()
        all_docs = list(self.documents.values())
        doc_scores = self.bm25.get_scores(tokenized_query)
        
        top_n_indices = sorted(range(len(doc_scores)), key=lambda i: doc_scores[i], reverse=True)[:top_k]
        
        results = []
        for i in top_n_indices:
            doc = all_docs[i]
            new_metadata = doc.metadata.model_copy()
            new_metadata.bm25_score = doc_scores[i]
            
            result_doc = LoadedDocument(
                id=doc.id,
                score=0.0,  # Vector score is not applicable here, set to 0.0
                content=doc.content,
                metadata=new_metadata
            )
            results.append(result_doc)
        return results


def reciprocal_rank_fusion(
    results: List[VectorStoreQueryResult], k: int = 60
) -> VectorStoreQueryResult:
    """
    Performs Reciprocal Rank Fusion on multiple lists of search results,
    preserving original vector scores.
    """
    fused_scores: Dict[str, float] = {}
    doc_map: Dict[str, LoadedDocument] = {}

    # --- [FIX] Process vector results first to preserve original vector scores ---
    # Assumption: The first list in 'results' is always from the vector search.
    if not results:
        return []
    vector_results = results[0]
    other_results = results[1:]

    # First, populate the doc_map with vector results.
    # The 'score' field here is the definitive vector similarity score.
    for doc in vector_results:
        doc_id = str(doc.id)
        doc_map[doc_id] = doc

    # Now, process all lists for RRF scoring.
    all_result_lists = [vector_results] + other_results
    for result_list in all_result_lists:
        for rank, doc in enumerate(result_list):
            doc_id = str(doc.id)
            if doc_id not in fused_scores:
                fused_scores[doc_id] = 0.0
                # If a doc was only in a non-vector list (e.g., BM25), add it to the map.
                if doc_id not in doc_map:
                    doc_map[doc_id] = doc
            
            # If the doc is from a BM25 result, enrich the canonical doc in doc_map.
            if doc.metadata.bm25_score is not None:
                doc_map[doc_id].metadata.bm25_score = doc.metadata.bm25_score

            fused_scores[doc_id] += 1.0 / (k + rank + 1)
    # --- End of fix ---

    reranked_ids = sorted(fused_scores.keys(), key=lambda id: fused_scores[id], reverse=True)

    final_results = []
    for doc_id in reranked_ids:
        doc = doc_map[doc_id]
        # Store the final RRF score in metadata for observability.
        doc.metadata.rrf_score = fused_scores[doc_id]
        final_results.append(doc)

    return final_results


class QdrantRepository(VectorStoreRepository):
    """Asynchronous, concrete repository for Qdrant with Hybrid Search."""

    def __init__(self, host: str, port: int, collection_name: str, embedding_dimension: int):
        self.collection_name = collection_name
        self.embedding_dimension = embedding_dimension
        self.client = AsyncQdrantClient(host=host, port=port)
        self.bm25_index: Optional[BM25Index] = None

    async def initialize(self):
        await self._ensure_collection_exists()
        await self._build_bm25_index()

    async def _ensure_collection_exists(self) -> None:
        try:
            await self.client.get_collection(collection_name=self.collection_name)
        except Exception:
            logger.info(f"Collection '{self.collection_name}' not found. Creating new collection.")
            await self.client.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=self.embedding_dimension, distance=models.Distance.COSINE),
            )
            logger.info(f"Successfully created collection '{self.collection_name}'.")

    async def _build_bm25_index(self) -> None:
        logger.info("Building in-memory BM25 index from Qdrant data...")
        try:
            all_points, _ = await self.client.scroll(
                collection_name=self.collection_name, limit=10_000,
                with_payload=True, with_vectors=False,
            )
            
            if not all_points:
                logger.warning("No documents in Qdrant to build BM25 index.")
                self.bm25_index = BM25Index(documents=[])
                return

            all_docs = [
                LoadedDocument(
                    id=point.id, score=0.0, # This score is irrelevant for the index
                    content=(point.payload or {}).pop("content", ""),
                    metadata=ChunkMetadata(**(point.payload or {}))
                )
                for point in all_points
            ]
            
            self.bm25_index = BM25Index(documents=all_docs)
        except Exception as e:
            logger.error(f"Failed to build BM25 index: {e}", exc_info=True)
            self.bm25_index = BM25Index(documents=[])

    async def add_documents(self, documents: List[EmbeddedChunk]) -> List[str]:
        if not documents: return []
        points_to_upsert = [
            models.PointStruct(
                id=doc.id, vector=doc.embedding,
                payload={**doc.metadata.model_dump(exclude_none=True), "content": doc.content},
            ) for doc in documents
        ]
        operation_info = await self.client.upsert(
            collection_name=self.collection_name, wait=True, points=points_to_upsert
        )
        if operation_info.status != UpdateStatus.COMPLETED:
            logger.error(f"Failed to add documents. Status: {operation_info.status}")
            return []
        logger.info(f"Successfully added {len(points_to_upsert)} documents to Qdrant.")
        await self._build_bm25_index()
        return [doc.id for doc in documents]

    async def search(
        self, query_text: str, query_embedding: List[float], top_k: int,
        filters: Optional[Dict[str, Any]] = None,
    ) -> VectorStoreQueryResult:
        vector_search_task = self._vector_search(query_embedding, top_k * 2, filters)
        bm25_search_task = self._bm25_search(query_text, top_k * 2)

        vector_results, bm25_results = await asyncio.gather(vector_search_task, bm25_search_task)

        logger.info(f"Fusing {len(vector_results)} vector results and {len(bm25_results)} BM25 results.")
        # Pass vector results first, as assumed by the RRF function
        fused_results = reciprocal_rank_fusion([vector_results, bm25_results])
        
        return fused_results[:top_k]

    async def _vector_search(
        self, query_embedding: List[float], top_k: int,
        filters: Optional[Dict[str, Any]] = None
    ) -> VectorStoreQueryResult:
        qdrant_filter = None
        if filters:
            must_conditions = [
                models.FieldCondition(key=key, match=models.MatchValue(value=value))
                for key, value in filters.items()
            ]
            if must_conditions: qdrant_filter = Filter(must=must_conditions)

        search_result = await self.client.search(
            collection_name=self.collection_name, query_vector=query_embedding,
            query_filter=qdrant_filter, limit=top_k, with_payload=True,
        )
        return [
            LoadedDocument(
                id=point.id, score=point.score,
                content=(point.payload or {}).pop("content", ""),
                metadata=ChunkMetadata(**(point.payload or {}))
            ) for point in search_result
        ]
    
    async def _bm25_search(self, query: str, top_k: int) -> VectorStoreQueryResult:
        if not self.bm25_index:
            logger.warning("BM25 index not available. Skipping keyword search.")
            return []
        return self.bm25_index.search(query, top_k)

    async def clear_collection(self) -> bool:
        try:
            await self.client.delete(
                collection_name=self.collection_name,
                points_selector=FilterSelector(filter=Filter(must=[])), wait=True,
            )
            logger.info(f"Successfully cleared collection '{self.collection_name}'.")
            self.bm25_index = BM25Index(documents=[])
            return True
        except Exception as e:
            logger.error(f"Failed to clear collection: {e}", exc_info=True)
            return False