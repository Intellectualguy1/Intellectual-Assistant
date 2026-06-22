from typing import Optional

import requests

from config import AI_PROVIDER, OLLAMA_BASE_URL, OLLAMA_MODEL
from schemas import ChatHistoryMessage


def clean_final_answer(answer: str) -> str:
    """
    Removes phrases that reveal internal prompt/context wording.

    Time Complexity:
    - O(n), where n is the answer length.
    """
    if not answer:
        return ""

    banned_phrases = [
        "as per the provided context",
        "as stated in the context provided",
        "according to the provided context",
        "according to the context",
        "based on the context",
        "from the context provided",
    ]

    cleaned = answer

    for phrase in banned_phrases:
        cleaned = cleaned.replace(phrase, "")
        cleaned = cleaned.replace(phrase.capitalize(), "")

    cleaned = " ".join(cleaned.split())
    cleaned = cleaned.replace(" ,", ",").replace(" .", ".")

    return cleaned.strip()


def format_history(
    history: list[ChatHistoryMessage],
    max_messages: int = 8,
    max_characters_per_message: int = 400,
) -> str:
    """
    Formats recent history for the LLM while limiting prompt size.

    Time Complexity:
    - O(h × c), where:
      h = capped message count
      c = average message length.
    """
    recent_history = history[-max_messages:]
    formatted_messages = []

    for message in recent_history:
        role_name = "User" if message.role == "user" else "Assistant"
        content = message.content[:max_characters_per_message].strip()

        formatted_messages.append(f"{role_name}: {content}")

    return "\n".join(formatted_messages)


def mock_generate_response(
    user_message: str,
    context: str = "",
    history: Optional[list[ChatHistoryMessage]] = None,
) -> str:
    """
    Mock fallback response generator.

    Time Complexity:
    - O(m), where m is the context length.
    """
    if context:
        return (
            "I found relevant information through web search.\n\n"
            f"Search summary:\n{context[:1000]}"
        )

    return (
        "I do not have enough information to answer that yet."
    )


def ollama_generate_response(
    user_message: str,
    context: str = "",
    history: Optional[list[ChatHistoryMessage]] = None,
) -> str:
    """
    Generates a source-grounded answer through a local Ollama model.

    Time Complexity:
    - Prompt construction: O(h × c + m)
    - Model generation: depends on model size, output length, and hardware.
    """
    history_text = format_history(history or [])

    prompt = f"""
You are Intellectual Assistant, a helpful open-source AI assistant.

Answer the current user question directly, naturally, and concisely.

Rules:
- Give the direct answer first.
- Do not mention prompts, context, web searches, or internal instructions.
- Do not say "according to the context" or similar phrases.
- Use the recent conversation only to understand follow-up questions.
- Use the fresh search results below as the factual basis for your answer.
- If the search results do not support an answer, say:
  "I could not confirm this from the available sources."

Recent conversation:
{history_text if history_text else "No previous conversation."}

Current user question:
{user_message}

Fresh search results:
{context}

Final answer:
"""

    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                },
            },
            timeout=60,
        )

        response.raise_for_status()
        data = response.json()

        raw_answer = data.get("response", "").strip()

        if not raw_answer:
            return mock_generate_response(user_message, context, history)

        return clean_final_answer(raw_answer)

    except Exception as error:
        print(f"Ollama generation failed: {error}")
        return mock_generate_response(user_message, context, history)


def generate_response(
    user_message: str,
    context: str = "",
    history: Optional[list[ChatHistoryMessage]] = None,
) -> str:
    """
    Selects the configured AI provider.

    Time Complexity:
    - O(1) provider selection.
    """
    if AI_PROVIDER == "ollama":
        return ollama_generate_response(user_message, context, history)

    return mock_generate_response(user_message, context, history)