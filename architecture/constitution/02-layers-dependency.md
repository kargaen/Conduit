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
