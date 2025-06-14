"""
file: TGB-MicroSuite./services/a-rag/src/agent/engine.py

Core orchestration engine for the RAG (Retrieval-Augmented Generation) pipeline.

This module contains the primary logic for loading the GGUF Language Model,
processing a user query, constructing a prompt, and generating a final answer
using the loaded model.
"""

import logging
from typing import List, Optional

# Import the Llama class from the newly installed library
from llama_cpp import Llama

# Import our application's settings and prompt construction logic
from .prompt_template import construct_prompt

# A module-level global variable to hold the loaded LLM instance.
# This follows a singleton-like pattern to ensure the model is loaded only once.
llm: Optional[Llama] = None


def load_llm_model() -> Optional[Llama]:
    """
    Loads the GGUF model from the path specified in the settings.

    This function initializes the Llama object from llama-cpp-python,
    configuring it with parameters suitable for a RAG chat model.
    The loaded model is stored in the global `llm` variable.
    """
    # global llm
    # if llm is not None:
    #    logging.info("LLM model is already loaded.")
    #    return

    # Use the new, absolute path property from settings.
    model_path = r""
    logging.info(f"Attempting to load LLM model from absolute path: {model_path}")

    try:
        # Initialize the Llama model.
        # These parameters are crucial for performance and behavior.
        llm = Llama(
            model_path=model_path,
            # n_ctx: The context size. 4096 is a common value.
            n_ctx=4096,
            # n_gpu_layers: Number of layers to offload to the GPU.
            # -1 means offload all possible layers, which is ideal for performance.
            # Set to 0 if you want to run on CPU only.
            n_gpu_layers=-1,
            # Set to True to see more detailed Llama.cpp logs.
            verbose=False,
        )
        logging.info("LLM model loaded successfully.")

        return llm
    except Exception as e:
        logging.exception(f"Failed to load LLM model from {model_path}: {e}")
        # llm remains None, and subsequent calls will fail until the app is restarted.
        llm = None

        return llm


def generate_text(llm: Llama, prompt: str) -> str:
    """
    Generates text using the loaded Llama model.

    Args:
        prompt: The fully constructed prompt to send to the model.

    Returns:
        The text generated by the model.
    """
    # if llm is None:
    #    raise RuntimeError("LLM model is not loaded. Cannot generate text.")

    # Call the model to generate a response.
    # This is a synchronous call, so we wrap it in an async function if needed elsewhere.
    output = llm(
        prompt,
        max_tokens=512,  # Max tokens for the generated response.
        stop=["USER:", "\n"],  # Stop generation when these tokens are encountered.
        echo=False,  # Do not echo the prompt in the output.
    )

    # The output is a dictionary. We need to extract the text from 'choices'.
    generated_text = output["choices"][0]["text"].strip()
    return generated_text


async def process_user_query(llm: Llama, user_query: str) -> str:
    """
    Orchestrates the full RAG pipeline for a given user query.

    This is the main asynchronous entry point for the agent's logic.

    Args:
        user_query: The raw text query from the user.

    Returns:
        A string containing the generated answer or an error message.
    """
    # if llm is None:
    #    logging.error("Cannot process query because LLM model is not loaded.")
    #    return "Sorry, the AI model is currently unavailable. Please try again later."

    try:
        # 1. Retrieval Step (currently mocked)
        logging.info(f"Retrieving context for query: '{user_query[:50]}...'")
        mock_context_chunks: List[str] = [
            "Principle 1: Clean Code should be read like well-written prose.",
            "Principle 2: A function should do one thing and do it well.",
        ]

        # 2. Prompt Construction Step
        final_prompt = construct_prompt(
            question=user_query, context_chunks=mock_context_chunks
        )

        # 3. Generation Step
        logging.info("Sending prompt to LLM for generation...")
        # Note: `llama_cpp.Llama`'s generation is a blocking, CPU/GPU-bound operation.
        # In a high-concurrency FastAPI app, you might run this in a separate
        # thread pool to avoid blocking the main event loop, but for now, a
        # direct call is sufficient.
        llm_response = generate_text(llm, final_prompt)
        logging.info("Received response from LLM.")

        return llm_response
    except Exception as e:
        logging.exception(f"An error occurred during RAG pipeline execution: {e}")
        return "I'm sorry, I encountered an error while trying to generate a response."
