"""
tgrambuddy/tgramllm/backend/main.py

Main entry point for the TgramLLM backend FastAPI application.
"""

import os
import logging
import asyncio
import subprocess
from contextlib import asynccontextmanager
from pathlib import Path
import uvicorn
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.routers import (
    auth_router,
    llm_router
)
from src.services import engine as llm_engine
from database.db_adapter import DBAdapter
from src.core.security import get_password_hash
from database.models import User

# Basic logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_database_migrations():
    """
    Run Alembic migrations to initialize or update the database schema.
  
    """
    logging.info("Init database and run migrations...")

    try:
        db_url = settings.get_db_path()

        if not db_url:
            logging.error("ASYNCSQLITE_DB_URL not set in settings. Migrations canceled.")
            raise ValueError("ASYNCSQLITE_DB_URL is not configured")

        logging.info("Database URL: %s", db_url)

        if db_url.startswith("sqlite"):
            path_part = db_url.split("///")[-1]

            if path_part and path_part != ":memory:":
                db_file = Path(path_part)
                db_dir = db_file.parent
                db_dir.mkdir(parents=True, exist_ok=True)

                logging.info("DB folder has been created: %s", db_dir.resolve())

        os.environ["DATABASE_URL_ALEMBIC"] = db_url
        logging.info("DATABASE_URL_ALEMBIC: %s", db_url)
        logging.info("alembic upgrade head...")

        project_root_dir = Path(__file__).resolve().parent
        alembic_ini_path = project_root_dir / "alembic.ini"

        if not alembic_ini_path.exists():
            logging.warning("alembic.ini not found at: %s. \
                Attempting to run without explicit -c.", alembic_ini_path)
            alembic_command = ["alembic", "upgrade", "head"]
            cwd_for_alembic = project_root_dir
        else:
            logging.info("Using Alembic configuration: %s", alembic_ini_path)
            alembic_command = ["alembic", "-c", str(alembic_ini_path), "upgrade", "head"]
            cwd_for_alembic = project_root_dir

        process = subprocess.run(
            alembic_command,
            capture_output=True,
            text=True,
            check=False,
            cwd=str(cwd_for_alembic)
        )

        if process.returncode != 0:
            logging.error("Alembic migration error. Exit code: %s", process.returncode)
            logging.error("Stdout: %s", process.stdout)
            logging.error("Stderr: %s", process.stderr)
            raise RuntimeError(f"Alembic migration error: {process.stderr}")
        else:
            logging.info("Alembic migration successfully completed. Stdout: %s", process.stdout)

    except FileNotFoundError:
        logging.error("'alembic' command not found. Make sure Alembic is installed.")
        raise
    except Exception as e:
        logging.error("Error during DB initialization: %s", e, exc_info=True)
        raise


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

    logging.info("Initializing DB...")
    run_database_migrations()

    logging.info("Creating instance of DBAdapter...")
    db_adapter_instance = DBAdapter(db_engine='sqlite')
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

    if hasattr(tgramllm_app.state, 'db_adapter') and tgramllm_app.state.db_adapter:
        logging.info("Closing DBAdapter sessions...")
        await tgramllm_app.state.db_adapter.close()
        logging.info("DBAdapter sessions closed.")

    logging.info("Service stopped successfully.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
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
    auth_router.router,
    prefix=settings.API_V1_STR + "/auth",
    tags=["Authentication"]
)

app.include_router(
    llm_router.router,
    prefix=settings.API_V1_STR + "/llm",
    tags=["LLM Processing"]
)

app.include_router(
    keys_router.router,
    prefix=settings.API_V1_STR + "/api-key",
    tags=["API KEYS CRUD"]
)


@app.get(
    "/",
    tags=["Root"],
    summary="Root endpoint",
    description="Returns a welcome message and provides the link to the API documentation.",
    response_description="A welcome message including the project name."
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
