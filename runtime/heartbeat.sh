#!/usr/bin/env bash
# yourco runtime heartbeat — the one instrument that can measure its own absence.
#
# WHY THIS EXISTS. Kemba owned "runtime uptime (%)" and nothing in the repo measured availability.
# It is also precondition #1 of the client SLA (processes/contracts/sla.md §7), whose §6 says an
# unmeasured month reads as a MISS — so the absence of this file was a standing failure, not a gap.
#
# WHY A HEARTBEAT AND NOT A LOG. A log can only record what happened while the box was working. This
# writes one line every INTERVAL_MIN minutes and nothing else, so **uptime is computed from
# expected-vs-received, never from what the file says**: a missing line IS the outage. Same principle
# the OS already learned the hard way — learnings/ops/2026-08-07_absence-is-invisible-to-this-os.
#
# WHY PURE SHELL. Zero Anthropic API calls and no `claude` run, so it survives a dead credit balance
# — which is how the runtime actually went dark for three days (2026-06-16..18) and again in July.
# The one thing that must keep working during an outage cannot depend on the thing that is out.
#
# WHY IT DOES NOT COMMIT. `runtime/run-loop.sh` already does `git add -A` under the repo lock after
# every loop, so beats ride along with the next run — no commit noise, no second timer, and no lock
# contention. The consequence is deliberate and stated in dashboard/uptime.py: this measures **the
# runtime working**, not the box having power. A box that is up while every loop is dead is not "up"
# in any sense that matters to an agent.
#
# Store: loops/_health/heartbeat.jsonl (COMMITTED — deliberately not loops/_runtime/, which is
# gitignored and is exactly why none of this was visible from the Mac).
#
# Install (host, the Founder):
#   sudo cp runtime/systemd/yourco-heartbeat.{service,timer} /etc/systemd/system/
#   sudo systemctl daemon-reload && sudo systemctl enable --now yourco-heartbeat.timer
# Self-check anywhere:  runtime/heartbeat.sh --dry-run
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/loops/_health/heartbeat.jsonl"
INTERVAL_MIN=15          # must match yourco-heartbeat.timer AND dashboard/uptime.py INTERVAL_MIN
DRY=0
[ "${1:-}" = "--dry-run" ] && DRY=1

ts="$(date -u +%FT%TZ)"

# Host uptime + boot, so a reboot is visible as a fact rather than inferred from a gap.
# Linux only, on purpose. The first version had a macOS fallback for --dry-run and its sed was
# greedy — it captured `usec` instead of `sec` and reported a 56-year uptime. Off /proc these are
# null: a dry run that prints an invented number teaches you to trust an invented number.
up_s=null; boot=""
if [ -r /proc/uptime ]; then
  up_s="$(cut -d. -f1 /proc/uptime)"
  boot="$(date -u -d "@$(( $(date +%s) - up_s ))" +%FT%TZ 2>/dev/null || echo "")"
fi

load1="$(uptime 2>/dev/null | sed -n 's/.*load average[s]*: \([0-9.]*\).*/\1/p')"
disk_pct="$(df -P "$ROOT" 2>/dev/null | awk 'NR==2{gsub("%","",$5); print $5}')"

# PAUSED is not DOWN. A deliberate pause is the runtime being available and idle; conflating the two
# would let a planned stand-down read as an outage and vice versa.
paused=false
[ -f "$ROOT/runtime/.paused" ] && paused=true

# systemd facts — the difference between "the box is down", "the timers are gone" and "the loops are
# failing", which is the diagnosis every past outage post-mortem had to guess at.
timers=0; failed=0
if command -v systemctl >/dev/null 2>&1; then
  timers="$(systemctl list-timers 'yourco-*' --no-legend --no-pager 2>/dev/null | grep -c . || echo 0)"
  failed="$(systemctl list-units 'yourco-*' --state=failed --no-legend --no-pager 2>/dev/null | grep -c . || echo 0)"
fi

head="$(cd "$ROOT" && git rev-parse --short HEAD 2>/dev/null || echo "")"

# Minutes since ANY loop last wrote a status line. loops/_runtime/ is host-local and gitignored, so
# this number is the only way that evidence ever reaches the repo.
last_loop_min=null
newest=0
for f in "$ROOT"/loops/_runtime/*.log; do
  [ -e "$f" ] || continue
  m="$(date -u -r "$f" +%s 2>/dev/null || stat -c %Y "$f" 2>/dev/null || echo 0)"
  [ "$m" -gt "$newest" ] && newest="$m"
done
[ "$newest" -gt 0 ] && last_loop_min=$(( ( $(date +%s) - newest ) / 60 ))

line="{\"ts\":\"${ts}\",\"interval_min\":${INTERVAL_MIN},\"boot\":\"${boot}\",\"up_s\":${up_s:-null}"
line="${line},\"paused\":${paused},\"timers\":${timers:-0},\"failed_units\":${failed:-0}"
line="${line},\"disk_pct\":${disk_pct:-null},\"load1\":${load1:-null}"
line="${line},\"head\":\"${head}\",\"last_loop_min\":${last_loop_min}}"

if [ "$DRY" -eq 1 ]; then
  printf '%s\n' "$line"
  echo "[dry-run] would append to $OUT" >&2
  exit 0
fi

mkdir -p "$(dirname "$OUT")"
# A single-line O_APPEND write is atomic, so a concurrent reader sees a whole line or none. No seq
# field: a shell writer cannot allocate one safely, so ordering is by `ts` and the reader says so.
printf '%s\n' "$line" >> "$OUT"

# ---- opportunistic sync ---------------------------------------------------------------------
# Beats normally ride along with the next loop's `git add -A`. But if NO loop runs — which is the
# case during the very outage this is meant to catch — nothing would reach the repo, and a real
# outage would be indistinguishable from "nothing has synced lately". So push on our own at most
# every SYNC_EVERY_H hours: ~4 commits a day, and staleness bounded to that.
#
# Never blocks and never fails. If the repo lock is held by a running loop we skip this cycle and
# try again next beat — instrumentation must not be able to make a good run into a failed one.
SYNC_EVERY_H=6
STAMP="$ROOT/loops/_health/.last-sync"
now="$(date +%s)"
last=0; [ -r "$STAMP" ] && last="$(cat "$STAMP" 2>/dev/null || echo 0)"
if [ $(( now - last )) -ge $(( SYNC_EVERY_H * 3600 )) ]; then
  # shellcheck disable=SC1090,SC1091
  if . "$ROOT/runtime/repo-lock.sh" 2>/dev/null && REPO_LOCK_WAIT=5 repo_lock_acquire 2>/dev/null; then
    (
      cd "$ROOT" || exit 0
      git add loops/_health >/dev/null 2>&1 || true
      git commit -q -m "heartbeat: ${ts}" >/dev/null 2>&1 || true
      git pull --rebase --autostash -q >/dev/null 2>&1 || true
      git push -q >/dev/null 2>&1 || true
    )
    echo "$now" > "$STAMP" 2>/dev/null || true
    repo_lock_release 2>/dev/null || true
  fi
fi
