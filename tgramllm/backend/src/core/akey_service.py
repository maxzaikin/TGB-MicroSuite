import secrets
import hashlib
import hmac
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from database.models import ApiKey
from ..schemas.akey_schemas import (
    ApiKeyCreate,
    ApiKeyUpdate
)

class APIKeyService:
    def __init__(self, session: AsyncSession):
        """
        Service for managing API keys.

        Args:
            session (AsyncSession): Async SQLAlchemy session.
        """
        self.session = session

    async def get_all_keys(self) -> list[ApiKey]:
        """
        Get all API keys.

        Returns:
            List of ApiKey objects.
        """
        result = await self.session.scalars(select(ApiKey))
        return result.all()

    async def get_key(self, key_id: int) -> ApiKey | None:
        """
        Get an API key by ID.

        Args:
            key_id (int): API key ID.

        Returns:
            ApiKey or None.
        """
        return await self.session.get(ApiKey, key_id)

    async def create_key(self, key_data: ApiKeyCreate) -> ApiKey:
        """
        Create a new API key.

        Raises HTTPException if key already exists.

        Args:
            key_data (APIKeyCreate): Data for new API key.

        Returns:
            Created ApiKey object.
        """

        existing = await self.session.scalar(select(ApiKey).where(ApiKey.key_hash == key_data.key))
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="API key already exists"
            )

        new_key = ApiKey(
            key=key_data.key,
            name=key_data.name,
            comment=key_data.custom_data,
            is_active=key_data.is_active,
            created_at=datetime.utcnow()
        )
        self.session.add(new_key)
        try:
            await self.session.commit()
            await self.session.refresh(new_key)
            return new_key
        except IntegrityError:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create API key due to duplication"
            )

    async def update_key(self, key_id: int, key_data: ApiKeyUpdate) -> ApiKey:
        """
        Update existing API key.

        Args:
            key_id (int): ID of the key to update.
            key_data (APIKeyUpdate): Updated fields.

        Raises:
            HTTPException if key not found or key value duplicates.

        Returns:
            Updated ApiKey object.
        """
        key = await self.get_key(key_id)
        if not key:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found")

        if key_data.key and key_data.key != key.key:
            exists = await self.session.scalar(select(ApiKey).where(ApiKey.key_hash == key_data.key))
            if exists:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="API key already exists")
            key.key = key_data.key

        if key_data.name is not None:
            key.name = key_data.name

        if key_data.comment is not None:
            key.comment = key_data.comment

        if key_data.is_active is not None:
            key.is_active = key_data.is_active

        await self.session.commit()
        await self.session.refresh(key)
        return key

    async def revoke_key(self, key_id: int) -> ApiKey:
        """
        Revoke API key by setting revoked_at and is_active = False.

        Args:
            key_id (int): ID of the key to revoke.

        Returns:
            Updated ApiKey object.
        """
        key = await self.get_key(key_id)
        if not key:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found")

        key.is_active = False
        await self.session.commit()
        await self.session.refresh(key)
        return key

    async def delete_key(self, key_id: int) -> None:
        """
        Delete API key by ID.

        Args:
            key_id (int): ID of the key.

        Raises:
            HTTPException if key not found.
        """
        key = await self.get_key(key_id)
        if not key:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found")

        await self.session.delete(key)
        await self.session.commit()
