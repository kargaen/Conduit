# Architecture — Unified Task Aggregator

> Codename: **Conduit** · Companion to `epic-task-aggregator.md` (why/what/flows)
> and `CLAUDE.md` (working rules).

**Status: starter.** This is the source of truth for structure, stack, naming,
state, and dependency direction. Sections that should not be locked in yet are
marked **`Decision: open`** — fill them as slices demand, not before.

What is **firm** here (do not invent around it): the architectural style, the
dependency direction, the connector contracts, and the rule that the core stays
pure. Everything else is negotiable until a slice forces the choice.

---

## Write Policy

| Class | Location | Written by | Agent may |
|---|---|---|---|
| **Constitution** | `architecture/constitution/` | Humans, by review | **Cite. Never edit.** |
| **Description** | `architecture/description/` | `epic-closeout`, after a slice ships | Amend, reactively |
| **Decisions** | `architecture/10-decisions.md` | Any, append-only | Tick `[x]` when resolved |
| **Change History** | `architecture/25-change-history.md` | `epic-closeout` | Append one row per amendment |

The three-class rule: if a sentence would survive unchanged after the code was
rewritten to do something else, it is Constitution. If it describes what exists
right now, it is Description. If it describes what will exist, it is Deferred and
belongs in an epic, not here.

---

## Index

| § | File | Class | Contains |
|---|---|---|---|
| 1 | `architecture/constitution/01-architectural-style.md` | Constitution | Ports & Adapters style; Engine vs. Chassis split |
| 2 | `architecture/constitution/02-layers-dependency.md` | Constitution | Layer boundaries; dependency direction rule |
| 3 | `architecture/constitution/03-contracts-ports.md` | Constitution | Port interfaces: Source, Extractor, Sink, TaskStore, LLMProvider, LLMRegistry |
| 4 | `architecture/description/04-module-structure.md` | Description | Module/file layout; current folder tree |
| 5 | `architecture/description/05-tech-stack.md` | Description | Language, LLM provider, persistence choices |
| 6 | `architecture/description/06-state-persistence.md` | Description | State kinds and externalization contract |
| 7 | `architecture/constitution/07-naming-conventions.md` | Constitution | Adapter, port, and field naming rules |
| 8 | `architecture/constitution/08-testing-strategy.md` | Constitution | Test approach per layer |
| 9 | `architecture/constitution/09-layer-mapping.md` | Constitution | MVC ↔ pipeline layer mapping for agent working rules |
| 10 | `architecture/10-decisions.md` | Decisions | Open and resolved decisions log |
| 11 | `architecture/description/11-pipeline-composability.md` | Description | Swappable chain; minimum viable integration |
| 12 | `architecture/constitution/12-north-star.md` | Constitution | Target use case; multi-output extraction model |
| 25 | `architecture/25-change-history.md` | History | Append-only; one row per Description amendment |
| 26 | `architecture/constitution/26-branch-model.md` | Constitution | Branch naming, integration/release flow, human gate |
