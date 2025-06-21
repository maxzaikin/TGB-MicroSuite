# file: services/a-rag/src/agent/engine.py
"""
Core orchestration engine for AI services, including LLM and RAG.

This module initializes and provides access to the core AI components:
1. The LlamaCPP model adapter for LlamaIndex.
2. The RAG Query Engine for knowledge base retrieval.
It exposes a single function to generate chat responses, which internally
leverages both RAG and conversational memory.
"""

import json
import logging
from typing import Dict, List, Optional, Tuple

import chromadb
from llama_index.core import VectorStoreIndex, Settings as LlamaSettings
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


def initialize_ai_services() -> Tuple[Optional[LlamaCPP], Optional[RetrieverQueryEngine],
                                      Optional[MemoryService]]:
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
    
    # 1. Initialize the LlamaCPP model adapter
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
        logging.exception("Fatal error during LlamaCPP adapter initialization. AI services will be unavailable.")
        return None, None, None
    
    # 2. Initialize MemoryService
    # We check for the `tokenize` method on the tokenizer object.
    local_memory_service: Optional[MemoryService] = None
    
    if hasattr(local_llm_adapter._model, "tokenizer") and callable(local_llm_adapter._model.tokenizer):
        tokenizer_callable = local_llm_adapter._model.tokenize
        local_memory_service = MemoryService(tokenizer=tokenizer_callable)
    else:
        logging.error("Tokenizer not available from LLM adapter. MemoryService could not be initialized.")
   
    # 3. Initialize the RAG Pipeline
    local_query_engine: Optional[RetrieverQueryEngine] = None
    try:
        with log_execution_time("RAG Pipeline Initialization"):
            embed_model = HuggingFaceEmbedding(model_name="all-MiniLM-L6-v2")
            chroma_client = chromadb.HttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)
            collection = chroma_client.get_or_create_collection("rag_documentation")
            vector_store = ChromaVectorStore(chroma_collection=collection)
            index = VectorStoreIndex.from_vector_store(vector_store, embed_model=embed_model)
            
            # The query engine will now use the correctly initialized adapter.
            local_query_engine = index.as_query_engine(
                llm=local_llm_adapter,
                similarity_top_k=3
            )
        logging.info("RAG Query Engine initialized successfully.")
    except Exception:
        logging.exception("Failed to initialize RAG pipeline. Query engine will be unavailable.")
        # Still return the llm_adapter so the bot can work without RAG.
    
    return local_llm_adapter, local_query_engine, local_memory_service


async def generate_chat_response(
    llm: LlamaCPP,
    user_id: str,
    user_prompt: str,
    memory_service: MemoryService,
    rag_engine: Optional[RetrieverQueryEngine],
) -> str:
    """
    Generates a contextual chat response using RAG and conversation memory.
    """
    if not llm or not memory_service:
        # This check is a safeguard. The router should have already handled this.
        raise RuntimeError("Core AI services (LLM or Memory) were not provided to generate_chat_response.")
   
    
    logging.info(f"Processing chat response for user '{user_id}'...")

    # 1. RAG Retrieval Step (if the engine is available)
    context_chunks = []
    with log_execution_time("RAG Context Retrieval"):
        if rag_engine:
            try:
                retrieval_response = await rag_engine.aquery(user_prompt)
                context_chunks = [node.get_content() for node in retrieval_response.source_nodes]
                logging.info(f"Retrieved {len(context_chunks)} context chunks for the query.")
            except Exception:
                logging.exception("Error during RAG retrieval. Proceeding without context.")
        else:
            logging.warning("RAG query engine not initialized, skipping knowledge base retrieval.")

    # 2. Short-Term Memory Retrieval
    with log_execution_time("Redis History Retrieval"):
        history = await memory_service.get_history(user_id)
        logging.info(f"Retrieved {len(history)} messages from history for user '{user_id}'.")
    
    # 3. Prompt Construction
    with log_execution_time("Prompt Construction"):
        messages_for_llm = build_chat_prompt(
            history=history,
            user_prompt=user_prompt,
            context_chunks=context_chunks
        )

    # Log the final prompt for debugging
    messages_as_dicts = [msg.model_dump() for msg in messages_for_llm]
    prompt_design_for_log = json.dumps(messages_as_dicts, indent=2, ensure_ascii=False)
    logging.info(
        f"[LLM_PROMPT] Sending to LLM for user '{user_id}':\n{prompt_design_for_log}"
    )

    # 4. LLM Generation Step
    with log_execution_time("LLM Generation"):
        response = await llm.achat(messages_for_llm)
        generated_text = response.message.content.strip()       
        
    
    logging.info(f"LLM generated response: '{generated_text[:100]}...'")

    # 5. Update Short-Term Memory
    with log_execution_time("Redis History Update"):
        await memory_service.add_message_to_history(
            user_id=user_id, role="user", content=user_prompt
        )
        await memory_service.add_message_to_history(
            user_id=user_id, role="assistant", content=generated_text
        )

    return generated_text