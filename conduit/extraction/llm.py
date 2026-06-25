from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any, Literal

from conduit.core.ports import CandidateTask, LLMRegistry, RawItem
from conduit.core.task import Priority, TaskKind


_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "array",
    "items": {
        "type": "object",
        "required": ["title", "kind", "confidence", "triggering_statement"],
        "properties": {
            "title":                {"type": "string"},
            "kind":                 {"type": "string", "enum": ["action", "planning"]},
            "confidence":           {"type": "number", "minimum": 0.0, "maximum": 1.0},
            "triggering_statement": {"type": "string"},
            "triggering_location":  {"type": "string"},
            "due_date":             {"type": "string", "description": "YYYY-MM-DD"},
            "due_time":             {"type": "string", "description": "HH:MM 24h"},
            "priority":             {"type": "string", "enum": ["low", "normal", "high"]},
            "description":          {"type": "string"},
        },
    },
}


def _build_prompt(text: str, today: date) -> str:
    return f"""You are a task extraction assistant. Extract actionable tasks and planning questions from the text below.

Today's date is {today.isoformat()}.

Return a JSON array. For each task include:
- title: imperative verb phrase, e.g. "Send birthday invitations"
- kind: "action" for concrete executable tasks, "planning" for open questions or things to consider
- confidence: 0.0–1.0 — how certain this is a real task vs background context
- triggering_statement: the exact phrase or sentence that produced this task
- triggering_location: location in source if identifiable, e.g. "line 34" or "00:14:22" (omit if unknown)
- due_date: YYYY-MM-DD resolved from context using today's date (omit if none)
- due_time: HH:MM 24h if a time is mentioned (omit if none)
- priority: "low", "normal", or "high" based on urgency cues (omit if unclear)
- description: additional context worth preserving (omit if none)

Rules:
- One entry per distinct action or consideration
- For open-ended requests like "what else do I need?", produce one planning task whose description lists the open questions
- Resolve relative dates ("next Friday", "in 3 weeks") using today's date
- Return an empty array if no tasks are present

Text:
{text}"""


class LLMExtractor:
    def __init__(self, registry: LLMRegistry, today: date | None = None) -> None:
        self._registry = registry
        self._today = today  # injectable for deterministic tests

    def extract(
        self,
        item: RawItem,
        tier: Literal["bulk", "accurate"] = "accurate",
    ) -> list[CandidateTask]:
        if not item.text.strip():
            return []  # vision path (image_bytes) not yet supported

        today = self._today or date.today()
        raw = self._registry.active_provider().complete(
            prompt=_build_prompt(item.text, today),
            output_schema=_OUTPUT_SCHEMA,
            tier=tier,
        )
        return _parse(raw)


# ---------------------------------------------------------------------------
# Response parsing
# ---------------------------------------------------------------------------

def _parse(raw: Any) -> list[CandidateTask]:
    if not isinstance(raw, list):
        return []
    results = []
    for entry in raw:
        candidate = _parse_entry(entry)
        if candidate is not None:
            results.append(candidate)
    return results


def _parse_entry(entry: Any) -> CandidateTask | None:
    if not isinstance(entry, dict):
        return None
    title = (entry.get("title") or "").strip()
    confidence = entry.get("confidence")
    triggering = (entry.get("triggering_statement") or "").strip()
    if not title or confidence is None or not triggering:
        return None

    priority_raw = (entry.get("priority") or "").lower()
    priority = Priority[priority_raw.upper()] if priority_raw in ("low", "normal", "high") else None

    kind_raw = (entry.get("kind") or "action").lower()
    kind = TaskKind.PLANNING if kind_raw == "planning" else TaskKind.ACTION

    return CandidateTask(
        title=title,
        confidence=float(confidence),
        triggering_statement=triggering,
        triggering_location=entry.get("triggering_location") or None,
        due=_parse_due(entry.get("due_date"), entry.get("due_time")),
        priority=priority,
        kind=kind,
        description=entry.get("description") or None,
    )


def _parse_due(due_date: Any, due_time: Any) -> datetime | None:
    if not due_date:
        return None
    try:
        d = date.fromisoformat(str(due_date))
    except ValueError:
        return None
    if due_time:
        try:
            h, m = str(due_time).split(":")
            return datetime(d.year, d.month, d.day, int(h), int(m), tzinfo=timezone.utc)
        except (ValueError, TypeError):
            pass
    return datetime(d.year, d.month, d.day, tzinfo=timezone.utc)
