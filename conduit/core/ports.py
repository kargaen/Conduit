from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal, Protocol

from conduit.core.task import Priority, SourceRef, Task, TaskKind


# ---------------------------------------------------------------------------
# Shared value objects (cross-boundary data carriers)
# ---------------------------------------------------------------------------

Cursor = datetime | None  # per-source watermark; None = fetch from beginning


@dataclass(frozen=True)
class RawItem:
    source_ref: SourceRef
    text: str = ""                  # populated by text sources
    image_bytes: bytes | None = None  # populated by vision sources (reMarkable images)


@dataclass
class CandidateTask:
    """Output of the extractor before orchestration promotes it to a Task."""
    title: str
    confidence: float               # 0.0–1.0
    triggering_statement: str
    kind: TaskKind = TaskKind.ACTION
    due: datetime | None = None
    priority: Priority | None = None
    description: str | None = None
    triggering_location: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PushResult:
    pushed: int
    failed: int
    errors: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Port interfaces
# Structural typing via Protocol — no isinstance checks against these.
# ---------------------------------------------------------------------------

class Source(Protocol):
    id: str

    def fetch(self, since: Cursor) -> list[RawItem]: ...


class Extractor(Protocol):
    def extract(
        self,
        item: RawItem,
        tier: Literal["bulk", "accurate"] = "accurate",
    ) -> list[CandidateTask]: ...


class Sink(Protocol):
    id: str

    def push(self, tasks: list[Task]) -> PushResult: ...


class TaskStore(Protocol):
    def upsert(self, tasks: list[Task]) -> None: ...
    def seen(self, id: str) -> bool: ...
    def cursor(self, source_id: str) -> Cursor: ...
    def set_cursor(self, source_id: str, cursor: Cursor) -> None: ...


class LLMProvider(Protocol):
    id: str

    def complete(
        self,
        prompt: str,
        output_schema: dict[str, Any],
        tier: Literal["bulk", "accurate"],
    ) -> Any: ...


class LLMRegistry(Protocol):
    def register(self, provider: LLMProvider) -> None: ...
    def active_provider(self) -> LLMProvider: ...
