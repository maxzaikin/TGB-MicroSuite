# file: services/a-rag/src/agent/engine.py

"""
Core orchestration engine for AI services, including the advanced RAG pipeline.
This version interacts with the LLM via a dedicated inference server.
"""
import asyncio
import logging
import json
from typing import Dict, List, Optional, Tuple

from openai import AsyncOpenAI

from src.agent import prompt_constructor, rag_steps
from src.core.config import settings
from src.core.profiling import log_execution_time
from src.core.schemas.rag_schemas import LoadedDocument, RAGQuery
from src.memory.service import MemoryService
from src.models.embedding_service import embedding_model_service
from src.storage.vec_db.base import VectorStoreRepository
from src.storage.vec_db.factory import get_vector_store_repository

AIEngineComponents = Tuple[Optional["RAGEngine"], Optional[MemoryService]]
KB_COLLECTION_NAME = "knowledge_base"
CHAT_HISTORY_COLLECTION_NAME = "chat_history"
logger = logging.getLogger(__name__)


class RAGEngine:
    """Orchestrates the advanced RAG pipeline using an external LLM service."""

    def __init__(
        self,
        llm_client: AsyncOpenAI,
        memory_service: MemoryService,
        kb_vector_store: VectorStoreRepository,
        chat_history_vector_store: VectorStoreRepository,
    ):
        """Initializes the RAGEngine with all its dependencies."""
        self.llm_client = llm_client
        self.memory = memory_service
        self.kb_vector_store = kb_vector_store
        self.chat_history_vector_store = chat_history_vector_store
        self.query_expansion = rag_steps.QueryExpansionStep(llm_client=self.llm_client)
        self.self_query = rag_steps.SelfQueryStep()
        self.reranker = rag_steps.CrossEncoderReranker()
        

    @log_execution_time("Full RAG Context Retrieval")
    async def _retrieve_context(self, user_prompt: str) -> List[LoadedDocument]:
        """Executes the full retrieval pipeline with hybrid search and a robust fallback."""
        rag_query = RAGQuery(original_query=user_prompt)
        rag_query = await self.query_expansion.transform(rag_query)
        rag_query = await self.self_query.transform(rag_query)

        search_queries = rag_query.get_queries_for_search()
        
        # --- [FIX] Correct implementation of the fallback logic ---
        candidate_docs_map = {}
        # 1. First, try searching with the extracted filters if they exist.
        if rag_query.filters:
            logger.info(f"Attempting search with filters: {rag_query.filters}")
            search_tasks_with_filters = [
                self.kb_vector_store.search(
                    query_text=q,
                    query_embedding=embedding_model_service.get_embedding(q),
                    top_k=10,
                    filters=rag_query.filters,
                )
                for q in search_queries
            ]
            results_from_searches = await asyncio.gather(*search_tasks_with_filters)
            
            # Populate the map with results from the filtered search
            candidate_docs_map = {str(doc.id): doc for sublist in results_from_searches for doc in sublist}

        # 2. If the filtered search returned no results, or if there were no filters
        #    to begin with, perform a search without filters.
        if not candidate_docs_map:
            if rag_query.filters:
                 logger.warning("Filtered search returned no results. Performing fallback search without filters.")
            else:
                 logger.info("No filters extracted. Performing standard search without filters.")
                 
            search_tasks_no_filters = [
                self.kb_vector_store.search(
                    query_text=q,
                    query_embedding=embedding_model_service.get_embedding(q),
                    top_k=10,
                    filters=None,  # Explicitly no filters
                )
                for q in search_queries
            ]
            fallback_results = await asyncio.gather(*search_tasks_no_filters)
            candidate_docs_map = {str(doc.id): doc for sublist in fallback_results for doc in sublist}
        # --- End of fix ---

        all_retrieved_docs = list(candidate_docs_map.values())
        
        final_docs = await self.reranker.rerank(
            query=rag_query, documents=all_retrieved_docs, top_k=3
        )
        return final_docs

    async def generate_response(self, user_id: str, user_prompt: str) -> Dict[str, str]:
        """Generates a dual response by making API calls to the LLM server."""
        logger.info(f"Processing DUAL chat response for user '{user_id}'...")
        
        retrieved_docs = await self._retrieve_context(user_prompt)
        retrieved_context_chunks = [doc.content for doc in retrieved_docs]
        history = await self.memory.get_history(user_id)

        rag_messages_for_api = prompt_constructor.build_chat_prompt(
            history=history,
            user_prompt=user_prompt,
            kb_context_chunks=retrieved_context_chunks,
            chat_context_chunks=[]
        )
        llm_only_messages_for_api = prompt_constructor.build_chat_prompt(
            history=history,
            user_prompt=user_prompt,
            kb_context_chunks=[],
            chat_context_chunks=[]
        )
        
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                "Payload for RAG LLM call:\n%s",
                json.dumps(rag_messages_for_api, indent=2)
            )
            logger.debug(
                "Payload for LLM-Only call:\n%s",
                json.dumps(llm_only_messages_for_api, indent=2)
            )
        
        rag_response_task = self.llm_client.chat.completions.create(
            model=settings.LLM_MODEL_NAME,
            messages=rag_messages_for_api,
            temperature=0.7,
            max_tokens=1024,
        )
        llm_response_task = self.llm_client.chat.completions.create(
            model=settings.LLM_MODEL_NAME,
            messages=llm_only_messages_for_api,
            temperature=0.7,
            max_tokens=1024,
        )
        
        try:
            rag_response, llm_response = await asyncio.gather(rag_response_task, llm_response_task)
        except Exception as e:
            logger.error(f"An error occurred during LLM API call: {e}", exc_info=True)
            return {
                "rag_answer": "Sorry, I encountered an error while contacting the AI model with context.",
                "llm_answer": "Sorry, I encountered an error while contacting the AI model."
            }
        
        rag_answer = rag_response.choices[0].message.content.strip() if rag_response.choices[0].message.content else ""
        llm_answer = llm_response.choices[0].message.content.strip() if llm_response.choices[0].message.content else ""

        await self.memory.add_message_to_history(user_id=user_id, role="user", content=user_prompt)
        await self.memory.add_message_to_history(user_id=user_id, role="assistant", content=rag_answer)

        return {"rag_answer": rag_answer, "llm_answer": llm_answer}


def initialize_ai_services() -> AIEngineComponents:
    """Initializes and returns all core AI services."""
    logger.info("--- AI Services Initialization (Client-Server): START ---")
    
    llm_client = AsyncOpenAI(
        base_url=settings.LLM_SERVER_BASE_URL,
        api_key="not-needed-for-local-server"
    )
    
    try:
        kb_store = get_vector_store_repository(
            collection_name=KB_COLLECTION_NAME,
            embedding_dimension=settings.EMBEDDING_DIMENSION
        )
        chat_history_store = get_vector_store_repository(
            collection_name=CHAT_HISTORY_COLLECTION_NAME,
            embedding_dimension=settings.EMBEDDING_DIMENSION
        )
    except Exception:
        logger.exception("FATAL: Could not initialize Vector Store Repositories.")
        return None, None
        
    memory_service = MemoryService(
        llm_client=llm_client,
        chat_history_store=chat_history_store
    )
    
    rag_engine = RAGEngine(
        llm_client=llm_client,
        memory_service=memory_service,
        kb_vector_store=kb_store,
        chat_history_vector_store=chat_history_store
    )
    logger.info("Advanced RAGEngine (Client Mode) initialized successfully.")
        
    return rag_engine, memory_service