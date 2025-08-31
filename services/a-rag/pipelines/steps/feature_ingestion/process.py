# file: services/a-rag/pipelines/steps/feature_ingestion/process.py

"""
ZenML step for cleaning and chunking raw documents.
"""

import logging
from typing import Annotated, List

from zenml import get_step_context, step

# Import our data contracts and processor logic
from src.core.schemas.pipeline_schemas import Chunk, RawDocument
from .processors import get_processor

logger = logging.getLogger(__name__)


@step
def clean_and_chunk_documents(
    documents: List[RawDocument],
    chunk_size: int,
    chunk_overlap: int,
) -> Annotated[List[Chunk], "processed_chunks"]:
    """
    Cleans and chunks documents using a strategy pattern based on document type.

    This step iterates through raw documents, selects the appropriate processor
    (strategy) for each, and applies cleaning and chunking logic.

    Args:
        documents: A list of RawDocument objects from the 'extract' step.
        chunk_size: The target size for text chunks.
        chunk_overlap: The overlap size between consecutive chunks.

    Returns:
        A list of Chunk objects ready for the 'embed' step.
    """
    logger.info(f"Starting 'clean_and_chunk_documents' step for {len(documents)} documents.")
    
    all_chunks: List[Chunk] = []
    for doc in documents:
        try:
            # Factory selects the right strategy based on document type
            processor = get_processor(doc.document_type)
            
            # The strategy processes the document
            processed_chunks = processor.process(
                document=doc,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )
            all_chunks.extend(processed_chunks)
            logger.debug(f"Processed '{doc.source_path}', created {len(processed_chunks)} chunks.")
        except Exception as e:
            logger.error(f"Failed to process document {doc.source_path}: {e}", exc_info=True)
            # We can choose to continue or fail the step. Let's continue.
            continue
            
    # --- [MLOps] Metadata Enrichment ---
    step_context = get_step_context()
    step_context.add_output_metadata(
        output_name="processed_chunks",
        metadata={
            "num_input_documents": len(documents),
            "num_chunks_created": len(all_chunks),
            "total_characters_in_chunks": sum(len(c.content) for c in all_chunks),
            "avg_chars_per_chunk": (sum(len(c.content) for c in all_chunks) / len(all_chunks)) if all_chunks else 0,
        },
    )

    logger.info(f"Step finished. Total chunks created: {len(all_chunks)}.")
    return all_chunks