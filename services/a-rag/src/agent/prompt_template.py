"""
file: TGB-MicroSuite/services/a-rag/src/agent/prompt_template.py

Manages the construction of prompts for the Language Model.

This module defines the templates and logic required to build rich,
context-aware prompts using techniques like few-shot learning and RAG.
"""

from typing import Dict, List

# This could be loaded from a config file or a database in the future.
FEW_SHOT_EXAMPLES = [
    {
        "input": "What is dependency injection?",
        "output": "Dependency Injection is a design pattern used to implement IoC, where the control of creating and binding dependencies is passed to a container or framework.",
    },
    {
        "input": "Explain SOLID.",
        "output": "SOLID is an acronym for five design principles intended to make software designs more understandable, flexible, and maintainable. It stands for Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion.",
    },
]

# Using f-strings for simplicity, but Jinja2 could be used for more complex logic.
PROMPT_TEMPLATE = """
SYSTEM: You are a helpful and professional software engineering assistant. Your answers should be clear, concise, and based *only* on the provided context. If the context is not sufficient to answer, say "I don't have enough information to answer that question."

CONTEXT:
{context}

FEW-SHOT EXAMPLES:
{examples}

USER QUESTION:
{question}

ASSISTANT ANSWER:
"""


def format_examples(examples: List[Dict[str, str]]) -> str:
    """Formats the few-shot examples into a string for the prompt."""
    return "\n".join(
        [f"User: {ex['input']}\nAssistant: {ex['output']}" for ex in examples]
    )


def construct_prompt(question: str, context_chunks: List[str]) -> str:
    """
    Constructs the final prompt to be sent to the LLM.

    Args:
        question: The original question from the user.
        context_chunks: A list of relevant text chunks from the vector database.

    Returns:
        The fully formatted, context-rich prompt string.
    """
    formatted_context = "\n---\n".join(context_chunks)
    formatted_examples = format_examples(FEW_SHOT_EXAMPLES)

    return PROMPT_TEMPLATE.format(
        context=formatted_context, examples=formatted_examples, question=question
    )
