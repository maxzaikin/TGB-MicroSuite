# file: services/a-rag/pipelines/steps/feature_ingestion/embed.py

"""
ZenML step for creating vector embeddings from text chunks.
"""

import logging
from typing import Annotated, List

from zenml import get_step_context, step

# Import our data contracts and the embedding service
from src.core.config import settings
from src.core.schemas.pipeline_schemas import Chunk
from src.core.schemas.rag_schemas import ChunkMetadata, EmbeddedChunk
from src.models.embedding_service import embedding_model_service

logger = logging.getLogger(__name__)

@step
def embed_chunks(
    chunks: List[Chunk],
) -> Annotated[List[EmbeddedChunk], "embedded_chunks"]:
    """
    Takes a list of text chunks and creates vector embeddings for each.

    This step utilizes a singleton embedding service to ensure the model
    is loaded only once. It processes chunks in batches for efficiency and
    correctly maps rich, propagated metadata to the structured ChunkMetadata model.

    Args:
        chunks: A list of Chunk objects from the 'process' step.

    Returns:
        A list of EmbeddedChunk objects, now with vector embeddings.
    """
    if not chunks:
        logger.warning("No chunks to embed. Returning empty list.")
        return []

    logger.info(f"Starting 'embed_chunks' step for {len(chunks)} chunks.")

    texts_to_embed = [chunk.content for chunk in chunks]
    vector_embeddings = embedding_model_service.get_embeddings_batch(texts_to_embed)

    embedded_chunks: List[EmbeddedChunk] = []
    for i, chunk in enumerate(chunks):
        
        # --- [FIX] Correctly read the now-propagated rich metadata ---
        source_type_value = chunk.metadata.get("document_type", "unknown")
        source_type_str = source_type_value.value if hasattr(source_type_value, 'value') else str(source_type_value)
        
        # LlamaIndex (with PyMuPDFReader) provides the page number in 'page_label'.
        # We also normalize the source path to just the filename for cleaner display.
        source_filename = chunk.metadata.get("file_name", chunk.source_path)

        # Safely parse the page number from the 'page_label' metadata field.
        page_label = chunk.metadata.get("page_label")
        page_number = None
        if page_label:
            try:
                # page_label is a string, we need an integer.
                page_number = int(page_label)
            except (ValueError, TypeError):
                # Handle cases where page_label might not be a parsable number.
                logger.warning(
                    f"Could not parse page_label '{page_label}' to an integer "
                    f"for a chunk in source: {source_filename}."
                )

        structured_metadata = ChunkMetadata(
            source=source_filename,
            document_id=str(chunk.raw_document_id),
            chunk_index=chunk.metadata.get("chunk_index", i),
            page_number=page_number, # Use the safely parsed integer
            title=chunk.metadata.get("title"), # Pass title if available
            source_type=source_type_str,
            embedding_model=settings.EMBEDDING_MODEL_NAME,
            # Other fields will have their default values (e.g., None, [])
        )
        # --- End of fix ---

        # Create the final EmbeddedChunk object with the correct types
        embedded_chunk = EmbeddedChunk(
            id=str(chunk.id),
            content=chunk.content,
            embedding=vector_embeddings[i],
            metadata=structured_metadata,
        )
        embedded_chunks.append(embedded_chunk)

    # --- [MLOps] Metadata Enrichment ---
    step_context = get_step_context()
    step_context.add_output_metadata(
        output_name="embedded_chunks",
        metadata={
            "num_chunks_embedded": len(embedded_chunks),
            "embedding_model": settings.EMBEDDING_MODEL_NAME,
            "embedding_dimension": settings.EMBEDDING_DIMENSION,
        },
    )
    
    logger.info(f"Step finished. Successfully created {len(embedded_chunks)} embeddings.")
    return embedded_chunks