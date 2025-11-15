"""
file: TGB-MicroSuite/services/a-rag/src/api/endpoints/auth_router.py

API endpoint for user authentication and token management.

This module provides the `/token` route, which implements the OAuth2
password flow. It handles user authentication by verifying credentials
(username/password) and, upon success, issues a JWT access token.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from dependency_injector.wiring import inject, Provide

from core.container import AppContainer
from core.schemas import token_schemas
from core.services.auth_service import AuthService
from storage.rel_db.dependencies import get_db_session
from storage.rel_db.models import User

router = APIRouter()

@router.post(
    "/token",
    response_model=token_schemas.Token,
    summary="User Login",
    description="Authenticate user with email and password, and return a JWT access token.",
)
@inject
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service:AuthService = Depends(Provide[AppContainer.auth_service]),
    session: get_db_session = Depends(Provide[AppContainer.db_session_provider]),
)