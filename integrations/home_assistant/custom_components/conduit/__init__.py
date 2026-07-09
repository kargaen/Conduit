"""Conduit Task Extraction — Home Assistant integration.

Setup
-----
1. Copy this folder to <config>/custom_components/conduit/
2. Create <config>/conduit/config.json:
   {
     "llm_provider": "gemini",
     "llm_api_key":  "AIza...",
     "llm_model":    "gemini-2.5-flash",
     "inbox_dir":    "/config/conduit/inbox",
     "output_dir":   "/config/conduit/output",
     "db_path":      "/config/conduit/conduit.db",
     "confidence_threshold": 0.5
   }

   To switch providers, change values only — keys stay the same:
   {
     "llm_provider": "anthropic",
     "llm_api_key":  "sk-ant-...",
     "llm_model":    "claude-haiku-4-5-20251001",
     ...
   }
3. Restart Home Assistant.
4. Drop .txt files into the inbox_dir.
5. Call the service:  conduit.run  (no parameters needed).
6. Check output_dir for tasks_YYYYMMDD_HHMMSS.json.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from homeassistant.core import HomeAssistant, ServiceCall

from conduit.adapters.sinks.file import FileSink
from conduit.adapters.sources.file import FileSource
from conduit.adapters.store.sqlite import SQLiteTaskStore
from conduit.extraction.llm import LLMExtractor
from conduit.orchestration.pipeline import PipelineConfig, run_pipeline

_LOGGER = logging.getLogger(__name__)

DOMAIN = "conduit"
_CONFIG_PATH = Path("/config/conduit/config.json")


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    cfg = _load_config()
    if cfg is None:
        _LOGGER.error(
            "Conduit: missing config at %s — integration disabled", _CONFIG_PATH
        )
        return False

    hass.data[DOMAIN] = cfg

    async def handle_run(call: ServiceCall) -> None:
        await hass.async_add_executor_job(_run_pipeline, cfg)

    hass.services.async_register(DOMAIN, "run", handle_run)
    _LOGGER.info("Conduit: registered service conduit.run")
    return True


def _load_config() -> dict | None:
    if not _CONFIG_PATH.exists():
        return None
    try:
        return json.loads(_CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception as exc:
        _LOGGER.error("Conduit: failed to parse config.json: %s", exc)
        return None


def _build_provider(cfg: dict) -> Any:
    api_key = cfg["llm_api_key"]
    model   = cfg.get("llm_model")
    name    = cfg.get("llm_provider", "gemini").lower()
    if name == "anthropic":
        from conduit.adapters.llm.anthropic import AnthropicProvider
        kwargs = {"api_key": api_key}
        if model:
            kwargs["model"] = model
        return AnthropicProvider(**kwargs)
    # default: gemini
    from conduit.adapters.llm.gemini import GeminiProvider
    kwargs = {"api_key": api_key}
    if model:
        kwargs["model"] = model
    return GeminiProvider(**kwargs)


def _run_pipeline(cfg: dict) -> None:
    inbox_dir  = Path(cfg.get("inbox_dir",  "/config/conduit/inbox"))
    output_dir = Path(cfg.get("output_dir", "/config/conduit/output"))
    db_path    = Path(cfg.get("db_path",    "/config/conduit/conduit.db"))
    threshold  = float(cfg.get("confidence_threshold", 0.5))

    provider = _build_provider(cfg)

    # Minimal LLMRegistry inline — no extra classes needed.
    class _Registry:
        def register(self, p: Any) -> None: ...
        def active_provider(self) -> Any:
            return provider

    source  = FileSource(inbox_dir)
    sink    = FileSink(output_dir)
    extractor = LLMExtractor(registry=_Registry())
    pipeline_cfg = PipelineConfig(confidence_threshold=threshold)

    with SQLiteTaskStore(db_path) as store:
        result = run_pipeline(
            sources=[source],
            extractor=extractor,
            sink=sink,
            store=store,
            config=pipeline_cfg,
        )

    _LOGGER.info(
        "Conduit: pushed=%d  dedup=%d  below_threshold=%d  sources=%d  errors=%s",
        result.tasks_pushed,
        result.tasks_skipped_dedup,
        result.tasks_below_threshold,
        result.sources_processed,
        result.errors or "none",
    )
