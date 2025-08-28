# file: services/a-rag/src/api/endpoints/llm_router.py

"""
API endpoint for interacting with the Language Model and RAG system.

This module defines the routes for processing text through the RAG engine.
It exposes a `/chat/invoke` endpoint that accepts a user query and returns
a dual response, orchestrating all backend AI services.
"""

import logging
from fastapi import APIRouter, Body, HTTPException, Request
from src.core.schemas import llm_schemas

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post(
    "/chat/invoke",
    response_model=llm_schemas.RAGResponse,
    summary="Invoke the RAG Chat Agent with Dual Response",
)
async def invoke_rag_agent(
    request: Request,
    request_body: llm_schemas.RAGRequest = Body(...),
):
    """
    Accepts a user query, processes it through the advanced RAG pipeline,
    and returns a dual response: one augmented with context and one without.
    """
    if not request_body.user_query or not request_body.user_id:
        raise HTTPException(
            status_code=400,
            detail="Fields 'user_query' and 'user_id' are required."
        )

    rag_engine_instance = request.app.state.rag_engine
    if not rag_engine_instance:
        logger.error("RAGEngine is not available in the application state.")
        raise HTTPException(status_code=503, detail="AI services are not available")

    # The engine now returns a dictionary containing both answers.
    response_dict = await rag_engine_instance.generate_response(
        user_id=request_body.user_id,
        user_prompt=request_body.user_query,
    )

    # Populate the new response model with the results.
    return llm_schemas.RAGResponse(
        rag_answer=response_dict["rag_answer"],
        llm_answer=response_dict["llm_answer"],
        original_query=request_body.user_query,
    )