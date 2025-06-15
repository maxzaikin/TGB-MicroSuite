# file: TGB-MicroSuite/services/a-rag/src/api_keys/service.py

import hashlib
import secrets
from typing import Any, Dict, Optional

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.schemas.akey_schemas import ApiKeyClientData, ApiKeyGenerated, ApiKeyUpdate
from storage.rel_db.models import ApiKey

API_KEY_PREFIX = "tgb"  # "TgramBuddy" prefix for easy identification


class APIKeyService:
    def __init__(self, session: AsyncSession):
        """
        Service for managing API keys.

        Args:
            session (AsyncSession): Async SQLAlchemy session.
        """
        self.session = session

    def _generate_secure_key_and_hash(self) -> tuple[str, str]:
        """
        Generates a new secure API key and its HMAC-SHA256 hash.

        Returns:
            A tuple containing:
            - The raw, prefixed API key (e.g., "tgb_..."). This is shown to the user ONCE.
            - The hex-encoded HMAC hash of the key. This is stored in the database.
        """
        # Generate a cryptographically strong random string
        random_part = secrets.token_urlsafe(32)
        raw_key = f"{API_KEY_PREFIX}_{random_part}"

        # Create a hash of the key using HMAC for added security against rainbow table attacks.
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

        return raw_key, key_hash

    async def get_paginated_keys(
        self,
        user_id: int,
        page: int = 1,
        size: int = 10,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
        filters: Optional[Dict[str, Any]] = None,
    ) -> dict:
        """
        Retrieves a paginated, sorted, and filtered list of API keys for a user.

        Args:
            user_id (int): The ID of the user whose keys to retrieve.
            page (int): The page number to retrieve.
            size (int): The number of items per page.
            sort_by (Optional[str]): The field to sort by.
            sort_order (str): The sort order ('asc' or 'desc').
            filters (Optional[Dict[str, Any]]): A dictionary of column filters.

        Returns:
            A dictionary containing the list of items and pagination metadata.
        """
        query = select(ApiKey).where(ApiKey.created_by == user_id)

        # Apply per-column filtering dynamically
        if filters:
            for column, value in filters.items():
                if hasattr(ApiKey, column) and value:
                    query = query.where(getattr(ApiKey, column).ilike(f"%{value}%"))

        count_query = select(func.count()).select_from(query.subquery())
        total = await self.session.scalar(count_query) or 0

        if sort_by and hasattr(ApiKey, sort_by):
            column_to_sort = getattr(ApiKey, sort_by)
            query = query.order_by(
                column_to_sort.desc() if sort_order == "desc" else column_to_sort.asc()
            )

        offset = (page - 1) * size
        query = query.offset(offset).limit(size)

        result = await self.session.scalars(query)
        items = list(result.all())

        return {"items": items, "total": total, "page": page, "size": size}

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

    async def get_key_for_user(self, key_id: int, user_id: int) -> ApiKey:
        """
        Get a specific API key by its ID, ensuring it belongs to the specified user.
        This is a crucial security check.

        Args:
            key_id (int): The ID of the key to retrieve.
            user_id (int): The ID of the user who should own the key.

        Raises:
            HTTPException(404) if the key is not found or doesn't belong to the user.

        Returns:
            The ApiKey ORM object.
        """
        key = await self.session.get(ApiKey, key_id)
        if not key or key.created_by != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="API key not found"
            )
        return key

    async def create_key(
        self, client_data: ApiKeyClientData, user_id: int
    ) -> ApiKeyGenerated:
        """
        Creates a new API key, generates it securely, and stores its hash.

        Args:
            client_data (ApiKeyClientData): Data from the client.
            user_id (int): The ID of the user creating the key.

        Returns:
            An object containing the new key's data and the raw secret key.
        """
        raw_key, key_hash = self._generate_secure_key_and_hash()

        new_key_db = ApiKey(
            key_hash=key_hash,
            name=client_data.name,
            comment=client_data.comment,
            is_active=client_data.is_active,
            created_by=user_id,
        )
        self.session.add(new_key_db)

        try:
            await self.session.commit()
            await self.session.refresh(new_key_db)
        except IntegrityError:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not create a unique API key. Please try again.",
            )

        return ApiKeyGenerated(
            id=new_key_db.id,
            key_hash=new_key_db.key_hash,
            name=new_key_db.name,
            comment=new_key_db.comment,
            is_active=new_key_db.is_active,
            created_at=new_key_db.created_at,
            created_by=new_key_db.created_by,
            api_key=raw_key,
        )

    async def update_key(
        self,
        key_id: int,
        user_id: int,
        key_data: ApiKeyUpdate,
    ) -> ApiKey:
        """
        Update an existing API key for a specific user.

        Args:
            key_id (int): ID of the key to update.
            user_id (int): ID of the user making the request.
            key_data (ApiKeyUpdate): The fields to update.

        Returns:
            The updated ApiKey object.
        """
        # First, securely fetch the key, ensuring ownership
        key_to_update = await self.get_key_for_user(key_id, user_id)

        # Use model_dump to get only the fields that were provided by the client
        update_data = key_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(key_to_update, field, value)

        await self.session.commit()
        await self.session.refresh(key_to_update)
        return key_to_update

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
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="API key not found"
            )

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
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="API key not found"
            )

        await self.session.delete(key)
        await self.session.commit()
