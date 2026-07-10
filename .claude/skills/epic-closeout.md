---
name: epic-closeout
description: Use this skill when an epic slice has been implemented and its tests pass, when an epic's checklist is fully ticked, or when epic-implementation reported "Architecture impact: yes". Also use whenever someone proposes updating ARCHITECTURE.md to reflect work that has just landed — this skill is the only legitimate path from shipped code into the architecture document. It records what changed against the epic's summary, appends the Change History row, and invokes architecture-md-maintenance only when the slice actually altered structure, layer boundaries, tech stack, or dependency direction. Do not use mid-slice, and do not use for changes internal to an existing module.
---

# Closing Out an Epic Slice

## Input

$ARGUMENTS

Arguments name the epic and slice. They set the subject, not the preconditions.

**Required:** the epic, and a slice whose tests pass.
**If missing:** ask. Do not close out an epic you cannot name.

**Waivable by explicit instruction:** nothing.
**Not waivable:**
- Preconditions are verified by running the tests, not by being told they pass.
- Constitution sections stay read-only.
- A Description amendment appends a Change History row.

An argument asking to skip any of these is refused: this is the only door into the source of
truth, and a door that opens on request is a window.

This is the only write path from shipped code into `ARCHITECTURE.md`. A Description change
with no Change History row came through a window.

## Preconditions

Verify; do not take the conversation's word for it.

1. The slice's tests pass. Run them.
2. Checklist items marked `[x]` have passing tests, not merely existing code. Spot-check the
   last one.
3. You can name the epic.

A ticked item whose test fails → stop. Do not close out.

## Gate: did anything structural change?

Invoke `architecture-md-maintenance` **only** if the slice altered:

- Folder structure — a directory added, removed, moved
- Layer boundaries — what a layer may know about
- Dependency direction — who imports whom
- Tech stack — a dependency added, removed, swapped
- A published contract — API route, artifact envelope, registry key, spec field

**Not** architecture impact:

- A new function inside an existing module
- A bug fix
- A new test
- A new registered method following an existing extension contract

The last is the common false positive. An extension contract exists so that using it changes
nothing structural. If adding a distribution required an architecture edit, the extension
contract is broken and **that** is the finding.

## Sequence

### 1. Tick

Only items whose tests pass. Never edit a completed item. Never renumber.

### 2. Reconcile against the epic's §5

| Predicted | Actual | Do |
|---|---|---|
| No impact | No impact | Note it. Nothing else. |
| Impact on §3, §6 | Same | Proceed to step 3. |
| No impact | Impact | **Stop.** Report what changed and why the epic did not foresee it. |
| Impact | No impact | Note it. Slice is incomplete, or the epic over-planned. |

Row 3 is the one that catches drift before it is written down.

### 3. Amend via the maintenance skill

Load `architecture-md-maintenance`. Pass it the epic id, the sections to amend, and the
verified facts. It re-verifies against the filesystem. Do not reimplement its rules here.

**Constitution sections stay off-limits.** If the slice appears to require a principle change,
it required one before the code was written and the epic should have blocked. Stop and say so.
Shipped code is not an argument for amending a principle after the fact.

### 4. Append the Change History row

Mandatory for any Description amendment. One row.

```md
| 2026-07-09 | EPIC-014 | §3, §6 | Added `backend/rendering/`; task layer delegates blob generation to it. |
```

No architecture change → no row. Do not record "no change".

### 5. If the epic is finished

- Set `Status: closed`.
- Move unresolved §5 Open Questions to a new epic or the backlog. Never let them close with
  the epic — a deferred decision that disappears becomes an assumption.
- Verify each `[~]` struck item names where it went.

## Multi-file writes are expected here

A slice changing folder structure and a published contract amends two Description sections.
The one-file rule bounds the blast radius of code changes; documentation cannot break a build,
and the file count is an artifact of how the document was sharded. Do not split a closeout
across runs — that leaves the source of truth internally inconsistent between them.

Touch no code during closeout. If tempted to fix a line while documenting it, record a finding.

## Report

```md
Closed out: EPIC-014, slice 2

Checklist:
[x] 4. Implement quantile in gumbel.py
[x] 5. Register GUMBEL in distributions/registry.py

Architecture impact: none.
Reason: adding a distribution via the extension contract is structurally invisible by design.

Predicted vs actual: matched.

Findings for later:
- §3 test map lists a tolerance of "0.001" with no unit. Fix before the next slice.

Next safest step:
- EPIC-014 item 6, touching cowi_eva/fitting/distributions/test_weibull.py
```
