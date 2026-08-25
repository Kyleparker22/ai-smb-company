#!/usr/bin/env bash
# Portable advisory repo lock — serializes git writers that share ONE working tree.
#
# Why not flock: macOS (where the Mac backup + Cowork sessions run) ships no `flock`. A `mkdir`
# is atomic on every POSIX fs, so it's the portable mutex. Scope: this coordinates writers on the
# SAME machine/clone (concurrent Cowork sessions on the Mac; concurrent loops on the VPS). It does
# NOT span Mac↔VPS — those are separate clones and coordinate via pull --rebase before push.
#
# Usage:  source "$(dirname "$0")/repo-lock.sh"   # after REPO is set (defaults to git root)
#         repo_lock_acquire || exit 1              # auto-releases on EXIT
# Env:    REPO_LOCK_WAIT  max seconds to wait for the lock (default 300)
#         REPO_LOCK_STALE seconds after which a held lock is presumed crashed + stolen (default 900)

: "${REPO:=$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
REPO_LOCK_DIR="$REPO/.repo-sync.lock"   # gitignored

_repo_lock_mtime() {  # epoch mtime of $1, BSD (macOS) then GNU (Linux)
  stat -f %m "$1" 2>/dev/null || stat -c %Y "$1" 2>/dev/null || echo 0
}

repo_lock_acquire() {
  local waited=0 max="${REPO_LOCK_WAIT:-300}" stale="${REPO_LOCK_STALE:-900}"
  while ! mkdir "$REPO_LOCK_DIR" 2>/dev/null; do
    # Steal a stale lock (holder crashed without releasing): dir older than $stale seconds.
    if [ -d "$REPO_LOCK_DIR" ]; then
      local age=$(( $(date +%s) - $(_repo_lock_mtime "$REPO_LOCK_DIR") ))
      if [ "$age" -gt "$stale" ]; then
        rm -f "$REPO_LOCK_DIR/pid" 2>/dev/null || true
        rmdir "$REPO_LOCK_DIR" 2>/dev/null || true
        continue
      fi
    fi
    waited=$((waited + 1))
    if [ "$waited" -ge "$max" ]; then
      echo "repo-lock: timed out after ${max}s waiting for $REPO_LOCK_DIR" >&2
      return 1
    fi
    sleep 1
  done
  echo "$$" > "$REPO_LOCK_DIR/pid" 2>/dev/null || true
  trap 'repo_lock_release' EXIT
  return 0
}

repo_lock_release() {
  rm -f "$REPO_LOCK_DIR/pid" 2>/dev/null || true
  rmdir "$REPO_LOCK_DIR" 2>/dev/null || true
}
