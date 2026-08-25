# CRM backlog (David)

Ideas worth building into the native CRM, not yet scheduled. David reads this; the Founder prioritizes. Keep it short — graduate items to a build or delete them.

## ✅ Shipped — moved out of the backlog 2026-08-23

These sat here as "not yet scheduled" for **66 days after they were built**, and because The Board
reads this file, HQ was listing five completed items as open work. The evidence for each is the
newest `loops/_crm-hygiene/` artifact, which signs off with:
*"Automations: auto next-step · stale digest · closed-won ping — `runtime/crm_hygiene.py`
(weekdays 08:05 ET)."*

| Item | Shipped as | Evidence |
|---|---|---|
| Auto-create a follow-up task on stage advance | `runtime/crm_hygiene.py` — auto next-step | Runs weekdays 08:05 ET |
| No-activity / stale-deal alert (>14d) | `runtime/crm_hygiene.py` — stale digest | Latest run: **"Stale (> 14d): 12 — digest posted to #yourco-david"** |
| Slack on Closed Won | `runtime/crm_hygiene.py` — closed-won ping | Same module, same schedule |
| Auto-log activities from email/calendar | The `crm-autolog` loop + `_pending-activities.json` (confirm-in-UI is the gate) | 12 dated artifacts in `loops/crm-autolog/` |
| Weighted-pipeline forecast on the dashboard | `crm/index.html` — "weighted pipeline", "weighted value by stage" | Was already flagged here as *"probably already served"* |

---

## Automations — scheduled (build next; from the Twenty benchmark, 2026-06-18 — `decisions/2026-06-18_twenty-crm-client-component.md`)
Three pipeline automations Twenty ships as "first automations." All run David-side against `data.json`; all respect the approval gate (Slack posts OK, **no auto-send of client-facing comms**; drafts only).
- ✅ SHIPPED — **Auto-create a follow-up task when a deal advances to `proposal`** (and, more generally, stamp a `nextAction` + `nextDate` on any forward stage move that lacks one). Closes the "deal moved but nothing's queued" gap. Writes a task/activity, not an email. *Likely the real gap — we don't have this yet.*
- ✅ SHIPPED — **No-activity / stale-deal alert.** Any open deal with `lastTouch` > 14 days → flag on the dashboard (Needs-You view already exists — confirm it surfaces this) **and** post a digest to `#yourco-david`. Pipeline hygiene; reuses stale detection if present, adds the Slack nudge.
- ✅ SHIPPED — **Slack on Closed Won** — when a deal moves to `closed`/`won`, post a celebratory line to `#yourco-david` (and the digest). Cheap morale + a real-time revenue signal.
- ✅ SHIPPED — **Weighted-pipeline forecast number on the dashboard.** *Probably already served* by the predictive pipeline (winProb × value). David: confirm a single weighted-forecast figure is surfaced; don't rebuild if the predictive layer already computes it.

## From the Attio benchmark (2026-06-14 — `decisions/2026-06-14_crm-build-vs-buy-attio.md`)
- ✅ SHIPPED — **Auto-log activities from email/calendar.** Attio's best feature is records that build themselves from the inbox. yourco's activity log is still manual. Wire the Gmail/Calendar connector to **auto-draft activity entries that the Founder confirms** (never silent writes). Biggest quality-of-life upgrade to the CRM; reuses the runtime Gmail connector + the existing add_activity path. Gate: confirm-to-save, no auto-send, same posture as Melanie's command layer.
- **AI Attributes.** An auto-computed field refreshed on change — e.g. a one-line "why this prospect is a fit," or a company auto-summary. Fits the existing derived-field pattern (winProb, fitScore, signals); compute via the Claude brain (`dashboard/melanie.py`), cache it, show it on the company/hot-list card.

*(Already have, for reference — don't rebuild: Enrich = Attio's Web Research Agent; Melanie = Ask Attio, with source-citations; agentic write-commands = AI Workflows.)*
