## 26. Branch Model

**Work branch** → **integration** → **release**

| Branch | Purpose | Name pattern |
|---|---|---|
| Work | One epic or triage slug | `epic/014-slug` or `fix/slug` |
| Integration | Accumulates merged work; RC cuts from here | `dev` |
| Release | Stable, tagged releases | `master` |

Rules:
- A push to `dev` cuts a release candidate (pre-release tag `rc-<sha>`).
- A release is cut from `master` via manual workflow dispatch (`major` / `minor` / `patch`).
- A work branch is named for its epic (`epic/014-slug`) or its triage slug (`fix/slug`).
- A work branch is deleted when it merges to `dev`.
- The only human gate in the system is confirming a release candidate before it
  is promoted to `master`.

`branch-lifecycle` reads these names from git config:

```bash
git config branch.integration  # dev
git config branch.release       # master
git config gate.testcmd         # pytest -q
```
