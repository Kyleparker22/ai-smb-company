---
name: loop-liveness-blindspot
description: A runtime loop that silently stops emitting its artifact is invisible — no watchdog checks per-loop artifact freshness, so a multi-day silent stop only surfaces when a human notices missing files.
metadata:
  type: project
---

The inbox-triage desk loop stopped emitting its daily artifact from ~2026-07-16 through 2026-07-27 (prior artifact 07-15, next 07-28 — a 13-day gap). The runtime VPS was only offline 07-23 → 07-27 (host billing lapse, `[[2026-07-10_host-billing-is-a-runtime-death-vector]]`), which accounts for 5 of those days but **not** the 07-16 → 07-22 stretch when the box was up (payments failing, but not yet suspended). So the loop was silent for ~8 days *before* the outage, cause unknown from inside the loop (no shell/Bash — gate-denied).

**Why it matters:** nothing alarmed. The governance watchdog (Mon 07:45 ET) diffs `runtime/agent-registry.json` — it verifies a loop is *sanctioned*, not that it *ran*. There is no check on artifact freshness, so a loop that silently stops (crashed timer, disabled unit, unhandled error, host down) produces no signal until a human eyeballs a `loops/<name>/` folder and notices the dates stop. This is the same class of failure as the silent credit/billing deaths (`[[2026-06-18_runtime-silent-credit-death]]`, `[[2026-07-20_keyless-source-loop-silent-zero]]`) and the midweek watchdog gap (`[[2026-07-10_watchdog-midweek-blindspot]]`): the failure mode is *absence of output*, and absence is exactly what a diff-against-registry or a scan-of-what's-present can't see.

**How to apply:**
- Platform (Kemba): add an **off-box artifact-staleness / loop-liveness heartbeat** — for each scheduled loop, record its expected cadence and alarm (via a channel that survives a host death, e.g. healthchecks.io) when an expected daily/weekly artifact doesn't land within its window. This is the durable fix `[[2026-07-10_host-billing-is-a-runtime-death-vector]]` already called for, generalized from "is the box up" to "did each loop actually produce its output."
- Any loop, cheaply, until that exists: at Step 0, compare the prior artifact's date to today against the loop's cadence; if there's an unexplained multi-run gap, **say so at the top of the artifact** (the desk did this 07-28) so the gap is at least visible in the human-facing output instead of buried.
- Don't infer a cause you can't see: from inside a gate-restricted loop you can observe the gap but not why the timer didn't fire — report the gap + flag it, don't fabricate a root-cause.

Triggers: loop:watchdog, agent:atlas, loop liveness, missing run, dead loop, absence
