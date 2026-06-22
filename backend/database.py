import sqlite3
from pathlib import Path


DATABASE_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "intellectual_assistant.db"
)


def get_connection() -> sqlite3.Connection:
    """
    Creates a SQLite connection.

    Time Complexity:
    - O(1)
    """
    DATABASE_FILE.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_FILE, timeout=15)
    connection.row_factory = sqlite3.Row

    return connection


def _ensure_column(
    connection: sqlite3.Connection,
    column_name: str,
    column_definition: str,
) -> None:
    """
    Adds a missing column for lightweight database migrations.

    Time Complexity:
    - O(c), where c is the number of table columns.
    """
    columns = connection.execute(
        "PRAGMA table_info(messages)"
    ).fetchall()

    existing_columns = {column["name"] for column in columns}

    if column_name not in existing_columns:
        connection.execute(
            f"ALTER TABLE messages ADD COLUMN {column_definition}"
        )


def initialize_database() -> None:
    """
    Creates the persistent conversation-memory table and indexes.

    Time Complexity:
    - O(1) for normal startup with a small schema.
    """
    connection = get_connection()

    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                source TEXT,
                sources_json TEXT NOT NULL DEFAULT '[]',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        _ensure_column(
            connection,
            "source",
            "source TEXT",
        )

        _ensure_column(
            connection,
            "sources_json",
            "sources_json TEXT NOT NULL DEFAULT '[]'",
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_messages_conversation_id
            ON messages(conversation_id, id)
            """
        )

        connection.commit()

    finally:
        connection.close()