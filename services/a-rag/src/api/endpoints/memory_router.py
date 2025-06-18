"""
file: services/a-rag/src/api/endpoints/memory_router.py

API endpoints for managing user conversation memory.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from memory.service import MemoryService

router = APIRouter()

@router.delete(
    "/history/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Clear conversation history for a user",
)
async def clear_user_history(
    request: Request,
    user_id: str,
):
    """
    Deletes all cached conversation history for a given user ID.
    This action is irreversible.
    """
    memory_service: MemoryService = request.app.state.memory_service
    await memory_service.clear_history(user_id)
    # A 204 response does not have a body, so we return None.
    return None