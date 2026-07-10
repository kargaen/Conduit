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
