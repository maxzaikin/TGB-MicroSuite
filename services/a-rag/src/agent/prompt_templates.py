# file: services/a-rag/src/agent/prompt_templates.py

"""
Manages the construction of prompts for the Language Model.

This module defines the templates required for various RAG and generation tasks.
All templates are defined as standard strings with named placeholders to be
used with the .format() method.
"""

from typing import Dict, List

# --- Templates for Advanced RAG Steps ---

QUERY_EXPANSION_PROMPT_TEMPLATE = """You are a helpful AI assistant. Your task is to generate {num_queries} different versions of the given user question to retrieve relevant documents from a vector database.
By generating multiple perspectives on the user question, your goal is to help the user overcome some of the limitations of distance-based similarity search.
Provide these alternative questions separated by a newline character.
Do not number the questions.

Original question: {question}"""


# --- [FIX] ---
# This is now a simple template string with TWO placeholders:
# {valid_doc_types} and {query}.
# All formatting will be done at the point of use in `rag_steps.py`.
# All literal curly braces are escaped by doubling them (e.g., {{ and }}).

SELF_QUERY_PROMPT_TEMPLATE = """You are an expert AI assistant that extracts structured information from a user's query to be used for database filtering.
Your task is to extract any of the following metadata fields if they are present in the user's query.
If a value for a field is not present in the query, do not include the key for that field in your response.

The valid fields to extract are:
- 'author': The name of an author.
- 'document_type': The type of a document. Valid values for 'document_type' are: {valid_doc_types}.

Respond ONLY with a valid JSON object. Do not include any explanations, markdown formatting, or any text before or after the JSON object.
If no relevant information is found, return an empty JSON object: {{}}.

Here are some examples:

User Query: "Tell me about RAG based on articles by Paul Iusztin"
JSON Response: {{"author": "Paul Iusztin"}}

User Query: "Show me some python examples from the markdown files"
JSON Response: {{"document_type": "md"}}

User Query: "What is Query Expansion?"
JSON Response: {{}}

---
User Query:
{query}
"""