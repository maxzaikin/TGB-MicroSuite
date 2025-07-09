"""
file: services/a-rag/pipelines/steps/data_processing.py

# --- [ISSUE-26] Implement ZenML for MLOps Pipeline Management ---

ZenML steps for the document ingestion and processing pipeline.

This module contains atomic, reusable functions that form the building blocks
of our MLOps pipelines. Each function is decorated as a @step, allowing ZenML
to orchestrate, track, and version its execution and artifacts.
"""

import os
import logging
from pathlib import Path
from typing import List, Annotated

import chromadb
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import Document
from llama_index.core.storage.storage_context import StorageContext
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from zenml import step, get_step_context

# We reuse the existing, centralized configuration from the src directory.
# This ensures consistency between the online API and offline pipelines.
from src.core.config import settings

# Configure logging for this module
logger = logging.getLogger(__name__)

@step
def load_documents(
    source_dir: Path,
) -> Annotated[List[Document], "loaded_documents"]:
    """
    ZenML step to load documents and enrich the output artifact with metadata.

    This step loads data from a directory and attaches key metadata to the
    resulting ZenML artifact, providing full traceability and observability.

    Args:
        source_dir: The path to the directory containing source documents.

    Returns:
        A list of LlamaIndex Document objects.
    """
    logger.info(f"Executing step: load_documents from {source_dir}")
    if not source_dir.is_dir():
        raise FileNotFoundError(
            f"Source directory not found at {source_dir.resolve()}"
        )

    try:
        reader = SimpleDirectoryReader(input_dir=source_dir, recursive=True)
        documents = reader.load_data()
        if not documents:
            raise ValueError(
                f"No documents found in source directory: {source_dir.resolve()}"
            )
        logger.info(f"Successfully loaded {len(documents)} document(s).")

        # --- [MLOps] Start of Metadata Enrichment ---

        # 1. Получаем контекст текущего шага пайплайна.
        step_context = get_step_context()

        # 2. Извлекаем и вычисляем полезные метаданные.
        # LlamaIndex сохраняет путь к файлу в `metadata['file_path']`
        # или `metadata['file_name']`. Мы проверим оба варианта.
        loaded_filenames = [
            doc.metadata.get("file_path") or doc.metadata.get("file_name", "unknown") 
            for doc in documents
        ]
        
        # Убираем дубликаты, если один файл был разбит на несколько документов
        unique_filenames = sorted(list(set(loaded_filenames)))

        # Вычисляем общий размер загруженных файлов
        total_size_bytes = sum(
            os.path.getsize(f) for f in unique_filenames if os.path.exists(f)
        )

        # 3. Собираем все метаданные в один словарь.
        # Мы можем логировать все, что считаем важным.
        loading_metadata = {
            "source_directory": str(source_dir.resolve()),
            "num_documents_loaded": len(documents),
            "num_files_loaded": len(unique_filenames),
            "loaded_files": unique_filenames,
            "total_size_bytes": total_size_bytes,
        }
        
        # 4. "Прикрепляем" словарь с метаданными к нашему выходному артефакту.
        # Имя 'output_name' должно совпадать с именем в аннотации типа: "loaded_documents".
        step_context.add_output_metadata(
            output_name="loaded_documents",
            metadata=loading_metadata
        )
        logger.info("Successfully attached metadata to the output artifact.")

        # --- [MLOps] End of Metadata Enrichment ---

        return documents

    except ValueError as e:
        logger.error(f"Failed to load documents: {e}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred during document loading: {e}")
        raise

@step
def ensure_vector_store_exists(
    collection_name: str,
) -> Annotated[str, "collection_name"]:
    """
    ZenML step to ensure the ChromaDB service is available and the
    target collection exists.

    This step acts as a gatekeeper, preventing subsequent steps from running
    if the vector database is not accessible. It returns simple, serializable
    data (the collection name string).

    Args:
        collection_name: The name of the collection to use in ChromaDB.

    Returns:
        The validated collection name, to be passed to the next step.
    """
    logger.info(f"Executing step: ensure_vector_store_exists for collection '{collection_name}'")
    try:
        chroma_client = chromadb.HttpClient(
            host=settings.CHROMA_HOST,
            port=settings.CHROMA_PORT,
            settings=chromadb.config.Settings(anonymized_telemetry=False),
        )
        chroma_client.heartbeat()
        logger.info("Successfully connected to ChromaDB service.")

        chroma_client.get_or_create_collection(collection_name)
        logger.info(f"Collection '{collection_name}' exists or was created.")
        
        # --- ИЗМЕНЕНИЕ ЗДЕСЬ ---
        # Get the context and log metadata for the *output artifact*.
        # The correct method is `add_output_metadata`.
        step_context = get_step_context()
        step_context.add_output_metadata(
            output_name="collection_name", # This must match the output name in Annotated[]
            metadata={
                "chroma_host": settings.CHROMA_HOST,
                "chroma_port": settings.CHROMA_PORT,
                "collection_name": collection_name
            }
        )
        # --- КОНЕЦ ИЗМЕНЕНИЯ ---
        
        return collection_name
    except Exception as e:
        logger.error(f"Failed to connect to or configure ChromaDB: {e}")
        raise ConnectionError("Could not connect to the ChromaDB service.")


@step
def index_documents(
    documents: List[Document], collection_name: str
) -> Annotated[bool, "indexing_complete"]:
    """
    ZenML step to build an index and ingest documents into the vector store.

    This step now receives the collection name and creates its own connection,
    making it self-contained and robust to serialization issues.

    Args:
        documents: The list of documents to index.
        collection_name: The name of the collection to ingest into.

    Returns:
        True if indexing was successful.
    """
    logger.info(
        f"Executing step: index_documents for {len(documents)} documents into '{collection_name}'."
    )
    try:
        # --- Create connection inside the step ---
        chroma_client = chromadb.HttpClient(host=settings.CHROMA_HOST, port=int(settings.CHROMA_PORT))
        chroma_collection = chroma_client.get_collection(collection_name)
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        # --- End of connection creation block ---

        embed_model = HuggingFaceEmbedding(model_name="all-MiniLM-L6-v2")
        node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=20)
        
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        logger.info("Building index and ingesting documents...")
        VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
            transformations=[node_parser],
            embed_model=embed_model,
            show_progress=True,  # Progress will be visible in ZenML logs
        )
        logger.info("Successfully completed document indexing.")
        return True
    except Exception as e:
        logger.error(f"Failed during the indexing and ingestion step: {e}")
        raise