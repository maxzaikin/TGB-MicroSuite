"""
file: services/a-rag/src/core/schemas/chat_schemas.py

Pydantic schemas for chat interactions and message structures.
"""

from typing import Literal

from pydantic import BaseModel, Field

# Defines the possible roles in a conversation, adhering to the ChatML standard.
Role = Literal["system", "user", "assistant"]


class ChatMessage(BaseModel):
    """
    Represents a single message in a conversation, following the ChatML format.
    """

    role: Role = Field(..., description="The role of the message author.")
    content: str = Field(..., description="The text content of the message.")
