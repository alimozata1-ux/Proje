from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


@dataclass(slots=True)
class ChatMessage:
    role: str
    content: str
    created_at: str | None = None


class ConversationMemory:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()

    def add(self, role: str, content: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO conversations(role, content) VALUES (?, ?)",
                (role, content),
            )
            conn.commit()

    def bulk_add(self, messages: Iterable[ChatMessage]) -> None:
        payload = [(m.role, m.content) for m in messages]
        if not payload:
            return
        with self._connect() as conn:
            conn.executemany(
                "INSERT INTO conversations(role, content) VALUES (?, ?)",
                payload,
            )
            conn.commit()

    def latest(self, limit: int = 10) -> List[ChatMessage]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT role, content, created_at
                FROM conversations
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [ChatMessage(role=r[0], content=r[1], created_at=r[2]) for r in rows]

    def save_metric(self, name: str, value: float) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO metrics(metric_name, metric_value) VALUES (?, ?)",
                (name, value),
            )
            conn.commit()

    def metric_series(self, name: str, limit: int = 60) -> list[float]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT metric_value
                FROM metrics
                WHERE metric_name = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (name, limit),
            ).fetchall()
        return [float(r[0]) for r in rows[::-1]]

    def clear(self) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM conversations")
            conn.execute("DELETE FROM metrics")
            conn.commit()
