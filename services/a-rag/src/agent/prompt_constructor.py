# file: services/a-rag/src/agent/prompt_constructor.py
"""
Module for constructing sophisticated, role-based prompts for the LLM.
...
"""
from typing import Dict, List
# --- ИМПОРТИРУЕМ ChatMessage ИЗ LlamaIndex, А НЕ ИЗ НАШИХ СХЕМ ---
from llama_index.core.llms import ChatMessage, MessageRole

# Наша собственная схема нужна только для истории из Redis
from core.schemas.chat_schemas import ChatMessage as AppChatMessage

# --- System Prompt & Persona Definition ---
SYSTEM_PROMPT_TEMPLATE = """You are TGBuddy, a helpful and direct assistant for the TGB-MicroSuite project.
Provide concise, factual answers based on the provided context.
If the context does not contain the answer, say "I do not have enough information to answer that."

--- CONTEXT ---
{context_str}
---------------
"""

# --- Few-Shot Examples ---
# Теперь мы их сразу создаем как объекты ChatMessage
FEW_SHOT_EXAMPLES: List[ChatMessage] = [
    ChatMessage(role=MessageRole.USER, content="What is your name?"),
    ChatMessage(role=MessageRole.ASSISTANT, content="My name is TGBuddy."),
]

# --- Context Separator ---
CONTEXT_SEPARATOR: List[ChatMessage] = [
    ChatMessage(role=MessageRole.USER, content="Okay, I understand how you work. Let's start our conversation now."),
    ChatMessage(role=MessageRole.ASSISTANT, content="Great! I'm ready. How can I help you?"),
]


def build_chat_prompt(
    history: List[AppChatMessage], # Принимает наши Pydantic-объекты
    user_prompt: str,
    context_chunks: List[str],
) -> List[ChatMessage]: # <-- Возвращает объекты LlamaIndex
    """
    Constructs the full message list for the LLM call using LlamaIndex's
    ChatMessage objects.
    """
    # 1. Format the RAG context
    context_str = "\n\n---\n\n".join(context_chunks) if context_chunks else "No context provided."

    # 2. Inject context into the system prompt
    final_system_prompt = SYSTEM_PROMPT_TEMPLATE.format(context_str=context_str)
    
    # 3. Assemble the final message list using LlamaIndex's ChatMessage
    messages: List[ChatMessage] = [
        ChatMessage(role=MessageRole.SYSTEM, content=final_system_prompt)
    ]
    messages.extend(FEW_SHOT_EXAMPLES)
    messages.extend(CONTEXT_SEPARATOR)
    
    # Конвертируем нашу историю из Redis в формат LlamaIndex
    for msg in history:
        messages.append(ChatMessage(role=msg.role, content=msg.content))
        
    messages.append(ChatMessage(role=MessageRole.USER, content=user_prompt))

    return messages