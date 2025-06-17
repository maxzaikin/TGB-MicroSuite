"""
file: TGB-MicroSuite/services/a-rag/src/api/endpoints/llm_router.py

API endpoint for interacting with the Language Model (LLM).

This module defines the routes for processing text through the RAG agent
or the underlying LLM. It exposes a `/process` endpoint that accepts a
prompt and returns a generated response. Access is protected and linked
to an authenticated user.
"""

from fastapi import APIRouter, Body, HTTPException, Request
from src.agent import engine as rag_engine  # Import the new engine function
from src.core.schemas import llm_schemas  # Assuming a new schema for chat

router = APIRouter()


@router.post(
    "/chat/invoke",
    response_model=llm_schemas.RAGResponse,
    summary="Invoke the Chat Agent with Memory [AUTH DISABLED]",
)
async def invoke_rag_agent(
    # The dependency on the current user remains for security and logging.
    # current_user: Annotated[User, Depends(security.fetch_user_by_jwt)],
    # token: Optional[str] = Depends(security.oauth2_scheme),
    # We use a new schema to reflect the new request format.
    request: Request,
    request_body: llm_schemas.RAGRequest = Body(...),
):
    """
    Accepts a user query, processes it through the RAG pipeline,
    and returns the generated answer.
    """
    if not request_body.user_query:
        raise HTTPException(
            status_code=400, detail="Field 'user_query' cannot be empty."
        )

    # logging.info(
    #    f"[A-RAG] Received query from user '{current_user.email}': '{request_body.user_query}'"
    # )
    llm_instance = request.app.state.llm
    if llm_instance is None:
        raise HTTPException(status_code=503, detail="AI model is not available")

    memory_service_instance = request.app.state.memory_service

    # The router's job is simply to delegate the call to the engine.
    generated_response = (
        await rag_engine.generate_chat_response(  # <-- Вызываем новую функцию
            llm=llm_instance,
            memory_service=memory_service_instance,
            user_id=request_body.user_id,
            user_prompt=request_body.user_query,
        )
    )

    # logging.info(
    #    f"[A-RAG] Sending response to user '{current_user.email}': '{generated_response[:100]}...'"
    # )

    return llm_schemas.RAGResponse(
        answer=generated_response,
        original_query=request_body.user_query,
        # user_email=current_user.email,
        user_email="test@test.com",
    )
