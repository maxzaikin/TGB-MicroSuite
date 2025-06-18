"""
file: services/a-rag/src/agent/engine.py

Core orchestration engine for generating contextual chat responses.

This module contains the primary logic for:
1. Loading the GGUF Language Model using llama-cpp-python.
2. Constructing a structured, role-based prompt (ChatML format).
3. Interacting with the MemoryService to retrieve and update conversation history.
4. Generating a final answer using the loaded model.
"""

import json
import logging
from typing import Optional

from llama_cpp import Llama

from core.config import settings
from core.profiling import log_execution_time
from memory.service import MemoryService

from .prompt_constructor import build_chat_prompt


def load_llm_model() -> Optional[Llama]:
    """
    Loads the GGUF model from the path specified in the application settings.

    This function initializes the Llama object from llama-cpp-python,
    configuring it with parameters suitable for a chat model.

    Returns:
        An instance of the Llama model if successful, otherwise None.
    """
    # Get the model path from our centralized settings configuration.
    model_path = settings.MODEL_PATH
    logging.info(f"Attempting to load LLM model from path: {model_path}")

    try:
        llm = Llama(
            model_path=str(model_path),
            n_ctx=4096,  # Context window size
            n_gpu_layers=-1,  # Offload all possible layers to GPU
            verbose=False,  # Set to True for detailed Llama.cpp logs
        )
        logging.info("LLM model loaded successfully.")
        return llm
    except Exception:
        # Use logging.exception to automatically include the traceback
        logging.exception(f"Failed to load LLM model from {model_path}")
        return None


async def generate_chat_response(
    llm: Llama,
    memory_service: MemoryService,
    user_id: str,
    user_prompt: str,
) -> str:
    """
    Generates a contextual chat response using the prompt constructor and memory.
    """
    if llm is None:
        raise RuntimeError("LLM model is not loaded. Cannot generate text.")

    logging.info(f"Generating response for user '{user_id}'...")

    # 1. Retrieve history from memory
    with log_execution_time("Redis History Retrieval"):
        history = await memory_service.get_history(user_id)

    logging.info(
        f"Retrieved {len(history)} messages from history for user '{user_id}'."
    )

    # 2. Build the final prompt using our new, sophisticated constructor
    with log_execution_time("Prompt Construction"):
        messages_for_llm = build_chat_prompt(history, user_prompt)

    # 3. Log the final prompt design for debugging
    prompt_design_for_log = json.dumps(messages_for_llm, indent=2, ensure_ascii=False)
    logging.info(
        f"[LLM_PROMPT] Sending to LLM for user '{user_id}':\n{prompt_design_for_log}"
    )

    # 4. Call the model
    with log_execution_time("LLM Generation"):
        output = llm.create_chat_completion(
            messages=messages_for_llm,
            max_tokens=512,
        )

    generated_text = output["choices"][0]["message"]["content"].strip()
    logging.info(f"LLM generated response: '{generated_text[:100]}...'")

    # 5. Update history (этот код остается без изменений)
    await memory_service.add_message_to_history(
        user_id=user_id, role="user", content=user_prompt
    )
    await memory_service.add_message_to_history(
        user_id=user_id, role="assistant", content=generated_text
    )

    return generated_text
