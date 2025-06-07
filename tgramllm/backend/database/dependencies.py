#src/database/dependencies.py

from typing import AsyncGenerator
from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from .db_adapter import DBAdapter
from ..src.core.akey_service import APIKeyService

async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides a SQLAlchemy AsyncSession for database operations.

    Retrieves the global DBAdapter from the FastAPI app state,
    then creates a new AsyncSession using the adapter.

    Yields:
        AsyncSession: An active asynchronous SQLAlchemy session.

    Raises:
        Any exception from downstream usage will trigger rollback and re-raise.
    """
    db_adapter: DBAdapter = request.app.state.db_adapter
    session: AsyncSession = await db_adapter.get_session()

    try:
        yield session
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()

async def get_api_key_service(
    session: AsyncSession = Depends(get_db_session),
) -> APIKeyService:
    """
    Dependency that provides an instance of APIKeyService.

    This service handles business logic related to API key management.
    The database session is injected as a dependency.

    Args:
        session (AsyncSession): An asynchronous SQLAlchemy session.

    Returns:
        APIKeyService: A service instance with DB access.
    """
    return APIKeyService(session)
