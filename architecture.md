# Architecture — Unified Task Aggregator

> Codename: **Conduit** · Companion to `epic-task-aggregator.md` (why/what/flows)
> and `AGENTS.md` (working rules).

**Status: starter.** This is the source of truth for structure, stack, naming,
state, and dependency direction. Sections that should not be locked in yet are
marked **`Decision: open`** — fill them as slices demand, not before.

What is **firm** here (do not invent around it): the architectural style, the
dependency direction, the connector contracts, and the rule that the core stays
pure. Everything else is negotiable until a slice forces the choice.

---

## 1. Architectural Style — Ports & Adapters (Hexagonal)

This is a headless pipeline, not a screen-based app, so classic screen-MVC does
not map cleanly. The natural fit for "pluggable source/sink connectors behind a
stable contract" is **ports and adapters**:

- The **domain core** (canonical model + dedup + the port interfaces) is pure and
  knows nothing about reMarkable, Teams, CalDAV, HTTP, or any database.
- Everything external is an **adapter** implementing a **port** the core defines.

`AGENTS.md` is written in MVC vocabulary. That still applies — see the mapping in
§9 so "one file / one layer at a time" continues to work. A review UI, when it
arrives, is a separate bounded module that *follows* the MVC conventions in
`AGENTS.md` and consumes the core; it does not live inside it.

---

## 2. Layers & Dependency Direction

**The one firm rule: dependencies point inward. The core depends on nothing.**

```
        ┌─────────────────────────────────────────────┐
        │            Orchestration / wiring            │  ← composition root, scheduler
        │   ┌─────────────────────────────────────┐    │
        │   │   Adapters (source / sink / store)   │    │  ← I/O lives only here
        │   │   ┌─────────────────────────────┐    │    │
        │   │   │        Domain core          │    │    │  ← pure: model, dedup, ports
        │   │   │   (no I/O, no frameworks)   │    │    │
        │   │   └─────────────────────────────┘    │    │
        │   └─────────────────────────────────────┘    │
        └─────────────────────────────────────────────┘
```

| Layer | Responsibility | May depend on |
| --- | --- | --- |
| Domain core | Canonical `Task`, invariants, dedup logic, **port interfaces** | nothing |
| Extraction | Text → candidate tasks (behind a port) | core |
| Adapters | Source/sink/store/extractor implementations | core |
| Orchestration | Wires adapters to ports, owns the run + schedule | all |
| Review UI (later) | Approve/dismiss low-confidence tasks | core (read), orchestration |

If a change makes the core import an adapter, it is wrong — stop (rabbit hole).

---

## 3. The Contracts (Ports)

These interfaces are the load-bearing part of the whole system. Method *shapes*
are firm; concrete types are indicative until the language is chosen.

```
// A source knows only how to pull content out of its platform.
port Source {
  id: string                       // "remarkable", "teams"
  fetch(since: Cursor): RawItem[]  // RawItem = { text, source_ref, kind }
}

// Extraction turns unstructured text into candidate tasks.
port Extractor {
  extract(item: RawItem): CandidateTask[]   // each carries a confidence score
}

// A sink knows only how to write the canonical model into one target.
port Sink {
  id: string
  push(tasks: Task[]): PushResult
}

// Persistence is hidden behind the core, never used directly by adapters.
port TaskStore {
  upsert(tasks: Task[]): void      // idempotent on Task.id
  seen(id: string): boolean        // exact-dedup check
  cursor(sourceId): Cursor         // watermark per source
}

// LLM provider — abstraction over any model backend.
// Orchestration passes a tier hint; if the provider has only one model
// configured, it is used for both tiers — never fail on a missing tier.
port LLMProvider {
  id: string                              // "anthropic", "openai", …
  complete(
    prompt: string,
    output_schema: JSONSchema,
    tier: "bulk" | "accurate"            // bulk = fast/cheap; accurate = quality
  ): structured_output                    // validated against output_schema
}

// Registry holds one or more LLMProvider implementations.
// active_provider() returns the configured default.
// Switching providers = change config, not code.
port LLMRegistry {
  register(provider: LLMProvider): void
  active_provider(): LLMProvider
}
```

Adding "whatever meeting platform" = implement `Source`. Adding a target = implement
`Sink`. Adding a model backend = implement `LLMProvider` and register it.
The core and orchestration never change for any of these.

**`Decision: open`** — whether the deterministic fast-path (explicit `TODO:` syntax)
is a second `Extractor` implementation or a pre-filter in orchestration. Lean:
pre-filter, so the LLM extractor stays single-purpose.

---

## 4. Module / File Structure

A *shape*, not a mandate — the exact tree follows the chosen language's idioms.
Group by layer, not by feature, so the dependency direction is visible on disk.

```
src/
  core/            // pure domain — Task model, dedup, ports. No I/O.
  extraction/      // Extractor implementations (LLM + rules)
  adapters/
    sources/       // remarkable/, teams/, ... one folder per platform
    sinks/         // caldav/, todotxt/, webhook/, markdown/
    store/         // TaskStore implementation(s)
  orchestration/   // composition root, the pipeline run, scheduling
  config/          // env loading, per-connector credentials
```

**`Decision: open`** — language-specific layout (package vs. module vs. folder
conventions) is set once §6 lands.

---

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

## 6. State & Persistence

All state is **externalized** — the core and adapters hold none locally. There are
four kinds, all reached through the `TaskStore` (or a sibling) port:

- **Canonical tasks** — the output of record.
- **Dedup index** — `Task.id` hashes for exact-dedup / idempotency.
- **Source cursors** — per-source watermark so runs are incremental.
- **Connector credentials / tokens** — secrets, never in code or the task store.

**`Decision: open`** — whether cursors and credentials share the store or use a
dedicated secret manager. They diverge the moment multi-tenant arrives (epic Phase 2).

---

## 7. Naming Conventions

Light and firm where it aids navigation; open elsewhere.

- Source adapters: named by platform (`remarkable`, `teams`).
- Sink adapters: named by output format (`caldav`, `todotxt`, `webhook`).
- Ports: nouns describing capability (`Source`, `Sink`, `TaskStore`).
- `source_ref` is the canonical provenance field everywhere — never reinvented per adapter.

**`Decision: open`** — casing/file-naming conventions inherit from §6's language.

---

## 8. Testing Strategy

Aligns with the `AGENTS.md` test rule (suggest tests only once a suite exists).

- **Core** is pure → fast unit tests for dedup and model invariants.
- **Adapters** → contract tests against the port with the platform mocked; a real
  call is an integration test, kept separate.
- **Extraction** → fixture/"golden set" tests: known input text → expected task
  JSON, so prompt changes are caught as regressions.

**`Decision: open`** — test framework follows §6.

---

## 9. MVC ↔ Pipeline Layer Mapping

So `AGENTS.md`'s "one MVC layer at a time" keeps working on a headless pipeline:

| `AGENTS.md` layer | Here it means | Touch when the task is… |
| --- | --- | --- |
| Model | Domain core: `Task`, invariants, dedup | core domain logic |
| Service / Infrastructure | Adapters + extraction + store | a connector or I/O concern |
| Controller | Orchestration use-case (the pipeline run) | wiring the run flow |
| View | (none in core) Review UI later | UI work only |
| Navigation / Composition | Composition root + scheduler | startup/wiring |
| Tests | Per-layer tests above | testing |

"Work on the reMarkable sink/source" → Service/Infrastructure layer only; do not
touch the domain core or orchestration.

---

## 10. Open Decisions Log

Resolve as the dependent slice arrives — not earlier (per Assumption Policy).

```
[x] Language + project layout  → Python; src/ layout per §4
[x] LLM provider abstraction  → LLMProvider + LLMRegistry ports (§3); Anthropic default
[x] Extraction model tiers    → bulk: claude-haiku-4-5 / accurate: claude-sonnet-4-6; single-model providers use one for both
[x] Fast-path                 → pre-filter in orchestration (not a second Extractor)
[x] MVP sink                  → Jot via HTTP (Supabase Edge Function + scoped bearer token); direct DB insert for local dev only
[ ] Bulk / accurate model IDs → confirm claude-haiku-4-5 and claude-sonnet-4-6 are the right model IDs
[ ] Persistence engine        → dev free-tier choice (§5)
[ ] reMarkable access method  → cloud fork vs USB (§5)
[ ] Trigger                   → scheduled poll vs webhook for v1
[ ] Confidence defaults       → threshold value + fallback action shipped in default config
```
