---
name: dependency-change
description: Use this skill when a change would add, remove, upgrade, or replace a package, or when an implementation seems to require a library the project does not already depend on. Produces the justification block — why existing code cannot solve it, what risk it introduces, what smaller no-dependency option exists — and links to official installation documentation rather than writing install commands. Do not use for importing modules already present in the manifest.
---

# Dependency Change

A dependency is a permanent decision made during a temporary task.

## Input

$ARGUMENTS

**Required:** the package, and what it is for.
**If missing:** ask. Do not infer the package from an import you were about to write.

**Waivable by explicit instruction:** nothing.
**Not waivable:**
- You do not add the dependency in the same run that proposes it.
- You do not write install commands. Link the official docs.

## First: is it already there?

Read the manifest. Importing a module that is already a declared dependency is not a
dependency change and this skill does not apply.

A transitive dependency is **not** already there. Depending on it declares a contract nobody
agreed to, and it disappears when the direct dependency drops it.

## Justification block

```md
Proposed dependency: <name> <version constraint>
For: <the one thing it does that is needed>

Why existing code cannot solve it:
<the specific gap — not "it would be more work">

Smaller option without the dependency:
<what a from-scratch version costs, in lines and in risk. "None" is an answer, but say it.>

Risk introduced:
- Maintenance: <last release, maintainer count, or "unknown">
- Surface: <what it pulls in transitively>
- Reversibility: <how hard to remove once code depends on it>

Architecture impact:
<Tech stack is a Description section. Adding a dependency amends it — which means this is
an epic, not a slice. Say so.>

Install: <link to official documentation>

Nothing was added. Proceed?
```

## The three questions that decide it

1. **Is the gap real?** "More work" is not a gap. "Correctly implementing this is a research
   project" is.
2. **Is the smaller option actually smaller?** Forty lines you own beats a package you do not,
   until it is four hundred. Estimate honestly.
3. **Can it be removed?** A dependency that touches one module is reversible. One whose types
   appear in your public signatures is permanent.

## Escalation

Adding, removing, or swapping a dependency changes the tech stack, which is an architecture
Description section. Therefore:

- It cannot land as a direct slice. Route to `change-triage` → `epic-formulation`.
- It reaches `ARCHITECTURE.md` only through `epic-closeout`.
- An upgrade within an existing constraint is not a stack change and may be a slice.

## Do not

- Do not run the installer to "check whether it works". That mutates the environment before
  the decision is made.
- Do not add a dependency to avoid writing a test double.
- Do not pin by copying a version from a search result. Read the project's own constraint
  policy first.
