# file: services/a-rag/src/core/schemas/pipeline_schemas.py

"""
Pydantic models for data objects passed between ZenML pipeline steps.
"""

import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class DocumentType(str, Enum):
    """Enumeration for the types of documents we can process."""
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    MD = "md"
    UNKNOWN = "unknown"

    @classmethod
    def from_path(cls, path: Path) -> "DocumentType":
        """Determines the document type from a file's extension."""
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            return cls.PDF
        elif suffix in [".docx", ".doc"]:
            return cls.DOCX
        elif suffix == ".txt":
            return cls.TXT
        elif suffix == ".md":
            return cls.MD
        return cls.UNKNOWN


class RawDocument(BaseModel):
    """
    Represents a document freshly extracted from a source file.
    This is the output of the 'extract' step.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    content: str
    source_path: str
    document_type: DocumentType
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Chunk(BaseModel):
    """
    Represents a chunk of text from a document, ready for embedding.
    This is the output of the 'process' step.
    It links back to the original raw document.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    content: str
    raw_document_id: uuid.UUID  # Foreign key to the RawDocument
    source_path: str # Denormalized for easier access
    metadata: Dict[str, Any] = Field(default_factory=dict)