from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from conduit.core.ports import PushResult
from conduit.core.task import Priority, Status, Task, TaskKind


class FileSink:
    """Writes extracted tasks to a JSON file in an output directory.

    Each run produces one timestamped file: tasks_YYYYMMDD_HHMMSS.json
    This is the alpha "consume" path — the same interface Jot and other
    real sinks will implement.
    """

    def __init__(self, output_dir: Path, sink_id: str = "file") -> None:
        self.id = sink_id
        self._output_dir = output_dir
        self._output_dir.mkdir(parents=True, exist_ok=True)

    def push(self, tasks: list[Task]) -> PushResult:
        if not tasks:
            return PushResult(pushed=0, failed=0)

        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        out_path = self._output_dir / f"tasks_{ts}.json"

        payload = [_task_to_dict(t) for t in tasks]
        out_path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")

        return PushResult(pushed=len(tasks), failed=0)


def _task_to_dict(task: Task) -> dict:
    ref = task.source_ref
    return {
        "id": task.id,
        "title": task.title,
        "kind": task.kind.value if isinstance(task.kind, TaskKind) else task.kind,
        "confidence": task.confidence,
        "priority": task.priority.value if isinstance(task.priority, Priority) else task.priority,
        "status": task.status.value if isinstance(task.status, Status) else task.status,
        "due": task.due.isoformat() if task.due else None,
        "description": task.description,
        "created": task.created.isoformat(),
        "source": {
            "source_id": ref.source_id,
            "item_ref": ref.item_ref,
            "fetched_at": ref.fetched_at.isoformat(),
            "triggering_statement": ref.triggering_statement,
            "triggering_location": ref.triggering_location,
        },
        "metadata": task.metadata,
    }
