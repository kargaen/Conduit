from datetime import datetime, timezone

import pytest

from conduit.extraction.llm import _parse, _parse_due, _parse_entry
from conduit.core.task import Priority, TaskKind


class TestParseDue:
    def test_date_only(self):
        result = _parse_due("2026-08-01", None)
        assert result == datetime(2026, 8, 1, tzinfo=timezone.utc)

    def test_date_and_time(self):
        result = _parse_due("2026-08-01", "14:30")
        assert result == datetime(2026, 8, 1, 14, 30, tzinfo=timezone.utc)

    def test_none_date_returns_none(self):
        assert _parse_due(None, None) is None
        assert _parse_due(None, "14:00") is None

    def test_invalid_date_returns_none(self):
        assert _parse_due("not-a-date", None) is None

    def test_invalid_time_falls_back_to_midnight(self):
        result = _parse_due("2026-08-01", "bad-time")
        assert result == datetime(2026, 8, 1, tzinfo=timezone.utc)

    def test_empty_string_date_returns_none(self):
        assert _parse_due("", None) is None


class TestParseEntry:
    def _valid(self, **kwargs):
        base = {
            "title": "Buy milk",
            "confidence": 0.9,
            "triggering_statement": "We need milk",
            "kind": "action",
        }
        return {**base, **kwargs}

    def test_valid_entry(self):
        result = _parse_entry(self._valid())
        assert result is not None
        assert result.title == "Buy milk"
        assert result.confidence == 0.9
        assert result.triggering_statement == "We need milk"

    def test_kind_action(self):
        result = _parse_entry(self._valid(kind="action"))
        assert result.kind == TaskKind.ACTION

    def test_kind_planning(self):
        result = _parse_entry(self._valid(kind="planning"))
        assert result.kind == TaskKind.PLANNING

    def test_unknown_kind_defaults_to_action(self):
        result = _parse_entry(self._valid(kind="unknown"))
        assert result.kind == TaskKind.ACTION

    def test_priority_high(self):
        result = _parse_entry(self._valid(priority="high"))
        assert result.priority == Priority.HIGH

    def test_priority_low(self):
        result = _parse_entry(self._valid(priority="low"))
        assert result.priority == Priority.LOW

    def test_priority_omitted_is_none(self):
        result = _parse_entry(self._valid())
        assert result.priority is None

    def test_missing_title_returns_none(self):
        entry = self._valid()
        del entry["title"]
        assert _parse_entry(entry) is None

    def test_empty_title_returns_none(self):
        assert _parse_entry(self._valid(title="")) is None
        assert _parse_entry(self._valid(title="   ")) is None

    def test_missing_confidence_returns_none(self):
        entry = self._valid()
        del entry["confidence"]
        assert _parse_entry(entry) is None

    def test_missing_triggering_statement_returns_none(self):
        entry = self._valid()
        del entry["triggering_statement"]
        assert _parse_entry(entry) is None

    def test_description_preserved(self):
        result = _parse_entry(self._valid(description="Some extra context"))
        assert result.description == "Some extra context"

    def test_due_date_parsed(self):
        result = _parse_entry(self._valid(due_date="2026-08-01", due_time="09:00"))
        assert result.due == datetime(2026, 8, 1, 9, 0, tzinfo=timezone.utc)

    def test_non_dict_returns_none(self):
        assert _parse_entry("a string") is None
        assert _parse_entry(42) is None
        assert _parse_entry(None) is None


class TestParse:
    def test_empty_list(self):
        assert _parse([]) == []

    def test_non_list_returns_empty(self):
        assert _parse({}) == []
        assert _parse(None) == []
        assert _parse("string") == []

    def test_skips_invalid_entries(self):
        raw = [
            {"title": "Good task", "confidence": 0.9, "triggering_statement": "Do it"},
            {"bad": "entry"},
            None,
        ]
        result = _parse(raw)
        assert len(result) == 1
        assert result[0].title == "Good task"

    def test_multiple_valid_entries(self):
        raw = [
            {"title": "Task A", "confidence": 0.8, "triggering_statement": "A"},
            {"title": "Task B", "confidence": 0.7, "triggering_statement": "B"},
        ]
        result = _parse(raw)
        assert len(result) == 2
        assert {r.title for r in result} == {"Task A", "Task B"}
