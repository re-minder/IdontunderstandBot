import os
import sqlite3
from datetime import datetime
from typing import Optional


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS stored_video (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  file_id TEXT NOT NULL,
  created_at TEXT NOT NULL
);
"""


class VideoStorage:
    def __init__(self, database_path: str) -> None:
        self.database_path = database_path
        self._ensure_parent_directory()
        self._initialize()

    def _ensure_parent_directory(self) -> None:
        parent_directory = os.path.dirname(self.database_path)
        if parent_directory and not os.path.exists(parent_directory):
            os.makedirs(parent_directory, exist_ok=True)

    def _initialize(self) -> None:
        with sqlite3.connect(self.database_path) as connection:
            connection.execute("PRAGMA journal_mode=WAL;")
            connection.execute(SCHEMA_SQL)
            connection.commit()

    def upsert_video(self, file_id: str) -> None:
        now_iso = datetime.utcnow().isoformat()
        with sqlite3.connect(self.database_path) as connection:
            connection.execute(
                """
                INSERT INTO stored_video (id, file_id, created_at)
                VALUES (1, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                  file_id = excluded.file_id,
                  created_at = excluded.created_at
                """,
                (file_id, now_iso),
            )
            connection.commit()

    def get_video_file_id(self) -> Optional[str]:
        with sqlite3.connect(self.database_path) as connection:
            cursor = connection.execute("SELECT file_id FROM stored_video WHERE id = 1")
            row = cursor.fetchone()
            return row[0] if row else None

    def has_video(self) -> bool:
        return self.get_video_file_id() is not None


