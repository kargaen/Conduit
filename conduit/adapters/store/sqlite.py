from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from conduit.core.ports import Cursor
from conduit.core.task import Priority, SourceRef, Status, Task, TaskKind


_SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id                   TEXT PRIMARY KEY,
    title                TEXT NOT NULL,
    source_id            TEXT NOT NULL,
    item_ref             TEXT NOT NULL,
    fetched_at           TEXT NOT NULL,
    triggering_statement TEXT NOT NULL,
    triggering_location  TEXT,
    confidence           REAL NOT NULL,
    created              TEXT NOT NULL,
    kind                 TEXT NOT NULL,
    due                  TEXT,
    priority             TEXT,
    status               TEXT NOT NULL,
    description          TEXT,
    metadata             TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS source_cursors (
    source_id TEXT PRIMARY KEY,
    cursor     TEXT
);
"""


class SQLiteTaskStore:
    def __init__(self, db_path: Path) -> None:
        self._conn = sqlite3.connect(str(db_path))
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    def upsert(self, tasks: list[Task]) -> None:
        self._conn.executemany(
            """
            INSERT OR REPLACE INTO tasks (
                id, title, source_id, item_ref, fetched_at,
                triggering_statement, triggering_location, confidence,
                created, kind, due, priority, status, description, metadata
            ) VALUES (
                :id, :title, :source_id, :item_ref, :fetched_at,
                :triggering_statement, :triggering_location, :confidence,
                :created, :kind, :due, :priority, :status, :description, :metadata
            )
            """,
            [_to_row(t) for t in tasks],
        )
        self._conn.commit()

    def seen(self, id: str) -> bool:
        return self._conn.execute(
            "SELECT 1 FROM tasks WHERE id = ?", (id,)
        ).fetchone() is not None

    def cursor(self, source_id: str) -> Cursor:
        row = self._conn.execute(
            "SELECT cursor FROM source_cursors WHERE source_id = ?", (source_id,)
        ).fetchone()
        if row is None or row["cursor"] is None:
            return None
        return datetime.fromisoformat(row["cursor"])

    def set_cursor(self, source_id: str, cursor: Cursor) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO source_cursors (source_id, cursor) VALUES (?, ?)",
            (source_id, cursor.isoformat() if cursor else None),
        )
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> SQLiteTaskStore:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


def _to_row(task: Task) -> dict:
    ref = task.source_ref
    return {
        "id": task.id,
        "title": task.title,
        "source_id": ref.source_id,
        "item_ref": ref.item_ref,
        "fetched_at": ref.fetched_at.isoformat(),
        "triggering_statement": ref.triggering_statement,
        "triggering_location": ref.triggering_location,
        "confidence": task.confidence,
        "created": task.created.isoformat(),
        "kind": task.kind.value if isinstance(task.kind, TaskKind) else task.kind,
        "due": task.due.isoformat() if task.due else None,
        "priority": task.priority.value if isinstance(task.priority, Priority) else task.priority,
        "status": task.status.value if isinstance(task.status, Status) else task.status,
        "description": task.description,
        "metadata": json.dumps(task.metadata),
    }
