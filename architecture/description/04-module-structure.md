## 4. Module / File Structure

Grouped by layer, not by feature — the dependency direction is visible on disk.
The project has three top-level concerns: the engine package, the integrations,
and tests.

```
conduit/                    # pip-installable package — the engine
  __init__.py
  core/                     # pure domain: Task, SourceRef, ports, dedup. No I/O.
  extraction/               # Extractor implementations
    llm.py                  # LLM-backed extractor (uses LLMProvider port)
    rules.py                # deterministic fast-path (TODO: syntax)
  adapters/
    sources/                # one folder per platform
      home_assistant/       # receives pushes from HA webhook
      remarkable/           # polls reMarkable cloud or USB
      transcript/           # generic transcript file adapter
    sinks/
      jot/                  # Jot via Supabase Edge Function
      todotxt/              # plain-text todo.txt
      markdown/             # Obsidian-style checkbox lists
    store/                  # TaskStore implementations
      sqlite.py             # Phase 0: local SQLite file
      postgres.py           # Phase 1+: managed Postgres
    llm/                    # LLMProvider implementations
      anthropic.py          # Claude (bulk + accurate tiers)
      ollama.py             # local Ollama (fully offline option)
  orchestration/            # pipeline runner — accepts Protocol implementations
    pipeline.py             # run_pipeline(sources, extractor, sink, store, config)
  config/                   # settings dataclasses, env + HA secrets loading

integrations/               # hosting wrappers — the chassis, framework-specific only
  home_assistant/           # reference integration
    custom_components/
      conduit/
        __init__.py         # HA entry point: calls conduit.orchestration.run_pipeline()
        manifest.json       # HACS / HA manifest
        services.yaml       # exposes run_pipeline as an HA service call
        config_flow.py      # HA UI for credentials + confidence settings

tests/                      # mirrors conduit/ layer structure
  core/
  extraction/
  adapters/
  orchestration/
```

**Code pattern:** every inter-layer dependency is via a `Protocol` defined in
`conduit/core/ports.py`. No concrete class is imported across layer boundaries —
only the Protocol type. `isinstance` checks against Protocols are forbidden;
duck typing is the contract. The pipeline runner is a plain function that accepts
Protocol-typed arguments; the integration's composition root is the only place
that instantiates concrete adapters and passes them in.

> **Side note:** current code lives at `src/core/task.py`. This needs to move to
> `conduit/core/task.py` before the package is installable. Tracked in §10.

---
