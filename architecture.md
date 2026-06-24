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

### Engine vs. Chassis

**Conduit is the engine** — the steering wheel, gearbox, and drivetrain. It
provides the pipeline logic, the canonical model, the port contracts, and the
adapter implementations. It is a standalone Python package with no dependency
on any hosting platform.

**Integrations are the chassis** — the fuel, the body, the ignition. An
integration wires Conduit's engine into a specific hosting environment
(Home Assistant, a cron container, a serverless function) by implementing the
composition root. It calls `conduit.orchestration.run_pipeline()` with whatever
implementations it chooses to supply.

This means anyone can build their own car with Conduit. The HA integration is
the reference chassis — it is what *we* build against, but the engine runs
equally well in any other chassis. An advanced integration may also substitute
individual pipeline links (e.g. replace the LLM extractor with its own parser)
while keeping the rest of the chain intact — see §11.

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

## 12. North Star: Multi-Output Extraction & Task Kinds

The target use case that shapes the extractor's output contract:

> *"I will have my 40th birthday Friday in 3 weeks — plan for shopping and sending
> out invitations. What else do I need to do?"*

Expected pipeline output — **three tasks from one voice input:**

1. `kind: action` — "Buy birthday party supplies" · due: 3 weeks · priority: normal
2. `kind: action` — "Send out birthday invitations" · due: 3 weeks · priority: high
3. `kind: planning` — "Birthday party open questions" · body: LLM-generated list of
   things the user hasn't thought of (guest count, venue, theme, catering, cake, etc.)

**Implications for the canonical model:**

`Task` carries a `kind` field:

```
kind: "action" | "planning"
```

- `action` — a concrete, executable item. Always pushed to the sink.
- `planning` — a scaffold of considerations or open questions. Pushed as a
  single task whose `description` contains the generated list. The sink may
  route it differently (different area, different icon).

`kind` defaults to `"action"`. The extractor sets it explicitly when the LLM
determines the output is advisory rather than executable.

**Implication for the extractor output schema:**

The LLM is asked to return a list of candidate tasks, each with a `kind` field.
A single source item may produce any number of candidates of mixed kinds.
Confidence gating applies to all kinds equally.

> **Side note:** `Task.kind` needs to be added to `conduit/core/task.py`.
> Tracked in §10.

---

## 10. Open Decisions Log

Resolve as the dependent slice arrives — not earlier (per Assumption Policy).

```
[x] Language                  → Python
[x] LLM provider abstraction  → LLMProvider + LLMRegistry ports (§3); Anthropic default
[x] Extraction model tiers    → bulk: claude-haiku-4-5 / accurate: claude-sonnet-4-6; single-model providers use one for both
[x] Fast-path                 → pre-filter in orchestration (not a second Extractor)
[x] MVP sink                  → Jot via HTTP (Supabase Edge Function + scoped bearer token)
[x] Phase 0 hosting           → Home Assistant (BYO); integrations/home_assistant/ is reference chassis
[x] Pipeline composability    → swappable chain via Protocol interfaces (§11)
[x] Multi-output extraction   → extractor returns list of mixed-kind candidates (§12)
[ ] Package layout            → rename src/ → conduit/ for installable package
[ ] Task.kind field           → add "action" | "planning" to core/task.py
[ ] Bulk / accurate model IDs → confirm claude-haiku-4-5 and claude-sonnet-4-6 are correct
[ ] Persistence engine        → SQLite for Phase 0 (confirmed); Postgres for Phase 1
[ ] reMarkable access method  → cloud fork vs USB
[ ] Trigger                   → HA automation (time-based) for poll; HA webhook for push
[ ] Confidence defaults       → threshold value + fallback action in default config
```
