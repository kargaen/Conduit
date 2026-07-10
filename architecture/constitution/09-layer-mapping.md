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
