"""
tgrambuddy/tgramllm/src/llm/routers/akey_router.py

"""
from typing import (
    List,
    Annotated
)
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from  ..core import security
from database.models import User
from database.dependencies import (
    get_db_session,
    get_api_key_service
)
from src.core.akey_service import APIKeyService
from src.schemas.akey_schemas import (ApiKeyCreate,
                                      ApiKeyGenerated
)

router = APIRouter()

@router.post("/",
             response_model=ApiKeyGenerated,
             status_code=status.HTTP_201_CREATED,
             summary="Create new API key")
async def create_api_key(key_data: ApiKeyCreate,
                         current_user: Annotated[User, Depends(security.fetch_user_by_jwt)],
                         service: Annotated[APIKeyService, Depends(get_api_key_service)],):
    """
    Create a new API key.

    Args:
        key_data (APIKeyCreate): API key creation data.

    Returns:
        Created API key.
    """

    key_data.created_by = current_user.id
    new_key = await service.create_key(key_data)

    return new_key
