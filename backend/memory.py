import json

from database import get_connection
from schemas import (
    ChatHistoryMessage,
    ConversationMessage,
    Source,
)


def save_message(
    conversation_id: str,
    role: str,
    content: str,
    source: str,
    sources: list[Source] | None = None,
) -> None:
    """
    Stores one chat message in SQLite.

    Time Complexity:
    - O(s), where s is the number of source links saved.
    - Database insertion is effectively O(log n) with the index.
    """
    source_payload = [
        source.model_dump()
        for source in (sources or [])
    ]

    connection = get_connection()

    try:
        connection.execute(
            """
            INSERT INTO messages (
                conversation_id,
                role,
                content,
                source,
                sources_json
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                conversation_id,
                role,
                content,
                source,
                json.dumps(source_payload),
            ),
        )

        connection.commit()

    finally:
        connection.close()


def get_recent_history(
    conversation_id: str,
    limit: int = 12,
) -> list[ChatHistoryMessage]:
    """
    Returns recent conversation messages in chronological order.

    Time Complexity:
    - Indexed database lookup: O(log n + h)
    - h is the capped history length.
    """
    safe_limit = max(1, min(limit, 20))

    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT role, content
            FROM messages
            WHERE conversation_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (conversation_id, safe_limit),
        ).fetchall()

    finally:
        connection.close()

    chronological_rows = list(reversed(rows))

    return [
        ChatHistoryMessage(
            role=row["role"],
            content=row["content"],
        )
        for row in chronological_rows
    ]


def get_conversation_messages(
    conversation_id: str,
    limit: int = 100,
) -> list[ConversationMessage]:
    """
    Loads saved messages so the frontend can restore a chat after refresh.

    Time Complexity:
    - Indexed lookup: O(log n + m)
    - JSON source decoding: O(s)
    - m = returned message count
    - s = source links per message
    """
    safe_limit = max(1, min(limit, 100))

    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT role, content, source, sources_json, created_at
            FROM messages
            WHERE conversation_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (conversation_id, safe_limit),
        ).fetchall()

    finally:
        connection.close()

    restored_messages = []

    for row in reversed(rows):
        try:
            decoded_sources = json.loads(row["sources_json"] or "[]")
        except json.JSONDecodeError:
            decoded_sources = []

        sources = [
            Source(
                title=item.get("title", "Untitled Source"),
                url=item.get("url", ""),
            )
            for item in decoded_sources
            if isinstance(item, dict)
        ]

        restored_messages.append(
            ConversationMessage(
                role=row["role"],
                content=row["content"],
                source=row["source"] or "assistant",
                sources=sources,
                created_at=row["created_at"],
            )
        )

    return restored_messages