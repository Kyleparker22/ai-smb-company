#!/usr/bin/env bash
# YourCo always-on loop runner.
#
# Usage:  runtime/run-loop.sh <loop-name>
#   Reads runtime/prompts/<loop-name>.md as the agent prompt, runs it headless via
#   Claude Code, then commits + pushes any artifacts the loop produced.
#
# Invoked by the systemd timers in runtime/systemd/. The approval gate is NOT here —
# it lives in the host's ~/.claude/settings.json permissions (see runtime/README.md),
# so every loop self-gates (drafts/posts allowed; send/delete/pay denied).
set -uo pipefail

LOOP="${1:?usage: runtime/run-loop.sh <loop-name>}"
REPO="$HOME/yourco-os"

# Global pause switch (host-local, gitignored). If runtime/.paused exists, EVERY loop is a no-op —
# checked before env/lock/pull/model so a paused run costs ~zero credits and makes no Slack post.
#   Pause:  touch  ~/yourco-os/runtime/.paused
#   Resume: rm     ~/yourco-os/runtime/.paused
# Exits 0 with a PAUSED (not FAILED) log line, so runtime-alarm.sh does not false-trigger.
if [ -f "$REPO/runtime/.paused" ]; then
  mkdir -p "$REPO/loops/_runtime"
  echo "[$(date -u +%FT%TZ)] ${LOOP} PAUSED (runtime/.paused present) — skipped, no model call" \
    >> "$REPO/loops/_runtime/${LOOP}.log"
  exit 0
fi

# Secrets (ANTHROPIC_API_KEY, SLACK_BOT_TOKEN, ...) + node toolchain (claude/npx via nvm)
# shellcheck disable=SC1090,SC1091
source "$HOME/.yourco/env"
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"

cd "$REPO" || { echo "no repo at $REPO" >&2; exit 1; }

PROMPT_FILE="runtime/prompts/${LOOP}.md"
[ -f "$PROMPT_FILE" ] || { echo "no prompt file: $PROMPT_FILE" >&2; exit 1; }

mkdir -p loops/_runtime
LOG="loops/_runtime/${LOOP}.log"
TS="$(date -u +%FT%TZ)"

# Serialize the WHOLE run (pull → claude → commit → push) across all loops on this host, so two
# loops can't stash/commit each other's in-flight work or race the index (bug-hunt H2/medium).
# shellcheck disable=SC1090,SC1091
source "$REPO/runtime/repo-lock.sh"
if ! repo_lock_acquire; then
  echo "[${TS}] ${LOOP} FAILED (repo lock timeout)" >> "$LOG"
  echo "run-loop: ${LOOP} could not acquire repo lock" >&2
  exit 1
fi

# Pull current state before running so the loop reads the latest artifacts.
# Self-heal a rebase left wedged by a prior conflicted run FIRST — otherwise HEAD is detached
# and the commit below lands on a detached HEAD (orphaned, un-pushable; the documented incident).
if [ -d .git/rebase-merge ] || [ -d .git/rebase-apply ]; then
  git rebase --abort >/dev/null 2>&1 || true
  echo "[${TS}] ${LOOP} recovered a wedged rebase (aborted)" >> "$LOG"
fi
# Pull without swallowing failure: on conflict, abort back to a clean branch and log FAILED so
# runtime-alarm.sh fires. We stay on-branch (never detached), so the commit below is always safe;
# the push may then be rejected (behind remote) and that too is logged loudly.
if ! git pull --rebase --autostash >/dev/null 2>&1; then
  git rebase --abort >/dev/null 2>&1 || true
  echo "[${TS}] ${LOOP} FAILED (git pull rebase conflict — resolve on host)" >&2
  echo "[${TS}] ${LOOP} FAILED (git pull rebase conflict)" >> "$LOG"
fi

# Optional model pin: set MODEL_PIN in ~/.yourco/env to pin every loop to one model
# (e.g. MODEL_PIN=claude-fable-5). Empty/unset = the CLI default; upgrades ride the
# CLI update on this host. Log a decisions/ entry when changing it.
MODEL_ARGS=()
[ -n "${MODEL_PIN:-}" ] && MODEL_ARGS=(--model "$MODEL_PIN")

echo "===== ${LOOP} :: ${TS} =====" >> "$LOG"
# The result JSON goes to its own file first, not straight into the log. It carries
# total_cost_usd + usage — the only per-loop cost data this business generates — and $LOG is
# gitignored and host-local, so appending it there was throwing the numbers away ~20x/day.
# ---- Step 0, run in the WRAPPER because the session cannot run it -------------------------
# The loop contract tells every prompt to run `learning_triggers.py` at Step 0. The host approval
# gate denies Bash, so inside `claude -p` that command does not exist — and the loops adapted by
# hand-globbing their own domain folder. That fallback silently reopened the exact gap `Triggers:`
# was built to close: measured 2026-08-24, 57 of 90 trigger hits across the 26 loops (63%) come
# from a domain the loop's own prompt never names, including both entries tagged `always`.
#
# So it runs HERE instead, before the session, and the result is prepended to the prompt — the same
# pattern that already lets `run_journal --record` survive the gate. No posture change: this is a
# read-only retrieval over files the agent may read anyway.
#
# Non-fatal by construction. If retrieval fails the loop still runs on the prompt alone, exactly as
# it does today — instrumentation must never be able to turn a good run into a no run.
STEP0="$(python3 runtime/learning_triggers.py --loop "$LOOP" --max 8 2>>"$LOG")" || STEP0=""

# The anti-library, same wall, DIFFERENT fix. The contract also tells the run to clear
# `rejections.py --check "<the idea>"` before proposing anything — and that one cannot be
# pre-computed, because the idea does not exist until mid-run. What CAN be handed over is the whole
# list: it is ~1.9KB for 7 entries, so the run checks against a LIVE list by reading instead of a
# remembered one. That distinction is not theoretical — the 08-17 and 08-18 initiative runs both
# hand-listed 7 rejection files when there were 8, and the one they missed was directly on point
# (learnings/ops/2026-08-19_anti-library-hand-check-needs-glob.md).
#
# Injected for EVERY loop, not a curated list of "the idea loops": that list would be one more thing
# to keep in step, and a loop that proposes nothing simply ignores this block.
ANTILIB="$(python3 runtime/rejections.py --list 2>>"$LOG")" || ANTILIB=""

PROMPT_TEXT="$(cat "$PROMPT_FILE")"
PREFIX=""
if [ -n "$STEP0" ]; then
  PREFIX="Step 0 (retrieved for you by the runtime wrapper — the Bash tool is gate-denied in this
session, so treat the list below AS the output of \`runtime/learning_triggers.py --loop ${LOOP}\`
and apply it per the loop contract. It is trigger-ranked across ALL domains, not just the ones this
prompt names, which is the point):

${STEP0}"
  echo "[${TS}] ${LOOP} step0 injected ($(printf '%s' "$STEP0" | grep -c '^  • ') learning(s))" >> "$LOG"
else
  echo "[${TS}] ${LOOP} step0 retrieval returned nothing (non-fatal)" >> "$LOG"
fi
if [ -n "$ANTILIB" ]; then
  PREFIX="${PREFIX}

THE ANTI-LIBRARY (live, as of this run — again because Bash is denied here). If and only if this run
PROPOSES something, check it against the list below and put the contract's verdict line in your
artifact: either \`not previously rejected\`, or \`previously rejected <date> (<file>) because
<reason>; what has changed since is <X>\`. Re-proposing is expected — it just has to carry evidence.
Do NOT rely on a list from a previous run's artifact; this one is current:

${ANTILIB}"
  echo "[${TS}] ${LOOP} anti-library injected ($(printf '%s' "$ANTILIB" | grep -cE '^[[:space:]]+\[') entries)" >> "$LOG"
else
  echo "[${TS}] ${LOOP} anti-library list returned nothing (non-fatal)" >> "$LOG"
fi
# Injected material goes AFTER the stable prompt, not before it (changed 2026-08-24).
#
# It was prepended when this was written earlier the same day, which is the documented anti-pattern:
# a prompt's KV-cache is valid only up to the first token that differs, so putting content that
# changes run-to-run — retrieved learnings, the anti-library — at the FRONT invalidates the cache for
# everything after it, i.e. the whole prompt. Manus published the numbers on this
# (decisions/2026-07-05_tool-triage.md §Addendum 2026-08-24): cached input is roughly a tenth the
# price of uncached on the same model.
#
# Honest scope: whether these headless runs are hitting a cross-run cache at all is unmeasured, so
# the saving is not claimed — but the ordering is wrong either way and costs nothing to fix.
# It is also better on a second axis: Manus found that material near the END of the context sits in
# the model's recent attention span, which is exactly what you want for "apply this before working".
# The `Step 0 — feed-forward` contract is about when the agent ACTS, not where the text sits.
if [ -n "$PREFIX" ]; then
  PROMPT_TEXT="$(printf '%s\n\n---\n\n%s' "$PROMPT_TEXT" "$PREFIX")"
fi

RUN_JSON="$(mktemp -t yourco-run.XXXXXX)"
if claude -p "$PROMPT_TEXT" "${MODEL_ARGS[@]}" --output-format json > "$RUN_JSON" 2>> "$LOG"; then
  echo "[${TS}] ${LOOP} OK" >> "$LOG"
else
  echo "[${TS}] ${LOOP} FAILED (exit $?)" >> "$LOG"
fi
cat "$RUN_JSON" >> "$LOG"   # log behaviour unchanged — the JSON still lands here too
# Record it in the committed run journal. Non-fatal by design: a journal failure must never
# turn a good loop run into a failed one (that would make the instrumentation load-bearing).
python3 runtime/run_journal.py --record --loop "$LOOP" --file "$RUN_JSON" >> "$LOG" 2>&1 \
  || echo "[${TS}] ${LOOP} run-journal record failed (non-fatal)" >> "$LOG"
rm -f "$RUN_JSON"

# Persist + sync whatever the loop wrote (artifacts). Logs are gitignored.
# A failed push MUST land in the log as "<loop> FAILED" — that exact shape is
# what runtime-alarm.sh greps; a silent push failure strands artifacts on this host.
git add -A >/dev/null 2>&1 || true
git commit -q -m "loop:${LOOP} ${TS}" >/dev/null 2>&1 || true
git push -q >/dev/null 2>&1
PUSH_RC=$?
if [ "$PUSH_RC" -ne 0 ]; then
  echo "[${TS}] ${LOOP} FAILED (git push, exit ${PUSH_RC})" >> "$LOG"
  echo "run-loop: ${LOOP} git push failed (exit ${PUSH_RC})" >&2
fi
