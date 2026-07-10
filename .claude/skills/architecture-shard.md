---
name: architecture-shard
description: Use this skill once per repository, to split a monolithic ARCHITECTURE.md into an index plus an architecture/ directory of constitution and description sections. Applies the one-responsibility split rule to section titles containing "and", preserves every section number via letter suffixes so existing cross-references keep resolving, and writes the root index. Do not use for routine amendments — that is architecture-md-maintenance — and do not use to reorganise a document that is already sharded.
---

# Sharding ARCHITECTURE.md

A one-shot migration. Content is moved, never rewritten.

## Input

$ARGUMENTS

**Required:** the document to shard.
**If missing:** ask.

**Waivable by explicit instruction:** the target layout.
**Not waivable:**
- Section numbers survive. Every existing cross-reference must still resolve.
- Prose is moved verbatim. This is not the moment to improve it.
- Constitution/Description membership is confirmed by the user, not guessed.

## Why shard

Selective reading. An agent reads the index and loads two sections instead of fourteen
thousand tokens. Secondarily, and more durably: the write policy becomes a path rule that
CODEOWNERS can enforce, rather than a paragraph asking nicely.

## Target layout

```text
ARCHITECTURE.md                  # index + north star + write policy. Always read.
architecture/
├── constitution/                # CODEOWNERS: zone owners. Agents: read-only.
│   ├── 01-guiding-principles.md
│   └── ...
├── description/                 # Written only by epic-closeout. Reactionary.
│   ├── 03-repository-structure.md
│   └── ...
└── 25-change-history.md         # neither; append-only
```

Three classes, three locations. If a section fits none, do not shard it — ask.

## Sequence

### 1. Classify, then confirm

Propose the membership of every section. Do not begin moving until the user confirms. The
Constitution/Description line is a judgement about who may write, and getting it wrong makes
a read-only section writable.

### 2. Split titles containing "and"

The codebase forbids a module that does two things. Apply it to the document.

`11. Auth and Permissions Model` → `11a-auth-model.md`, `11b-permissions-model.md`

**Letter suffixes, never renumbering.** "Section 11" still resolves by prefix. A reference to
a split section resolves to both halves, which is correct — the reference was written when
they were one thing.

Watch for sections whose two halves belong to *different* classes. A versioning section that
states a retention commitment and describes the current stack shape splits into constitution
and description. These are the valuable splits; they were hiding a write-policy violation.

### 3. Move verbatim

Copy prose unchanged. Resist every improvement. A shard that also edits cannot be reviewed,
because the diff shows everything as new.

### 4. Write the index

One line per file. The filename carries the meaning; the line disambiguates.

```md
| § | File | Contains |
|---|---|---|
| 3 | `description/03-repository-structure.md` | Annotated folder tree, depth 3 |
```

### 5. Verify

- Every original section number appears in exactly one filename, or two with `a`/`b`.
- Every internal cross-reference resolves.
- Concatenating the shards reproduces the original prose. Diff it.

```bash
cat architecture/*/*.md | diff - <(sed -n '/^## 1\./,$p' ARCHITECTURE.md.bak) || true
```

Differences should be headers and nothing else. Any prose difference is a bug.

### 6. Stop

Do not update AGENTS.md. It refers to `ARCHITECTURE.md` by name, which still exists and is
still the entry point. If sharding required an AGENTS.md change, the layout is wrong.
