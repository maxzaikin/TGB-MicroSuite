"""
tgrambuddy/tgramllm/src/database/models.py

Database models for TGramLLM project.

This module defines the SQLAlchemy ORM models for users, access tokens,
and API keys with full typing and relationships.

Requires:
    - SQLAlchemy 2.x
    - Python 3.10+
"""

from datetime import datetime
from sqlalchemy import (
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)
from sqlalchemy.types import JSON
from .db_adapter import Model

class User(Model):
    """User model representing application users."""

    __tablename__ = "users"
    __table_args__ = {"comment": "Registered users of the system"}

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    #################################################################################
    # Relationships
    access_tokens: Mapped[list["AccessToken"]] = relationship(
        "AccessToken", back_populates="user", cascade="all, delete-orphan"
    )
    api_keys: Mapped[list["ApiKey"]] = relationship(
        "ApiKey", back_populates="user", cascade="all, delete-orphan"
    )
    ################################################################################

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}')>"


class AccessToken(Model):
    """AccessToken model representing authentication tokens issued to users."""

    __tablename__ = "access_tokens"
    __table_args__ = {"comment": "Tokens issued to users for authentication sessions"}

    access_token: Mapped[str] = mapped_column(String(255), primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    expiration_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    device_info: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="access_tokens")

    def __repr__(self) -> str:
        return f"<AccessToken(token='{self.access_token[:10]}...', user_id={self.user_id})>"


class ApiKey(Model):
    """ApiKey model for managing application-level API keys."""

    __tablename__ = "api_keys"
    __table_args__ = {"comment": "API keys for external integrations or internal automation"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=False)
    comment: Mapped[str | None] = mapped_column(String(255), nullable=True)
    key_hash: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Filed structure architecture:
    # {
    #   "feature_name_1": {
    #       "read": true,
    #       "write": false
    #   },
    #   "feature_name_2": {
    #       "read": true,
    #       "write": true,
    #       "delete": false
    #   }
    # }
    permissions: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Example: { "ip": "127.0.0.1", "tags": ["internal"] }
    custom_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="api_keys")

    def __repr__(self) -> str:
        return f"<ApiKey(id={self.id}, name='{self.name}', is_active={self.is_active})>"
