"""
file: TGB-MicroSuite/services/a-rag/src/core/schemas/user_schemas.py

Schemas for user authentication using Pydantic.

Defines the data model for user login credentials.
"""

from pydantic import BaseModel


class UserLogin(BaseModel):
    """
    Schema representing user login credentials.

    Attributes:
        email (str): The user's email address.
        password (str): The user's password.
    """

    email: str
    password: str
