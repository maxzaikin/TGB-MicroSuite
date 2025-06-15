# file: TGB-MicroSuite/services/a-rag/src/core/schemas/akey_schemas.py

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

# --- Base Schemas ---


class ApiKeyBase(BaseModel):
    """Base schema for API Key, containing common attributes."""

    key_hash: str = Field(
        ..., max_length=255, description="The SHA-256 hash of the API key."
    )

    name: str = Field(..., description="A descriptive name for the API key.")

    comment: Optional[str] = Field(
        default=None, description="An optional comment for the key."
    )

    model_config = {"from_attributes": True}


# --- Schemas for Client Interaction ---


class ApiKeyClientData(BaseModel):
    """Schema for data provided by the client when creating a key."""

    name: str = Field(..., description="A descriptive name for the API key.")

    comment: Optional[str] = Field(
        default=None, description="An optional comment for the key."
    )

    is_active: bool = Field(
        default=True, description="Whether the API key should be active upon creation."
    )


class ApiKeyUpdate(BaseModel):
    """Schema for updating an existing API Key. All fields are optional."""

    name: Optional[str] = Field(
        default=None, description="A new descriptive name for the API key."
    )

    comment: Optional[str] = Field(
        default=None, description="A new optional comment for the key."
    )

    is_active: Optional[bool] = Field(
        default=None, description="Set to true to activate or false to deactivate."
    )


# --- Schemas for Server Responses ---


class ApiKeyRead(ApiKeyBase):
    """Schema for returning API Key information to the client."""

    id: int = Field(..., description="The unique identifier of the API key.")

    is_active: bool = Field(..., description="Whether the API key is currently active.")

    created_at: datetime = Field(
        ..., description="The timestamp when the API key was created."
    )

    created_by: int = Field(
        ..., description="The ID of the user who created the API key."
    )


class ApiKeyGenerated(ApiKeyRead):
    """Schema for the response after creating a key, including the raw secret."""

    api_key: str = Field(
        ..., description="The generated secret API key. This is shown only once."
    )


class PaginatedApiKeyResponse(BaseModel):
    """Schema for paginated list of API keys."""

    items: List[ApiKeyRead] = Field(
        ..., description="The list of API keys for the current page."
    )

    total: int = Field(
        ..., description="The total number of API keys matching the filter criteria."
    )

    page: int = Field(..., description="The current page number (1-based).")

    size: int = Field(..., description="The number of items per page.")
