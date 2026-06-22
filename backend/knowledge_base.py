import json
from pathlib import Path


KNOWLEDGE_FILE = Path(__file__).resolve().parent.parent / "data" / "knowledge.json"


def load_knowledge():
    """
    Loads knowledge base from JSON file.

    Time Complexity:
    - O(n), where n is the number of knowledge entries.
    """
    if not KNOWLEDGE_FILE.exists():
        return []

    with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def search_knowledge(user_message: str):
    """
    Searches the local knowledge base before using AI/web search.

    Time Complexity:
    - O(n * k), where:
      n = number of knowledge entries
      k = average number of keywords per entry
    """
    knowledge_items = load_knowledge()
    user_message = user_message.lower()

    for item in knowledge_items:
        keywords = item.get("keywords", [])

        for keyword in keywords:
            if keyword.lower() in user_message:
                return item.get("answer")

    return None