---
name: epic-formulation
description: Use this skill whenever an epic is being written or updated — and also whenever the user describes work that does not exist in the code yet, whether or not they say the word "epic". Triggers include "plan a feature", "how should we build X", "write up the work for Y", "break this down", and any proposal that architecture-md-maintenance or agents-md-maintenance has just rejected as speculative. Produces a fixed-format document: BDD user flows, optional function signatures, a TDD strategy naming what pins each call's output, an actionable checklist, and a summary flagging architecture impact and north-star deviation. Use it for updating existing epics too — the format and its preservation rules apply identically.
---

# Formulating an Epic

## Input

$ARGUMENTS

Arguments are the epic's subject — the feature, problem, or rejected proposal to write up.
Treat them as the raw material for §1, not as instructions about the format.

**Required:** what the epic is about.
**If missing:** ask. Do not open the template with a placeholder title.

**Waivable by explicit instruction:** §2 signatures (already optional), the number of flows,
the level of checklist detail.
**Not waivable:** the §5 north-star answer and the architecture-impact declaration. An epic
without them cannot be reviewed for safety, which is what §5 is for.

An epic is the only legitimate home for what does not exist yet. Everything the architecture
document rejects lands here.

## Before writing

Read, in order:

1. The architecture's **north star** — §5 requires you to answer whether this epic erodes it.
2. The Description sections the epic will touch. Only those; the index routes you.
3. The existing epic, if updating.

Epics live at `epics/EPIC-<NNN>-<slug>.md`. Numbers are sequential and never reused.

## Format

Use `assets/EPIC_TEMPLATE.md` verbatim. Section order is fixed:

**BDD flows → function signatures → TDD strategy → checklist → summary**

### §1 BDD flows

Given/When/Then, observable from outside. A flow naming a class or table is implementation —
push it to §2 or §3.

Include **Out of scope**: the cheapest bug to prevent is someone implementing a flow you
deliberately excluded.

### §2 Function signatures — usually omit on first revision

Write them only when a contract constrains other work: an interface another layer depends on,
or one where the wrong shape forces a rewrite. Never enumerate helpers.

If omitting, write `*(deferred to revision 2)*` so it reads as a choice, not an oversight.

### §3 TDD strategy

For each function under test, name **one authority** that pins its output:

1. Textbook or published standard — cite it.
2. Published benchmark dataset.
3. **Legacy application output** — when replacing an existing routine, the new call must
   reproduce the archived output on the archived cases.

State tolerances in the units of the quantity — `±0.01 m`, not `0.001`. A bare tolerance
cannot be reviewed.

Write **what is deliberately not tested**, or someone will later add it believing they are
fixing an oversight.

### §4 Checklist

Absent explicit items from the user, the checklist is **your implementation plan**, in the
order you would do it.

Every item should trace to an entry in §3's test map. If it does not, ask what it is for.

- Reject: `[ ] Implement caching`
- Reject: `[ ] Update the frontend to handle the new artifact`
- Accept: `[ ] 3. Add failing test for quantile at p=0.99 in test_gumbel.py — done when it fails for the right reason`
- Accept: `[ ] 4. Implement quantile in gumbel.py — done when test 3 passes`

Rules:
- Tests before the code they pin.
- One file per item. An item spanning files is a plan — split it.
- Dependency order, never convenience order.
- `[x]` only when the item's test passes, not when the code is written.

### §5 Summary

**Architecture impact.** Which Description sections this amends when it ships. A required
Constitution change is a human decision and **blocks the epic** — say so at the top.

**North star deviation.** Quote it, answer plainly. "No" should be the common answer. Look
for the epic that erodes the property the architecture protects — typically one that makes a
generic zone know about a domain zone's contents.

**Open questions.** Heavy decisions surfaced but not settled. This is where a POC or MVP slice
legitimately parks a deferred decision: name it, say whether it blocks. An unnamed deferred
decision becomes an assumption, and assumptions become architecture by accident.

**New capability.** One sentence if this introduces features the north star never alluded to.
Scope expansion is not forbidden; silent scope expansion is.

## Updating an epic

- Never edit a completed item. `[x]` is a claim that a test passed.
- Never renumber. Numbers appear in commits, work orders, and closeout rows.
- Mark additions: `[ ] 12. (added <date>) …`
- Never silently drop scope. Strike visibly: `[~] 7. ~~Support dfs0 preview~~ — deferred to EPIC-019`
- Re-run the §5 checks. They are not write-once.

If an update changes §1 flows that already have `[x]` items beneath them, stop. Implemented
and specified behaviour have diverged.

## Push back on

- Flows describing implementation ("When the controller calls the service").
- Checklist items with no "done when".
- A TDD section naming no authority.
- A **missing** north-star answer — the absence is the tell, not the answer.
- An epic that is two epics: flows sharing no fixture and no file; a summary with two
  architecture impacts.

Propose, wait, name the destination.
