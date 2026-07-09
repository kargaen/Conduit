from __future__ import annotations

from typing import Any, Literal

import anthropic as _anthropic


# Anthropic tool-use requires the top-level schema to be an object.
# We wrap the array output schema in an object and unwrap the response.
_TOOL_NAME = "extract_tasks"


class AnthropicProvider:
    """LLMProvider backed by Anthropic Claude.

    tier is ignored at the model level — both tiers use the same model.
    Route to different models by instantiating separate providers if needed.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "claude-haiku-4-5-20251001",
    ) -> None:
        self.id = "anthropic"
        self._client = _anthropic.Anthropic(api_key=api_key)
        self._model = model

    def complete(
        self,
        prompt: str,
        output_schema: dict[str, Any],
        tier: Literal["bulk", "accurate"],
    ) -> Any:
        tool_schema: dict[str, Any] = {
            "type": "object",
            "required": ["tasks"],
            "properties": {"tasks": output_schema},
        }

        response = self._client.messages.create(
            model=self._model,
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
