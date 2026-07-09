from __future__ import annotations

import json
from typing import Any, Literal

import google.genai as genai
from google.genai import types


class GeminiProvider:
    """LLMProvider backed by Google Gemini.

    Uses Gemini's native JSON mode (response_mime_type + response_schema) for
    structured output — no schema wrapping needed unlike Anthropic tool-use.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.5-flash",
    ) -> None:
        self.id = "gemini"
        self._client = genai.Client(api_key=api_key)
        self._model = model

    def complete(
        self,
        prompt: str,
        output_schema: dict[str, Any],
        tier: Literal["bulk", "accurate"],
    ) -> Any:
        response = self._client.models.generate_content(
            model=self._model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=output_schema,
            ),
        )
        try:
            return json.loads(response.text)
        except (json.JSONDecodeError, TypeError):
            return []
