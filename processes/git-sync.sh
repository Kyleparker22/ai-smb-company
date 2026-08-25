#!/usr/bin/env bash
# YourCo OS → GitHub FULL BACKUP sync. `git add -A` + commit + push everything uncommitted.
#
# This is the catch-all safety net — it intentionally sweeps the WHOLE working tree. Because of
# that, do NOT use it to commit one session's specific work: in a shared clone it will also grab
# any OTHER concurrent session's uncommitted files and bury them under this commit's message.
# To commit your own work, use `runtime/commit-scoped.sh "msg" <paths>` (scoped + locked) instead.
# Safe to run anytime: exits clean with no commit if nothing changed.
set -euo pipefail

cd "$(dirname "$0")/.."
REPO="$(pwd)"
# shellcheck disable=SC1090,SC1091
source "$REPO/runtime/repo-lock.sh"
repo_lock_acquire || { echo "git-sync: could not acquire repo lock — another writer is active." >&2; exit 1; }

if [[ -z "$(git status --porcelain)" ]]; then
  echo "git-sync: nothing to commit, working tree clean."
  exit 0
fi

# Self-heal the CRM static mirror (crm/data.js) from its source of truth (crm/data.json) before adding.
# data.js is a *generated* file kept tracked only as the offline fallback (crm/index.html → window.CRM_DATA).
# Regenerating it here guarantees the committed mirror always matches data.json — so a stale/test-polluted
# mirror (e.g. from an ad-hoc CRM write during testing) can never be committed. Non-fatal if it can't run.
if [[ -f crm/data.json ]]; then
  python3 -c "import sys; sys.path.insert(0,'dashboard'); import json, melanie; melanie.write_mirror(json.load(open('crm/data.json')))" 2>/dev/null || true
fi

# GUARD: refuse to sweep in a nested git repository (added 2026-08-16).
# On 2026-08-11 this script's `add -A` committed a stray 346MB clone of yourco-os into yourco-os as an
# orphan gitlink — 924 duplicate .md files that doubled every repo-wide search and handed fresh clones a
# mystery empty directory. `add -A` cannot tell a stray clone from a real file, so the check happens here.
# A nested repo is never intentional in this tree; if one is ever wanted it needs a real submodule + a
# .gitmodules entry, which this guard deliberately does not try to guess at.
NESTED="$(find . -mindepth 2 -name .git -maxdepth 4 -not -path './.git/*' -not -path './.claude/worktrees/*' 2>/dev/null || true)"
if [[ -n "$NESTED" ]]; then
  echo "git-sync: REFUSING TO COMMIT — nested git repo(s) found inside the working tree:" >&2
  echo "$NESTED" | sed 's|/\.git$||' | sed 's/^/  /' >&2
  echo "git-sync: a stray clone here becomes an orphan gitlink and duplicates the whole repo." >&2
  echo "git-sync: remove it (or add it to .gitignore), then re-run." >&2
  exit 1
fi

git add -A

# GUARD: never commit a gitlink. Belt-and-braces behind the check above — mode 160000 in the index is
# the exact shape the 08-11 incident took, and it is cheaper to catch here than to unpick from history.
if git diff --cached --raw | awk '{print $2}' | grep -q '^160000$'; then
  echo "git-sync: REFUSING TO COMMIT — a gitlink (mode 160000) is staged:" >&2
  git diff --cached --raw | awk '$2=="160000"{print "  " $NF}' >&2
  git reset -q
  exit 1
fi

git commit -m "OS sync — ${1:-automated daily backup ($(date +%Y-%m-%d))}"

# The VPS runtime pushes to origin/main dozens of times a day. Without pulling first, this
# push is a non-fast-forward rejection whenever the VPS pushed since our last pull — set -e
# then aborts with the commit stranded, and trees diverge further each day (the documented
# two-writer conflicts). Rebase our commit onto the remote before pushing; surface a real
# conflict loudly instead of silently corrupting a same-day loops/ artifact.
if ! git pull --rebase --autostash origin main; then
  git rebase --abort 2>/dev/null || true
  echo "git-sync: rebase conflict against origin/main — resolve manually (git pull --rebase), then re-run." >&2
  exit 1
fi

git push origin main
echo "git-sync: pushed to origin/main."
