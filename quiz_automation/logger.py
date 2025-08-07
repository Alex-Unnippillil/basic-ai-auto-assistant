"""SQLite logging for quiz automation events."""
from __future__ import annotations

import sqlite3
from datetime import datetime


class Logger:
    """Simple SQLite logger that records events with timestamps."""

    def __init__(self, path: str = "quiz_log.db") -> None:
        self.conn = sqlite3.connect(path)
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                ts TEXT,
                action TEXT,
                data TEXT
            )
            """
        )

    def log(self, action: str, data: str) -> None:
        ts = datetime.utcnow().isoformat()
        self.conn.execute(
            "INSERT INTO events (ts, action, data) VALUES (?, ?, ?)",
            (ts, action, data),
        )
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()
