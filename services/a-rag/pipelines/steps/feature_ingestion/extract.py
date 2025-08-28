# file: services/a-rag/pipelines/steps/feature_ingestion/extract.py

"""
ZenML step for extracting raw documents from a source directory.
"""
import logging
from pathlib import Path
from typing import Annotated, List, Dict

# --- [FIX] Import the robust PyMuPDFReader ---
from llama_index.core import SimpleDirectoryReader
from llama_index.readers.file import PyMuPDFReader
from zenml import get_step_context, step

from src.core.schemas.pipeline_schemas import DocumentType, RawDocument

logger = logging.getLogger(__name__)


@step
def extract_documents(
    source_dir: Path,
) -> Annotated[List[RawDocument], "raw_documents_from_files"]:
    """
    Loads documents from a source directory in a robust manner.

    This step scans a given directory, uses the reliable PyMuPDF for PDFs,
    converts them to `RawDocument` format, and enriches the output artifact
    with metadata.

    Args:
        source_dir: The path to the directory containing source documents.

    Returns:
        A list of `RawDocument` objects.
    """
    logger.info(f"Executing 'extract_documents' step from source: {source_dir}")
    resolved_path = source_dir.resolve()

    if not resolved_path.is_dir():
        error_msg = f"Source directory not found at {resolved_path}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)

    logger.info(f"Scanning for files in: {resolved_path}")

    files_to_process = [p for p in resolved_path.rglob("*.*") if p.is_file()]

    if not files_to_process:
        logger.warning(
            f"No files found in the source directory: {resolved_path}. "
            "The pipeline will continue with an empty dataset."
        )
        return []
    
    logger.info(f"Found {len(files_to_process)} potential files to process.")

    try:
        # --- [FIX] Configure SimpleDirectoryReader to use PyMuPDFReader for .pdf files ---
        # This is the key to fixing the text corruption issue ("c o n t e n t").
        # We define a dictionary mapping file extensions to specific reader instances.
        file_extractor: Dict = {".pdf": PyMuPDFReader()}
        
        reader = SimpleDirectoryReader(
            input_dir=str(resolved_path), 
            recursive=True,
            file_extractor=file_extractor
        )
        # --- End of fix ---

        llama_documents = reader.load_data()

        raw_documents: List[RawDocument] = []
        loaded_files = set()

        for doc in llama_documents:
            file_path = Path(doc.metadata.get("file_path", "unknown"))
            doc_type = DocumentType.from_path(file_path)
            
            if doc_type == DocumentType.UNKNOWN:
                logger.warning(f"Skipping unsupported file: {file_path}")
                continue

            # PyMuPDFReader automatically adds 'page_label' to metadata for each page.
            # This is crucial for citations and context.
            raw_doc = RawDocument(
                content=doc.get_content(),
                source_path=str(file_path),
                document_type=doc_type,
                metadata={
                    "file_name": file_path.name,
                    "file_size_bytes": file_path.stat().st_size if file_path.exists() else 0,
                    **doc.metadata,
                },
            )
            raw_documents.append(raw_doc)
            loaded_files.add(str(file_path))

        logger.info(f"Successfully converted {len(raw_documents)} documents to RawDocument format.")

        step_context = get_step_context()
        step_context.add_output_metadata(
            output_name="raw_documents_from_files",
            metadata={
                "source_directory": str(resolved_path),
                "num_documents_extracted": len(raw_documents),
                "num_unique_files_processed": len(loaded_files),
                "processed_files_list": sorted(list(loaded_files)),
            },
        )
        logger.info("Successfully attached metadata to the output artifact.")
        
        return raw_documents

    except Exception as e:
        logger.error(f"An unexpected error occurred in 'extract_documents': {e}", exc_info=True)
        raise