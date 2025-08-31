# file: services/a-rag/src/scripts/check_retrieval.py

"""
A command-line script to verify the RAG retrieval process.

This script performs an end-to-end check of the retrieval part of RAG:
1. Takes a user query as input.
2. Uses the same embedding model as the ingestion pipeline to vectorize the query.
3. Connects to the configured vector database (Qdrant/Chroma).
4. Performs a similarity search in the specified collection.
5. Prints the top retrieved results, including their content, metadata, and score.

This is crucial for debugging and validating the ingestion pipeline's output.
"""

import argparse
import logging
import sys
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ensure the script can find the 'src' module.
# This allows running the script from the service root directory, e.g.,
# `python -m src.scripts.check_retrieval "What is a pipeline?"`
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.core.config import settings
from src.models.embedding_service import embedding_model_service
from storage.vec_db.legacy.factory import get_vector_store_repository


def main():
    """Parses CLI arguments and runs the retrieval check."""
    parser = argparse.ArgumentParser(
        description="Perform a test retrieval from the vector database.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    
    parser.add_argument(
        "query",
        type=str,
        help="The question to search for.",
    )
    parser.add_argument(
        "--collection-name",
        type=str,
        default="main_knowledge_base",
        help="The name of the vector database collection to search in.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="The number of top results to retrieve.",
    )
    
    args = parser.parse_args()

    logger.info("--- Starting Retrieval Verification Script ---")

    try:
        # 1. Vectorize the user query using the singleton service
        logger.info(f"Vectorizing query: '{args.query}'...")
        query_embedding = embedding_model_service.get_embedding(args.query)
        logger.info(f"Query vectorized into a {len(query_embedding)}-dimensional vector.")

        # 2. Get the vector store repository instance from the factory
        logger.info(f"Connecting to '{settings.VECTOR_DATABASE_TYPE}' and collection '{args.collection_name}'...")
        repo = get_vector_store_repository(
            collection_name=args.collection_name,
            embedding_dimension=settings.EMBEDDING_DIMENSION,
        )
        logger.info("Successfully connected to the vector store.")

        # 3. Perform the similarity search
        logger.info(f"Performing similarity search for top {args.top_k} results...")
        search_results = repo.search(query_embedding=query_embedding, top_k=args.top_k)
        
        # 4. Print the results
        if not search_results:
            logger.warning("Search returned no results. The collection might be empty or the query irrelevant.")
        else:
            logger.info("--- Top Search Results ---")
            for i, result in enumerate(search_results):
                # result.metadata is a Pydantic model (ChunkMetadata), so we use attribute access.
                metadata = result.metadata
                source_info = metadata.source if hasattr(metadata, 'source') else 'N/A'
                page_info = f", Page: {metadata.page_number}" if hasattr(metadata, 'page_number') and metadata.page_number is not None else ""

                print(f"\n--- Result {i+1} ---")
                print(f"  Score: {result.score:.4f}")
                print(f"  Source: {source_info}{page_info}")
                # The text of the chunk is an attribute of the top-level result object.
                # It must be `result.content` to match our Pydantic models.
                print(f"  Content: \n\"{result.content.strip()}\"")
                print("--------------------")

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
    
    finally:
        logger.info("--- Retrieval Verification Script Finished ---")


if __name__ == "__main__":
    main()