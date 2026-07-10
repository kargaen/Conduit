---
name: architecture-drift-audit
description: Use this skill when the user asks whether ARCHITECTURE.md is still accurate, before starting a new epic, or when a request depends on a structural claim in ARCHITECTURE.md that cannot be verified in the code. Reads the actual folder structure, dependency manifests, and layer boundaries and reports every divergence as a finding. This skill is read-only — it never edits ARCHITECTURE.md. Hand confirmed drift to architecture-md-maintenance. Do not use to update the document after a slice lands; that is epic-closeout.
---

# Architecture Drift Audit

Read-only. Report divergence. Edit nothing.

## Input

$ARGUMENTS

**Required:** nothing. Default scope is the whole document.
**If given:** a section or a path narrows the audit.

**Waivable by explicit instruction:** nothing.
**Not waivable:** this skill does not write. Not the tree, not a typo, not "while I'm here".

## Why read-only

When the document and the code disagree, you do not know which is wrong. The code may have
drifted from an intentional constraint — in which case the code is the bug, and silently
"correcting" the document destroys the only evidence that the constraint ever existed.

Every finding is a decision for a human or an epic. None is an edit.

## What to check

**Folder structure.** Regenerate and diff. Do not paste the result anywhere.

```bash
python ../architecture-md-maintenance/scripts/tree.py <repo-root> --depth 3 --merge ARCHITECTURE.md
```

Added paths are undocumented. Removed paths are documented fiction. Both are findings.

**Tech stack.** Every entry in the stack table appears in a manifest, and every direct
manifest entry that shapes the architecture appears in the table.

**Layer boundaries.** The declared dependency direction is enforced, or it is a wish.

```bash
lint-imports            # if import-linter contracts exist
rg -n "^from|^import" <layer-path> | rg "<forbidden-layer>"
```

A boundary with no mechanical enforcement is itself a finding, even when currently respected.

**Published contracts.** Routes, artifact fields, registry keys, spec fields named in the
document exist in the code, with the names the document gives them.

**Change history.** Every Description section that differs from the last audit has a row. A
Description change with no row was written illegitimately — treat its content as unverified.

**Deferred items.** Anything the document describes with "will", "eventually", "to be
formalized", or "if we ever" is speculative content that escaped into a Description section.

## Finding format

One block per divergence. No fixes.

```md
Finding <n>: <one line>

Document says:
§<n> — <quote or paraphrase>

Code says:
$ <command>
<output>

Which is wrong is not obvious:
- If the document is stale, an epic shipped without a closeout.
- If the code is wrong, a constraint was violated and the document is the evidence.

Needs: <a decision | an epic | a Change History row>
```

The middle block is not padding. It is the reason this skill does not fix anything.

## Report

```md
Audited: ARCHITECTURE.md against <commit sha>

Verified: §3, §6, §12, §21
Findings: 3
Unverifiable: §7 — no mechanical enforcement of the layer boundary; respected by inspection only.

<findings>

Nothing was edited. Route confirmed drift to architecture-md-maintenance.
```

Report `Verified` explicitly. An audit that lists only problems cannot be distinguished from
an audit that stopped early.
