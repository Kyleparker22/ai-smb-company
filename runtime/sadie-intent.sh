#!/usr/bin/env bash
# Sadie's scheduled intent sweep — pulls the configured Google Alerts + News feeds, ranks
# prospects-first, posts a digest to #yourco-sadie, and commits the board. Run by the
# yourco-sadie-intent systemd timer (NOT via claude -p: deterministic + needs the bot token).
# Mirrors runtime/run-loop.sh's env bootstrap so the script + any tools resolve.
set -uo pipefail
REPO="$HOME/yourco-os"

# Global pause switch (same flag as runtime/run-loop.sh): if runtime/.paused exists, skip — go fully quiet.
if [ -f "$REPO/runtime/.paused" ]; then
  mkdir -p "$REPO/loops/_runtime"
  echo "[$(date -u +%FT%TZ)] sadie-intent PAUSED (runtime/.paused present) — skipped" \
    >> "$REPO/loops/_runtime/sadie-intent.log"
  exit 0
fi

# Secrets (SLACK_BOT_TOKEN, YOUTUBE_API_KEY, …)
# shellcheck disable=SC1090,SC1091
source "$HOME/.yourco/env" 2>/dev/null || true
cd "$REPO" || { echo "no repo at $REPO" >&2; exit 1; }

mkdir -p loops/_runtime
TS="$(date -u +%FT%TZ)"
# Serialize with the other loops on this host (shared clone) — same lock as runtime/run-loop.sh.
# shellcheck disable=SC1090,SC1091
source "$REPO/runtime/repo-lock.sh"
if ! repo_lock_acquire; then
  echo "[${TS}] sadie-intent FAILED (repo lock timeout)" >> loops/_runtime/sadie-intent.log
  exit 1
fi
# Self-heal a wedged rebase, then pull without swallowing — mirrors runtime/run-loop.sh so a conflict
# can't leave HEAD detached (which would orphan this loop's commit).
if [ -d .git/rebase-merge ] || [ -d .git/rebase-apply ]; then
  git rebase --abort >/dev/null 2>&1 || true
  echo "[${TS}] sadie-intent recovered a wedged rebase (aborted)" >> loops/_runtime/sadie-intent.log
fi
if ! git pull --rebase --autostash >/dev/null 2>&1; then
  git rebase --abort >/dev/null 2>&1 || true
  echo "[${TS}] sadie-intent FAILED (git pull rebase conflict)" >> loops/_runtime/sadie-intent.log
fi

echo "===== sadie-intent :: ${TS} =====" >> loops/_runtime/sadie-intent.log
if python3 runtime/sadie_intent_loop.py >> loops/_runtime/sadie-intent.log 2>&1; then
  echo "[${TS}] sadie-intent OK" >> loops/_runtime/sadie-intent.log
else
  echo "[${TS}] sadie-intent FAILED (exit $?)" >> loops/_runtime/sadie-intent.log
fi

git add -A >/dev/null 2>&1 || true
git commit -q -m "loop:sadie-intent ${TS}" >/dev/null 2>&1 || true
# A silent push failure strands the board on this host; log the exact "FAILED" shape that
# runtime-alarm.sh greps (same as runtime/run-loop.sh) so the watchdog catches it.
git push -q >/dev/null 2>&1
PUSH_RC=$?
if [ "$PUSH_RC" -ne 0 ]; then
  echo "[${TS}] sadie-intent FAILED (git push, exit ${PUSH_RC})" >> loops/_runtime/sadie-intent.log
  echo "sadie-intent: git push failed (exit ${PUSH_RC})" >&2
fi
