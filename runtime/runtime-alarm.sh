#!/usr/bin/env bash
# yourco runtime alarm — API-INDEPENDENT failure + credit watchdog.
#
# Why this exists: the Claude-based watchdog (loops/watchdog.md) runs on the
# same Anthropic credits as every other loop. When the balance hits zero, ALL
# loops — including the watchdog — die instantly, so nothing can alert. That's
# exactly how the runtime went silently dead for 3 days (2026-06-16..18).
#
# This is pure shell + curl: zero Anthropic API calls, so it SURVIVES a dead
# credit balance and is the one thing that can still raise the flag. It scans
# each loop's run log for the most recent status; if the latest run FAILED
# (incl. "Credit balance is too low"), it posts to Slack via an incoming
# webhook. A state file prevents re-alerting the same failed run.
#
# Setup on the host (claudeops): create runtime/.alarm.env (gitignored) with:
#   SLACK_ALARM_WEBHOOK=https://hooks.slack.com/services/XXX/YYY/ZZZ
# No webhook -> self-check mode (prints what it WOULD post, sends nothing).
# Runs hourly via systemd (yourco-runtime-alarm.timer). NOT a `claude` run, so
# it is unaffected by the ~/.claude approval gate (no API, no model).

set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOGDIR="$ROOT/loops/_runtime"
STATE="$LOGDIR/.alarm-state"          # gitignored (loops/_runtime/ is in .gitignore)
ENVF="$ROOT/runtime/.alarm.env"

[ -f "$ENVF" ] && . "$ENVF"
WEBHOOK="${SLACK_ALARM_WEBHOOK:-}"

[ -d "$LOGDIR" ] || { echo "[alarm] no $LOGDIR yet — nothing to check."; exit 0; }
touch "$STATE" 2>/dev/null || true

alerts=""
credit=0
newkeys=""   # collected here; persisted to $STATE ONLY after the Slack post succeeds (see below).
             # Writing keys before the post would permanently silence an alert whose post failed —
             # the very failure mode this alarm exists to prevent.
for log in "$LOGDIR"/*.log; do
  [ -e "$log" ] || continue
  loop="$(basename "$log" .log)"
  # status lines look like:  [2026-06-18T10:45:06Z] inbox-triage FAILED (exit 1)
  last="$(grep -E "\] ${loop} (OK|FAILED)" "$log" | tail -1)"
  [ -z "$last" ] && continue
  case "$last" in
    *FAILED*)
      ts="$(printf '%s' "$last" | sed -n 's/^\[\([^]]*\)\].*/\1/p')"
      key="${loop}@${ts}"
      grep -qxF "$key" "$STATE" 2>/dev/null && continue   # already alerted this run
      if tail -40 "$log" | grep -qi "Credit balance is too low"; then credit=1; fi
      alerts="${alerts:+$alerts, }${loop} (FAILED ${ts})"
      newkeys="${newkeys}${key}"$'\n'
      ;;
  esac
done

[ -z "$alerts" ] && { echo "[alarm] all clear — no new FAILED runs."; exit 0; }

msg=":rotating_light: Runtime alarm — failing loop(s): ${alerts}."
if [ "$credit" -eq 1 ]; then
  msg="${msg}  Cause: Anthropic credit balance too low — the WHOLE runtime is down until you top up at console.anthropic.com (enable auto-reload)."
fi
msg="${msg}  (Shell alarm, no API; clears on the next OK run.)"

if [ -z "$WEBHOOK" ]; then
  echo "[alarm] WOULD POST: $msg"
  echo "[alarm] no SLACK_ALARM_WEBHOOK in $ENVF — self-check only, nothing sent."
  # Do NOT burn the dedup keys here: with no webhook the alert was never delivered, so a real
  # failure that occurred before the webhook is configured must still alert once it is.
  exit 0
fi

# msg contains no double-quotes/backslashes/newlines, so this inline JSON is safe.
if curl -fsS -X POST -H 'Content-type: application/json' \
     --data "{\"text\":\"${msg}\"}" "$WEBHOOK" >/dev/null 2>&1; then
  # Persist dedup keys ONLY now that the post is confirmed delivered.
  printf '%b' "$newkeys" >> "$STATE"
  echo "[alarm] posted to Slack."
else
  echo "[alarm] Slack post FAILED (webhook unreachable) — keys NOT recorded, will retry next run."
  exit 1
fi
