import re
from typing import Optional

from schemas import ChatHistoryMessage


def normalize_message(message: str) -> str:
    """
    Normalizes text for lightweight conversation matching.

    Time Complexity:
    - O(l), where l is the message length.
    """
    cleaned = re.sub(r"[^a-zA-Z0-9\s']", "", message.lower())
    return " ".join(cleaned.split())


def get_conversation_response(message: str) -> Optional[str]:
    """
    Handles common casual conversation locally without web search.

    Time Complexity:
    - Normalization: O(l)
    - Set lookups: O(1) average
    - Phrase checks: O(p × l), with p being a small fixed number of phrases.
    """
    normalized = normalize_message(message)

    greetings = {
        "hello",
        "hello there",
        "hi",
        "hi there",
        "hey",
        "hey there",
        "good morning",
        "good afternoon",
        "good evening",
    }

    wellbeing_phrases = (
        "how are you",
        "how are you doing",
        "how is it going",
        "how are things",
        "how do you do",
    )

    positive_replies = {
        "good",
        "great",
        "fine",
        "okay",
        "ok",
        "not bad",
        "im good",
        "i am good",
        "im fine",
        "i am fine",
        "doing good",
        "doing well",
        "very good",
    }

    thank_you_messages = {
        "thanks",
        "thank you",
        "thank you so much",
        "thanks a lot",
        "thank you very much",
    }

    goodbye_messages = {
        "bye",
        "goodbye",
        "see you",
        "see you later",
        "good night",
    }

    help_messages = {
        "help",
        "can you help me",
        "i need help",
        "what can you do",
    }

    if normalized in greetings:
        return (
            "Hello! I am Intellectual Assistant. "
            "What would you like help with today?"
        )

    if any(phrase in normalized for phrase in wellbeing_phrases):
        return (
            "I'm doing well and ready to help. "
            "How has your day been so far?"
        )

    if normalized in positive_replies:
        return (
            "Glad to hear that. "
            "What would you like help with today?"
        )

    if normalized in thank_you_messages:
        return (
            "You are welcome. "
            "Let me know what you would like to explore next."
        )

    if normalized in goodbye_messages:
        return "Goodbye! It was nice helping you."

    if normalized in help_messages:
        return (
            "I can answer from my knowledge base, search the web for current "
            "information, and provide source links for web-based answers."
        )

    return None


def get_previous_user_message(
    history: list[ChatHistoryMessage],
) -> str:
    """
    Gets the most recent user message from conversation history.

    Time Complexity:
    - O(h), where h is capped at 8.
    """
    for history_message in reversed(history):
        if history_message.role == "user":
            return history_message.content.strip()

    return ""


def resolve_what_about_follow_up(
    message: str,
    previous_question: str,
) -> Optional[str]:
    """
    Resolves follow-ups such as:

    Previous: Who is the president of France?
    Current: What about Nigeria?
    Result: Who is the president of Nigeria?

    Time Complexity:
    - Regex matching/replacement: O(q), where q is question length.
    """
    follow_up_match = re.fullmatch(
        r"\s*(?:and\s+)?what\s+about\s+(.+?)\s*\??\s*",
        message,
        flags=re.IGNORECASE,
    )

    if not follow_up_match or not previous_question:
        return None

    new_subject = follow_up_match.group(1).strip()

    # Handles a question ending in "of France?", "in France?", etc.
    location_pattern = r"\b(of|in|for|about)\s+[A-Za-z][A-Za-z\s-]*\??$"

    if re.search(location_pattern, previous_question, flags=re.IGNORECASE):
        rewritten_question = re.sub(
            location_pattern,
            lambda match: f"{match.group(1)} {new_subject}?",
            previous_question,
            flags=re.IGNORECASE,
        )

        return rewritten_question

    # A safe fallback that preserves both the subject and context.
    return f"{previous_question} Specifically for {new_subject}."


def build_search_query(
    message: str,
    history: list[ChatHistoryMessage],
) -> str:
    """
    Builds a clear web-search query.

    It resolves short follow-ups into a full question before Tavily searches.

    Time Complexity:
    - Previous-message lookup: O(h), with h capped at 8.
    - Follow-up resolution: O(q), where q is question length.
    """
    previous_user_message = get_previous_user_message(history)

    resolved_query = resolve_what_about_follow_up(
        message=message,
        previous_question=previous_user_message,
    )

    if resolved_query:
        print(f"Resolved follow-up query: {resolved_query}")
        return resolved_query

    return message