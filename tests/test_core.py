from datetime import datetime, timezone

import pytest

from conduit.core.task import (
    Priority,
    SourceRef,
    Status,
    Task,
    TaskKind,
    dedup_id,
)


def _ref(**kwargs) -> SourceRef:
    defaults = dict(
        source_id="src",
        item_ref="item-1",
        fetched_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        triggering_statement="Do the thing",
    )
    return SourceRef(**{**defaults, **kwargs})


class TestDedupId:
    def test_deterministic(self):
        ref = _ref()
        assert dedup_id(ref, "Buy milk") == dedup_id(ref, "Buy milk")

    def test_strips_and_lowercases(self):
        ref = _ref()
        assert dedup_id(ref, "  Buy Milk  ") == dedup_id(ref, "buy milk")

    def test_differs_by_source_id(self):
        assert dedup_id(_ref(source_id="a"), "Task") != dedup_id(_ref(source_id="b"), "Task")

    def test_differs_by_item_ref(self):
        assert dedup_id(_ref(item_ref="a"), "Task") != dedup_id(_ref(item_ref="b"), "Task")

    def test_differs_by_title(self):
        ref = _ref()
        assert dedup_id(ref, "Task A") != dedup_id(ref, "Task B")

    def test_returns_32_char_hex(self):
        result = dedup_id(_ref(), "Buy milk")
        assert len(result) == 32
        assert all(c in "0123456789abcdef" for c in result)


class TestTask:
    def test_id_set_on_init(self):
        ref = _ref()
        task = Task(
            title="Buy milk",
            source_ref=ref,
            confidence=0.9,
            created=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
        assert task.id == dedup_id(ref, "Buy milk")

    def test_defaults(self):
        task = Task(
            title="T",
            source_ref=_ref(),
            confidence=1.0,
            created=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
        assert task.status == Status.OPEN
        assert task.kind == TaskKind.ACTION
        assert task.priority is None
        assert task.due is None
        assert task.description is None
        assert task.metadata == {}

    def test_two_tasks_same_source_different_titles_have_different_ids(self):
        ref = _ref()
        now = datetime(2026, 1, 1, tzinfo=timezone.utc)
        t1 = Task(title="A", source_ref=ref, confidence=1.0, created=now)
        t2 = Task(title="B", source_ref=ref, confidence=1.0, created=now)
        assert t1.id != t2.id


class TestEnums:
    def test_priority_values(self):
        assert Priority.LOW.value == "low"
        assert Priority.NORMAL.value == "normal"
        assert Priority.HIGH.value == "high"

    def test_status_values(self):
        assert Status.OPEN.value == "open"
        assert Status.DONE.value == "done"
        assert Status.DISMISSED.value == "dismissed"

    def test_task_kind_values(self):
        assert TaskKind.ACTION.value == "action"
        assert TaskKind.PLANNING.value == "planning"
