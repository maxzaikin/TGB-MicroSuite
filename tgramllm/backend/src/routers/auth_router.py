"""
tgrambuddy/tgramllm/src/llm/routers/auth_router.py

"""
import logging
from typing import Annotated
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from database.dependencies import get_db_session
from ..core import security
from ..schemas import token_schemas
from ..core.config import settings

router = APIRouter()

@router.post(
    "/token",
    response_model=token_schemas.Token,
    summary="User Login",
    description="Authenticate user with email and password, and return a JWT access token."
)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_db_session)],
):
    """
     Authenticates a user and returns an access token.

    This endpoint expects an OAuth2-compatible form with `username` and `password`
    fields. If the provided credentials are valid, it returns a JWT access token
    for use in subsequent authenticated requests.

    Args:
        form_data (OAuth2PasswordRequestForm): Form containing username and password.
        session (AsyncSession): Asynchronous SQLAlchemy session dependency.

    Returns:
        dict: A dictionary containing the access token and token type.

    Raises:
        HTTPException: If the credentials are invalid (401 Unauthorized).
    """

    logging.info("Trying to log-in. email_to_auth:%s, pass: %s",
                 form_data.username,
                 "***")


    user = await security.authenticate_user(email_to_auth=form_data.username,
                                            password_to_auth=form_data.password,
                                            session=session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = security.create_access_token(
        data={"sub": user.email}
    )

    return {
        "access_token": access_token, 
        "token_type": "bearer"
        }
