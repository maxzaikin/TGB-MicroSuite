"""
tgrambuddy/tgramllm/src/llm/services/engine.py

This module simulates a Large Language Model (LLM) engine service with mock
functions to load, unload, and generate text from an LLM model.

The mock implementations imitate the delays and behaviors of a real LLM
without performing actual model inference.
"""

import time
import asyncio
from ..core.config import settings  # For accessing MODEL_PATH_DUMMY if needed

# Global variable to simulate model load state
_mock_model_loaded = False

def load_llm_model():
    """
    Simulates loading of the LLM model.

    This function sets the global model loaded state to True after a delay,
    mimicking the time taken to load a large model from disk or memory.
    """
    global _mock_model_loaded
    if not _mock_model_loaded:
        print(f"LLM Engine: Simulating loading model from '{settings.MODEL_PATH_DUMMY}'...")
        time.sleep(1)  # Simulate delay
        _mock_model_loaded = True
        print("LLM Engine: Model 'loaded' (mock).")

def unload_llm_model():
    """
    Simulates unloading of the LLM model.

    This function resets the global model loaded state to False after a delay,
    mimicking the time taken to release model resources.
    """
    global _mock_model_loaded
    if _mock_model_loaded:
        print("LLM Engine: Simulating unloading model...")
        time.sleep(0.5)  # Simulate delay
        _mock_model_loaded = False
        print("LLM Engine: Model 'unloaded' (mock).")

async def generate_text(prompt: str, max_tokens: int = 150) -> str:
    """
    Simulates text generation by the LLM model.

    Args:
        prompt (str): The input text prompt to generate text from.
        max_tokens (int, optional): The maximum number of tokens to generate.
            Defaults to 150.

    Returns:
        str: A mock generated response or an error message if the model is
        not loaded.
    """
    if not _mock_model_loaded:
        # Could auto-load here, but for simplicity return error message
        # load_llm_model()  # Uncomment to enable auto-loading on first call
        return "Error: LLM model is not loaded (mock)."
    
    print(f"LLM Engine (mock): Received prompt '{prompt[:30]}...', max_tokens={max_tokens}")
    await asyncio.sleep(0.2)  # Simulate asynchronous processing delay
    return f"Mock response for: '{prompt}'. Generated (simulated) {max_tokens} tokens."

