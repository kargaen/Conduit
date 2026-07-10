---
name: change-triage
description: Use this skill whenever a change is requested without naming an epic — "fix this", "this is broken", "add a button that does X", "quick change", "why is this returning null". Also use when a request looks small enough to skip planning. Decides whether the work is a direct slice (correct behaviour is already decided somewhere) or must escalate to an epic (correct behaviour is still being decided). Runs five mechanical escalation triggers and refuses to authorise anything it cannot ground in an existing architecture section, epic flow, or test authority. Do not use when the user already named an epic — that is epic-implementation.
---

# Triaging a Change

Decide the route. Do not edit anything.

## Input

$ARGUMENTS

Arguments describe the change. They set the subject, not the verdict.

**Required:** what is being changed, and where.
**If missing:** ask which file or behaviour. Do not go looking for it.

**Waivable by explicit instruction:** nothing.
**Not waivable:** an escalation trigger that fires. The user calling something "a quick fix"
is not evidence about its blast radius.

## The question

Not "is this small?" but:

> **Does something already decide what correct looks like?**

An epic exists to decide correct behaviour. If correct is already written down, you are not
deciding — you are implementing. Skip the epic.

| | Correct is already decided | Correct is still being decided |
|---|---|---|
| **Route** | direct slice | epic |
| **Authority** | ARCHITECTURE.md section, a shipped epic's flow, or a test authority | none yet |

## Escalation triggers

Any one hit → epic. Check all five; do not stop at the first miss.

1. **New contract** — an API route, artifact field, registry key, spec field, or public
   signature that does not exist yet.
2. **Structural change** — folder structure, dependency direction, layer boundary, or tech
   stack.
3. **No authority can pin the test** — no textbook, no benchmark, no legacy output, no flow
   from a shipped epic. If you cannot say what the test asserts *against*, this is a feature
   request wearing a bug report's clothes.
4. **More than one zone touched.**
5. **Correct behaviour is contested** — the user and the document disagree, or two people do.

Trigger 3 is the one that gets skipped. Check it explicitly.

## Bug fixes

A bug is the code disagreeing with something already written down. The fix restores described
behaviour, so it never amends the architecture.

**If a bug fix would require an architecture change, it was never a bug.** It is a design gap.
Escalate, and say that plainly — the fix is not blocked, the *classification* was wrong, and
shipping it as a bug fix would move the architecture without a Change History row.

## Verdict

Name the authority or escalate. There is no third outcome.

**Direct slice:**

```md
Route: direct slice

Correct behaviour is decided by:
ARCHITECTURE.md §7 — orchestration is the only layer that combines api/, core/, state/.

Triggers checked: 1 no, 2 no, 3 no (test asserts against §7), 4 no, 5 no.

Scope: frontend/features/results/panel.py — one file, one layer.
Test: the failing test that reproduces it.

Proceed with direct-slice.
```

**Escalate:**

```md
Route: epic

Trigger 1 fired: the button calls `POST /jobs/{id}/preview`, which does not exist.

Nothing decides what correct looks like here — there is no flow, no contract, and no
authority to pin a test against.

Proposed epic stub:
<title, and the BDD flow the button implies>

Proceed with epic-formulation.
```

**Cannot ground it:**

If no trigger fires but you also cannot name the section, flow, or authority that decides
correct behaviour, **do not authorise the slice.** That combination means you have not found
the authority, not that none exists. Say which you searched and ask.

## Do not

- Do not edit code. Triage is read-only.
- Do not write the epic. Hand the stub to `epic-formulation`.
- Do not size the work. A one-line change that introduces a contract is an epic; a
  fifty-line change inside a decided contract is a slice.
