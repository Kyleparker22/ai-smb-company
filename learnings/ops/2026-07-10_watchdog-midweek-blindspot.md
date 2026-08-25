---
name: watchdog-midweek-blindspot
description: The runtime watchdog's only self-liveness signal is "no Slack line on a Monday" — so a Tue–Thu watchdog death goes unsurfaced for up to 6 days. It cannot reliably watch itself.
metadata:
  type: feedback
---

On 2026-07-10 the watchdog caught that **it itself had been dark 07-07 → 07-09** (3 consecutive days): `loops/_runtime/watchdog.log` jumped from `2026-07-06 OK` straight to `2026-07-10`, with no run header or artifact for the three missing days. Every *other* loop ran normally those days (inbox-triage, open-loops, crm-autolog, crm-hygiene, aeo-geo all `OK`), so it was an isolated `yourco-watchdog.timer` failure, not a runtime/credit outage — and it self-recovered without intervention.

**Why it stayed silent for 3 days:** the SOP's only self-liveness rule is *"no watchdog line on a **Monday** → the watchdog itself didn't fire."* That check only looks on Mondays, and a clean non-Monday deliberately posts nothing to avoid daily noise. So a watchdog death on Tue/Wed/Thu is invisible until the next Monday heartbeat — up to a 6-day blind spot. This run only caught it because a *later* watchdog run happened to fire and read its own log history; had the outage continued, nothing would have alerted.

**Why:** this is the "a monitor must not depend on the thing it monitors" rule (`[[2026-06-18_runtime-silent-credit-death]]`, `[[2026-07-10_host-billing-is-a-runtime-death-vector]]`) applied to the watchdog's *own timer*. The watchdog can catch every loop except the one failure mode that also mutes the watchdog — its own scheduler not firing. On-box self-monitoring has the same structural hole as the on-box credit alarm and the on-box host-billing alarm.

**How to apply:**
1. **Detection (this run's behavior — keep doing it):** every watchdog run should read its own `watchdog.log` for gaps since the prior run's date, not just assume "if I'm running, I'm healthy." A gap of ≥1 expected daily slot in the watchdog's own log = surface it as a MISS immediately, any day of the week, don't wait for the Monday heartbeat rule.
2. **Durable fix (backlog, needs the Founder/Kemba):** add a cadence-independent, ideally **off-box** liveness check for the watchdog specifically — a dead-man's-switch (healthchecks.io/UptimeRobot) the watchdog pings on each successful run; a missed ping alerts from outside the box. That is the only monitor that survives the watchdog's own timer/service/host death.
3. **Root-cause the timer:** when this recurs, the direct check is `systemctl status yourco-watchdog.timer` + `journalctl -u yourco-watchdog` on the VPS (Bash is gate-denied in headless runs, so it's a human host action) — look for a disabled unit, a service error, or OnCalendar drift.

Triggers: loop:watchdog, agent:atlas, monitoring cadence, coverage blindspot, timer schedule
