from datetime import datetime, timezone
from typing import Literal

import pytest

from conduit.core.ports import CandidateTask, Cursor, PushResult, RawItem
from conduit.core.task import Priority, SourceRef, Task, TaskKind
from conduit.orchestration.pipeline import (
    PipelineConfig,
    PipelineResult,
    _fast_path,
    run_pipeline,
)


# ---------------------------------------------------------------------------
# Stubs
# ---------------------------------------------------------------------------

def _ref(source_id="src", item_ref="note.txt") -> SourceRef:
    return SourceRef(
        source_id=source_id,
        item_ref=item_ref,
        fetched_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        triggering_statement="placeholder",
    )


def _item(text: str, source_id="src", item_ref="note.txt") -> RawItem:
    return RawItem(source_ref=_ref(source_id, item_ref), text=text)


class _StubSource:
    def __init__(self, items: list[RawItem], source_id: str = "src"):
        self.id = source_id
        self._items = items

    def fetch(self, since: Cursor) -> list[RawItem]:
        return self._items


class _StubExtractor:
    def __init__(self, candidates: list[CandidateTask]):
        self._candidates = candidates

    def extract(self, item: RawItem, tier: Literal["bulk", "accurate"] = "accurate") -> list[CandidateTask]:
        return self._candidates


class _StubSink:
    def __init__(self):
        self.id = "stub-sink"
        self.received: list[Task] = []

    def push(self, tasks: list[Task]) -> PushResult:
        self.received.extend(tasks)
        return PushResult(pushed=len(tasks), failed=0)


class _StubStore:
    def __init__(self):
        self._seen: set[str] = set()
        self._cursors: dict[str, Cursor] = {}

    def upsert(self, tasks: list[Task]) -> None:
        for t in tasks:
            self._seen.add(t.id)

    def seen(self, id: str) -> bool:
        return id in self._seen

    def cursor(self, source_id: str) -> Cursor:
        return self._cursors.get(source_id)

    def set_cursor(self, source_id: str, cursor: Cursor) -> None:
        self._cursors[source_id] = cursor


# ---------------------------------------------------------------------------
# Fast-path tests
# ---------------------------------------------------------------------------

class TestFastPath:
    def test_basic_todo(self):
        result = _fast_path(_item("TODO: Buy milk"))
        assert result is not None
        assert len(result) == 1
        assert result[0].title == "Buy milk"
        assert result[0].confidence == 1.0

    def test_todo_with_date(self):
        result = _fast_path(_item("TODO: Plan party @2026-08-01"))
        assert result is not None
        assert result[0].due == datetime(2026, 8, 1, tzinfo=timezone.utc)

    def test_todo_with_priority(self):
        result = _fast_path(_item("TODO: Call boss !high"))
        assert result is not None
        assert result[0].priority == Priority.HIGH

    def test_todo_low_priority(self):
        result = _fast_path(_item("TODO: Water plants !low"))
        assert result is not None
        assert result[0].priority == Priority.LOW

    def test_non_todo_returns_none(self):
        assert _fast_path(_item("Remember to buy milk")) is None

    def test_empty_returns_none(self):
        assert _fast_path(_item("")) is None

    def test_todo_case_insensitive(self):
        result = _fast_path(_item("todo: lowercase task"))
        assert result is not None
        assert result[0].title == "lowercase task"


# ---------------------------------------------------------------------------
# run_pipeline integration tests (all stubs, no I/O)
# ---------------------------------------------------------------------------

class TestRunPipeline:
    def test_basic_push(self):
        candidate = CandidateTask(
            title="Buy milk",
            confidence=0.9,
            triggering_statement="We need milk",
        )
        source = _StubSource([_item("We need milk")])
        extractor = _StubExtractor([candidate])
        sink = _StubSink()
        store = _StubStore()

        result = run_pipeline([source], extractor, sink, store)

        assert result.tasks_pushed == 1
        assert result.sources_processed == 1
        assert result.errors == []
        assert len(sink.received) == 1
        assert sink.received[0].title == "Buy milk"

    def test_below_threshold_discarded(self):
        candidate = CandidateTask(
            title="Maybe do something",
            confidence=0.3,
            triggering_statement="possibly",
        )
        source = _StubSource([_item("possibly")])
        extractor = _StubExtractor([candidate])
        sink = _StubSink()
        store = _StubStore()
        cfg = PipelineConfig(confidence_threshold=0.5)

        result = run_pipeline([source], extractor, sink, store, config=cfg)

        assert result.tasks_pushed == 0
        assert result.tasks_below_threshold == 1
        assert sink.received == []

    def test_below_threshold_tagged(self):
        candidate = CandidateTask(
            title="Maybe do something",
            confidence=0.3,
            triggering_statement="possibly",
        )
        source = _StubSource([_item("possibly")])
        extractor = _StubExtractor([candidate])
        sink = _StubSink()
        store = _StubStore()
        cfg = PipelineConfig(
            confidence_threshold=0.5,
            fallback_action="tag",
            fallback_tag_prefix="[REVIEW]",
        )

        result = run_pipeline([source], extractor, sink, store, config=cfg)

        assert result.tasks_pushed == 1
        assert sink.received[0].title == "[REVIEW] Maybe do something"

    def test_dedup_skips_seen_task(self):
        candidate = CandidateTask(
            title="Buy milk",
            confidence=0.9,
            triggering_statement="We need milk",
        )
        source = _StubSource([_item("We need milk")])
        extractor = _StubExtractor([candidate])
        sink = _StubSink()
        store = _StubStore()

        run_pipeline([source], extractor, sink, store)
        result2 = run_pipeline([source], extractor, sink, store)

        assert result2.tasks_skipped_dedup == 1
        assert result2.tasks_pushed == 0

    def test_fast_path_used_over_extractor(self):
        extractor = _StubExtractor([])  # would return nothing
        source = _StubSource([_item("TODO: Buy milk")])
        sink = _StubSink()
        store = _StubStore()

        result = run_pipeline([source], extractor, sink, store)

        assert result.tasks_pushed == 1
        assert sink.received[0].title == "Buy milk"
        assert sink.received[0].confidence == 1.0

    def test_empty_source_no_push(self):
        source = _StubSource([])
        extractor = _StubExtractor([])
        sink = _StubSink()
        store = _StubStore()

        result = run_pipeline([source], extractor, sink, store)

        assert result.tasks_pushed == 0
        assert result.sources_processed == 1

    def test_fetch_error_captured(self):
        class _FailSource:
            id = "bad-src"
            def fetch(self, since): raise RuntimeError("network down")

        sink = _StubSink()
        store = _StubStore()
        extractor = _StubExtractor([])

        result = run_pipeline([_FailSource()], extractor, sink, store)

        assert result.tasks_pushed == 0
        assert any("fetch failed" in e for e in result.errors)
