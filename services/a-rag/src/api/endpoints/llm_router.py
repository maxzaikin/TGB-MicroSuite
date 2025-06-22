"""
file: services/a-rag/src/api/endpoints/llm_router.rc.py

API endpoint for interacting with the Language Model (LLM).

This module defines the routes for processing text through the RAG agent
or the underlying LLM. It exposes a `/process` endpoint that accepts a
prompt and returns a generated response. Access is protected and linked
to an authenticated user.
"""

import logging
from fastapi import APIRouter, Body, HTTPException, Request
from agent import engine as rag_engine
from core.schemas import llm_schemas

router = APIRouter()

@router.post(
    "/chat/invoke",
    response_model=llm_schemas.RAGResponse,
    summary="Invoke the Chat Agent with Memory",
)
async def invoke_rag_agent(
    request: Request,
    request_body: llm_schemas.RAGRequest = Body(...),
):
    """
    Accepts a user query, processes it through the RAG pipeline,
    and returns the generated answer.
    """
    if not request_body.user_query or not request_body.user_id:
        raise HTTPException(status_code=400, detail="Fields 'user_query' and 'user_id' are required.")

    llm_adapter_instance = request.app.state.llm_adapter
    memory_service_instance = request.app.state.memory_service
    kb_query_engine_instance = request.app.state.kb_query_engine

    if not llm_adapter_instance or not memory_service_instance:
        logging.error("Core AI services (LLM or Memory) are not available.")
        raise HTTPException(status_code=503, detail="AI services are not available")

    generated_response = await rag_engine.generate_chat_response(
        llm=llm_adapter_instance,
        memory_service=memory_service_instance,
        kb_rag_engine=kb_query_engine_instance,
        user_id=request_body.user_id,
        user_prompt=request_body.user_query,
    )

    return llm_schemas.RAGResponse(
        answer=generated_response,
        original_query=request_body.user_query,
        user_email="test@test.com", # Placeholder
    )