# file: services/a-rag/pipelines/steps/feature_ingestion/processors.py

"""
Document Processing Strategies.

This module implements the Strategy design pattern for cleaning and chunking
documents. Each processor is tailored for a specific document type.
"""
import logging
import re
from abc import ABC, abstractmethod
from typing import List

from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.core.schemas.pipeline_schemas import Chunk, DocumentType, RawDocument

logger = logging.getLogger(__name__)

# --- Strategy Interface ---

class DocumentProcessor(ABC):
    """Abstract base class for a document processing strategy."""
    @abstractmethod
    def process(self, document: RawDocument, **kwargs) -> List[Chunk]:
        """Cleans and chunks a raw document into a list of Chunk objects."""
        ...

# --- Concrete Strategies ---

class GenericTextProcessor(DocumentProcessor):
    """A generic processor for plain text-like documents (TXT, DOCX, etc.)."""

    def _clean_text(self, text: str) -> str:
        """Basic cleaning: removes multiple newlines and spaces."""
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"\s{2,}", " ", text)
        return text.strip()

    def process(self, document: RawDocument, **kwargs) -> List[Chunk]:
        """Implements the processing for generic text."""
        chunk_size = kwargs.get("chunk_size", 512)
        chunk_overlap = kwargs.get("chunk_overlap", 50)

        cleaned_content = self._clean_text(document.content)
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""],
        )
        
        split_texts = text_splitter.split_text(cleaned_content)
        
        chunks = []
        for i, text in enumerate(split_texts):
            # --- [FIX] Properly propagate metadata from parent document to chunk ---
            # 1. Create a copy of the parent document's metadata dictionary.
            # This ensures that 'file_name', 'page_label', etc. are preserved.
            chunk_metadata = document.metadata.copy()
            
            # 2. Add or update chunk-specific metadata.
            chunk_metadata["chunk_index"] = i
            # --- End of fix ---

            chunks.append(
                Chunk(
                    content=text,
                    raw_document_id=document.id,
                    source_path=document.source_path,
                    metadata=chunk_metadata
                )
            )
        return chunks


class PdfProcessor(GenericTextProcessor):
    """
    A processor specifically for PDF documents.
    It inherits the robust processing from GenericTextProcessor.
    """
    def _clean_text(self, text: str) -> str:
        text = super()._clean_text(text)
        logger.debug("Applying PDF-specific cleaning.")
        return text


class MarkdownProcessor(DocumentProcessor):
    """
    A processor for Markdown files.
    """
    def process(self, document: RawDocument, **kwargs) -> List[Chunk]:
        logger.debug("Using generic processor for Markdown file.")
        return GenericTextProcessor().process(document, **kwargs)


# --- Factory Function ---

def get_processor(doc_type: DocumentType) -> DocumentProcessor:
    """Factory function to get the appropriate processing strategy."""
    if doc_type == DocumentType.PDF:
        return PdfProcessor()
    elif doc_type == DocumentType.MD:
        return MarkdownProcessor()
    return GenericTextProcessor()