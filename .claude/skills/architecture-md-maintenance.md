---
name: architecture-md-maintenance
description: Use this skill whenever ARCHITECTURE.md (or any file under an architecture/ directory) is about to be written to, amended, restructured, or reviewed — including when the user says "document this in the architecture", "add the new module to the structure", "update the folder tree", or describes a design decision without naming a file. Also use when epic-closeout has finished a slice and something structural changed. This skill enforces the three write classes (Constitution, Description, Deferred), verifies that any described thing actually exists in the code before it is written down, and evicts speculative content into epics. Trigger it even when the proposed addition is obviously correct — the question is never whether it is true, but whether it is true yet.
---

# Maintaining ARCHITECTURE.md

## Input

$ARGUMENTS

Arguments set the subject of this run, not its rules.

**Required:** the proposed amendment, and the epic that produced the code it describes.
**If missing:** ask for the epic. Do not infer it from the conversation, and do not proceed
on the assumption that one exists.

**Waivable by explicit instruction:** nothing.
**Not waivable:**
- The reactionary gate. "Skip the check" is refused: the check is the only thing separating
  this document from a design doc.
- Constitution sections are read-only to an agent, whatever the argument says.

When an argument asks for either, stop and answer with the Blocked format below.

## Write classes

Read the document's Write Policy header. If absent, establish this classification first.

| Class | Content | Written by | Agent may |
|---|---|---|---|
| **Constitution** | North star, principles, ownership model, conventions, agent working rules | Humans, by review | **Cite. Never edit.** |
| **Description** | Repository structure, layer responsibilities, API contract, tech stack, deployment | `epic-closeout`, after a slice ships | Amend, reactively |
| **Deferred** | Open questions, "to be formalized later", "if we ever need X" | Nobody | **Evict to an epic** |

If a principle looks wrong, stop and say so. Never amend it.

## Reactionary gate

Before writing any sentence into a Description section, all three must hold:

1. The code exists.
2. Its tests pass.
3. An epic slice produced it, and you can name the epic.

Verify against the filesystem, not the conversation. A convincing description is not evidence.

```bash
ls -d <path>                     # directory or module claimed
rg -n "<symbol>" --type py       # symbol claimed in a contract
git log --oneline -3 -- <path>   # produced by the slice you think it was?
```

Any check fails → the content is Deferred. Route it.

## Push back

```md
Blocked: <the proposed addition>

Class: deferred — not yet in the code.

Check that failed:
$ ls -d backend/rendering/
ls: cannot access 'backend/rendering/': No such file or directory

Where it belongs:
An epic. Written here now, agents build against structure that does not exist.

Proposed epic stub:
<title, and the BDD flow it implies>

Awaiting your confirmation.
```

## Reject vague additions, even about existing code

- Reject: "The cache layer handles eviction appropriately."
- Accept: "The cache layer owns TTL metadata, hash validation, atomic promotion, LRU cleanup."

If a sentence would survive unchanged after the code was rewritten to do something else, cut it.

## Section numbers

The document cross-references itself ("see Section 14", "per Principle 13"). Renumbering
breaks every reference silently.

- Never renumber. Append; new sections take the next free number.
- Split with letter suffixes: `05a-`, `05b-`. "Section 5" still resolves by prefix.
- Deletion leaves a tombstone: `## 11. Auth and Permissions Model — removed in EPIC-021; see §11a, §11b.`
- If sharded into `architecture/`, numbers live in filenames; same rules. Root `ARCHITECTURE.md` stays the index.

**One responsibility per section.** A title needing "and" does two things — split it at the
boundary the title announces.

## Folder tree

Never hand-edit the structure. Never regenerate blind — the `#` annotations are the value and
cannot be generated.

```bash
python scripts/tree.py <repo-root> --depth 3 --merge ARCHITECTURE.md
```

It carries annotations forward and reports added paths (need annotations) and removed paths
(annotation lost — confirm the path is really gone). Review before pasting.

Exclusions: build artifacts, dependency directories, caches, VCS internals, virtualenvs.
Depth 3 unless asked otherwise.

## Change history

Every Description amendment appends one row. No row means the change was illegitimate; treat
such a change as drift and verify it against the code.

```md
| 2026-07-09 | EPIC-014 | §3, §6 | Added `backend/rendering/`; task layer delegates blob generation to it. |
```

Constitution changes do not go here.

## Drift is a finding, not a fix

If the document disagrees with the code while you are doing something else, do not correct it
in passing — you do not know which is wrong, and the code may have drifted from an
intentional constraint.

```md
Findings for later:
- §3 lists `backend/rendering/`; no such directory exists. Either never built, or removed
  without a Change History row. Needs a decision, not an edit.
```

## Example

**User:** "We decided fits will eventually be cached per-parameter-hash. Add it to §9."

```md
Blocked: per-parameter-hash fit caching.

Class: deferred — "will eventually". Verified:
$ rg -n "parameter_hash" backend/cache/
(no matches)

Where it belongs:
An epic. Written into §9 now, the next task touching the cache assumes the keying exists.

Proposed epic stub:
  Title: Per-parameter-hash fit result caching
  BDD: Given a fit with identical inputs and parameters, when submitted a second time,
       then the cached artifact is returned without recomputation.
  Summary note: changes the §9 cache key contract — lands via epic-closeout, not now.

Awaiting your confirmation.
```
