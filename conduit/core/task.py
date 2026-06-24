from __future__ import annotations

import hashlib
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class Priority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class Status(str, Enum):
    OPEN = "open"
    DONE = "done"
    DISMISSED = "dismissed"


@dataclass(frozen=True)
class SourceRef:
    source_id: str                          # adapter id — "remarkable", "teams", …
    item_ref: str                           # source-specific item identifier
    fetched_at: datetime
    triggering_statement: str               # the text that produced this task
    triggering_location: str | None = None  # "line 34", "00:14:22", …


@dataclass
class Task:
    title: str
    source_ref: SourceRef
    confidence: float                       # 0.0–1.0 from extractor
    created: datetime
    due: datetime | None = None
    priority: Priority | None = None        # None = not inferred
    status: Status = Status.OPEN
    description: str | None = None          # optional plain-text context from extractor
    metadata: dict[str, Any] = field(default_factory=dict)
    id: str = field(init=False)

    def __post_init__(self) -> None:
        self.id = dedup_id(self.source_ref, self.title)


def dedup_id(source_ref: SourceRef, title: str) -> str:
    """Stable content-addressed id. Idempotent across re-runs of the same source."""
    normalized = unicodedata.normalize("NFKC", title).lower().strip()
    key = f"{source_ref.source_id}:{source_ref.item_ref}:{normalized}"
    return hashlib.sha256(key.encode()).hexdigest()[:32]
