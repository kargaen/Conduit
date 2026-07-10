## 8. Testing Strategy

Aligns with the `AGENTS.md` test rule (suggest tests only once a suite exists).

- **Core** is pure → fast unit tests for dedup and model invariants.
- **Adapters** → contract tests against the port with the platform mocked; a real
  call is an integration test, kept separate.
- **Extraction** → fixture/"golden set" tests: known input text → expected task
  JSON, so prompt changes are caught as regressions.

**`Decision: open`** — test framework follows §6.

---
