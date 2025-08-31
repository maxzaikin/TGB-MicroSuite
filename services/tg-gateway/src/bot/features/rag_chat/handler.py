# file: services/tg-gateway/src/bot/features/rag_chat/handler.py

"""
Core logic for handling general text messages for RAG processing.

This module is responsible for taking a user's text message, forwarding it
to the backend A-RAG API service, receiving a dual response, formatting it,
and sending it back to the user. It includes logic to handle messages that
exceed Telegram's character limit.
"""

import logging
from typing import List

from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from src.clients.rag_api_client import RagApiClient

def _format_dual_response(rag_answer: str, llm_answer: str) -> str:
    """
    Formats the two answers into a single, well-structured Telegram message.

    Args:
        rag_answer: The context-aware answer from the RAG pipeline.
        llm_answer: The standalone answer from the LLM.

    Returns:
        A formatted string ready to be sent to the user.
    """
    # Using basic Markdown for formatting.
    return (
        f"🤖 *Ответ от Mistral (общие знания):*\n"
        f"{llm_answer}\n\n"
        f"--- \n\n"
        f"📚 *Ответ из Базы Знаний (Qdrant):*\n"
        f"{rag_answer}"
    )

def _split_long_message(text: str, max_length: int = 4096) -> List[str]:
    """
    Splits a long text message into multiple chunks that respect Telegram's limit.

    This function attempts to split text intelligently by paragraphs first,
    then falls back to character-based splitting for oversized paragraphs.

    Args:
        text: The full text content to be split.
        max_length: The maximum character length for each chunk.

    Returns:
        A list of text chunks, each guaranteed to be under the max_length.
    """
    if len(text) <= max_length:
        return [text]

    chunks = []
    current_chunk = ""
    
    # Split by paragraphs to maintain message structure
    paragraphs = text.split('\n\n')
    for paragraph in paragraphs:
        # Check if adding the next paragraph exceeds the limit
        if len(current_chunk) + len(paragraph) + 2 <= max_length:
            current_chunk += paragraph + "\n\n"
        else:
            # If the current chunk is not empty, add it to the list
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            # If a single paragraph is too long, it must be split forcefully
            if len(paragraph) > max_length:
                for i in range(0, len(paragraph), max_length):
                    chunks.append(paragraph[i:i + max_length])
                current_chunk = "" # Reset chunk as the long paragraph is fully processed
            else:
                # Start a new chunk with the current paragraph
                current_chunk = paragraph + "\n\n"
    
    # Add the last remaining chunk if it exists
    if current_chunk:
        chunks.append(current_chunk.strip())
        
    # A final check to ensure no chunk is empty
    return [c for c in chunks if c]


async def handle_text_message(
    message: Message, session: AsyncSession, rag_client: RagApiClient
):
    """
    Processes a non-command text message from the user, handles long responses,
    and sends a dual response.
    """
    if not message.text or not message.from_user:
        return

    # In your code, the method is named get_rag_response, let's stick to it.
    user_id_str = str(message.from_user.id) 
    query_text = message.text

    logging.info(f"[TG-GW] Received message from user {user_id_str}: '{query_text}'")

    # 1. Provide immediate feedback to the user.
    await message.bot.send_chat_action(message.chat.id, action="typing")

    # 2. Get the structured response object from the API client.
    # Note: I'm using your method name `get_rag_response`.
    dual_response = await rag_client.get_rag_response(
        user_query=query_text, user_id=user_id_str
    )

    # 3. Format the final message based on the response.
    if dual_response and "rag_answer" in dual_response:
        response_text = _format_dual_response(
            rag_answer=dual_response.get("rag_answer", "N/A"),
            llm_answer=dual_response.get("llm_answer", "N/A")
        )
    else:
        # Provide a user-friendly error message if the backend fails or returns an error.
        logging.error(f"Failed to get a valid response from A-RAG API for user {user_id_str}. Response: {dual_response}")
        response_text = "Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте позже."

    logging.info(f"[TG-GW] Sending response to user {user_id_str}: '{response_text[:100]}...'")

    # 4. --- [FIX] Split the message and send it in chunks ---
    message_chunks = _split_long_message(response_text)
    
    first_chunk = True
    for chunk in message_chunks:
        if first_chunk:
            # The first part is a reply to the user's original message.
            await message.reply(chunk, parse_mode="Markdown")
            first_chunk = False
        else:
            # Subsequent parts are sent as separate messages to the chat.
            await message.answer(chunk, parse_mode="Markdown")