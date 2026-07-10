---
name: epic-review
description: Use this skill before the first slice of an epic is implemented, when an epic is handed over for approval, when an epic has been updated and implementation is about to resume, or when the user asks whether an epic is ready. Verifies the epic's claims against the repository rather than reading them back — every named authority, fixture, section, and contract is checked to exist. Returns exactly one of two verdicts: blocked or approved. Do not use to write or fix the epic; that is epic-formulation.
---

# Reviewing an Epic

Verify claims against the repository. Two verdicts. No third.

## Input

$ARGUMENTS

**Required:** the epic file.
**If missing:** ask which epic. Do not review the most recently modified one.

**Waivable by explicit instruction:** nothing.
**Not waivable:**
- Every check runs. A reviewer that stops at the first failure hides the other four.
- Claims are verified, not read. The epic asserting something is not evidence of it.
- The verdict is `blocked` or `approved`. Never "approved with suggestions".

## Why this is not epic-formulation's checklist again

`epic-formulation` self-checks while writing, from the same context that produced the epic.
This skill has the repository. Its job is the checks that require touching disk.

## Checks

Run all. Report all. One failure blocks.

### 1. Baseline is current

The epic names an `Architecture baseline`. If `ARCHITECTURE.md` has changed since — a
Change History row was appended, a Description section moved — the epic was planned against
a document that no longer exists.

```bash
git log --oneline <baseline>..HEAD -- ARCHITECTURE.md architecture/
```

Non-empty → blocked, unless the epic is re-checked against the current document.

### 2. Every named authority exists

§3's test map names, per call, a textbook, a benchmark, or a legacy output. Check the third
kind especially — it points at files.

```bash
ls -d <fixture path>          # the archived legacy case
rg -n "<benchmark name>" tests/
```

A test map row whose authority cannot be located is a row with no test behind it.

### 3. Every checklist item traces to a test map row

An item with no row is unpinnable: nothing decides when it is done. An item whose `done when`
names a test that appears nowhere in §3 is worse — it looks pinned.

### 4. Every checklist item names one file, and that file's directory exists

```bash
ls -d $(dirname <path>)
```

A new file in an existing directory is fine. A new file in a new directory is a structural
change, which §5 must have declared.

### 5. §5 architecture impact matches what the checklist implies

Read the checklist. Derive the impact yourself. Compare.

| Checklist implies | §5 says | Verdict |
|---|---|---|
| No structural change | No impact | pass |
| New directory, new route, new registry key | The matching sections | pass |
| New directory | No impact | **blocked** — the epic does not know what it will do |
| Nothing structural | Impact declared | finding, not blocking — likely over-planned |

Row 3 is the reason this check exists.

### 6. Constitution change → blocked, always

If the epic requires a principle, ownership, or convention change, it does not proceed. That
is a human decision made before code, not a thing an epic can grant itself.

### 7. Tolerances have units

`±0.01 m` passes. `0.001` blocks. A bare tolerance cannot be reviewed by anyone.

### 8. The north-star answer is present and argued

Absent → blocked. `No` with no reasoning → blocked. `Yes` with a stated trade → passes; the
trade is the user's call, not the reviewer's.

### 9. One epic, not two

Flows sharing no fixture and no file. Two architecture impacts. Two north-star answers. Any
of these → blocked, with the proposed split.

## Verdict

```md
Review: EPIC-014 — BLOCKED

Failed:
- Check 2: §3 names `tests/fixtures/legacy/gumbel_1998.csv` — does not exist.
    $ ls -d tests/fixtures/legacy/gumbel_1998.csv
    ls: cannot access ...
- Check 5: item 6 creates `backend/rendering/`; §5 declares no architecture impact.

Passed: 1, 3, 4, 6, 7, 8, 9

Findings (non-blocking):
- Item 9 and item 10 could be one slice.

Nothing was edited. Route to epic-formulation.
```

Report `Passed` explicitly. A review listing only failures cannot be distinguished from a
review that stopped early.

## Do not

- Do not fix the epic. Blocked findings go to `epic-formulation`.
- Do not soften a block because the epic is otherwise good. The good epics are the ones whose
  single wrong claim survives review.
- Do not approve an epic whose baseline is stale on the grounds that the change "looks
  unrelated". Re-check it, or block.
