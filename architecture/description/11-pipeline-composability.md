## 11. Pipeline Composability — Swappable Chain

The pipeline is a chain of independently swappable links. Conduit ships default
implementations for every link; an integration may replace any single link while
keeping the rest unchanged.

```
Source ──▶ Extractor ──▶ Core (dedup + model) ──▶ Sink
             ▲                                      ▲
         swap for                               swap for
         own parser                             own target
```

| Link | Default | Swap condition |
| --- | --- | --- |
| `Source` | HA webhook / reMarkable | New platform to ingest from |
| `Extractor` | LLM via `LLMProvider` | Integration has its own NLP parser |
| `LLMProvider` | Anthropic Claude | Cost preference, local/offline (Ollama), other vendor |
| `TaskStore` | SQLite | Scale (Postgres), cloud (Supabase) |
| `Sink` | Jot/Supabase | Different todo app, CalDAV, file export |

**Minimum viable integration** needs only: one `Source`, one `Extractor` (or the
rules fast-path only), one `Sink`, and a call to `run_pipeline()`. Everything
else is optional enrichment.

**What does not change between integrations:** the canonical `Task` model and the
`dedup_id` function. These are the only things both sides of the pipeline share.
An integration that bypasses extraction still produces `Task` objects in the
canonical shape before handing them to a sink.

---
