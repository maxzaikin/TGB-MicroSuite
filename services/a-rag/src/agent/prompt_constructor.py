"""
file: services/a-rag/src/agent/prompt_constructor.rc.py

Module for constructing sophisticated, role-based prompts for the LLM.

This module encapsulates the logic for prompt engineering. It assembles a
multi-context prompt by combining:
1. A base system instruction (persona).
2. Factual context retrieved from the knowledge base (RAG on documents).
3. Relevant conversational context from past messages (RAG on chat history).
4. Few-shot examples to guide response style.
5. The immediate short-term chat history (from Redis).
6. The latest user query.
"""
from typing import Dict, List

from llama_index.core.llms import ChatMessage, MessageRole
from core.schemas.chat_schemas import ChatMessage as AppChatMessage

# --- Base System Prompt & Persona Definition ---
BASE_SYSTEM_PROMPT = "You are TGBuddy, a helpful and direct assistant for the TGB-MicroSuite project. Provide concise, factual answers based on the provided context."

# --- Few-Shot Examples ---
FEW_SHOT_EXAMPLES: List[ChatMessage] = [
    ChatMessage(role=MessageRole.USER, content="What is your name?"),
    ChatMessage(role=MessageRole.ASSISTANT, content="My name is TGBuddy."),
]

# --- Context Separator ---
CONTEXT_SEPARATOR: List[ChatMessage] = [
    ChatMessage(role=MessageRole.USER, content="Okay, I understand the instructions. Let's start our conversation now."),
    ChatMessage(role=MessageRole.ASSISTANT, content="Great! I'm ready. How can I help you?"),
]

# --- [ISSUE-23] Start of changes: Multi-Context Prompting ---

def _format_context_block(title: str, chunks: List[str]) -> str:
    """Helper function to format a list of context chunks into a string block."""
    if not chunks:
        return ""
    # Joins chunks with a clear separator and adds a title.
    return f"--- {title.upper()} ---\n" + "\n\n".join(chunks)

def build_chat_prompt(
    history: List[AppChatMessage],
    user_prompt: str,
    kb_context_chunks: List[str],
    chat_context_chunks: List[str],
) -> List[ChatMessage]:
    """
    Constructs the full message list for the LLM call using multiple context sources.

    Args:
        history: A list of recent ChatMessage objects from short-term memory (Redis).
        user_prompt: The current prompt from the user.
        kb_context_chunks: A list of relevant text chunks from the knowledge base.
        chat_context_chunks: A list of relevant text chunks from the long-term chat history.

    Returns:
        A list of LlamaIndex's ChatMessage objects, ready for the LLM.
    """
    # 1. Format the retrieved context blocks.
    kb_context_str = _format_context_block("CONTEXT FROM KNOWLEDGE BASE", kb_context_chunks)
    chat_history_context_str = _format_context_block("RELEVANT PAST MESSAGES", chat_context_chunks)

    # 2. Dynamically build the final system prompt.
    system_prompt_parts = [BASE_SYSTEM_PROMPT]
    if kb_context_str:
        system_prompt_parts.append(kb_context_str)
    if chat_history_context_str:
        system_prompt_parts.append(chat_history_context_str)
    
    # Add a closing instruction if any context was provided.
    if kb_context_str or chat_history_context_str:
        system_prompt_parts.append("Based on the context above, answer the user's question.")
    
    final_system_prompt = "\n\n".join(system_prompt_parts)

    # 3. Assemble the final message list.
    messages: List[ChatMessage] = [
        ChatMessage(role=MessageRole.SYSTEM, content=final_system_prompt)
    ]
    messages.extend(FEW_SHOT_EXAMPLES)
    messages.extend(CONTEXT_SEPARATOR)
    
    # Convert our app's ChatMessage history to LlamaIndex's ChatMessage objects.
    for msg in history:
        # Ensure role is a valid MessageRole enum member
        role_enum = MessageRole(msg.role)
        messages.append(ChatMessage(role=role_enum, content=msg.content))
        
    messages.append(ChatMessage(role=MessageRole.USER, content=user_prompt))

    return messages
# --- [ISSUE-23] End of changes: Multi-Context Prompting ---