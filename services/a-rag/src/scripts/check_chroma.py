# file: services/a-rag/src/scripts/check_chroma.py
"""
A small utility script to connect to the running ChromaDB service
and inspect the contents of a collection.
"""
import chromadb
import json
import logging

from core.config import settings

logging.basicConfig(level=logging.INFO, format="%(message)s")

def check_collection():
    """Connects to ChromaDB, fetches data, and prints it."""
    try:
        logging.info(f"--- Connecting to ChromaDB at {settings.CHROMA_HOST}:{settings.CHROMA_PORT} ---")
        client = chromadb.HttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)
        client.heartbeat() # Check if server is alive
        logging.info("--- Connection successful ---")

        collection_name = "rag_documentation"
        logging.info(f"--- Fetching collection: '{collection_name}' ---")
        collection = client.get_collection(name=collection_name)

        item_count = collection.count()
        logging.info(f"Found {item_count} items in the collection.")

        if item_count > 0:
            logging.info("--- Retrieving first 5 items for inspection ---")
            results = collection.get(limit=5, include=["documents", "metadatas"])
            # Pretty-print the results for readability
            print(json.dumps(results, indent=2))
        
    except Exception:
        logging.exception("An error occurred while trying to check ChromaDB.")

if __name__ == "__main__":
    check_collection()