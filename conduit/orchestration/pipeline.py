from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal

from conduit.core.ports import CandidateTask, Cursor, Extractor, RawItem, Sink, Source, TaskStore
from conduit.core.task import Priority, SourceRef, Task, TaskKind, dedup_id


_TODO_RE = re.compile(
    r"^TODO:\s+(?P<title>.+?)(?:\s+@(?P<date>\d{4}-\d{2}-\d{2}))?(?:\s+!(?P<priority>low|normal|high))?\s*$",
    re.IGNORECASE,
)

_PRIORITY_MAP: dict[str, Priority] = {
    "low": Priority.LOW,
    "normal": Priority.NORMAL,
    "high": Priority.HIGH,
}


@dataclass
class PipelineConfig:
    confidence_threshold: float = 0.5
    fallback_action: Literal["discard", "tag"] = "discard"
    fallback_tag_prefix: str | None = None  # e.g. "[REVIEW]"; used when fallback_action == "tag"


@dataclass
class PipelineResult:
    tasks_pushed: int = 0
    tasks_skipped_dedup: int = 0
    tasks_below_threshold: int = 0
    sources_processed: int = 0
    errors: list[str] = field(default_factory=list)


def run_pipeline(
    sources: list[Source],
    extractor: Extractor,
    sink: Sink,
    store: TaskStore,
    config: PipelineConfig | None = None,
    tier: Literal["bulk", "accurate"] = "accurate",
) -> PipelineResult:
    """
    fetch → fast-path / extract → confidence gate → dedup → push → advance cursor
    """
    cfg = config or PipelineConfig()
    result = PipelineResult()
    now = datetime.now(timezone.utc)
    to_push: list[Task] = []

    for source in sources:
        cursor: Cursor = store.cursor(source.id)
        try:
            items = source.fetch(since=cursor)
        except Exception as exc:
            result.errors.append(f"[{source.id}] fetch failed: {exc}")
            continue

        for item in items:
            try:
                fast = _fast_path(item)
                candidates: list[CandidateTask] = (
                    fast if fast is not None else extractor.extract(item, tier=tier)
                )
            except Exception as exc:
                result.errors.append(f"[{source.id}] extraction failed: {exc}")
                continue

            for candidate in candidates:
                _route(candidate, item, cfg, store, to_push, result, now)

        store.set_cursor(source.id, now)
        result.sources_processed += 1

    if to_push:
        try:
            push_result = sink.push(to_push)
            store.upsert(to_push)
            result.tasks_pushed += push_result.pushed
            result.errors.extend(push_result.errors)
        except Exception as exc:
            result.errors.append(f"[{sink.id}] push failed: {exc}")

    return result


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _route(
    candidate: CandidateTask,
    item: RawItem,
    cfg: PipelineConfig,
    store: TaskStore,
    to_push: list[Task],
    result: PipelineResult,
    now: datetime,
) -> None:
    if candidate.confidence < cfg.confidence_threshold:
        result.tasks_below_threshold += 1
        if cfg.fallback_action != "tag" or not cfg.fallback_tag_prefix:
            return
        candidate.title = f"{cfg.fallback_tag_prefix} {candidate.title}"

    task_id = dedup_id(item.source_ref, candidate.title)
    if store.seen(task_id):
        result.tasks_skipped_dedup += 1
        return

    to_push.append(_promote(candidate, item.source_ref, now))


def _fast_path(item: RawItem) -> list[CandidateTask] | None:
    """Return a full-confidence candidate for explicit TODO: markers; None otherwise."""
    match = _TODO_RE.match(item.text.strip())
    if not match:
        return None
    due = None
    if match.group("date"):
        try:
            due = datetime.fromisoformat(match.group("date")).replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    return [
        CandidateTask(
            title=match.group("title").strip(),
            confidence=1.0,
            triggering_statement=item.text.strip(),
            priority=_PRIORITY_MAP.get((match.group("priority") or "").lower()),
            due=due,
        )
    ]


def _promote(candidate: CandidateTask, source_ref: SourceRef, created: datetime) -> Task:
    """Merge extractor output with source provenance into a canonical Task."""
    ref = SourceRef(
        source_id=source_ref.source_id,
        item_ref=source_ref.item_ref,
        fetched_at=source_ref.fetched_at,
        triggering_statement=candidate.triggering_statement,
        triggering_location=candidate.triggering_location,
    )
    return Task(
        title=candidate.title,
        source_ref=ref,
        confidence=candidate.confidence,
        created=created,
        kind=candidate.kind,
        due=candidate.due,
        priority=candidate.priority,
        description=candidate.description,
        metadata=dict(candidate.metadata),
    )
