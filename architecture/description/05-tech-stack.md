## 5. Tech Stack

Held open on purpose. Each row states the *constraint* the choice must satisfy so
the decision is principled when made.

| Concern | Leaning | Must satisfy | Status |
| --- | --- | --- | --- |
| Language | Python | First-class LLM SDK, embedding libs, reMarkable tooling | **Python** |
| LLM provider | Anthropic (Claude) | Interchangeable via `LLMProvider` port; bulk + accurate tiers | **Anthropic default** |
| Extraction model — bulk | claude-haiku-4-5 | Fast, cheap, high-volume runs | `Decision: open` |
| Extraction model — accurate | claude-sonnet-4-6 | Quality, ambiguous intent, date resolution | `Decision: open` |
| Persistence | Postgres | Managed free tier in dev, idempotent upsert by `id` | `Decision: open` |
| reMarkable access | `ddvk/rmapi` fork or USB web UI | Non-interactive, scriptable | `Decision: open` |
| Embeddings (later) | — | Similarity search for semantic dedup | deferred |
| Queue (later) | — | Decouple extraction from sinks | deferred |
| CalDAV server (later) | Radicale | Lightweight, self-hostable | deferred |
| Hosting | per epic phases | Scheduler + (later) public webhook URL | see epic |

Per `AGENTS.md`: no install commands here — link the official docs when a choice
is made, and do not add dependencies as a side effect of a code task.

---
