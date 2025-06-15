"""
file: TGB-MicroSuite/services/a-rag/src/core/schemas/token_schemas.py

Schemas for authentication tokens and token data using Pydantic.

Defines the data models for access tokens and optional token payload data.
"""

from typing import Optional

from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    """
    Schema representing an authentication token.

    Attributes:
        access_token (str): The actual token string used for authentication.
        token_type (str): The type of the token (e.g., "bearer").
    """

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    Schema representing the data contained within a token.

    Attributes:
        email (Optional[EmailStr]): Optional email associated with the token.
            May be None if not present.
    """

    email: Optional[EmailStr] = None
