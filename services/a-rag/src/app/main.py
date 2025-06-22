"""
file: services/a-rag/src/app/main.rc.py

Main entry point for the A-RAG API service's FastAPI application.

This module initializes the FastAPI application, sets up middleware, manages the
application's lifespan (startup/shutdown events), and includes all API routers.
"""
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import application-specific components
from agent import engine as rag_engine
from api.endpoints import akey_router, auth_router, llm_router, memory_router
from core.config import settings
from storage.rel_db.db_adapter import DBAdapter
from storage.redis_client import redis_client
from core.profiling import log_execution_time

# Configure basic structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
)



@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Asynchronous context manager to handle application startup and shutdown events.

    On startup, it initializes all necessary resources:
    - The LLM model.
    - The RAG pipeline.
    - The MemoryService for Redis-based chat history.
    - The database adapter for relational data.

    On shutdown, it gracefully closes all connections.    
    """
    # --- Application Startup ---
    logging.info(f"--- Service '{settings.PROJECT_NAME}' is starting up ---")

    # 1. Load the Language Model
    logging.info("--- Initializing AI Services ---")    
    with log_execution_time("Total AI Services Initialization"):
        llm, rag, mem = rag_engine.initialize_ai_services()
        app.state.llm_adapter = llm
        app.state.kb_query_engine = rag
        app.state.memory_service = mem

    if app.state.llm_adapter:
        logging.info("LLM adapter initialized.")
    if app.state.kb_query_engine:
        logging.info("Knowledge Base RAG pipeline initialized.")
    if app.state.memory_service:
        logging.info("MemoryService (Redis & ChromaDB) initialized.")
    # 3. Initialize services and store them in the app state
    # This makes them available to all request handlers via the `request.app.state`.
    #app.state.memory_service = MemoryService()
    #logging.info("MemoryService (Redis) initialized.")

    app.state.db_adapter = DBAdapter()
    logging.info("DBAdapter (SQL) initialized.")
    
    logging.info("--- Application startup complete. Ready to serve requests. ---")

    yield

    # --- Application Shutdown ---
    # logging.info(f"--- Service '{settings.PROJECT_NAME}' is shutting down ---")

    if hasattr(app.state, "db_adapter") and app.state.db_adapter:
        await app.state.db_adapter.close()
        logging.info("DBAdapter connections closed.")

    await redis_client.close()
    logging.info("Redis client connection closed.")

    logging.info("--- Service shutdown complete. ---")


# Initialize the main FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Configure CORS (Cross-Origin Resource Sharing) middleware
# This allows our frontend (rag-admin) to make requests to this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # TODO: # In production, restrict this to frontend's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Include API Routers ---
# Each router handles a specific domain of the API.
app.include_router(
    auth_router.router,
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["Authentication"],
)
app.include_router(
    llm_router.router,
    prefix=f"{settings.API_V1_STR}/llm",
    tags=["LLM & RAG"],
)
app.include_router(
    akey_router.router,
    prefix=f"{settings.API_V1_STR}/api-keys",
    tags=["API Key Management"],
)
app.include_router(
    memory_router.router,
    prefix=f"{settings.API_V1_STR}/memory",
    tags=["Memory Management"],
)


@app.get("/", tags=["Root"], include_in_schema=False)
async def read_root():
    """Root endpoint for basic health check and welcome message."""
    return {"message": f"Welcome to the {settings.PROJECT_NAME}! API docs at /docs"}