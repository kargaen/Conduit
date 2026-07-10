## 7. Naming Conventions

Light and firm where it aids navigation; open elsewhere.

- Source adapters: named by platform (`remarkable`, `teams`).
- Sink adapters: named by output format (`caldav`, `todotxt`, `webhook`).
- Ports: nouns describing capability (`Source`, `Sink`, `TaskStore`).
- `source_ref` is the canonical provenance field everywhere — never reinvented per adapter.

**`Decision: open`** — casing/file-naming conventions inherit from §6's language.

---
