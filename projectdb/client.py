from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


class ProjectDatabase:
    """Proje kayıtları için özel SQLite kütüphanesi."""

    def __init__(self, db_path: str | Path):
        self.db_path = str(db_path)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    size_mb TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    download_count INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def add_project(self, title: str, description: str, size_mb: str, filename: str) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO projects (title, description, size_mb, filename)
                VALUES (?, ?, ?, ?)
                """,
                (title, description, size_mb, filename),
            )
            return int(cur.lastrowid)

    def list_projects(self) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, title, description, size_mb, filename, download_count, created_at
                FROM projects
                ORDER BY id DESC
                """
            ).fetchall()
            return [dict(row) for row in rows]

    def get_project(self, project_id: int) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT id, title, description, size_mb, filename, download_count, created_at
                FROM projects
                WHERE id = ?
                """,
                (project_id,),
            ).fetchone()
            if not row:
                return None

            conn.execute(
                "UPDATE projects SET download_count = download_count + 1 WHERE id = ?",
                (project_id,),
            )
            updated = dict(row)
            updated["download_count"] += 1
            return updated
