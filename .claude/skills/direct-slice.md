---
name: direct-slice
description: Use this skill to implement a change that change-triage routed as a direct slice — a bug fix, or a small feature built entirely from contracts that already exist. The regression test is the specification: write the failing test, watch it fail, fix one file, watch it pass. No BDD document, no checklist, no closeout. Do not use when no triage has run, when the change introduces a new contract or structural change, or when an epic already covers the work — those are change-triage, epic-formulation, and epic-implementation respectively.
---

# Implementing a Direct Slice

One file. One failing test. Stop.

## Input

$ARGUMENTS

Arguments name the change and the authority triage found. They set the subject, not the
discipline.

**Required:** the triage verdict, including the architecture section, epic flow, or test
authority that decides correct behaviour.
**If missing:** run `change-triage` first. Do not proceed on a request that has not been
routed — the escalation triggers exist because "small" is not observable from the request.

**Waivable by explicit instruction:** the one-file default. Say what you are about to touch
before touching it.
**Not waivable:**
- The failing test comes first, and is observed failing.
- No architecture edit. Ever. See Escalation below.

## The test is the spec

There is no BDD document here, so the regression test carries the whole specification. Write
it as the artifact a reader would consult to learn what this change was for.

**For a bug fix:** the test reproduces the bug. It asserts the behaviour the authority already
describes — quote the section in the test's docstring, so the next reader can check it without
re-deriving it.

**For a small feature:** the test specifies the behaviour, in terms of contracts that already
exist. If writing the test requires inventing a contract, triage was wrong. Stop.

## Sequence

1. **Write the failing test.** Name the authority in its docstring.
2. **Run it. Watch it fail.** Confirm it fails for the expected reason — not an import error,
   not a missing fixture. A test that passes before the fix has not reproduced anything, and
   the bug is elsewhere.
3. **Fix one file.** The smallest change that turns it green.
4. **Run the test, then the file's existing test module.** The smallest suite that would catch
   a regression you just caused.
5. **Stop.** Report.

No ticking, no checklist, no Change History row. Nothing here is epic state.

## Escalation

Stop and hand back to `change-triage` if, mid-slice:

- The fix requires a new contract — route, artifact field, registry key, spec field.
- The fix requires touching a second zone.
- The fix would change what an architecture Description section says. **A direct slice that
  changes the architecture is a triage failure.** Do not amend the document, do not open
  `epic-closeout`. Report the disagreement.
- No authority actually pins the test once you try to write it. Triage said one existed; it
  did not. Say which.
- The bug cannot be reproduced. An unreproducible bug has no test, and therefore no fix.

Escalating mid-slice is expected and cheap. Discovering the escalation after merging is not.

## Do not

- Do not refactor adjacent code. Record a finding.
- Do not fix an unrelated failing test. Record a finding.
- Do not add a dependency. That is `dependency-change`, and it forces an epic.
- Do not batch a second obvious fix into the same run.

## Report

```md
Fixed:
- <file>: <the exact change>

Authority:
- ARCHITECTURE.md §7 — orchestration is the only layer that combines api/, core/, state/.

Test:
- <test name>: reproduced the bug, then passed

Findings for later:
- <noticed, not acted on>

Next safest step:
- <or: nothing; this change is complete>
```

If the slice revealed an architecture disagreement, replace the report with the escalation and
say nothing about what you would have done. The disagreement is the finding.
