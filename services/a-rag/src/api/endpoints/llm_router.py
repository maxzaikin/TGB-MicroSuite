"""
file: TGB-MicroSuite/services/a-rag/src/api/endpoints/llm_router.py

API endpoint for interacting with the Language Model (LLM).

This module defines the routes for processing text through the RAG agent
or the underlying LLM. It exposes a `/process` endpoint that accepts a
prompt and returns a generated response. Access is protected and linked
to an authenticated user.
"""

from typing import Annotated

from fastapi import APIRouter, Body, Depends

from agent import engine
from core import security
from core.schemas import llm_schemas
from storage.rel_db.models import User

router = APIRouter()


@router.post("/process", response_model=llm_schemas.LLMResponse)
async def process_text_with_llm(
    request_body: llm_schemas.LLMRequest = Body(...),
    current_user: Annotated[User, Depends(security.fetch_user_by_jwt)] = None,
):
    if not engine._mock_model_loaded:
        return llm_schemas.LLMResponse(
            generated_text="LLM model is not accessable.",
            input_text=request_body.text,
            user_email=current_user.email,
        )

    generated_response = await engine.generate_text(
        prompt=request_body.text, max_tokens=request_body.max_tokens
    )
    return llm_schemas.LLMResponse(
        generated_text=generated_response,
        input_text=request_body.text,
        user_email=current_user.email,
    )
