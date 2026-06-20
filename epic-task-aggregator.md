# Epic — Unified Task Aggregator

> Codename: **Conduit** (provisional — rename freely)

A middleware that turns scattered human input — handwritten notes, meeting
transcripts, and more — into structured tasks, and delivers them into whatever
todo app the user already uses, through standard interchange formats.

This document owns the **why, what, user flows, and phasing**.
It is a companion to:

- `AGENTS.md` — how agents work in this repo (workflow, MVC, stop conditions).
- `architecture.md` — source of truth for file structure, tech stack, naming,
  state management, and dependency direction.

Implementation specifics do **not** live here. If something in this epic implies
a concrete structure, that decision belongs in `architecture.md`.

---

## North Star

**Capture should never be lost to the medium it was captured in.**

A task scribbled in a notebook or said out loud in a meeting is worth nothing if
it dies there. Conduit is the layer that reliably moves an intention from
*wherever a human expressed it* to *the one place that human manages work* — and
keeps doing it across every new input source and every new target app, without a
rewrite each time.

Success looks like: the user stops manually re-typing action items, and trusts
that anything they wrote or said shows up as a clean task in their own app.

---

## Overall Goal

Build a source-agnostic, sink-agnostic task pipeline:

1. **Aggregate** task-bearing content from many input sources.
2. **Extract** structured tasks from that content.
3. **Normalize and de-duplicate** into one canonical model.
4. **Deliver** into any target app via a common, standards-based format.

The same core must serve a single hobby user on day one and a multi-tenant
product later, by *scaling* the same architecture rather than replacing it.

---

## Foundation (load-bearing principles)

These are the commitments the whole design rests on. Treat them like
`architecture.md`: do not violate them to satisfy a narrow request.

| Principle | What it means |
| --- | --- |
| Canonical model in the middle | Every source maps *into* one task schema; every sink maps *out of* it. Nothing speaks source-to-sink directly. |
| Symmetric pluggable connectors | Sources and sinks are interchangeable adapters behind a stable contract. Adding one never touches the core. |
| Stateless + externalized state | Compute holds no local state. Dedup store, tasks, and tokens live in managed storage. This is what makes hobby→business a config change, not a rewrite. |
| Standards over bespoke | The interchange backbone is iCalendar `VTODO` over CalDAV — the de facto task-interop standard — not a private format. |
| LLM only for interpretation | The model is the semantic extraction layer, nothing else. Plumbing and formatting stay deterministic. |
| Deterministic fast-path | Explicitly-marked tasks bypass the LLM entirely (cheaper, instant, reliable). |
| Provenance is mandatory | Every task carries where it came from. Required for trust, dedup, and per-source rules. |
| Confidence gating | Extracted tasks carry a confidence score; low-confidence items wait for review instead of auto-flooding the target app. |

---

## The Middleware

Conceptual pipeline. Stage boundaries are firm; the tech behind each stage is an
`architecture.md` concern.

```
Sources  ──▶  Extraction  ──▶  Canonical Core  ──▶  Sinks
(adapters)    (LLM / rules)    (normalize+dedupe)    (adapters)
```

### Source connectors
Each connector knows only how to *get content out of its platform*. It does not
know about tasks.

- reMarkable — notes, using the device's **built-in OCR** for handwriting→text.
- Meeting transcripts — Teams, Zoom, Meet, etc. (each is just "fetch a transcript").
- Future — email, Slack, and anything else that emits text.

Sources are of two kinds:

- **Unstructured** (notes, transcripts) → must pass through Extraction.
- **Structured** (an API that already has discrete items) → map straight to the core.

### Extraction layer
Turns freeform text into structured candidate tasks. This is the only place the
LLM is load-bearing. It must:

- **Classify actionability** — separate tasks from context/journaling.
- **Segment** — split one run-on note into discrete tasks.
- **Resolve relative dates** — "before Fri" → an ISO datetime given today.
- **Infer priority** — from tone and phrasing.
- **Score confidence** — feeding the review gate.

Driven via the model's **structured-output / JSON-schema mode** so it returns
typed objects, not free text to re-parse. Explicitly-marked tasks
(e.g. `TODO: x @friday !high`) take the deterministic fast-path and skip the model.

> OCR is **parked**: reMarkable handles handwriting→text. With OCR gone, the LLM's
> role narrows to interpretation — and becomes *more* central, because it is the
> shared step every text source (notes and transcripts alike) depends on.

### Canonical core
Holds the canonical task model, the dedup logic, and provenance.

- **Exact dedup** first: a stable `id` derived from a hash of source + task text
  makes re-runs idempotent (a cron job re-scanning the same notebook won't
  duplicate).
- **Semantic dedup** later: embeddings to catch the same item phrased differently
  across two sources (note vs. transcript). Deferred — see Out of Scope.

### Sink connectors
Translate the canonical model into a target format. Pure deterministic templating.

- **VTODO / CalDAV** — the primary, standards-based backbone. Self-hosted CalDAV
  server (e.g. Radicale) lets any compatible app subscribe with zero bespoke work.
- **todo.txt** — lightweight plain-text option.
- **Your todo app** — via webhook (or `.ics`/JSON file drop until it has an API).
- **Obsidian / Markdown** — checkbox task lists.

---

## Canonical Task Model

The contract every connector translates to or from. Field names and types are
indicative; the authoritative definition lives in `architecture.md`.

```
Task {
  id           // stable hash of (source_ref + normalized title) — dedup key
  title        // imperative, single action
  due          // ISO datetime or null
  priority     // low | normal | high
  status       // open | done | dismissed
  description  // optional context
  source_ref   // provenance: which source, which item, timestamp
  confidence   // 0.0–1.0 from extraction; gates auto-push vs review
  created      // ingest timestamp
}
```

Adding an output format never touches ingest; adding an input source never
touches sinks. The model is the only thing both sides share.

---

## User Flows

### Flow A — Note to task (MVP happy path)
1. User writes a note on reMarkable and uses its OCR to convert to text.
2. Scheduled job fetches new text content via the reMarkable connector.
3. Extraction emits structured tasks with confidence scores.
4. Core assigns stable ids and drops exact duplicates.
5. High-confidence tasks are pushed to the target app.
6. User sees the tasks appear in the app they already use.

### Flow B — Meeting transcript to reviewed tasks
1. A meeting connector (e.g. Teams) fetches the transcript.
2. Same Extraction layer pulls candidate action items.
3. Speculative items ("we should maybe look into…") score low confidence.
4. Low-confidence items land in a **review queue**, not the app.
5. User approves/dismisses; approved items flow to the sink.

### Flow C — Same task from two sources (dedup)
1. "Send Sarah the deck" appears in both a note and the meeting transcript.
2. Exact dedup misses it (different wording); semantic dedup (later phase)
   merges them by similarity.
3. The user gets one task, with provenance from both sources.

### Flow D — Explicit task (deterministic fast-path)
1. User writes `TODO: pay invoice @friday !high`.
2. A rule parses it directly — no LLM call.
3. Task is created instantly with full confidence.

---

## MVP Slice (first iteration)

Thinnest end-to-end vertical slice that proves the loop. One source, one sink,
no speculative extensibility.

```
[ ] reMarkable source connector (uses device OCR → raw text)
[ ] Extraction layer → canonical tasks via JSON-schema output
[ ] Canonical model + exact (hash) dedup
[ ] One sink: target app via webhook OR .ics/JSON file drop
[ ] Scheduled run that ties the four together end-to-end
```

Deliberately **excluded from the MVP** (added later, not now):

- Meeting / transcript connectors
- CalDAV server (use file-based sink first)
- Semantic dedup
- Confidence review queue (auto-push everything in MVP, gate later)
- Multi-tenant anything
- Enrichment (auto-tagging, project routing, context summaries)

---

## Infrastructure (phased)

The workload is **not** an always-on busy server. It is a periodic batch job, an
occasional webhook receiver, and one genuinely always-on light piece (the CalDAV
endpoint, deferred). Hosting follows that shape. Free-tier specifics shift fast —
re-verify before committing; this captures the *shape*, not fixed quotas.

### Phase 0 — Dev / free
- **Orchestrator:** scheduled job (GitHub Actions cron is the clean hobby answer —
  free compute, built-in secrets, no server).
- **State:** free managed Postgres (Supabase / Neon), or a committed state file
  while tiny.
- **Sink:** file-based (`.ics`/JSON) to dodge running a CalDAV server.
- **Note:** Fly.io and Railway no longer offer a real free tier; Render's free
  tier spins down (~30–50s cold start) — fine for a background job.

### Phase 1 — Beta / small real usage
- Scale-to-zero container (e.g. Cloud Run) on a scheduler.
- Managed Postgres (paid small tier).
- A queue between extraction and sinks so a slow sink can't stall ingestion.
- Stand up the CalDAV server (small always-on host) when live sync is needed.

### Phase 2 — Business / multi-tenant
- **OAuth broker** for every connector (Teams, Google, Zoom…).
- Per-tenant data isolation and real secrets management.
- Queue + horizontal workers (each source connector becomes a worker).
- Container orchestration, managed queue, object storage.
- **EU data residency / GDPR** once storing other users' content and tokens.

> **Cost reality:** infra is near-free for a long time. The real cost driver is
> **LLM extraction calls**, which scale per task with usage. That — not hosting —
> is what future pricing must cover, which is healthy: cost tracks value delivered.

---

## Out of Scope (non-goals, for now)

To keep iterations honest and avoid rabbit holes:

- OCR — delegated to reMarkable; not built here.
- Source-to-sink shortcuts that bypass the canonical model.
- Multi-tenant infrastructure before the single-user loop works.
- Semantic dedup before exact dedup is in place.
- Any enrichment before extraction is reliable.

---

## Open Questions / Assumptions

Resolve before the slices that depend on them (per Assumption Policy — ask, don't guess):

- Does the target todo app accept **webhooks**, or only file import, for the MVP sink?
- reMarkable access method for v1: cloud API (maintained `ddvk/rmapi` fork) or
  local USB web interface?
- v1 trigger: **poll on a schedule** vs. webhook-driven? (Polling is simpler for MVP.)
- Which extraction model/provider, and where its key is stored? (An `architecture.md`
  + secrets decision.)

---

## Glossary

- **Source connector** — adapter that pulls content out of one platform.
- **Sink connector** — adapter that writes the canonical model into one target format.
- **Canonical model** — the single shared task schema in the middle.
- **VTODO / CalDAV** — the iCalendar task component and its sync protocol; the
  interop backbone.
- **Provenance (`source_ref`)** — where a task originated.
- **Confidence gate** — threshold routing low-confidence tasks to review.
- **Deterministic fast-path** — rule-based parse for explicitly-marked tasks.
