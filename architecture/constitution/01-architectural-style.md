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
