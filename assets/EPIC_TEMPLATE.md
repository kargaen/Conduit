# EPIC-<NNN>: <Title>

**Status:** draft | active | closed
**Created:** <YYYY-MM-DD>
**Architecture baseline:** <commit sha or ARCHITECTURE.md revision this epic was written against>

---

## 1. BDD — User Flows

The behaviour this epic delivers, from the outside. No implementation. If a flow mentions a
class, a module, or a database, it belongs in section 2 or 3, not here.

### Flow 1: <name>

```gherkin
Given <the state of the world before>
When <the user or system does one thing>
Then <the observable outcome>
And <any further observable outcome>
```

### Flow 2: <name>

```gherkin
Given ...
When ...
Then ...
```

**Out of scope for this epic:**
- <behaviour a reader would reasonably expect here, and why it is not included>

---

## 2. Function Call Signatures

> Optional. Frequently omitted in the first revision, and that is correct — writing
> signatures before the flows are agreed is design-by-guessing. Add them once a flow has
> survived contact with the code, or delete this section and say so.

```python
def <name>(<args>) -> <return>:
    """<one line: what it guarantees, not how>"""
```

**Not comprehensive.** Only signatures that constrain the design — a contract another layer
depends on, or one where getting the shape wrong forces a rewrite later. Do not enumerate
every helper.

---

## 3. TDD — Testing Strategy

How the flows in §1 become failing tests, and what each function call is measured against.

### Authority for correctness

For every function under test, name which authority pins its output. In descending order of
preference:

| Authority | Use when | Example |
|---|---|---|
| Textbook / published standard | The method has a canonical closed form | Gumbel quantile at p=0.99 |
| Published benchmark dataset | The method is standard but has no closed form | Peaks-over-threshold on a reference series |
| **Legacy application output** | Replacing an existing routine — the new call must reproduce the old one | Fit result vs. archived legacy Fortran run |

Legacy parity is the load-bearing one during migration. A function that replaces a legacy
routine is not correct because it is well-written; it is correct because it reproduces the
archived output on the archived cases. State the tolerance, and state it in the units of the
quantity, not as a bare float.

### Test map

| Flow | Function call | Authority | Fixture | Tolerance |
|---|---|---|---|---|
| 1 | `<call>` | legacy Fortran | `<path to archived case>` | ±<x> <unit> |

### What is deliberately not tested

<Appearance, ordering, incidental structure. Say so, so nobody adds it later thinking it was
an oversight.>

---

## 4. Checklist

Actionable items, top to bottom, each one a slice. An item is actionable when a competent
implementer needs no further decisions to do it — it names the file, the change, and the
condition under which it is done.

```md
[ ] 1. <verb> <what> in `<file>` — done when `<test>` passes
[ ] 2. ...
```

Rules:
- One file per item where possible. An item spanning files is a plan, not a slice — split it.
- Ordered by dependency, never by convenience.
- Tests come before the code they pin.
- `[x]` only when the item's test passes.

---

## 5. Summary

The section a reader skips to when deciding whether this epic is safe.

### Architecture impact

- [ ] No change to ARCHITECTURE.md expected
- [ ] Amends Description sections: <list>
- [ ] **Requires a Constitution change** — a human decision, blocks this epic until resolved

### North star deviation

Does this epic erode the property the architecture exists to protect? Quote the north star,
then answer plainly. "No" is a valid answer and should be the common one. If yes, say what is
being traded and why the trade is worth it. Do not bury this.

### Open questions

Heavy decisions this epic surfaces but does not settle. Each is a blocker or explicitly not
one. This is where a POC or MVP slice legitimately parks the decision it is deferring.

| # | Question | Blocks | Decision needed by |
|---|---|---|---|
| Q1 | | | |

### New capability

Is this epic introducing a set of features not alluded to anywhere in the architecture's
north star? If so, say so here in one sentence. An epic that quietly expands the product's
scope is the most expensive kind, and the only defence is naming it early.
