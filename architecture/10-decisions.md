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
