# file: services/a-rag/src/app/main.py

"""
Main entry point for the A-RAG API service's FastAPI application.

This module initializes the FastAPI application, sets up middleware, manages the
application's lifespan (startup/shutdown events), and includes all API routers.
It is refactored to work with a decoupled, service-oriented architecture where
the LLM runs as a separate inference server.
"""
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.agent import engine as rag_engine
from src.api.endpoints import akey_router, auth_router, llm_router, memory_router
from src.core.config import settings
from src.core.profiling import log_execution_time
from src.storage.rel_db.db_adapter import DBAdapter
from src.storage.redis_client import redis_client

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Handles application startup/shutdown events, including async initialization.

    On startup, it initializes:
    - The RAGEngine instance, which encapsulates the retrieval pipeline and
      holds the client for the external LLM server.
    - The MemoryService for conversational history.
    - The database adapter for relational data.
    """
    logging.info(f"--- Service '{settings.PROJECT_NAME}' is starting up ---")

    with log_execution_time("Total AI Services Initialization"):
        rag, mem = rag_engine.initialize_ai_services()
        
        if rag:
            logging.info("Performing async initialization of vector stores...")
            await rag.kb_vector_store.initialize()
            await rag.chat_history_vector_store.initialize()
            logging.info("Vector stores initialized successfully.")

        # Store the main service instances in the application state.
        app.state.rag_engine = rag
        app.state.memory_service = mem

    if app.state.rag_engine:
        logging.info("Advanced RAGEngine (Client Mode) initialized.")
    if app.state.memory_service:
        logging.info("MemoryService initialized.")

    app.state.db_adapter = DBAdapter()
    logging.info("DBAdapter (SQL) initialized.")
    logging.info("--- Application startup complete. Ready to serve requests. ---")

    yield

    # --- Application Shutdown ---
    if hasattr(app.state, "db_adapter") and app.state.db_adapter:
        await app.state.db_adapter.close()
        logging.info("DBAdapter connections closed.")

    await redis_client.close()
    logging.info("Redis client connection closed.")
    logging.info("--- Service shutdown complete. ---")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
app.include_router(llm_router.router, prefix=f"{settings.API_V1_STR}/llm", tags=["LLM & RAG"])
app.include_router(akey_router.router, prefix=f"{settings.API_V1_STR}/api-keys", tags=["API Key Management"])
app.include_router(memory_router.router, prefix=f"{settings.API_V1_STR}/memory", tags=["Memory Management"])


@app.get("/", tags=["Root"], include_in_schema=False)
async def read_root():
    """Root endpoint for basic health check and welcome message."""
    return {"message": f"Welcome to the {settings.PROJECT_NAME}! API docs at /docs"}