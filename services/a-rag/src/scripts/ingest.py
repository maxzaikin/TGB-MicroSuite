"""
file: services/a-rag/src/scripts/ingest.py
    deprecated after implementing
    --- [ISSUE-26] Implement ZenML for MLOps Pipeline Management ---

Script to ingest and embed documents into the ChromaDB vector store.

This utility is a self-contained command-line tool for populating the RAG
knowledge base. It accepts a path to a source directory, reads all
supported documents, and processes them into a ChromaDB collection. It is
designed to be robust and user-friendly, providing clear feedback.

"""
import argparse
import logging
from pathlib import Path

import chromadb
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.storage.storage_context import StorageContext
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from chromadb.config import Settings as ChromaSettings

# We need to import settings to connect to ChromaDB
# This assumes the script is run in an environment where `src` is importable
# (e.g., from the service root directory).
from core.config import settings

# Configure structured logging for clear and informative output.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [%(module)s.%(funcName)s] - %(message)s",
)

# Define the name for the collection in ChromaDB.
CHROMA_COLLECTION_NAME = "rag_documentation"


def ingest_documents(source_dir: Path, collection_name: str) -> None:
    """
    The main pipeline function for document ingestion.

    This function orchestrates the entire process, including pre-flight checks,
    document loading, connecting to the database, and indexing.

    Args:
        source_dir: The path to the directory containing source documents.
        collection_name: The name of the collection to create or use in ChromaDB.
    """
    logging.info("--- Document Ingestion Pipeline: START ---")
    logging.info(f"Attempting to read documents from: {source_dir.resolve()}")
    logging.info(f"Target ChromaDB collection: '{collection_name}'")

    # 1. Pre-flight Check: Validate that the source directory exists.
    if not source_dir.is_dir():
        logging.error(f"Source directory not found.")
        # Provide clear, actionable feedback to the user.
        print(f"\n[ERROR] The specified source directory does not exist: {source_dir.resolve()}")
        print("Please create this directory and place your documents inside it.")
        return

    # 2. Load Documents with robust error handling.
    try:
        # SimpleDirectoryReader will scan the directory. If it's empty, it
        # will raise a ValueError, which we handle gracefully.
        reader = SimpleDirectoryReader(input_dir=source_dir, recursive=True)
        documents = reader.load_data()
        
    except ValueError as e:
        # Catch the specific error for an empty directory.
        if "No files found" in str(e):
            logging.warning("Source directory is empty or contains no supported files.")
            # --- ИНСТРУКЦИЯ ДЛЯ ПОЛЬЗОВАТЕЛЯ ---
            print("\n[INFO] The source directory is empty. No documents to ingest.")
            print(f"Please add your files (e.g., .md, .txt, .pdf) to the following directory and run the script again:")
            print(f"  {source_dir.resolve()}")
            print("\n--- Document Ingestion Pipeline: SKIPPED (No data) ---")
            return
        else:
            # Handle other potential ValueErrors during loading.
            logging.exception("An unexpected ValueError occurred while loading documents.")
            return
    except Exception:
        # Catch any other critical errors during the loading process.
        logging.exception("A critical error occurred while loading documents.")
        return

    logging.info(f"Successfully loaded {len(documents)} document(s).")

    # 3. Connect to ChromaDB Vector Store
    try:
        chroma_client = chromadb.HttpClient(
            host=settings.CHROMA_HOST,
            port=settings.CHROMA_PORT,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                is_persistent=True,
                chroma_client_auth_provider=None,
                chroma_client_auth_credentials=None,
            )
        )
        chroma_client.heartbeat()
        logging.info("Successfully connected to ChromaDB service.")
        chroma_collection = chroma_client.get_or_create_collection(collection_name)
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
    except Exception:
        logging.exception("Failed to connect to or configure ChromaDB.")
        print("\n[ERROR] Could not connect to the ChromaDB service. Please ensure it is running.")
        return

    # 4. Initialize Models and Parsers
    embed_model = HuggingFaceEmbedding(model_name="all-MiniLM-L6-v2")
    node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=20)
    logging.info(f"Initialized embedding model ({embed_model.model_name}) and node parser.")

    # 5. Build index and ingest data
    logging.info("Building index and ingesting documents. This may take a while...")
    try:
        VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
            transformations=[node_parser],
            embed_model=embed_model,
            show_progress=True,
        )
        logging.info(f"--- Document Ingestion Pipeline for collection '{collection_name}': COMPLETED ---")
    except Exception:
        logging.exception("Failed during the final indexing and ingestion step.")


def main():
    """Parses command-line arguments and triggers the ingestion process."""
    parser = argparse.ArgumentParser(
        description="Ingest documents into a ChromaDB collection. Provide the path to your documents directory.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "--source-dir",
        dest="source_dir",
        type=Path,
        required=True,
        help="Path to the source directory containing documents to ingest.",
    )
    
    parser.add_argument(
        "--collection",
        dest="collection_name",
        type=str,
        default=CHROMA_COLLECTION_NAME,
        help=f"Name of the ChromaDB collection to use. (Default: {CHROMA_COLLECTION_NAME})",
    )

    args = parser.parse_args()
    ingest_documents(source_dir=args.source_dir, collection_name=args.collection_name)


if __name__ == "__main__":
    main()