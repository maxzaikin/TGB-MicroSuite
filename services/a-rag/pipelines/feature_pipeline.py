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

# Import the steps from our steps module
from .steps.data_processing import (
    index_documents_in_vector_store,
    get_vector_store,
    load_documents,
)


@pipeline(name="rag_feature_ingestion_pipeline")
def feature_ingestion_pipeline(source_dir: Path, collection_name: str):
    """
    The feature ingestion pipeline for our RAG system.

    This ZenML pipeline defines the Directed Acyclic Graph (DAG) for processing
    source documents and indexing them into our vector store.

    Args:
        source_dir: Path to the source directory containing documents.
        collection_name: Name of the ChromaDB collection to use.
    """
    # Each function call here corresponds to a step in the pipeline.
    # ZenML automatically handles passing the output of one step as input
    # to the next, based on the function signatures.

    # Step 1: Load documents from the source directory.
    documents = load_documents(source_dir=source_dir)

    # Step 2: Get a connection to our vector store.
    vector_store = get_vector_store(collection_name=collection_name)

    # Step 3: Index the loaded documents into the vector store.
    # This step depends on the outputs of the previous two steps.
    index_documents_in_vector_store(
        documents=documents, vector_store=vector_store
    )