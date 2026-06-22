import re
from dataclasses import dataclass
from typing import Optional

from schemas import ChatHistoryMessage


CREATOR_NAME = "Adesoji Abdulrahmon"

NAME_PATTERN = re.compile(
    r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b"
)

IGNORED_NAMES = {
    "Intellectual Assistant",
    "The President",
    "Federal Republic",
}


@dataclass(frozen=True)
class ContextResolution:
    rewritten_message: str
    direct_answer: Optional[str] = None


def normalize_message(message: str) -> str:
    """
    Normalizes a message before basic context matching.

    Time Complexity:
    - O(l), where l is message length.
    """
    cleaned = re.sub(r"[^a-zA-Z0-9\s']", "", message.lower())
    return " ".join(cleaned.split())


def history_mentions_creator(
    history: list[ChatHistoryMessage],
) -> bool:
    """
    Checks whether recent chat refers to Intellectual Assistant's creator.

    Time Complexity:
    - O(h × l), where h is capped conversation history.
    """
    history_text = " ".join(
        message.content.lower()
        for message in history
    )

    return (
        "creator" in history_text
        or CREATOR_NAME.lower() in history_text
    )


def extract_recent_named_entity(
    history: list[ChatHistoryMessage],
) -> Optional[str]:
    """
    Finds a likely person name from the most recent relevant messages.

    Time Complexity:
    - O(h × l), where h is capped history length.
    """
    for message in reversed(history):
        matches = NAME_PATTERN.findall(message.content)

        valid_matches = [
            match
            for match in matches
            if match not in IGNORED_NAMES
        ]

        if valid_matches:
            return valid_matches[-1]

    return None


def resolve_contextual_message(
    message: str,
    history: list[ChatHistoryMessage],
) -> ContextResolution:
    """
    Resolves short follow-up questions before knowledge lookup or web search.

    Examples:
    - "How old is he?" after a public-figure answer
      becomes "How old is Emmanuel Macron?"

    - "How old is he?" after creator information
      returns an honest local response rather than guessing.

    Time Complexity:
    - Message normalization: O(l)
    - History analysis: O(h × l)
    """
    normalized = normalize_message(message)

    is_age_question = any(
        phrase in normalized
        for phrase in (
            "how old is he",
            "how old is she",
            "how old are they",
            "what is his age",
            "what is her age",
            "what is their age",
        )
    )

    asks_about_age_source = (
        "how did you know" in normalized
        and ("age" in normalized or "old" in normalized)
    )

    creator_context = history_mentions_creator(history)

    if asks_about_age_source and creator_context:
        return ContextResolution(
            rewritten_message=message,
            direct_answer=(
                "I did not have verified information about "
                "Adesoji Abdulrahmon's age. I should not guess or present "
                "an unverified age as fact."
            ),
        )

    if is_age_question and creator_context:
        return ContextResolution(
            rewritten_message=message,
            direct_answer=(
                "You appear to be referring to Adesoji Abdulrahmon. "
                "I do not have verified information about his age, "
                "so I do not want to guess."
            ),
        )

    if is_age_question:
        entity = extract_recent_named_entity(history)

        if entity:
            return ContextResolution(
                rewritten_message=f"How old is {entity}?",
            )

        return ContextResolution(
            rewritten_message=message,
            direct_answer=(
                "Who are you referring to? Please mention the person's "
                "name so I can answer accurately."
            ),
        )

    return ContextResolution(
        rewritten_message=message,
    )