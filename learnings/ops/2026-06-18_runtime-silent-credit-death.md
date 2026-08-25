# Runtime died silently for 3 days on a depleted Anthropic credit balance

**Date:** 2026-06-18 · **Area:** ops / runtime reliability

## What happened
The VPS runtime ran clean through Mon 2026-06-15. Every scheduled loop from 2026-06-16 on failed instantly with `api_error_status: 400 — "Credit balance is too low"` → `FAILED (exit 1)`. The systemd timers fired perfectly on schedule; the Anthropic API account was simply out of credits. It went **unnoticed for 3 days** — surfaced only because the Founder happened to ask why his inbox wasn't being triaged.

## Why it went unnoticed (the real lesson)
The Claude-based health-watchdog (`processes/loops/watchdog.md`) runs on the **same Anthropic credits** as every other loop. When the balance hit zero, the watchdog died too — so the one thing meant to catch failures couldn't run. The only signal was the absence of the Monday heartbeat Slack post, and no human caught the absence.

> **A monitor that shares its target's root-cause failure can't report that failure.** A Claude watchdog can catch one stalled loop; it cannot catch a platform-wide credit/billing/auth death that takes the watchdog down with it.

## Fixes applied (this session)
1. **API-independent alarm** — `runtime/runtime-alarm.sh` + `yourco-runtime-alarm.timer` (hourly). Pure shell + curl: greps `loops/_runtime/*.log` for the latest run per loop, and on a FAILED run (incl. "Credit balance is too low") posts to a Slack incoming webhook. **Zero Anthropic API calls → survives a dead balance.** Self-checks (prints, sends nothing) if `runtime/.alarm.env` has no webhook.
2. **Daily watchdog** — the Claude watchdog moved from Monday-only to daily, so a single daily-loop stall is caught within ~1 day instead of up to 6 (still can't catch a credit death — that's what fix #1 is for).
3. **Anthropic credit auto-reload** — the Founder enables it in console.anthropic.com (the durable prevention; topped up 2026-06-18).

## Feed-forward
- For "is the runtime alive?" trust the **shell alarm**, not just the Claude watchdog.
- If credits lapse again: the alarm pings Slack within the hour → top up → the next scheduled run clears it automatically (`Persistent=true` catches up the missed slot).
- **Design rule for any future monitor:** it must not depend on the thing it monitors (no shared credits, key, host, or network path).

Triggers: loop:watchdog, agent:kemba, agent:atlas, runtime dark, credit balance, liveness, silent failure
