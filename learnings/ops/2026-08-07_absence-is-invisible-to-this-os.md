# The OS notices bad runs, never missing ones

**Observed:** 2026-08-07 · Source: gap audit `loops/gap-audit/2026-08-07.md` (Sweep 4) + open-loops `2026-08-07.md` · Domain: ops

## The pattern

Every detector yourco has built watches for a **bad output**. None watches for **no output**.

Three instances, all live on the day this was written:

1. **`runtime/runtime-alarm.sh`** is well-reasoned — pure shell, no API calls, specifically so it survives a dead credit balance. But it alerts only when a loop's log shows `FAILED`. A loop that never runs writes no line, so the alarm hits `[ -z "$alerts" ] && echo "all clear"` and exits 0. Through ~8 days of a dark runtime (org API spend **$0.83 across 08-01→08-06** against an ~$8/day baseline) it reported all clear every hour.
2. **The open-loops loop** — the loop whose entire job is chasing stalled items — stopped on 07-29 and nothing chased *it*. The 9-day gap was found because the Founder asked a question, not because anything fired.
3. **The gap audit** — the review designed to catch what's absent — was itself absent for 56 days against a monthly cadence, and has no timer or prompt in `runtime/` at all.

The common shape: **the detector lives inside the thing it watches.** A loop cannot report its own silence; a credit-funded alarm cannot outlive the credits; a review with no scheduler cannot notice it wasn't run.

## Why it keeps happening

A failure produces an artifact — a log line, a stack trace, a red badge — and artifacts are what this OS is excellent at processing. An absence produces nothing, and nothing is indistinguishable from "fine" to every surface we've built. So the OS is not merely bad at noticing absence; **it actively renders absence as health.**

The second-order version: `learnings/ops/2026-07-28_loop-liveness-blindspot.md` already recorded this and it recurred anyway — because that learning is read at Step 0 *by loops*, and a loop that isn't running doesn't read its Step 0.

## How to apply

- **When building any watcher, state its blind spot in the file.** "This catches X" is half a spec; "this cannot catch Y" is the half that matters. `runtime-alarm.sh` documents beautifully why it uses no API and never says it can't see a loop that simply stopped.
- **Prefer freshness checks to failure checks.** "Last artifact is N days old against an expected cadence of M" catches both failure *and* silence. Failure checks catch only one.
- **Put the liveness indicator somewhere the runtime cannot switch off.** Anything that depends on the runtime being alive to report the runtime being alive is circular. Two valid answers: an off-box heartbeat that expects a signal and shouts on its absence (still unbuilt, still unassigned), or a human-visible staleness readout computed from committed artifacts — **built 2026-08-07 as the System lane of The Board** (`dashboard/board.py`), which ages every sanctioned loop against its cadence and shows a per-source freshness strip.
- **Never treat silence as clearing evidence.** Same rule as [[2026-07-07_checkbox-is-not-clearing-evidence]], one level up: no failure mail is not a success receipt, and no alert is not an all-clear. Canva cleared on 08-07 because a *receipt* was found; Descript stayed open because 21 days of nothing is not proof of anything.
- **When a function has no DRI, expect exactly this failure.** "Is the OS alive" is owned by *"Kemba/platform (the Founder holds until built)"* — a placeholder that has held for two months, across three outages. Every other function has a real owner and none of them died silently.

## Related

- [[2026-07-28_loop-liveness-blindspot]] — the first statement of this; recurred because loops read learnings and dead loops don't
- [[2026-06-18_runtime-silent-credit-death]] — occurrence #1 of the credit vector
- [[2026-07-10_host-billing-is-a-runtime-death-vector]] — occurrence #2, the host variant
- [[2026-07-07_checkbox-is-not-clearing-evidence]] — the same epistemics, applied to task state
- [[2026-07-06_cross-session-drift]] — the sibling pattern: facts rot in the places nobody re-reads

Triggers: loop:watchdog, loop:gap-audit, agent:atlas, missing run, absence, nothing happened, detecting what did not fire
