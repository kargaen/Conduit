from __future__ import annotations

import json
from typing import Any, Literal

import anthropic as _anthropic


# Anthropic tool-use requires the top-level schema to be an object.
# We wrap the array output schema in an object and unwrap the response.
_TOOL_NAME = "extract_tasks"


class AnthropicProvider:
    """LLMProvider backed by Anthropic Claude.

    Both tiers map to a single model unless two distinct model IDs are given.
    If only `bulk_model` is provided, `accurate` calls fall back to it too —
    per the LLMRegistry design: never fail just because a second tier is absent.
    """

    def __init__(
        self,
        api_key: str,
        bulk_model: str = "claude-haiku-4-5-20251001",
        accurate_model: str | None = None,
    ) -> None:
        self.id = "anthropic"
        self._client = _anthropic.Anthropic(api_key=api_key)
        self._bulk_model = bulk_model
        self._accurate_model = accurate_model or bulk_model

    def complete(
        self,
        prompt: str,
        output_schema: dict[str, Any],
        tier: Literal["bulk", "accurate"],
    ) -> Any:
        model = self._accurate_model if tier == "accurate" else self._bulk_model

        # Wrap array schema in object — Anthropic requires object at root.
        tool_schema: dict[str, Any] = {
            "type": "object",
            "required": ["tasks"],
            "properties": {"tasks": output_schema},
        }

        response = self._client.messages.create(
            model=model,
            max_tokens=4096,
            tools=[
                {
                    "name": _TOOL_NAME,
                    "description": "Return structured task extraction results.",
                    "input_schema": tool_schema,
                }
            ],
            tool_choice={"type": "tool", "name": _TOOL_NAME},
            messages=[{"role": "user", "content": prompt}],
        )

        for block in response.content:
            if block.type == "tool_use" and block.name == _TOOL_NAME:
                return block.input.get("tasks", [])

        return []
