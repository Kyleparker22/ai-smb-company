# Runtime Watchdog Loop

> **Owner: Atlas** (runtime health — "who watches the watchers"). Confirms the scheduled loops actually fired vs. silently failed, and raises a Slack alert if any missed. **Reports only.** Runs **daily, 08:15 ET** (after the morning loops). Writes a dated artifact every day (the machine heartbeat); **Slacks only when something MISSED — plus a weekly all-green heartbeat on Mondays.** This daily cadence is what catches a *daily* loop (e.g. inbox-triage) that stalls mid-week — the old Monday-only cadence could miss a Tuesday failure for ~6 days. Heartbeat: if `#all-yourco` gets no watchdog line on a **Monday**, the watchdog itself didn't fire → investigate the runtime first.

## Inputs (read every run)
1. Each scheduled loop's most recent artifact in `loops/<loop>/`.
2. Each loop's run log tail in `loops/_runtime/<loop>.log` (gitignored; on the host).
3. The prior watchdog artifact in `loops/_watchdog/`.

## The scheduled loops + cadence (check the right ones for "this week")
| Loop | Cadence | Artifact dir | Log |
|---|---|---|---|
| monday-briefing | weekly (Mon) | `loops/monday-briefing/` | `monday-briefing.log` → `OK` |
| sales | weekly (Mon) | `loops/sales/` | `sales OK` |
| finance | weekly (Mon) | `loops/finance/` | `finance OK` |
| pipeline-report | weekly (Mon) | `loops/pipeline-report/` | `pipeline-report OK` |
| eval-review | weekly (Sun) | `loops/eval-review/` | `eval-review OK` |
| customer-health | weekly (Wed) | `loops/customer-health/` | `customer-health OK` |
| content | weekly (Fri) | `loops/content/` | `content OK` |
| source-watch | weekly (Fri 07:30) | `loops/source-watch/` | `source-watch OK` — added 2026-07-29; timer installed + enabled on the VPS 2026-07-29 |
| inbox-signal | weekly (Fri 07:15) | `loops/inbox-signal/` | `inbox-signal OK` — added 2026-08-24. ⚠️ **Repo-side only until the Founder installs the unit on the VPS** (`.claude/skills/add-runtime-loop/` steps 7-8); until `systemctl list-timers` shows it, 'never ran' here is expected, not a fault. |
| inbox-triage | daily | `loops/inbox-triage/` | `inbox-triage OK` |
| open-loops-chaser | daily (weekdays) | `loops/open-loops/` | `open-loops-chaser OK` |
| crm-hygiene | daily (weekdays) | `loops/_crm-hygiene/` | deterministic script — fresh dated artifact = healthy (no run-loop log) |
| crm-autolog | daily (weekdays) | `loops/crm-autolog/` | `crm-autolog OK` |
| initiative | daily (weekdays, 08:45) | `loops/initiative/` | `initiative OK` |
| connector-spotter | weekdays 09:10 — **STAGED, deliberately not installed** (Connector OS is counsel + launch gated) | `loops/connector-spotter/` | `connector-spotter OK` — **do not flag as MISSED while staged**; this row goes live the day the timer is installed |
| melanie-briefing | weekly (Tue 07:45) — timer installed 2026-07-06 after 3 weeks written-but-never-enabled; first fire expected 2026-07-07 | `loops/melanie-briefing/` | `melanie-briefing OK` |
| advisor | monthly | `loops/advisor/` | `advisor OK` |
| aeo-geo | monthly (1st Tue) | `loops/aeo-geo/` | `aeo-geo OK` — **added 2026-07-06 after its June miss went invisible (last artifact 06-14); a loop with no row here can die silently** |
| finance-close | monthly | `loops/finance-close/` | `finance-close OK` |
| brand-audit | monthly | `loops/brand-audit/` | `brand-audit OK` |
| pricing-review | quarterly | `loops/pricing-review/` | `pricing-review OK` |
| lineage-review | quarterly (2nd Mon of Jan/Apr/Jul/Oct) | `loops/lineage-review/` | `lineage-review OK` |

## Steps
1. **Classify each loop** HEALTHY vs MISSED:
   - **Weekly/daily loops** — expect a fresh artifact within the loop's cadence window (this week for weekly; today/yesterday for daily) **and** a recent `<loop> OK` in the log. Missing fresh artifact, a `FAILED` log, or a stale artifact = **MISSED**.
   - **Monthly/quarterly loops** — only flag if **overdue** (no artifact within its period). Not-yet-due = HEALTHY (note "not due").
   - Be honest about the runtime's age: a loop with no artifact only because its first scheduled slot hasn't occurred yet is **not** a failure — note it.
2. **Write the artifact** to `loops/_watchdog/<today>.md` — a table of loop → HEALTHY / MISSED / not-due → last-artifact-date, plus a one-line note on any nuance (off-cadence firing, cron still settling).
3. **Slack** — signed "— Atlas (watchdog)", to `#all-yourco`:
   - **Any day, anything MISSED** → post immediately, lead with the failure(s): `⚠️ Runtime watchdog: <loop(s)> did NOT run / failed — <one-line detail>. Check the runtime.`
   - **Monday + all green** → weekly heartbeat: `✅ Runtime watchdog: all due loops ran (<list>). All green.`
   - **Non-Monday + all green** → no Slack post (the dated artifact is the record; avoid daily noise).

Do NOT send any email. Report what you found and posted.

## Watchdog triggers (escalate)
- Any **daily** loop (inbox-triage) with no fresh artifact by the 08:15 ET check → MISSED, **alert same day** (this is the mid-week-stall case the daily cadence exists to catch).
- Any **weekly** loop MISSED → top of the Slack line + the artifact.
- The same loop MISSED two weeks running → escalate as a runtime fault, not a transient.
- A `FAILED` exit in any log → name the loop + the exit code.
- No watchdog line posted on a Monday → the watchdog itself failed (a human must notice the absence).

## Pre-scale handling
Pre-launch, several loops honestly report "quiet / no data yet." The watchdog's job is verifying they *ran* (produced a fresh artifact + an OK log), not that they found activity. Grade the firing, not the volume.
