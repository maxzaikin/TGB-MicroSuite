"""
tgrambuddy/tgramllm/src/llm/routers/llm_router.py

"""

from fastapi import APIRouter, Depends, Body
from typing import Annotated # Для Python 3.9+

from ..schemas import llm_schemas
from ..services import engine
from ..core import security
from database.models import User

router = APIRouter()

@router.post("/process", response_model=llm_schemas.LLMResponse)
async def process_text_with_llm(
    request_body: llm_schemas.LLMRequest = Body(...),
    current_user: Annotated[User, Depends(security.fetch_user_by_jwt)] = None
):
    if not engine._mock_model_loaded:
        return llm_schemas.LLMResponse(
            generated_text="LLM model is not accessable.",
            input_text=request_body.text,
            user_email=current_user.email
        )

    generated_response = await engine.generate_text(
        prompt=request_body.text,
        max_tokens=request_body.max_tokens
    )
    return llm_schemas.LLMResponse(
        generated_text=generated_response,
        input_text=request_body.text,
        user_email=current_user.email
    )