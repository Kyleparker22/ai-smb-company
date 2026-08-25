#!/usr/bin/env bash
# Commit ONLY the paths you name — never `git add -A`. This is how a session (Cowork or a loop)
# commits its own work in a shared clone WITHOUT sweeping another session's uncommitted files into
# its commit (the "buried under an OS-sync commit" problem). Holds the repo lock for the whole
# stage→commit→push so a concurrent writer can't interleave, and pulls --rebase before pushing.
#
# Usage:  runtime/commit-scoped.sh "commit message" <path> [<path> ...]
# Example: runtime/commit-scoped.sh "fix: installation filter" clients/sample-client/prototype/agent.py
#
# Exit 0 on commit+push (or "nothing staged" no-op), non-zero on lock timeout / push failure.
set -uo pipefail

MSG="${1:?usage: commit-scoped.sh \"message\" <path>...}"
shift
[ "$#" -ge 1 ] || { echo "commit-scoped: name at least one path to commit" >&2; exit 2; }

REPO="$(git rev-parse --show-toplevel 2>/dev/null)" || { echo "commit-scoped: not in a git repo" >&2; exit 1; }
cd "$REPO" || exit 1
# shellcheck disable=SC1090,SC1091
source "$REPO/runtime/repo-lock.sh"
repo_lock_acquire || exit 1

# Stage exactly the named paths (nothing else in the working tree is touched).
#
# `git add` is all-or-nothing: ONE pathspec that matches nothing makes it fail and stage
# NONE of the others. That failure used to be near-silent — the script carried on and
# committed whatever happened to be staged already, printing its usual success line. On
# 2026-08-23 that shipped a commit containing 1 file instead of 8, twice, because a path
# passed to it had just been `git mv`d and no longer existed. Check each path first and
# refuse loudly, naming the offender.
_missing=()
for _p in "$@"; do
  if [ ! -e "$_p" ] && ! git ls-files --error-unmatch -- "$_p" >/dev/null 2>&1; then
    _missing+=("$_p")
  fi
done
if [ ${#_missing[@]} -gt 0 ]; then
  echo "commit-scoped: these path(s) do not exist and are not tracked:" >&2
  printf '  %s\n' "${_missing[@]}" >&2
  echo "commit-scoped: NOTHING was committed. Drop them (a git-mv'd path is already staged" >&2
  echo "               by the mv itself and must not be listed again) and re-run." >&2
  repo_lock_release 2>/dev/null || true
  exit 1
fi

git add -- "$@" || {
  echo "commit-scoped: git add failed — nothing committed." >&2
  repo_lock_release 2>/dev/null || true
  exit 1
}
if git diff --cached --quiet; then
  echo "commit-scoped: nothing staged for the given paths — no commit."
  exit 0
fi

git commit -q -m "$MSG" || { echo "commit-scoped: commit failed" >&2; exit 1; }

# Sync with the remote before pushing (same-branch two-writer safety).
if ! git pull --rebase --autostash --quiet; then
  git rebase --abort 2>/dev/null || true
  echo "commit-scoped: committed locally, but pull --rebase hit a conflict — resolve then push." >&2
  exit 1
fi
if git push --quiet; then
  echo "commit-scoped: committed + pushed ($(git rev-parse --short HEAD)) — $* "
else
  echo "commit-scoped: committed locally but push failed — retry 'git push'." >&2
  exit 1
fi
