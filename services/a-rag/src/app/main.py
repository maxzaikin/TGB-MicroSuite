"""
file: TGB-MicroSuite/services/a-rag/src/api/main.py

Main entry point for the Agentic RAG service's FastAPI application.

This module initializes the FastAPI application, sets up middleware (e.g., CORS),
manages the application's lifespan (startup/shutdown events like loading models
and initializing database connections), and includes all the API routers from
the `endpoints` directory.
"""

import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agent import engine as llm_engine
from api.endpoints import (
    akey_router,
    auth_router,
    llm_router,
)
from core.config import settings
from storage.rel_db.db_adapter import DBAdapter

# Basic logging configuration
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


@asynccontextmanager
async def lifespan(tgramllm_app: FastAPI):
    """
    FastAPI lifespan context manager to handle startup and shutdown events.

    On startup:
    - Runs database migrations.
    - Initializes DB adapter and stores in app.state.
    - Loads the LLM model.

    On shutdown:
    - Unloads the LLM model.
    - Closes DB connections.

    Args:
        tgramllm_app (FastAPI): The FastAPI app instance.

    Yields:
        None
    """
    logging.info("TgramLLM service startup attempt...")

    logging.info("Creating instance of DBAdapter...")
    db_adapter_instance = DBAdapter(db_engine="sqlite")
    tgramllm_app.state.db_adapter = db_adapter_instance
    logging.info("DBAdapter initialized and saved in tgramllm_app.state.db_adapter")

    logging.info("Loading LLM model...")
    llm_engine.load_llm_model()
    logging.info("LLM model successfully loaded.")

    yield

    logging.info("Stopping service: %s", settings.PROJECT_NAME)
    logging.info("Unloading LLM model...")
    llm_engine.unload_llm_model()
    logging.info("LLM model unloaded.")

    if hasattr(tgramllm_app.state, "db_adapter") and tgramllm_app.state.db_adapter:
        logging.info("Closing DBAdapter sessions...")
        await tgramllm_app.state.db_adapter.close()
        logging.info("DBAdapter sessions closed.")

    logging.info("Service stopped successfully.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# The below middleware is needed in order to allow access to the backend API from react's front
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    auth_router.router, prefix=settings.API_V1_STR + "/auth", tags=["Authentication"]
)

app.include_router(
    llm_router.router, prefix=settings.API_V1_STR + "/llm", tags=["LLM Processing"]
)

app.include_router(
    akey_router.router, prefix=settings.API_V1_STR + "/api-keys", tags=["API KEYS CRUD"]
)


@app.get(
    "/",
    tags=["Root"],
    summary="Root endpoint",
    description="Returns a welcome message and provides the link to the API documentation.",
    response_description="A welcome message including the project name.",
)
async def read_root():
    """
    Root endpoint of the API.

    Returns:
        dict: A welcome message including the project name.
    """
    return {"message": f"Welcome to {settings.PROJECT_NAME}! Docs at /docs"}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting application directly for debug purposes.")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
