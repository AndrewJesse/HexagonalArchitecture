# Adapter — SQLite output adapter.
#
# Implements the PayloadWriter port for SQLite persistence.
# This is a "driven" (secondary) adapter: the application drives it
# through the port interface to persist data.
from pathlib import Path
import sqlite3

from domain.transform import Payload

_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS payload (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    date DATETIME NOT NULL
);
"""


class SqliteStore:
    def __init__(self, path: str = "app.db") -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(path)
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        self._conn.executescript(_SCHEMA_SQL)
        self._conn.commit()

    def write(self, data: Payload) -> None:
        self._conn.execute(
            "INSERT INTO payload (text, date) VALUES (?, ?)",
            (data.text, data.date),
        )
        self._conn.commit()
