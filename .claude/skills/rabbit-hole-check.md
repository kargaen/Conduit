---
name: rabbit-hole-check
description: Use this skill when a request cannot be safely implemented as asked — it conflicts with ARCHITECTURE.md, crosses layers without permission, requires hidden global state, solves a product problem with an architectural workaround, or needs a brittle hack. Also use when the same approach has failed twice: a fix broke working behaviour, a patch needed a patch, or the same error reappeared after a supposed fix. Provides the rabbit-hole and iteration-trap response formats and the exit-path checklist. Do not use for ordinary scope questions that stopping and asking would answer — that is the assumption policy in AGENTS.md.
---

# Rabbit Hole Check

Two distinct failures. Different formats. Same rule: stop editing.

## Input

$ARGUMENTS

**Required:** the request, and what went wrong — a conflict, or a repeated failure.
**If missing:** describe which of the two you are in before continuing.

**Waivable by explicit instruction:** nothing. The user asking again is not new information.
**Not waivable:** you do not implement the hack while explaining that it is a hack.

## Rabbit hole: the request cannot be safely implemented

Triggers — any one:

- It conflicts with `ARCHITECTURE.md`.
- It crosses architectural layers without explicit permission.
- It requires hidden global state, or state a layer is not allowed to know about.
- It solves a product problem with an architectural workaround.
- It requires a brittle hack, or debt that will be paid by someone who did not choose it.

```md
This is a rabbit hole.

What was asked:
<one sentence>

Why it cannot be done as asked:
<the specific conflict — cite the section, name the layer>

What it would cost:
<the debt, the hidden coupling, the thing that breaks later>

Exit paths:
1. <smallest change that satisfies the product goal within the architecture>
2. <a change to the architecture, as an epic, if the goal is worth it>
3. <do nothing, and why that may be correct>

Nothing was edited. Which path?
```

Path 3 is not padding. Sometimes the honest answer is that the product goal is not worth the
structure it would cost, and saying so is the whole value of stopping.

## Iteration trap: the same approach has failed twice

Triggers — any one:

- A fix broke behaviour that previously worked.
- A patch needed a patch.
- The same error reappeared after a supposed fix.
- Two attempts have changed the same file in opposite directions.

The third attempt is almost never the one that works. The premise is wrong, not the code.

```md
This is an iteration trap.

Attempts:
1. <what was tried, what happened>
2. <what was tried, what happened>

The premise both attempts share:
<the assumption neither attempt questioned>

What would falsify it:
<the one check — a test, a print, a file read — that settles it>

Nothing further was edited. Run the check?
```

Do not attempt a third fix. Find the premise.

## Exit path checklist

Before proposing any exit path, confirm:

- [ ] It does not cross a layer the request did not authorise.
- [ ] It introduces no new dependency (else → `dependency-change`).
- [ ] It requires no refactor of working code (else → `refactor-guard`).
- [ ] It leaves existing behaviour intact.
- [ ] It can be described as one file, or it is an epic.

An exit path failing any of these is another rabbit hole.

## Do not

- Do not implement while flagging. Flagging and implementing is implementing.
- Do not soften the finding because the user seems committed. Commitment is what produced it.
- Do not amend `ARCHITECTURE.md` to resolve the conflict. That is the conflict.
