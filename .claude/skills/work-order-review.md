---
name: work-order-review
description: Use this skill when an executor — a subagent, a cheaper model, or a separate session — returns the result of a work order and it is about to be accepted into the main agent's context. Verifies the diff against the order rather than trusting the executor's report, checks that only the named file changed and that no forbidden action was taken, and returns a compact summary rather than the executor's transcript. Do not use to review an epic (that is epic-review) or to review work the main agent did itself.
---

# Reviewing a Work Order Result

Review the diff, not the report. The report is a claim.

## Input

$ARGUMENTS

**Required:** the work order, and the executor's result.
**If missing the order:** stop. Without it there is no standard to review against, and a
review with no standard is an opinion.

**Waivable by explicit instruction:** nothing.
**Not waivable:**
- Verdict is `accepted` or `rejected`.
- The diff is read. An executor reporting success is not evidence of success.

## What this review can and cannot catch

It catches an executor that disobeyed: touched a second file, invented a symbol, skipped the
test, claimed a pass that did not happen.

**It cannot catch a wrong order.** If the same agent wrote the order and reviews the result,
it is checking execution against its own spec. That is a real gate against executor error and
no gate at all against planner error.

So: when the diff satisfies the order but the *result* looks wrong, the finding is about the
order. Say that explicitly. Do not reject the executor for obeying.

## Checks

Run all five against the diff.

### 1. Only the named file changed

```bash
git diff --name-only
```

Any other path → rejected. Including tests, formatting, and imports elsewhere.

### 2. Nothing in `Do not` was done

Read the diff for each prohibition. `Do not touch registry.py` is check 1. `Do not add
imports beyond scipy.stats` is not — it needs the diff read.

### 3. `Done when` actually passes

Run it. Do not read the executor's claim that it passed.

```bash
<the Done when command>
```

### 4. Nothing outside the file broke

The smallest suite that could catch a regression. If the order named a file in a module, run
that module's tests.

### 5. No symbol was invented

The order said stop if a required symbol is missing. Check that none was created instead — a
new class, a new field, a new config key, a stub returning `None`.

This is the most common quiet failure. An executor that cannot stop will improvise.

## Compact return

The main agent's context is the resource being protected. Return the finding, not the
transcript.

```md
Order: EPIC-014 item 4 — ACCEPTED

Diff: cowi_eva/fitting/distributions/weibull.py, +18 −0
Done when: pytest ...::test_quantile — passed (verified, not reported)
Module suite: 14 passed
Do not: respected

Findings:
- none
```

```md
Order: EPIC-014 item 4 — REJECTED

Violated: check 5.
The order said stop if DistributionSpec lacks a field. It lacks `support`. The executor added
`support: tuple = (0, inf)` to the spec instead of stopping.

Diff touched: distributions/weibull.py, fitting/spec.py  (check 1 also failed)

This is an order problem, not only an executor problem: item 4 was unimplementable as written.
Route to epic-formulation before re-issuing.

Not merged. Nothing from the executor's context was carried forward.
```

Never paste the executor's reasoning into the main context. It was produced without the
architecture, without the epic, and without the conversation. It is not evidence about
anything except what the executor did.

## Do not

- Do not fix the executor's work. Reject and re-issue a corrected order.
- Do not accept a diff that satisfies the order but breaks an unrelated test, on the grounds
  that the order did not forbid it. Check 4 exists.
- Do not accept `Done when: not run`. That is a rejection with extra steps.
