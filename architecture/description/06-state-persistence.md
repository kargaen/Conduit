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
