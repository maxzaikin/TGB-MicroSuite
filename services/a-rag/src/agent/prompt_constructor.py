# file: services/a-rag/src/agent/prompt_constructor.py
"""
Module for constructing sophisticated, role-based prompts for the LLM.

This module encapsulates the logic for prompt engineering, including the use of
system instructions, few-shot examples, and dynamic history to create a
context-aware and well-structured prompt in the ChatML format.
"""

from typing import Dict, List

from core.schemas.chat_schemas import ChatMessage

# --- System Prompt & Persona Definition ---
# The core identity and instructions for the model.
# Made more direct to combat verbosity.
SYSTEM_PROMPT = "You are TGBuddy, a helpful and direct assistant for the TGB-MicroSuite project. Provide concise, factual answers. Do not ask follow-up questions unless necessary."

# --- Few-Shot Examples ---
# These examples teach the model the desired tone and format.
FEW_SHOT_EXAMPLES: List[Dict[str, str]] = [
    {"role": "user", "content": "What is your name?"},
    {"role": "assistant", "content": "My name is TGBuddy."},
    {"role": "user", "content": "What is TGB-MicroSuite?"},
    {
        "role": "assistant",
        "content": "TGB-MicroSuite is a platform for building scalable, secure, and ethical Telegram bots using a microservices architecture.",
    },
    {"role": "user", "content": "How do I run the a-rag service?"},
    {
        "role": "assistant",
        "content": "Navigate to `services/a-rag` and use the command `arag dev-server` after setting up the environment.",
    },
]

# --- Context Separator ---
# A new message that explicitly tells the model that the examples are over
# and the real conversation begins now.
CONTEXT_SEPARATOR = {
    "role": "system",
    "content": "--- End of examples. Now, begin the actual conversation. ---"
}


def build_chat_prompt(
    history: List[ChatMessage], user_prompt: str
) -> List[Dict[str, str]]:
    """
    Constructs the full message list for the LLM call in ChatML format.

    This function assembles the system prompt, few-shot examples, a context
    separator, conversation history, and the latest user query into a single,
    structured list of messages.

    Args:
        history: A list of previous ChatMessage objects from memory (Redis).
        user_prompt: The current prompt from the user.

    Returns:
        A list of dictionaries, ready for the `create_chat_completion` method.
    """
    # Start with the system message that defines the bot's persona.
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Add the few-shot examples to guide the model's behavior.
    messages.extend(FEW_SHOT_EXAMPLES)
    
    # --- КЛЮЧЕВОЕ ИЗМЕНЕНИЕ ---
    # Add the separator message. This is a powerful signal to the model.
    messages.append(CONTEXT_SEPARATOR)
    # ---------------------------

    # Add the recent, real conversation history from Redis.
    messages.extend([msg.model_dump() for msg in history])

    # Finally, add the current user's prompt.
    messages.append({"role": "user", "content": user_prompt})

    return messages