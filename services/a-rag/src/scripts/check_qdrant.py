# file: services/a-rag/src/scripts/check_qdrant.py

"""
A command-line script to verify the vector database connection and basic operations.

This script is intended for development and diagnostics. It uses the
VectorStoreRepository factory to instantiate a client for the configured
database (e.g., Qdrant, Chroma), and then performs a simple cycle of
operations:
1. Clear the collection to ensure a clean state.
2. Add a few sample documents (embedded chunks).
3. Perform a similarity search.
4. Print the results to the console.

This allows for testing the storage layer in isolation from the main application.

How to test
# Make sure you are in the TGB-MicroSuite/ directory

# Set the PYTHONPATH to include the a-rag service directory
export PYTHONPATH=$(pwd)/services/a-rag

# Run the script using the python interpreter
python services/a-rag/src/scripts/check_vectordb.py

"""

import asyncio
import logging
import uuid
from typing import List

# Configure logging for clear output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Ensure the script can find the 'src' module
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# --- [FIX] ---
# Import the correct and current Pydantic models.
# `EmbeddedChunk` is used for adding data.
# `LoadedDocument` is the result of a search.
from src.core.schemas.rag_schemas import ChunkMetadata, EmbeddedChunk
from storage.vec_db.legacy.factory import get_vector_store_repository
# --- [END FIX] ---

# Use the dimension from our centralized settings for consistency.
from src.core.config import settings

TEST_COLLECTION_NAME = "test_rag_collection"


def generate_dummy_chunks(count: int) -> List[EmbeddedChunk]:
    """Generates a list of mock EmbeddedChunk objects for testing."""
    chunks = []
    doc_id = str(uuid.uuid4())
    for i in range(count):
        metadata = ChunkMetadata(
            source=f"test_document_{i}.txt",
            document_id=doc_id,
            chunk_index=i,
            source_type="txt",
            author="Test Author"
        )
        chunks.append(
            EmbeddedChunk(
                id=str(uuid.uuid4()),
                content=f"This is a test chunk number {i}. It talks about space and cosmology.",
                embedding=[float(i)] * settings.EMBEDDING_DIMENSION,
                metadata=metadata,
            )
        )
    # Add a chunk that is semantically different for search testing
    metadata_cats = ChunkMetadata(
        source="another_document.md",
        document_id=str(uuid.uuid4()),
        chunk_index=0,
        source_type="md",
        author="Another Author"
    )
    chunks.append(
        EmbeddedChunk(
            id=str(uuid.uuid4()),
            content="This chunk is about cats and the internet.",
            embedding=[-1.0] * settings.EMBEDDING_DIMENSION,
            metadata=metadata_cats,
        )
    )
    return chunks


async def main():
    """Main function to run the vector DB check."""
    logging.info("--- Starting Vector Database Verification Script ---")

    try:
        # 1. Get repository instance from the factory
        logging.info(f"Attempting to create repository for collection '{TEST_COLLECTION_NAME}'...")
        repo = get_vector_store_repository(
            collection_name=TEST_COLLECTION_NAME,
            embedding_dimension=settings.EMBEDDING_DIMENSION
        )
        logging.info(f"Successfully created repository of type: {type(repo).__name__}")

        # 2. Clear the collection
        logging.info(f"Clearing collection '{repo.collection_name}'...")
        success = repo.clear_collection()
        if not success:
            logging.error("Failed to clear collection. Aborting.")
            return
        logging.info("Collection cleared successfully.")

        # 3. Add sample documents
        dummy_docs = generate_dummy_chunks(3)
        logging.info(f"Adding {len(dummy_docs)} documents...")
        added_ids = repo.add_documents(dummy_docs)
        if not added_ids or len(added_ids) != len(dummy_docs):
            logging.error("Failed to add documents. Aborting.")
            return
        logging.info(f"Successfully added {len(added_ids)} documents.")

        await asyncio.sleep(1) # Give the DB a moment to index

        # 4. Perform a similarity search
        logging.info("Performing similarity search for 'space exploration'...")
        # This query vector is very similar to the first dummy chunk ("chunk 0")
        query_vector = [0.1] * settings.EMBEDDING_DIMENSION
        
        # --- [FIX] The search method returns LoadedDocument objects ---
        search_results = repo.search(query_embedding=query_vector, top_k=2)
        
        logging.info(f"Search completed. Found {len(search_results)} results.")

        # 5. Print results
        if not search_results:
            logging.warning("Search returned no results.")
        else:
            logging.info("--- Search Results ---")
            for i, result in enumerate(search_results):
                logging.info(f"  Result {i+1}:")
                logging.info(f"    ID: {result.id}")
                logging.info(f"    Score: {result.score:.4f}")
                logging.info(f"    Content: '{result.content}'")
                logging.info(f"    Metadata: {result.metadata.model_dump_json(indent=2)}")
            logging.info("----------------------")

        if search_results and search_results[0].content.startswith("This is a test chunk number 0"):
            logging.info("✅ Verification successful: The top search result is the expected document.")
        else:
            logging.error("❌ Verification failed: The top search result was not the expected document.")

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)
    
    finally:
        logging.info("--- Vector Database Verification Script Finished ---")


if __name__ == "__main__":
    # Note: Our repository methods are currently synchronous.
    # We use asyncio.run() for forward compatibility if they become async.
    asyncio.run(main())