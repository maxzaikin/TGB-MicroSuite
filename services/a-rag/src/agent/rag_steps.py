# file: services/a-rag/src/agent/rag_steps.py

"""
Defines modular, reusable steps for the advanced RAG pipeline.
"""
import json
import logging
from abc import ABC, abstractmethod
from typing import List

import instructor
from openai import AsyncOpenAI

from src.agent import prompt_templates
from src.core.config import settings
from src.core.schemas.pipeline_schemas import DocumentType
from src.core.schemas.rag_schemas import ExtractedFilters, LoadedDocument, RAGQuery
from src.models.reranker_service import reranker_model_service

logger = logging.getLogger(__name__)


# --- INTERFACES ---

class BaseQueryTransformer(ABC):
    """Abstract interface for pre-retrieval query modifications."""
    @abstractmethod
    async def transform(self, query: RAGQuery, **kwargs) -> RAGQuery:
        """Takes a RAGQuery object and returns a modified version of it."""
        pass

class BaseReranker(ABC):
    """Abstract interface for post-retrieval document refinement."""
    @abstractmethod
    async def rerank(self, query: RAGQuery, documents: List[LoadedDocument], **kwargs) -> List[LoadedDocument]:
        """Takes a list of retrieved documents and returns a refined list."""
        pass


# --- CONCRETE IMPLEMENTATIONS ---

class QueryExpansionStep(BaseQueryTransformer):
    """Expands a query using an external LLM inference service."""
    def __init__(self, llm_client: AsyncOpenAI, num_queries_to_generate: int = 3):
        self.llm_client = llm_client
        self.num_queries = num_queries_to_generate
        self.enabled = self.num_queries > 1
        if not self.enabled:
            logger.warning("QueryExpansionStep is disabled.")

    async def transform(self, query: RAGQuery, **kwargs) -> RAGQuery:
        if not self.enabled:
            query.expanded_queries = [query.original_query]
            return query
        logger.info(f"Expanding original query: '{query.original_query}'")
        prompt = prompt_templates.QUERY_EXPANSION_PROMPT_TEMPLATE.format(
            num_queries=self.num_queries - 1, question=query.original_query
        )
        messages = [{"role": "user", "content": prompt}]
        try:
            response = await self.llm_client.chat.completions.create(
                model=settings.LLM_MODEL_NAME,
                messages=messages,
                temperature=0.0,
            )
            generated_text = response.choices[0].message.content.strip()
            expanded_queries = [q.strip() for q in generated_text.split('\n') if q.strip()]
            all_queries = [query.original_query] + expanded_queries
            query.expanded_queries = list(dict.fromkeys(all_queries))
            logger.info(f"Generated {len(query.expanded_queries)} unique queries.")
        except Exception as e:
            logger.error(f"Failed to expand query: {e}", exc_info=True)
            query.expanded_queries = [query.original_query]
        return query


class SelfQueryStep(BaseQueryTransformer):
    """Extracts filters using an external LLM inference service."""
    def __init__(self):
        instructor_client = AsyncOpenAI(
            base_url=settings.LLM_SERVER_BASE_URL,
            api_key="not-needed-for-local-server",
        )
        self.client = instructor.patch(instructor_client, mode=instructor.Mode.JSON)
        self.llm_model_name = settings.LLM_MODEL_NAME

    async def transform(self, query: RAGQuery, **kwargs) -> RAGQuery:
        logger.info(f"Performing self-query on: '{query.original_query}'")
        try:
            valid_doc_types_str = ', '.join([dt for dt in DocumentType if isinstance(dt, str)])
            prompt_content = prompt_templates.SELF_QUERY_PROMPT_TEMPLATE.format(
                valid_doc_types=valid_doc_types_str, query=query.original_query
            )
            messages = [
                {"role": "system", "content": "You are a world class JSON extractor."},
                {"role": "user", "content": prompt_content}
            ]
            extracted_data: ExtractedFilters = await self.client.chat.completions.create(
                model=self.llm_model_name,
                response_model=ExtractedFilters,
                messages=messages,
                max_retries=1,
            )
            filters = extracted_data.model_dump(exclude_none=True)
            if filters:
                query.filters = filters
                logger.info(f"Self-query extracted filters: {filters}")
            else:
                logger.info("Self-query extracted no filters.")
        except Exception as e:
            logger.error(f"Failed to perform self-query: {e}", exc_info=True)
            query.filters = None
        return query


class CrossEncoderReranker(BaseReranker):
    """Reranks documents using a locally loaded Cross-Encoder model."""
    async def rerank(self, query: RAGQuery, documents: List[LoadedDocument], **kwargs) -> List[LoadedDocument]:
        top_k = kwargs.get("top_k", 3)
        if not documents:
            logger.info("No documents to rerank.")
            return []
        
        logger.info(f"Reranking {len(documents)} documents for query: '{query.original_query[:50]}...'")
        
        # --- [FIX] Enhanced logging for hybrid search observability ---
        logger.info("Top 5 candidates before Cross-Encoder reranking:")
        for i, doc in enumerate(documents[:5]):
            bm25_str = f"{doc.metadata.bm25_score:.4f}" if doc.metadata.bm25_score is not None else "N/A"
            rrf_str = f"{doc.metadata.rrf_score:.4f}" if doc.metadata.rrf_score is not None else "N/A"
            logger.info(
                f"  {i+1}. ID: {str(doc.id)[:8]}, "
                f"Vector Score: {doc.score:.4f}, "
                f"BM25 Score: {bm25_str}, "
                f"RRF Score: {rrf_str}, "
                f"Source: {doc.metadata.source} (Page: {doc.metadata.page_number})"
            )
        # --- End of fix ---

        pairs = [(query.original_query, doc.content) for doc in documents]
        try:
            scores = reranker_model_service.predict(pairs)
        except Exception as e:
            logger.error(f"Failed to get scores from reranker model: {e}", exc_info=True)
            return documents[:top_k]
            
        for doc, score in zip(documents, scores):
            doc.rerank_score = score # Populate the dedicated field
        
        sorted_documents = sorted(documents, key=lambda d: d.rerank_score, reverse=True)
        final_documents = sorted_documents[:top_k]
        
        logger.info(f"Top {len(final_documents)} documents after Cross-Encoder reranking:")
        for i, doc in enumerate(final_documents):
            logger.info(
                f"  {i+1}. Cross-Encoder Score: {doc.rerank_score:.4f}, "
                f"Source: {doc.metadata.source}, Page: {doc.metadata.page_number}"
            )
        return final_documents