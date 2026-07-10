---
name: agents-md-maintenance
description: Use this skill whenever AGENTS.md is being read for editing, added to, trimmed, or reviewed — including when the user says "add a rule for the agent", "the agent keeps doing X, stop it", "put this in AGENTS.md", or proposes any new agent instruction without naming a file. Also use when reviewing an AGENTS.md that may have accumulated project-specific content. This skill enforces the one invariant that makes AGENTS.md safe to copy across every repository, and routes rejected content to the file that should own it. Trigger it even for edits that look obviously fine — a single project noun is enough to break the invariant.
---

# Maintaining AGENTS.md

## Input

$ARGUMENTS

Arguments set the subject of this run, not its rules.

**Required:** the proposed rule or edit, or a file to review.
**If missing:** ask which rule is being added, or run `leak_check.py` on the current file and
report. Do not invent a rule.

**Waivable by explicit instruction:** the propose-and-wait step ("just do it" → apply, show
the diff).
**Not waivable:** the invariant. A project fact does not enter AGENTS.md because the user
asked twice. Route it and say why.

## Invariant

AGENTS.md contains nothing true of only one project. It is copied verbatim into every repo
and overwritten on re-broadcast; project content in it is silently clobbered on the next sync
and, until then, lies to every other repo. Cite this reason when pushing back.

## Test every line, added or existing

> Would this still be true and useful if this file were copied verbatim into every repository
> tomorrow?

## Verdicts

**1. Universal** — true anywhere, verifiable, names nothing specific. Accept.

**2. General rule, project vocabulary** — the rule is universal, its nouns are local. Do not
delete. Parameterize: AGENTS.md states the rule, `ARCHITECTURE.md` holds the vocabulary.

Proposed: `Work on one MVC layer at a time. Never edit a view during a controller task.`

Rewrite:
```md
Work on one architectural layer at a time. `ARCHITECTURE.md` declares this project's layer
model and the permitted dependency direction between layers.
```
Move the MVC table to `ARCHITECTURE.md`.

Without this verdict the file degenerates into platitudes. Use it.

**3. Project fact** — reject and route. Never soften into a vague version to keep it; a
generalized project fact is a platitude.

## Route every rejection

Never reject without naming a destination.

| Content | Destination |
|---|---|
| Structural fact about the codebase | `ARCHITECTURE.md` (via `architecture-md-maintenance`) |
| Rule applying only inside one directory | Nested `AGENTS.md` in that directory |
| Multi-step procedure or runbook | Skill under `.claude/skills/`, declared in `ARCHITECTURE.md` |
| Not built yet | An epic (via `epic-formulation`) |
| Personal, uncommitted preference | `AGENTS.local.md`, gitignored |

Nested `AGENTS.md` is honored by every major harness (closest file wins) and is underused.

## Detect

```bash
python scripts/leak_check.py AGENTS.md
```

Flags paths, camelCase/PascalCase identifiers, vendor names, named skills, non-whitelisted
documents. It misses semantic leaks. Also read the file for:

- **Declared architecture** — "The app uses an MVC pattern." Verdict 2.
- **Assumed toolchain** — "Run the test suite before finishing."
- **Assumed domain** — examples about profiles, carts, sensors.
- **Two projects' rules coexisting** — the invariant has already failed.

## Trim

AGENTS.md loads on every run in every repo forever. Also ask what should leave.

Extract a rule to a skill only if the agent notices the trigger without having read the skill:

- Extractable: "when adding a dependency…", "when a request conflicts with the architecture…"
- Not extractable: "prefer narrow changes" — by the time you would load the skill, the broad
  change is made.

Anything the agent needs in order to know it is in trouble stays resident.

## Push back

Propose, then wait. Never silently relocate or generalize.

```md
Verdict: <universal | general rule with project vocabulary | project fact>

Why:
<one sentence, citing the acceptance test>

Proposed for AGENTS.md:
<the parameterized rule, or "nothing">

Proposed for ARCHITECTURE.md §<n>:
<the fact being moved, ready to paste>

Awaiting your confirmation before editing either file.
```

Act without waiting only when removing a leak you introduced this session, or when the user
said "just do it" — then show the diff.

## Editing rules

- Merge duplicate rules. A rule stated twice will eventually be edited once.
- Never cite `ARCHITECTURE.md` section numbers from AGENTS.md; those numbers are project-specific.
- Every rule must be verifiable. If you cannot imagine the check, cut it.

## Example

**User:** "The agent keeps forgetting to run `pyside6-uic` after touching a `.ui` file. Add
that to AGENTS.md."

```md
Verdict: project fact

Why: `.ui` files and `pyside6-uic` exist in one repository. Copied elsewhere, this is noise.

Proposed for AGENTS.md:
nothing.

Proposed for ARCHITECTURE.md, Conventions:
Views are built via `.ui` files and converted with `pyside6-uic`. A `.ui` edit is not
complete until the conversion is run.

Better: this is a procedure with a self-announcing trigger. Make it a repo-specific skill,
which can also carry the exact command and flags.

Awaiting your confirmation.
```
