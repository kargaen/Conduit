---
name: planning-and-breakdown
description: Use this skill before the first edit of any run that changes code, and whenever a request has more than one part. Produces a short plan — mostly what, briefly why — and, when a task benefits from splitting, a checkbox breakdown of at most five parts, ordered top to bottom, each one file and one layer. Do not use for read-only requests, questions, or single-line edits whose plan is obvious. Do not use to plan work an epic already planned — that is epic-implementation.
---

# Planning and Breakdown

State the plan before the first edit. Then edit.

## Input

$ARGUMENTS

**Required:** the request.
**If missing:** nothing to plan. Ask.

**Waivable by explicit instruction:** the breakdown, when the user says the task is one step.
**Not waivable:** the plan precedes the first edit. A plan written afterwards is a summary.

## The plan

Roughly 80% what, 20% why. The *why* exists to let the user catch a wrong premise before code
is written, not to justify the approach.

```md
Plan:
- <what>, in `<file>`, because <the premise you are relying on>
- <what>, in `<file>`
```

Name the file. A plan that does not name files cannot be checked against the one-file rule,
which makes it decoration.

If the plan depends on an assumption you cannot verify, stop and ask instead. That is cheaper
than a plan built on it.

## When to break down

Break down when the request has more than one part, or when the plan has more than one file.
Do not break down a single obvious edit — the ceremony costs more than it saves.

- **At most five parts.** More than five means the task is an epic; route to `change-triage`.
- **Top to bottom.** Dependency order, never convenience order.
- **One file per part.** A part spanning files is not a part.
- **One layer per part.** `ARCHITECTURE.md` declares the layer model.

```md
Breakdown:
[ ] 1. <verb> <what> in `<file>` — done when <condition>
[ ] 2. ...
```

Each part needs a *done when*. Without it, the part cannot terminate and neither can the run.

## Stop instead of planning

- The breakdown needs more than five parts.
- Every ordering you try requires two files to keep the code working — the parts are not
  separable, and the boundary is wrong.
- The plan contradicts `ARCHITECTURE.md` → `rabbit-hole-check`.
- The plan requires a new dependency → `dependency-change`.
- The plan requires a refactor first → `refactor-guard`.

## Then do part one, and only part one

The breakdown is not permission to do all five. Execute the first part, report, stop.
