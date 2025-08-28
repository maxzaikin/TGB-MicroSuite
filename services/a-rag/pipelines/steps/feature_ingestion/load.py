# file: services/a-rag/pipelines/steps/feature_ingestion/load.py

"""
ZenML step for loading embedded chunks into the vector database.

This step connects to the vector database using the Repository Pattern.
It bridges the synchronous execution context of a ZenML step with the
asynchronous methods of the vector store repository using `asyncio.run`.
"""

import asyncio
import logging
from datetime import datetime, timezone
# --- [FIX] Import `Tuple` from the `typing` module ---
from typing import Annotated, List, Tuple

from zenml import get_step_context, log_artifact_metadata, step

from src.core.config import settings
from src.core.schemas.rag_schemas import EmbeddedChunk
from src.storage.vec_db.factory import get_vector_store_repository

logger = logging.getLogger(__name__)


@step
def load_to_vector_db(
    embedded_chunks: List[EmbeddedChunk],
    collection_name: str,
) -> Annotated[bool, "loading_complete"]:
    """
    Loads a list of embedded chunks into the configured vector database.

    This step uses a factory to get the correct database repository and then
    uses `asyncio.run()` to execute its async methods from within this
    synchronous ZenML step.

    Args:
        embedded_chunks: The list of EmbeddedChunk objects to load.
        collection_name: The name of the vector database collection.

    Returns:
        True if the loading was successful.
    """
    if not embedded_chunks:
        logger.warning("No chunks to load. Step is finishing.")
        step_context = get_step_context()
        log_artifact_metadata(
            artifact_name="loading_complete",
            metadata={"status": "skipped", "num_chunks_loaded": 0},
        )
        return True

    logger.info(f"Starting 'load_to_vector_db' step for {len(embedded_chunks)} chunks.")
    
    try:
        vector_store_repo = get_vector_store_repository(
            collection_name=collection_name,
            embedding_dimension=settings.EMBEDDING_DIMENSION
        )
        
        async def _async_load() -> Tuple[List[str], str]:
            """A nested async function to interact with the async repository."""
            await vector_store_repo.initialize()

            timestamp = datetime.now(timezone.utc).isoformat()
            for chunk in embedded_chunks:
                chunk.metadata.timestamp = timestamp

            logger.info(f"Clearing collection '{collection_name}' before ingestion.")
            await vector_store_repo.clear_collection()
            
            added_ids = await vector_store_repo.add_documents(embedded_chunks)
            
            return added_ids, timestamp

        added_ids, timestamp = asyncio.run(_async_load())
        
        if len(added_ids) != len(embedded_chunks):
            logger.warning(
                f"Mismatch in loaded documents. Expected {len(embedded_chunks)}, "
                f"but repository reported loading {len(added_ids)}."
            )

        step_context = get_step_context()
        log_artifact_metadata(
            artifact_name="loading_complete",
            metadata={
                "vector_db_type": settings.VECTOR_DATABASE_TYPE,
                "collection_name": collection_name,
                "num_chunks_loaded": len(added_ids),
                "ingestion_timestamp_utc": timestamp,
            },
        )

        logger.info(f"Step finished. Successfully loaded {len(added_ids)} documents.")
        return True

    except Exception as e:
        logger.error(f"Failed to load documents to vector database: {e}", exc_info=True)
        raise