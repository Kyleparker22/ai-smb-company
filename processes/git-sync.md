# Git Sync — Keeping the OS Backed Up

**Repo:** https://github.com/founder22/yourco-os (private)
**What's tracked:** the whole workspace except secrets (see `.gitignore`: `.env`, `*.key`, `.DS_Store`, `**/secrets*`, `node_modules/`).

This SOP keeps the YourCo OS mirrored to GitHub so the workspace survives a laptop loss and has version history. This is a **backup**, not the always-on runtime — that headless git-synced workspace is still to be built (`decisions/2026-06-09_always-on-runtime.md`).

---

## Manual sync (anytime)

From the workspace root:

```bash
./processes/git-sync.sh
```

Or by hand:

```bash
git add -A && git commit -m "OS sync — <what changed>" && git push
```

If nothing changed, the script exits clean (no empty commit).

## Automated daily sync

A scheduled task runs `git-sync.sh` once a day and pushes a timestamped commit.

> **Runtime caveat:** scheduled tasks only fire while the Cowork desktop session is open. Until the always-on runtime exists, treat the daily auto-commit as best-effort — run the manual sync after any substantial work session you want guaranteed backed up.

## Before pushing — secret check

The `.gitignore` blocks the obvious secret patterns, but it's not a guarantee. Before a push that adds new file types, glance at `git status` for anything holding a live API key, token, or credential. `finance/token_spend.md` is a cost-tracking doc, not a secret — safe to track.

## One-time setup (already done 2026-06-09)

- `gh repo create yourco-os --private --source=. --push` created the repo, wired `origin`, pushed `main`.
- Auth: `gh auth status` (logged in as founder22, `repo` scope).
