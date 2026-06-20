# AGENTS.md

## Primary Instruction

Follow `architecture.md` as the source of truth for how this app is structured and developed.

This file defines how agents must work inside the repository.

The default working mode is:

- Small iterations
- One file at a time
- One MVC layer at a time
- Minimal diffs
- No speculative rewrites
- Stop early rather than causing side effects

> A partial, safe implementation is better than a broad implementation with unpredictable consequences.

---

## Non-Negotiable Workflow Rules

### Work on One File at a Time

By default, modify exactly one file per prompt run.

Do not edit multiple files unless the user explicitly asks for a multi-file change.

If the requested task appears to require multiple files, do only the safest first file, then stop with a concise explanation of the next file that should be changed.

Do not "complete the feature" by spreading changes across the codebase unless explicitly instructed.

---

### Work on One MVC Layer at a Time

The app is developed using an MVC pattern. During feature work, focus on only one layer at a time:

- Model
- View
- Controller
- Service / Infrastructure
- Navigation / Composition
- Tests

Do not cross layers unless explicitly instructed.

| If the user asks for… | Do not touch…         |
| --------------------- | --------------------- |
| A controller task     | Views or models       |
| A view task           | Models or controllers |
| A model task          | Views or controllers  |
| Service work          | Screen composition    |

It is better to explain to the user why a requested feature in a requested file is not the right place to put the logic.

---

### Preserve Architecture

Always follow `architecture.md`.

Do not invent new structure, naming conventions, state-management patterns, routing patterns, dependency directions, or abstractions.

- If there is a conflict between this file and `architecture.md`, follow `architecture.md`.
- If the user's request conflicts with `architecture.md`, stop and explain the conflict before editing.

---

### Prefer Narrow Changes

Make the smallest change that satisfies the current request.

**Avoid:**

- Broad refactors
- Formatting unrelated code
- Renaming unrelated symbols
- Moving files
- Rewriting working code
- Changing public APIs unless required
- Changing behavior outside the requested scope
- Introducing new dependencies unless explicitly requested
- Introducing new architectural patterns unless already established

Preserve existing behavior unless the user explicitly asks to change it.

---

## Planning Rules

Before editing, provide a short plan. The plan should be:

- **~80% what** will be changed
- **~20% why** it is being changed

Do not write long explanations in plan mode. A good plan is 2–3 paragraphs of text. Anything more than that, see breakdown rules.

**Example:**

```md
Plan:

- Update only `src/features/profile/controllers/useProfileController.ts`.
- Keep the change inside the controller layer.
- Add handling for the empty profile state.
- Avoid touching views, services, models, navigation, or tests.
- Reason: keeps the behavior isolated and reduces side effects.
```

---

## Task Breakdown Rule

If the user's request clearly benefits from being broken into smaller parts, break it down before beginning.

Use this only when each part can safely add to the requested file without breaking the code while the larger request is still incomplete.

**Constraints:**

- Must stay within the file requested by the user
- Must stay within the MVC layer requested by the user
- Must stay within the current prompt scope
- Maximum of 5 parts
- Always work top to bottom

Before beginning, briefly explain why the task is being broken down. Then present the breakdown using this exact checkbox format:

```md
[x] Task 1
[ ] Task 2
[ ] Task 3
```

Use `[x]` for the part currently being worked on or completed. Use `[ ]` for parts not yet started.

After completing each part, update the checklist in the response. Do not start lower checklist items before higher ones are complete.

If the full request would require multiple files to follow the architecture, mention that as a side note but keep working only on the requested file.

**Example side note:**

> Side note: The complete architecture-correct implementation will likely need a controller update later, but this run will only modify the requested view file.

Do not edit additional files unless the user explicitly authorizes a multi-file change.

---

## Stop Conditions

Stop instead of continuing when any of these are true:

- The task requires touching several files but the user did not explicitly allow it
- The task crosses MVC layers but the user did not explicitly allow it
- The task breakdown would require multiple files or MVC layers to keep the code working
- The current request conflicts with `architecture.md`
- The implementation depends on unconfirmed assumptions
- The context is insufficient
- The requested change is likely to cause side effects outside the current layer
- The correct implementation path is unclear
- The feature is becoming a rewrite rather than an iteration
- The request would require brittle hacks or avoidable technical debt
- The request appears to solve a product problem with an architectural workaround

**When stopping, report:**

1. What was completed
2. Why you stopped
3. The next safest step

Do not compensate for uncertainty by editing more files.

---

## Context Rot Rule

If the current task appears to suffer from context rot, stale assumptions, or an unclear goal, stop early.

**Signs of context rot:**

- The requested file no longer matches the described behavior
- The implementation path depends on files not currently inspected
- Several unrelated areas seem involved
- The request starts broad but available context is narrow
- The agent would need to guess architecture decisions
- The request assumes behavior that is not present in the inspected code
- The requested change appears to contradict earlier established constraints

In this case, make no broad changes. Either make a small safe change or report the blocker.

---

## Rabbit Hole Rule

The user is primarily a product developer. They may think in terms of product behavior, user flows, fast iteration, and visible outcomes rather than implementation constraints. They may also get carried away and accidentally request work that drifts from the architecture, creates unnecessary complexity, or pushes the app toward brittle hacks.

If a request appears to violate `architecture.md`, require a nasty workaround, introduce avoidable technical debt, or go far outside established best practices — **stop before editing**.

Use the phrase **rabbit hole** explicitly so the user knows the request needs reassessment.

**Response format:**

```md
Rabbit hole:
[What part of the request is problematic]

Why this is risky:
[Why it is dangerous]

Underlying product goal:
[The simpler goal that seems to be underneath]

Safest next step:
[The smaller, safer action to take instead]
```

**Example:**

> **Rabbit hole:** This request would require bypassing the controller layer and pushing persistence logic into the view.
>
> **Why this is risky:** It breaks the MVC boundary, makes the screen harder to test, and may cause side effects when storage behavior changes.
>
> **Underlying product goal:** You want the user's preference saved immediately when they toggle the setting.
>
> **Safest next step:** Update only the controller so it receives the toggle event and delegates persistence to the existing service.

Do not continue with implementation until the risky direction has been narrowed or corrected. Don't continue boxing around with architecture restrictions.

**Trigger this rule when the user:**

- Asks for cross-layer changes without saying so explicitly
- Requests a shortcut that breaks MVC boundaries
- Asks for behavior that requires hidden global state
- Proposes duplicating state across model, controller, and view
- Asks for a broad rewrite to solve a narrow product issue
- Tries to solve a UX problem with architecture changes
- Tries to solve an architecture problem with UI hacks
- Requests work likely to make testing harder
- Adds requirements unnecessary for the current MVP iteration
- Keeps expanding scope before the current slice is working
- Asks for "just make it work" in a way that would damage maintainability

### Rabbit Hole — Iteration Trap

If an approach has been attempted **2 or more times** and each attempt either:

- broke something that was previously working,
- required a patch to fix the patch,
- or failed to produce the intended outcome —

**stop immediately. Do not attempt a third fix in the same direction.**

Declare the iteration trap explicitly using the phrase **rabbit hole** so the user knows we are stuck, not progressing.

**Response format:**

```md
Rabbit hole (iteration trap):
[What we have tried and how many times]

Why we are stuck:
[The root reason the approach keeps failing — framework limitation, wrong abstraction, incorrect assumption, etc.]

What continuing would cost:
[The likely damage of one more patch attempt]

Recommended exit:
[A fundamentally different approach, a rollback target, or an explicit decision to defer this to a different tool/layer/person]
```

**Do not:**

- Attempt a "just one more tweak" after two failed iterations
- Silently absorb the failure and try a variation without flagging it
- Blame framework quirks without questioning whether the approach itself is wrong

**Trigger this rule when:**

- The same error reappears after a supposed fix
- A fix resolves the symptom but surfaces a new failure in the same area
- The code has grown a chain of conditional patches around one core problem
- A workaround is needed to make a previous workaround function
- The agent has lost confidence in why the original approach should work at all

---

## Assumption Policy

Do not make assumptions. If a required assumption is unclear, stop the run early and ask.

Stopping to ask is always preferred over proceeding with an assumption that may be wrong. A partial result with no side effects is better than a completed run built on a wrong assumption. This is expected to happen often — it is not a failure.

**Stop early and ask when:**

- The correct behavior is ambiguous and more than one interpretation is plausible
- The request depends on context that has not been inspected
- Context rot makes it unclear whether the request still applies to the current state of the code
- The request is difficult or appears to require something that may not be possible
- The implementation path requires guessing at architecture decisions
- Proceeding without confirmation risks touching multiple files or layers

**When stopping, do not alarm or apologize. Simply:**

1. State what was completed, if anything
2. State what assumption you are unwilling to make
3. Ask the minimum number of questions needed to continue

**Avoid this:**

> I assumed the feature needed a new service, updated the model, rewired navigation, and changed the screen.

If an assumption would require a hack, trigger the Rabbit Hole Rule instead.

---

## Research Findings

During a prompt run, the agent may discover useful findings unrelated to the exact requested change. Do not act on them — record them at the end and let the user know.

**Format:**

```md
Findings for later:

- `ProfileService.getUserProfile` returns `null`, but the controller currently treats it as always defined.
- The view already has an unused `isLoading` prop that could support the next iteration.
```

Findings should be concise and actionable. Do not turn them into extra edits unless explicitly asked.

---

## MVC Iteration Strategy

The user works in multiple passes over a feature, not a single waterfall implementation. Each pass focuses on one layer at a time, getting to something testable quickly before refining.
The agent should not try to anticipate or complete later layers. Do not build ahead of what was asked.
If the current request has been completed and no other response conditions are triggered, close with a single discrete suggestion for a logical next step within the same layer — nothing more.
Format:

````Possible suggestion for improvement:
- ...```

Maximum 1-3 bullets and short suggestions.

---

## Feature Development Order

When building a feature, work layer by layer. A typical sequence is:

1. Model contract
2. Service or data adapter
3. Controller behavior
4. View rendering
5. Screen composition
6. Tests
7. Refinement

Only work on the layer requested by the user. If the user has not specified a layer, choose the smallest safe layer to begin with, inform the user and if in doubt, see assumption policy, and state that choice in the plan. Do not jump ahead to later layers because they seem obvious.

---

## File Editing Rules

**Before editing a file:**

- Identify the file
- Identify the MVC layer
- Identify the intended change
- Identify what will not be touched

**After editing a file:**

- Summarize the exact change
- Mention any checks run when relevant
- Mention any checks not run when relevant
- Mention the next safest step

Do not claim the whole feature is complete unless it actually is. Do not modify unrelated imports, formatting, comments, or neighboring code unless required for the current change.

If a requested change is only one part of a larger architecture-correct implementation, continue only in the requested file and state the missing pieces as a side note. Do not edit those pieces unless explicitly instructed.

Avoid redoing entire files. Prefer needle punch operations over major rewrites.

---

## Test Suggestion Rule

Only suggest adding tests when the repository already has a test suite. If not, omit this section entirely.

If a request would clearly benefit from a new test, mention it only as a closing statement — do not interrupt implementation to discuss it.

**Format:**

```md
Test suggestion:
- What to test: `useProfileController` returns the empty-state view model when the profile service returns `null`.
- Benefit: Protects the controller from regressing into a crash when a user has no profile data.
- Current gap: Existing controller tests cover successful profile loading but not the `null` response path.
````

Avoid vague suggestions like "Add tests for this."

---

## User-Required Action Rule

If the agent needs the user to perform a task it cannot perform itself, state it clearly at the very bottom of the response.

**This includes:**

- Creating or modifying a database table (if a migration flow is not ready)
- Running a migration requiring user-controlled infrastructure
- Setting environment variables in an external dashboard
- Creating a new external service for the app
- Configuring a third-party provider
- Adding API keys or secrets
- Changing App Store, Expo, Firebase, Supabase, Stripe, or other external project settings
- Manually validating behavior on a physical device

**Use this exact section title:**

```md
Action needed from you:

- ...
```

This section must always be the **final section** of the response when present. Do not bury required user actions in the middle of a reply.

Additionally, if the user appears to have missed or skipped an instruction the agent gave in a previous message that is still necessary to proceed correctly, the agent must reiterate it in ALL CAPS so it stands out clearly.

---

## Communication Style

Be concise. Avoid long explanations. Do not over-explain architecture unless asked.

**Standard response shape after work:**

```md
Changed:

- ...

Not changed:

- ...

Checks:

- ...

Findings for later:

- ...

Side note:

- ...

Test suggestion:

- What to test: ...
- Benefit: ...
- Current gap: ...

Next safest step:

- ...

Action needed from you:

- ...
```

Omit empty sections. If `Action needed from you` is present, it must always be the final section.

---

## View Cleanliness Rule

Never add unnecessary instructional text, developer notes, placeholder labels, or status messages directly inside a view if they don't belong there.

Views must render as clean, testable UI at all times. Any text rendered inside a view is product text — it will be seen by the user and must belong to the product.

**Do not add things like:**

- `"Update the title and note for this item. This is a local preview for now."`
- `"Remove this entry from the list preview. This is only affecting the current screen state."`
- `"Edit/delete buttons are placeholders for now."`
- Any `// TODO`, inline comments, or annotation strings rendered as visible UI

**If commentary on a view change is needed, put it in a todo comment — not in the view.**

This rule has no exceptions. A view with developer notes in it is not a testable view.

---

## Product-Development Alignment

The user works best by seeing something working quickly, validating the direction, and then refining.

**Optimize for:**

- Short feedback loops
- Visible progress
- Low-risk implementation
- Easy rollback
- Focused scope
- Practical MVP slices

**Do not optimize for:**

- Large up-front design
- Perfect abstractions before validation
- Speculative extensibility
- Broad rewrites
- Completing every possible edge case in one run

When the implementation direction is uncertain, prefer a smaller demonstrable step.

---

## Dependency Rules

Do not add dependencies unless explicitly requested. If a dependency seems necessary, stop and explain:

- Why the existing code cannot solve the problem
- What dependency would be added
- What risk it introduces
- What smaller no-dependency option exists

Do not install packages as a side effect of a narrow code task.

Do not write install commands. Package CLIs, options, and flags go stale and vary by environment. Instead, link directly to the official documentation's installation page and let the user follow it from there.

The user will inform about their install procedure and the agent can verify afterwards.

---

## Refactor Rules

Do not refactor unless the task explicitly asks for it. A refactor must be:

- Scoped to one file unless otherwise approved
- Related to the requested task
- Behavior-preserving
- Explained before editing

Do not combine feature work and refactoring unless explicitly requested. If a refactor appears necessary before the feature can proceed, stop and report that as the next safest step.

---

## Refactor Pass Policy

When the user is performing an explicit layer-by-layer refactor, the agent must complete the clean change in the target file without leaving old code behind to keep the rest of the app buildable.

**The app is allowed to be broken between layer passes. That is the user's responsibility, not the agent's.**

The agent must:

- Make the full, clean change in the target file as requested
- State clearly in a **Side note** which other files will need to be updated as a result
- Do NOT retain old exports, compatibility shims, duplicate implementations, or deprecated code in the target file just to avoid breaking dependants

The agent must NOT:

- Leave behind old function signatures "just in case"
- Keep deprecated exports alongside new ones to avoid cross-file breakage
- Soften or partially apply a refactor to preserve build stability
- Stop or refuse because downstream files will temporarily break

**Side note format during a refactor pass:**

```md
Side note:

- This change breaks the following dependants that must be updated in a later pass:
  - `src/features/profile/controllers/useProfileController.ts` — imports the old `getUserProfile` signature
  - `src/features/profile/screens/ProfileScreen.tsx` — uses the removed prop `isLoading`
```

The user will work through the affected files. Do not hold the current file hostage to that future work.

---

## Architecture Challenge Rule

If the user asks for something inconsistent with the app architecture, do not blindly comply. Respond with:

```md
Rabbit hole:
...

Why this conflicts with the architecture:
...

Safer alternative:
...
```

Then wait for a narrower instruction, or complete only the safe portion.

---

## Safety Priority

The priority order is:

1. Preserve existing working behavior
2. Follow `architecture.md`
3. Satisfy the user's exact request
4. Keep the diff small
5. Stay within one file
6. Stay within one MVC layer
7. Stop early if the safe path is unclear

> Never prioritize appearing productive over keeping the codebase stable.
