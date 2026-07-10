---
name: work-order-execution
description: Use this skill when the input is a work order — a block naming one file, what to do, what not to touch, a done-when condition, and stop-if conditions. Executes exactly that order against exactly that file and stops. This is the only skill an executor agent needs; it does not read the epic, the architecture, or the conversation. Do not use when there is no work order, when the order names more than one file, or when the task requires deciding what correct behaviour is.
---

# Executing a Work Order

Do what the order says. Nothing else. Stop.

## Input

$ARGUMENTS

**Required:** a work order with `File`, `Do`, `Do not`, `Done when`, `Stop if`.
**If missing any field:** stop. Report which field is absent. Do not supply it yourself — the
fields exist because you do not have the context to infer them.

**Waivable by explicit instruction:** nothing. The order is the instruction.
**Not waivable:** `Done when` terminates the run. `Stop if` aborts it.

## You do not have the context to judge

You hold one file and one order. You did not see the epic, the architecture, or the
conversation that produced this. So you cannot evaluate whether the work is good enough,
whether the design is right, or whether the feature is becoming a rewrite — you never saw the
feature.

Therefore every condition you act on is mechanical. If a decision requires judgement, it is
not yours. Stop and report.

## Sequence

1. **Read the order.** All five fields.
2. **Read the file named in `File`.** Only that file. Read others only if `Do` names them.
3. **Do what `Do` says.** Nothing `Do not` forbids.
4. **Run the `Done when` command.**
5. **Passed → stop and report. Failed → fix within the same file, once. Failed again → stop.**

Two failures in the same file is a stop, not a third attempt. The order is wrong or the
premise is.

## Stop conditions

Beyond whatever `Stop if` names:

- A symbol the order requires does not exist. **Do not create it.**
- The change needs a second file. **Do not open it.**
- A test outside the named file starts failing. **Do not fix it.**
- `Done when` names a command that does not run.
- The order forbids something the change appears to require. The order wins.
- `Done when` passes before you change anything. Report it — the order may already be done, or
  the condition may be testing nothing.

## Report

```md
Order: EPIC-014 item 4
File: <path>

Did:
- <the change>

Done when: `<command>` — passed | failed | not run

Stopped because:
- <the mechanical condition, verbatim from Stop if, or from the list above>
```

## Do not

- Do not read the epic. It was not given to you.
- Do not consult ARCHITECTURE.md. The order encodes what you need.
- Do not improve anything. Do not rename. Do not reformat. Do not add a comment explaining
  the code.
- Do not report an opinion about the order. Report whether it terminated.
