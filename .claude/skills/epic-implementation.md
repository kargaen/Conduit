---
name: epic-implementation
description: Use this skill whenever work is being done against an epic — the user says "continue the epic", "next slice", "implement item 4", names an epic file, or attaches notes for an upcoming slice. Also use when the user asks to build something and an epic already covers it. Reads the epic and any slice notes, selects exactly one checklist item, writes the failing test before the code, changes one file, and stops. If no notes are supplied, it takes one action at a time rather than inferring a batch. Do not use for writing or restructuring the epic itself (that is epic-formulation) or for updating ARCHITECTURE.md after a slice lands (that is epic-closeout).
---

# Implementing an Epic

## Input

$ARGUMENTS

Arguments name the epic, the slice, and any notes. They set the subject, not the discipline.

**Required:** the epic file.
**If missing:** ask which epic. Do not search for one and guess.
**If the epic is named but no slice or notes:** take the topmost unchecked item — that is the
"one action at a time" default, not a reason to ask.

**Waivable by explicit instruction:** the one-file default, and the one-slice default. The
user may authorize a multi-file change or a batch of items; say what you are about to touch
before you touch it.
**Not waivable:**
- The failing test comes first, and is observed failing.
- `[x]` only when the item's test passes.

Produce exactly one slice, then stop.

**If no notes are supplied, take one action at a time.** Do not infer a batch, do not finish
the obvious rest, do not complete items 5 and 6 because 4 made them trivial.

## Sequence

### 1. Read

- The epic file, all five sections. §3 tells you what pins the test you are about to write;
  §5 tells you whether you are inside a known architecture impact.
- The slice notes, if any.
- Only the architecture sections §5 names.

### 2. Select

- **With notes:** do what they say, bounded by the epic. If the notes ask for something the
  epic does not contain, stop — that is a scope change for `epic-formulation`.
- **Without notes:** take the **topmost unchecked item.** Not the easiest, not the one whose
  file you already have open.

If the topmost item depends on something that does not exist, stop and say so. Do not skip to
the next one — a checklist in the wrong order is a finding about the epic.

### 3. Write the failing test first

- Write the test named in §3's test map for this item.
- Run it. Watch it fail. Confirm it fails for the expected reason — not an import error, not
  a missing fixture.
- A test that passes before the code exists is testing nothing. Stop and find out why.

Required even when the code is trivial: the failing run is the only evidence the test is
connected to what it claims to pin.

### 4. Implement

One file. The smallest change that turns the test green.

- No refactoring adjacent code.
- No new dependency.
- Do not implement the next item because it is now obvious.
- Do not fix an unrelated failing test. Record it as a finding.

### 5. Verify

Run the test, then the file's existing test module — the smallest suite that could catch a
regression you just caused.

### 6. Tick and stop

`[x]` only if the item's test passes. Not if the code is written. Not if it "works when I try
it." Then stop. Do not proceed to the next item.

## Stop conditions

Beyond the repository's usual ones:

- The test map has no entry for this item — you do not know what pins it. Ask.
- The item names no file — send it back to `epic-formulation`.
- The failing test fails for the wrong reason — fix the test, not the code.
- The implementation would touch a second file — report it as the next slice.
- The implementation contradicts an architecture Description section — conversation, not edit.
- The item is already `[x]` but its test fails — stop immediately. Everything downstream was
  planned on a false record.

## Work orders

When a slice is handed to a separate or cheaper executor, emit a written contract.

```md
## Work Order — EPIC-014, item 4
File:        cowi_eva/fitting/distributions/weibull.py
Zone/Layer:  civil-engineer zone (feature-first; no layers)
Do:          Implement `quantile(p, params) -> float` per DistributionSpec.
Do not:      Touch registry.py. Touch test_weibull.py. Add imports beyond scipy.stats.
Done when:   pytest cowi_eva/fitting/distributions/test_weibull.py::test_quantile passes.
Stop if:     DistributionSpec lacks a field you need. Any other test starts failing.
```

`Done when` comes from §3's test map — it lets the executor terminate without judging whether
the work is good enough.

`Stop if` must be **mechanical**: a named symbol is missing, a test outside its file broke,
the order names one file and it needs two. An executor holding one file cannot evaluate
judgement conditions like "this is becoming a rewrite" — it never saw the feature.

Assume the executor has not read the epic. Everything it needs is in the order.

## Report

```md
Changed:
- <file>: <the exact change>

Test:
- <test name>: failed as expected, then passed

Checklist:
[x] 4. <item>
[ ] 5. <next item — not started>

Findings for later:
- <noticed, not acted on>

Next safest step:
- <item 5, and what it will touch>
```

If the slice changed folder structure, layer boundaries, tech stack, or dependency direction:

```md
Architecture impact: yes — §3, §6. Run epic-closeout before the next slice.
```

Never update `ARCHITECTURE.md` yourself. That path has one door and this is not it.
