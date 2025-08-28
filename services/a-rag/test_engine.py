# file: services/a-rag/_test_engine.py
"""
A simple, temporary script to directly test the RAG agent engine.

This script bypasses the API layer to quickly verify that the LLM model
can be loaded and can generate responses to a given prompt.
"""

import asyncio
import logging
import sys
from pathlib import Path

# --- Setup Python Path ---
# This is required to run the script from the service root and allow it
# to find the 'src' package.
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

# --- Import our engine ---
from agent import engine
from agent.prompt_templates import construct_prompt


async def run_test():
    """
    Main test execution function.
    """
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    # 1. Load the model
    print("--- 1. Loading LLM Model ---")
    engine.load_llm_model()
    if engine.llm is None:
        print("!!! MODEL FAILED TO LOAD. TEST ABORTED. !!!")
        return
    print("--- Model Loaded Successfully ---\n")

    # 2. Define a user query and construct a prompt
    print("--- 2. Constructing Prompt ---")
    user_query = "What is Clean Code? Explain in one sentence."

    # We use mock context, just like the real engine does for now.
    mock_context = [
        "Clean Code is readable and maintainable.",
        "It was written by Robert C. Martin.",
    ]

    final_prompt = construct_prompt(question=user_query, context_chunks=mock_context)

    print(f"User Query: {user_query}")
    print(f"Final Prompt (first 100 chars): {final_prompt[:100]}...")
    print("--- Prompt Constructed ---\n")

    # 3. Generate a response
    print("--- 3. Generating Response (this may take a moment) ---")

    # We call the synchronous `generate_text` function directly for this test.
    # In a real async app, we would use `asyncio.to_thread`.
    response_text = engine.generate_text(final_prompt)

    print("\n--- LLM RESPONSE ---")
    print(response_text)
    print("--------------------")


if __name__ == "__main__":
    # Run the asynchronous test function.
    asyncio.run(run_test())
