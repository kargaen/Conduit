---
name: refactor-guard
description: Use this skill when the user asks for a refactor, or when a refactor appears necessary before the requested work can proceed. Enforces that a refactor is scoped to one file, related to the task, behaviour-preserving, and explained before editing, and that feature work and refactoring are never combined in one run. Do not use for renames or extractions the user explicitly requested as the entire task — those are the task.
---

# Refactor Guard

A refactor changes structure and preserves behaviour. If behaviour changes, it is not a
refactor, and this skill does not authorise it.

## Input

$ARGUMENTS

**Required:** the refactor, and why now.
**If missing:** ask what should change and what must stay identical.

**Waivable by explicit instruction:** the one-file scope, when the user names the files.
**Not waivable:**
- Behaviour preservation. A refactor that changes behaviour is a feature or a bug.
- Never in the same run as feature work.

## The four tests

A refactor proceeds only if all four hold. State each.

1. **Behaviour-preserving.** There is a test that passes before and after, unchanged. If no
   such test exists, **write it first and watch it pass** — that is the characterisation test,
   and without it you cannot claim preservation, only hope for it.
2. **Related to the task.** Refactoring code you happened to read is scope creep. If it is
   unrelated, it is a finding, not a task.
3. **One file.** A refactor spanning files is an architecture change; route to `change-triage`.
4. **Explained before editing.** The user sees the shape of the change before the diff.

## Never combine

Feature work and refactoring never share a run. When both are needed:

1. Refactor. Tests pass, unchanged.
2. Stop. Report.
3. Feature. New test fails, then passes.

Combined, a failing test cannot distinguish "the refactor broke it" from "the feature is
wrong", and the diff cannot be reviewed by anyone.

If the user asks for both in one breath, do step 1 and stop. Say why.

## Proposal format

```md
Refactor: <what changes shape>
File: <one>
Behaviour preserved: <the test that proves it — existing, or the characterisation test written first>
Related to: <the task that needs it, or "nothing — this is a finding, not a task">

Before:
<shape, not the code>

After:
<shape>

Nothing was edited. Proceed?
```

## Stop instead

- No test pins the current behaviour, and writing one is not possible → the code is untestable,
  which is a finding about the architecture, not something to fix by refactoring blind.
- The refactor is required before the feature can be written *and* spans files → epic.
- The refactor would change a public signature → that is a contract change → `change-triage`.
- You have already started the feature. Finish it or revert it. Do not refactor mid-feature.

## Do not

- Do not rename symbols outside the file.
- Do not reformat unrelated code, even in the same file.
- Do not "clean up while you're in there". That sentence is the whole failure mode.
