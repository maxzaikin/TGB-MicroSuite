# file: services/a-rag/pipelines/feature_ingestion_pipeline.py

from pathlib import Path
from zenml import pipeline

# Import our new, granular steps
from .steps.feature_ingestion.extract import extract_documents
from .steps.feature_ingestion.process import clean_and_chunk_documents
from .steps.feature_ingestion.embed import embed_chunks
from .steps.feature_ingestion.load import load_to_vector_db

# Import settings to use defaults
from src.core.config import settings

@pipeline(name="feature_ingestion_pipeline")
def feature_ingestion_pipeline(
    source_dir: str, # ZenML works better with simple types like str
    collection_name: str = "main_knowledge_base",
    chunk_size: int = 512,
    chunk_overlap: int = 50,
):
    """
    The complete, modular feature ingestion pipeline for our RAG system.

    This pipeline orchestrates the extraction, processing, embedding, and
    loading of documents into the vector database, with each step being
    a distinct, trackable, and reusable component.

    Args:
        source_dir: Path to the source directory containing documents.
        collection_name: Name of the vector database collection to use.
        chunk_size: The target size for text chunks.
        chunk_overlap: The overlap size between consecutive chunks.
    """
    raw_docs = extract_documents(source_dir=Path(source_dir))
    
    chunks = clean_and_chunk_documents(
        documents=raw_docs,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    
    embedded_chunks = embed_chunks(chunks=chunks)
    
    load_to_vector_db(
        embedded_chunks=embedded_chunks,
        collection_name=collection_name,
    )