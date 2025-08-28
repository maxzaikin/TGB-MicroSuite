# services/a-rag/src/agent/prompt_constructor.py

"""
Module for constructing sophisticated, role-based prompts for the LLM.
This version uses a much stricter system prompt for contextual answers
to reduce hallucinations and force the model to rely on provided text.
"""
from typing import Dict, List

# We will use OpenAI's standard MessageRole strings directly
from llama_index.core.llms import MessageRole

from src.core.schemas.chat_schemas import ChatMessage as AppChatMessage

# --- Base System Prompt & Persona Definition ---
BASE_SYSTEM_PROMPT = "You are TGBuddy, a helpful and direct assistant for the TGB-MicroSuite project."

# --- Few-Shot Examples for priming conversation ---
# Now defined as a list of dictionaries, the expected API format.
FEW_SHOT_EXAMPLES: List[Dict[str, str]] = [
    {"role": MessageRole.USER.value, "content": "What is your name?"},
    {"role": MessageRole.ASSISTANT.value, "content": "My name is TGBuddy."},
]

def _format_context_block(title: str, chunks: List[str]) -> str:
    """Helper to format a list of text chunks into a single block."""
    if not chunks:
        return ""
    return f"--- {title.upper()} ---\n" + "\n\n".join(chunks)

def build_chat_prompt(
    history: List[AppChatMessage],
    user_prompt: str,
    kb_context_chunks: List[str],
    chat_context_chunks: List[str],
) -> List[Dict[str, str]]:
    """
    Constructs a list of message dictionaries compliant with the OpenAI API format.
    """
    system_prompt_parts = [BASE_SYSTEM_PROMPT]
    
    if kb_context_chunks:
        # This part for the RAG response is already strict and works well.
        contextual_instruction = """You are a machine that answers questions based ONLY on the provided text.
1. Read the user's question carefully.
2. Read the provided context carefully.
3. Your answer MUST be extracted or synthesized directly from the context.
4. DO NOT use any external or pre-existing knowledge.
5. If the answer is not in the context, you MUST state: 'The provided context does not contain the answer to this question.'
"""
        system_prompt_parts.append(contextual_instruction)
        
        kb_context_str = _format_context_block("CONTEXT", kb_context_chunks)
        system_prompt_parts.append(kb_context_str)
    else:
        # --- [FIX] Implement strict guardrails for the LLM-only (no-context) case ---
        # Instead of allowing general knowledge, we instruct the model to be cautious
        # and admit when it doesn't know the answer, especially for specific topics.
        non_contextual_instruction = """You are answering without access to the internal knowledge base.
Follow these rules strictly:
1. If the user asks a general knowledge question (e.g., 'What is the capital of France?'), answer it concisely.
2. If the user asks a question that seems specific to a particular domain, standard, or internal project (like IEC 62443, TGB-MicroSuite, CSMS), you MUST assume you do not have the detailed information.
3. In that case, you MUST respond with: 'I do not have access to the specific knowledge base to answer this question accurately.'
4. DO NOT attempt to guess or generate a detailed answer for specific, technical, or project-related questions. Prioritize accuracy and honesty over being helpful.
"""
        system_prompt_parts.append(non_contextual_instruction)
        # --- End of fix ---

    final_system_prompt = "\n\n".join(system_prompt_parts)

    messages: List[Dict[str, str]] = [
        {"role": MessageRole.SYSTEM.value, "content": final_system_prompt}
    ]
    
    # Few-shot examples are good for general conversation, let's keep them for the LLM-only case.
    if not kb_context_chunks:
        messages.extend(FEW_SHOT_EXAMPLES)

    # Add conversation history.
    for msg in history:
        content = msg.content if msg.content is not None else ""
        messages.append({"role": msg.role, "content": content})
        
    # Add the current user prompt.
    messages.append({"role": MessageRole.USER.value, "content": user_prompt})

    return messages