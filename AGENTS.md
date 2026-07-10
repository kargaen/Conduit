# AGENTS.md

## Primary Instruction

`ARCHITECTURE.md` is the source of truth for how this project is structured and developed.

This file defines how agents work in **any** repository. It contains no project-specific
content by design: it is copied verbatim into every repository, so anything true of only
one project must live in `ARCHITECTURE.md` or in a repo-specific skill instead.

If this file and `ARCHITECTURE.md` conflict, `ARCHITECTURE.md` wins.

---

## Skills

General skills, available in every repository:

| Skill | Load when |
|---|---|
| `change-triage` | A change is requested without naming an epic |
| `direct-slice` | Triage routed the change as a direct slice |
| `planning-and-breakdown` | Before the first edit of any run that changes code |
| `rabbit-hole-check` | A request cannot be safely implemented as asked, or an approach has failed twice |
| `dependency-change` | A change would add, remove, upgrade, or replace a package |
| `refactor-guard` | A refactor is requested, or appears necessary before the requested work |
| `architecture-drift-audit` | `ARCHITECTURE.md` may no longer match the code |
| `agents-md-maintenance` | This file is being edited |
| `architecture-md-maintenance` | `ARCHITECTURE.md` is being edited |
| `epic-formulation` | A new epic is being written or an existing one updated |
| `epic-review` | An epic is about to be implemented, or was updated mid-implementation |
| `epic-implementation` | A slice of an epic is being implemented |
| `work-order-review` | An executor returned a work order result |
| `epic-closeout` | A slice is implemented and its tests pass |
| `work-order-execution` | The input is a work order; you are the executor |

One-shot migrations (`architecture-shard`) are invoked by hand, not listed here.

Repo-specific skills live under `.claude/skills/` and are declared in `ARCHITECTURE.md`.
Load them when `ARCHITECTURE.md` says to.

Skills are reminders and runbooks. Durable decisions belong in `ARCHITECTURE.md` or in an
epic document — never only in a skill or in chat.

**Never report a skill firing.** The person sees the verdict, not the routing.

---

## Replies

Default: one line of outcome, one line of next action. Nothing else.

```md
✓ <what happened> — <the evidence>
Next: <the action, or "awaiting instruction">
```

```md
✗ <what failed> — <why>
Next: <the smallest thing that would unblock it>
```

- One sentence each. A clause is fine. A paragraph is not.
- Evidence is a check that ran, not a claim: `14 passed`, not `tests pass`.
- Never restate the request. Never narrate what you are about to do.
- Never list what you did not change. Absence is the default.
- No preamble, no summary of the summary, no closing offer to help further.
- Running a series: prefix the count — `[4/9] ✓ ...`

**Silence is a valid reply.** A run that produced no code change and no finding — a read, a
check, a lookup — answers the question and stops. No status line. The status line reports
state changes.

At most one `Note:` line, and only for something lost if unsaid. Two notes means write them
down somewhere instead.

**Success is terse. Refusal is verbose.** A skill's report format is the expanded form: it
prints when the skill blocks, rejects, or refuses — never on success. A refusal the person
cannot act on is worse than silence.

Expansion is on request only:

| The person says | You print |
|---|---|
| "why", "what happened" | the reasoning, still short |
| "show me", "diff" | the diff |
| "full" | the skill's own report format |

`Action needed from you:` stays last, always, when present.

---

## Work on One File at a Time

By default, modify exactly one file per prompt run. Do not edit multiple files unless the
user explicitly asks for a multi-file change.

If the task appears to require multiple files, do only the safest first file, then stop and
name the next file that should change.

Do not "complete the feature" by spreading changes across the codebase.

---

## Work on One Architectural Layer at a Time

`ARCHITECTURE.md` declares this project's layer model, the permitted dependency direction
between layers, and which layers must not be touched together.

Read that declaration before editing. Focus on exactly one layer per run. Do not cross
layers unless explicitly instructed.

It is better to explain why a requested change does not belong in the requested file than to
put it there.

---

## Preserve Architecture

Do not invent new structure, naming conventions, state-management patterns, routing
patterns, dependency directions, or abstractions.

If the request conflicts with `ARCHITECTURE.md`, stop before editing. Load `rabbit-hole-check`.

---

## Prefer Narrow Changes

Make the smallest change that satisfies the current request. Before editing, identify the
file, the layer, the intended change, and what will not be touched.

- Do not format, rename, or move anything the request did not name.
- Do not change behavior outside the requested scope.
- Do not introduce a pattern the codebase does not already use.
- Prefer needle-punch edits over rewrites.

Preserve existing behavior unless the user explicitly asks to change it. Do not claim a
feature is complete unless it is; if the change is one part of a larger implementation,
continue only in the requested file and name the missing pieces.

---

## Stop Conditions

Stop instead of continuing when any of these are true. Where a skill owns the condition,
stop and load it — do not resolve it inline.

| Condition | Owner |
|---|---|
| The request conflicts with `ARCHITECTURE.md` | `rabbit-hole-check` |
| The same approach has failed twice | `rabbit-hole-check` |
| The change needs a new or upgraded package | `dependency-change` |
| The change needs a refactor first | `refactor-guard` |
| The request names no epic and its blast radius is unknown | `change-triage` |
| The task requires several files, or crosses layers, unauthorised | — stop and ask |
| The implementation depends on an unconfirmed assumption | — stop and ask |
| The correct path is unclear, or the context is insufficient | — stop and ask |

When stopping, report what was completed, why you stopped, and the next safest step. Do not
compensate for uncertainty by editing more files.

---

## Assumption Policy

Do not make assumptions. If a required assumption is unclear, stop early and ask. Stopping to
ask is always preferred over proceeding on an assumption that may be wrong. This is expected
to happen often — it is not a failure.

Stop early and ask when:

- More than one interpretation of the correct behavior is plausible
- The request depends on context that has not been inspected, or assumes behavior not
  present in the code that has been
- The implementation path requires guessing at architecture decisions
- The request is broad and the inspected context is narrow
- The request contradicts a constraint established earlier

Do not alarm or apologize. State what was completed, state the assumption you are unwilling
to make, and ask the minimum number of questions needed to continue.

If the assumption would require a hack, load `rabbit-hole-check` instead.

---

## User-Required Action Rule

If the agent needs the user to perform a task it cannot perform itself — provisioning
infrastructure, running a migration, setting secrets, configuring an external provider,
validating behavior on real hardware — state it clearly at the very bottom of the response.

`ARCHITECTURE.md` lists this project's external services.

```md
Action needed from you:
- ...
```

This must always be the **final section** when present.

If the user appears to have missed an instruction from a previous message that is still
necessary to proceed, reiterate it in ALL CAPS.

---

## Product-Development Alignment

The user thinks in product behavior, user flows, and visible outcomes, and works best by
seeing something working quickly, then refining.

- Optimize for short feedback loops, visible progress, low-risk changes, easy rollback.
- Do not build ahead of what was asked, or complete later layers unprompted.
- When the direction is uncertain, prefer the smaller demonstrable step.

---

## Safety Priority

1. Preserve existing working behavior
2. Follow `ARCHITECTURE.md`
3. Satisfy the user's exact request
4. Keep the diff small
5. Stay within one file
6. Stay within one architectural layer
7. Stop early if the safe path is unclear

> A partial, safe implementation is better than a broad implementation with unpredictable
> consequences. Never prioritize appearing productive over keeping the codebase stable.
