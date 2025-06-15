"""
file: TGB-MicroSuite/services/a-rag/src/core/security.py

"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Annotated, Any, Dict, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.schemas.token_schemas import TokenData
from storage.rel_db.db_adapter import DBAdapter
from storage.rel_db.dependencies import get_db_session
from storage.rel_db.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")


async def fetch_user_by_email(email: str, db_adapter: DBAdapter) -> Optional[User]:
    """
    Retrieve a user from the database by email.

    Args:
        email (str): The email address of the user to retrieve.
        db_adapter (DBAdapter): The database adapter providing session access.

    Returns:
        Optional[User]: The User object if found, otherwise None.
    """

    session: AsyncSession = await db_adapter.get_session()
    logging.info("----------->get_user_from_db-email: %s", email)

    try:
        user: Optional[User] = await session.scalar(
            select(User).where(User.email == email)
        )
        logging.info("----------->Found user is: %s", user)
        return user

    except SQLAlchemyError as e:
        await session.rollback()
        logging.error(
            "Error while fetching  user:: %s from database.", e, exc_info=True
        )
        return None

    finally:
        await session.close()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify that a plaintext password matches its hashed version.

    Args:
        plain_password (str): The plaintext password to verify.
        hashed_password (str): The stored hashed password to compare against.

    Returns:
        bool: True if the password is correct, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a plaintext password using bcrypt.

    Args:
        password (str): The plaintext password to hash.

    Returns:
        str: The bcrypt hashed password.
    """
    return pwd_context.hash(password)


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Generate a JWT access token with optional expiration.

    Args:
        data (dict): The data payload to include in the token.
        expires_delta (Optional[timedelta]): Optional expiration delta.

    Returns:
        str: The encoded JWT token.
    """

    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    return encoded_jwt


async def fetch_user_by_jwt(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    token: str = Depends(oauth2_scheme),
) -> Optional[User]:
    """
    Retrieve the currently authenticated user based on the JWT token.

    Args:
        session (AsyncSession): The database session.
        token (str): The JWT bearer token.

    Raises:
        HTTPException: If the token is invalid or user is not found.

    Returns:
        User: The authenticated user.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        email: Optional[str] = payload.get("sub")

        if email is None:
            raise credentials_exception

        token_data = TokenData(email=email)
        user: Optional[User] = await session.scalar(
            select(User).where(User.email == token_data.email)
        )

        if user is None:
            raise credentials_exception

        return user

    except JWTError as exc:
        raise credentials_exception from exc

    finally:
        pass


async def authenticate_user(
    email_to_auth: str,
    password_to_auth: str,
    session: AsyncSession = Depends(get_db_session),
) -> Optional[User]:
    """
    Authenticate a user using email and password.

    Args:
        email_to_auth (str): The email address provided by the user.
        password_to_auth (str): The plaintext password to verify.
        session (AsyncSession): The database session injected by FastAPI.

    Returns:
        Optional[User]: The authenticated User object if credentials are valid, otherwise None.
    """
    user: Optional[User] = await session.scalar(
        select(User).where(User.email == email_to_auth)
    )

    if not user:
        return None

    if not verify_password(password_to_auth, user.hashed_password):
        return None

    return user


def generate_api_key(length: int = 60) -> str:
    """Generate a secure API key."""
    return secrets.token_urlsafe(length)


def hash_api_key(api_key: str, pepper: str) -> str:
    """Generate HMAC-SHA256 hash of the API key with pepper."""
    return hmac.new(pepper.encode(), api_key.encode(), hashlib.sha256).hexdigest()
