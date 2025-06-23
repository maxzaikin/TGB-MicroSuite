"""
file: services/a-rag/src/agent/engine.rc3.py

Core orchestration engine for AI services, including LLM and RAG.

This module initializes and provides access to all core AI components.
1. The LlamaCPP model adapter for LlamaIndex.
2. The RAG Query Engine for knowledge base retrieval.
It exposes a single function to generate chat responses, which internally
leverages both RAG and conversational memory.

It now manages two distinct RAG pipelines:
1. Knowledge Base RAG: For retrieving factual information from documents.
2. Chat History RAG: For retrieving relevant past messages for associative memory.
"""
import json
import logging
from typing import Dict, List, Optional, Tuple

import chromadb
from llama_index.core import VectorStoreIndex
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.llama_cpp import LlamaCPP
from llama_index.vector_stores.chroma import ChromaVectorStore

from core.config import settings
from core.profiling import log_execution_time
from core.schemas.chat_schemas import ChatMessage
from memory.service import MemoryService
from .prompt_constructor import build_chat_prompt

# --- Type Aliases for clarity ---
AIEngineComponents = Tuple[
    Optional[LlamaCPP],
    Optional[RetrieverQueryEngine],
    Optional[MemoryService],
]

# --- [ISSUE-23] Start of changes: Long-Term Memory ---
KB_COLLECTION_NAME = "knowledge_base"
CHAT_HISTORY_COLLECTION_NAME = "chat_history"
# --- [ISSUE-23] End of changes: Long-Term Memory ---


def initialize_ai_services() -> AIEngineComponents:
    """
    Initializes and returns all core AI services (LLM Adapter and RAG Engine).

    This function is the single entry point for setting up the AI capabilities.
    It loads the model via the LlamaCPP adapter, which makes it compatible with
    LlamaIndex, and then builds the RAG pipeline using that adapter.

    Returns:
        A tuple containing the LlamaCPP adapter and the RAG Query Engine.
        Returns (None, None) if a critical error occurs during initialization.
    """
    logging.info("--- AI Services Initialization: START ---")
    
    # 1. Initialize the LlamaCPP model adapter. This is a mandatory component.
    local_llm_adapter: Optional[LlamaCPP] = None
    try:
        with log_execution_time("LLM Model Loading via LlamaCPP Adapter"):
            # Parameters specific to the llama.cpp model (like n_gpu_layers)
            # must be passed via the `model_kwargs` dictionary.            
            local_llm_adapter = LlamaCPP(
                model_path=str(settings.MODEL_PATH),
                temperature=0.7,
                max_new_tokens=512,
                context_window=4096,
                # Pass model-specific kwargs here
                model_kwargs={"n_gpu_layers": -1},
                # Pass generation-specific kwargs here
                # These will be used as defaults for all generation calls
                generate_kwargs={"stop": ["\nuser:", "user:", "User:", "[INST]", "[/INST]"]},
                verbose=True,
            )
        logging.info("LlamaCPP adapter and underlying model loaded successfully.")
    except Exception:
        logging.exception("FATAL: LlamaCPP adapter initialization failed. AI services will be offline.")
        return None, None, None

    # 2. Initialize shared components for RAG and Memory
    try:
        embed_model = HuggingFaceEmbedding(model_name="all-MiniLM-L6-v2")
        chroma_client = chromadb.HttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)
        chroma_client.heartbeat()
    except Exception:
        logging.exception("FATAL: Could not connect to ChromaDB or load embedding model.")
        return local_llm_adapter, None, None
        
    # --- [ISSUE-23] Start of changes: Long-Term Memory ---
    # 3. Initialize the RAG Pipeline for the Knowledge Base
    kb_query_engine: Optional[RetrieverQueryEngine] = None
    try:
        with log_execution_time("Knowledge Base RAG Pipeline Initialization"):
            kb_collection = chroma_client.get_or_create_collection(KB_COLLECTION_NAME)
            kb_vector_store = ChromaVectorStore(chroma_collection=kb_collection)
            kb_index = VectorStoreIndex.from_vector_store(kb_vector_store, embed_model=embed_model)
            kb_query_engine = kb_index.as_query_engine(llm=local_llm_adapter, similarity_top_k=3)
        logging.info("Knowledge Base RAG Query Engine initialized successfully.")
    except Exception:
        logging.exception("Failed to initialize Knowledge Base RAG pipeline.")

    # 4. Initialize the Vector Store Index for Chat History
    chat_history_index: Optional[VectorStoreIndex] = None
    try:
        with log_execution_time("Chat History Index Initialization"):
            chat_collection = chroma_client.get_or_create_collection(CHAT_HISTORY_COLLECTION_NAME)
            chat_vector_store = ChromaVectorStore(chroma_collection=chat_collection)
            chat_history_index = VectorStoreIndex.from_vector_store(chat_vector_store, embed_model=embed_model)
        logging.info("Chat History Vector Index initialized successfully.")
    except Exception:
        logging.exception("Failed to initialize Chat History Vector Index.")
    
    # 5. Initialize MemoryService, injecting all its dependencies
    local_memory_service: Optional[MemoryService] = None
    if hasattr(local_llm_adapter._model, "tokenizer"):
        tokenizer_callable = local_llm_adapter._model.tokenize
        # --- [ISSUE-24] Start of changes: Summarization Memory ---
        local_memory_service = MemoryService(
            tokenizer=tokenizer_callable,
            llm_adapter=local_llm_adapter,
            chat_history_index=chat_history_index
        )
        # --- [ISSUE-24] End of changes: Summarization Memory ---
    else:
        logging.error("Tokenizer not available. MemoryService could not be initialized.")
    # --- [ISSUE-23] End of changes: Long-Term Memory ---
        
    return local_llm_adapter, kb_query_engine, local_memory_service


async def generate_chat_response(
    llm: LlamaCPP,
    memory_service: MemoryService,
    kb_rag_engine: Optional[RetrieverQueryEngine],
    user_id: str,
    user_prompt: str,
) -> str:
    """
    Generates a contextual chat response using RAG (from two sources) and memory.
    """
    if not llm or not memory_service:
        raise RuntimeError("Core AI services (LLM or Memory) were not provided.")
    
    logging.info(f"Processing chat response for user '{user_id}'...")

    # --- [ISSUE-23] Start of changes: Long-Term Memory ---
    # 1a. RAG Retrieval from Knowledge Base
    kb_context_chunks = []
    with log_execution_time("RAG Knowledge Base Retrieval"):
        if kb_rag_engine:
            try:
                retrieval_response = await kb_rag_engine.aquery(user_prompt)
                kb_context_chunks = [node.get_content() for node in retrieval_response.source_nodes]
                logging.info(f"Retrieved {len(kb_context_chunks)} context chunks from Knowledge Base.")
            except Exception:
                logging.exception("Error during Knowledge Base RAG retrieval.")
    
    # 1b. RAG Retrieval from Chat History
    chat_history_chunks = []
    with log_execution_time("RAG Chat History Retrieval"):
        if memory_service and memory_service.chat_history_index:
            try:
                history_retriever = VectorIndexRetriever(
                    index=memory_service.chat_history_index,
                    vector_store_query_mode="default",
                    vector_store_kwargs={"where": {"user_id": user_id}},
                    similarity_top_k=3,
                )
                retrieved_nodes = await history_retriever.aretrieve(user_prompt)
                chat_history_chunks = [node.get_content() for node in retrieved_nodes]
                logging.info(f"Retrieved {len(chat_history_chunks)} context chunks from Chat History.")
            except Exception:
                logging.exception("Error during Chat History RAG retrieval.")
    # --- [ISSUE-23] End of changes: Long-Term Memory ---

    # 2. Short-Term Memory Retrieval
    with log_execution_time("Redis History Retrieval"):
        history = await memory_service.get_history(user_id)
        logging.info(f"Retrieved {len(history)} messages from short-term memory (Redis).")
    
    # 3. Prompt Construction
    with log_execution_time("Prompt Construction"):
        messages_for_llm = build_chat_prompt(
            history=history,
            user_prompt=user_prompt,
            kb_context_chunks=kb_context_chunks,
            chat_context_chunks=chat_history_chunks,
        )

    # Log the final prompt for debugging
    messages_as_dicts = [msg.model_dump() for msg in messages_for_llm]
    prompt_design_for_log = json.dumps(messages_as_dicts, indent=2, ensure_ascii=False)
    logging.info(f"[LLM_PROMPT] Sending to LLM for user '{user_id}':\n{prompt_design_for_log}")

    # 4. LLM Generation Step
    with log_execution_time("LLM Generation"):
        response = await llm.achat(messages_for_llm)
        generated_text = response.message.content.strip()
    
    logging.info(f"LLM generated response: '{generated_text[:100]}...'")

    # 5. Update All Memories
    with log_execution_time("Memory Update"):
        await memory_service.add_message_to_history(
            user_id=user_id, role="user", content=user_prompt
        )
        await memory_service.add_message_to_history(
            user_id=user_id, role="assistant", content=generated_text
        )

    return generated_text