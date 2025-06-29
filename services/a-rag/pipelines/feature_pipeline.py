"""
file: services/a-rag/pipelines/feature_pipeline.py

# --- [ISSUE-26] Implement ZenML for MLOps Pipeline Management ---

Defines the ZenML pipeline for document ingestion and feature creation.

This pipeline orchestrates the steps defined in `pipelines.steps.*` to
create a reproducible and trackable workflow for populating our RAG
knowledge base.
"""
from pathlib import Path
from zenml import pipeline

# Import the steps from our steps module using explicit relative imports.
from .steps.data_processing import (
    ensure_vector_store_exists,
    index_documents,
    load_documents,
)


@pipeline(name="rag_feature_ingestion_pipeline")
def feature_ingestion_pipeline(source_dir: Path, collection_name: str):
    """
    The feature ingestion pipeline for our RAG system.
    
    This version is more robust, passing simple data types between steps
    instead of complex, non-serializable objects.

    Args:
        source_dir: Path to the source directory containing documents.
        collection_name: Name of the ChromaDB collection to use.
    """
    # Each function call here corresponds to a step in the pipeline.
    # ZenML automatically handles passing the output of one step as input
    # to the next, based on the function signatures.

    # Step 1: Load documents from the source directory.
    documents = load_documents(source_dir=source_dir)

    # Step 2: Ensure the vector database is available and the collection exists.
    # This step must complete before indexing can begin.
    validated_collection_name = ensure_vector_store_exists(
        collection_name=collection_name
    )

    # Step 3: Index the documents into the validated collection.
    # This step depends on the outputs of `load_documents` and `ensure_vector_store_exists`.
    # ZenML understands this dependency graph automatically.
    index_documents(
        documents=documents, collection_name=validated_collection_name
    )