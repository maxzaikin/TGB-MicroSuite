"""
file: TGB-MicroSuite/services/a-rag/src/api/endpoints/akey_router.py

API endpoints for managing user API keys.

This module defines the FastAPI routes for creating, listing, updating,
and deleting API keys (CRUD operations). All endpoints are protected and
require a valid JWT token for an authenticated user. The business logic
is delegated to the APIKeyService, which is injected as a dependency.
"""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query, status

from api_keys.service import APIKeyService
from core import security
from core.schemas.akey_schemas import (
    ApiKeyClientData,
    ApiKeyGenerated,
    ApiKeyRead,
    ApiKeyUpdate,
    PaginatedApiKeyResponse,
)
from storage.rel_db.dependencies import get_api_key_service
from storage.rel_db.models import User

router = APIRouter()


@router.post(
    "/",
    response_model=ApiKeyGenerated,
    status_code=status.HTTP_201_CREATED,
    summary="Create new API key",
)
async def create_api_key(
    key_data: ApiKeyClientData,
    current_user: Annotated[User, Depends(security.fetch_user_by_jwt)],
    service: Annotated[APIKeyService, Depends(get_api_key_service)],
):
    """
    Create a new API key for the authenticated user.
    The secret key value is generated securely on the server.
    """
    new_key_with_raw = await service.create_key(
        client_data=key_data, user_id=current_user.id
    )
    return new_key_with_raw


@router.get(
    "/",
    response_model=PaginatedApiKeyResponse,
    status_code=status.HTTP_200_OK,
    summary="List API keys for the current user",
)
async def list_api_keys(
    current_user: Annotated[User, Depends(security.fetch_user_by_jwt)],
    service: Annotated[APIKeyService, Depends(get_api_key_service)],
    page: int = Query(1, ge=1, description="Page number to retrieve."),
    size: int = Query(10, ge=1, le=100, description="Number of items per page."),
    sort_by: Optional[str] = Query(
        None, description="Field to sort by (e.g., 'name')."
    ),
    sort_order: str = Query(
        "asc", pattern="^(asc|desc)$", description="Sort order: 'asc' or 'desc'."
    ),
    # Per-column filters
    name: Optional[str] = Query(None, description="Filter by key name."),
    comment: Optional[str] = Query(None, description="Filter by comment."),
):
    """
    Retrieve a paginated, sorted, and filtered list of API keys.
    Filtering is performed on the server.
    """
    # Consolidate filters into a dictionary to pass to the service
    filters = {
        "name": name,
        "comment": comment,
    }
    # Remove None values so we don't process empty filters
    active_filters = {k: v for k, v in filters.items() if v is not None}

    paginated_result = await service.get_paginated_keys(
        user_id=current_user.id,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_order=sort_order,
        filters=active_filters,
    )
    return paginated_result


@router.patch(
    "/{key_id}",
    response_model=ApiKeyRead,
    status_code=status.HTTP_200_OK,
    summary="Update an API key",
)
async def update_api_key(
    key_id: int,
    key_data: ApiKeyUpdate,
    current_user: Annotated[User, Depends(security.fetch_user_by_jwt)],
    service: Annotated[APIKeyService, Depends(get_api_key_service)],
):
    """
    Update an existing API key's details.
    A user can only update their own keys.
    """

    updated_key = await service.update_key(
        key_id=key_id, user_id=current_user.id, key_data=key_data
    )
    return updated_key


@router.delete(
    "/{key_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete an API key"
)
async def delete_api_key(
    key_id: int,
    current_user: Annotated[User, Depends(security.fetch_user_by_jwt)],
    service: Annotated[APIKeyService, Depends(get_api_key_service)],
):
    """
    Permanently delete an API key.
    A user can only delete their own keys.
    """

    await service.delete_key(key_id=key_id, user_id=current_user.id)

    return None
