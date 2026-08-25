# Finance Pulse Loop

> **Owner: Charles** (YourCo's Finance Agent — see `agents/charles/`). Runs and signs as Charles. Atlas reads this loop's artifact for the Monday briefing but does not own it. (Handoff logged: `decisions/2026-06-07_charles-finance-agent.md`.)

## Cadence
Every Monday at 7:15 AM ET (runs after sales so the Founder has both in one morning read). Monthly close runs the first Monday of the month per `finance/monthly_close.md`.

## Goal
Keep the Founder aware of money state without a QuickBooks instance. Workspace-native finance only. This loop also catches logging gaps before they become a month-end mess.

## Inputs (read every run)
1. `CLAUDE.md`
2. `finance/README.md`, `revenue.md`, `expenses.md`, `token_spend.md`, `runway.md` — read each if it exists; flag missing files as a gap
3. `clients/*/cost.md` — the per-engagement spend ledgers (`log-build-cost` skill, phases discovery/build/tools/run): an active engagement with recent commits but no ledger rows this week is a **capture gap**, not $0 spend — flag it
4. Most recent prior artifact in `loops/finance/`
5. Gmail — invoice / payment / receipt / payroll / vendor threads in the last 7 days

## Steps
0. **Read recent learnings.** Before anything else, read the most recent entries (last ~5, past 30 days) in `/learnings/finance/` and `/learnings/ops/` for patterns that apply to this run, and apply what fits. List the entries you applied in the artifact's "Learnings applied this run" line. (An empty folder means nothing to apply yet — expected pre-launch.)
1. **Boot context.**
2. **Check logging gaps.** Is each ledger file (`revenue.md`, `expenses.md`, `token_spend.md`) current as of last week? List any missing entries Charles can infer from Gmail.
3. **Scan inbox.** Find invoice-related and receipt threads in the last 7 days. List items that should be logged but aren't yet.
4. **Compute current state.** Cash on hand (from `runway.md` last entry — the Founder to supply at the monthly close), MRR (sum recurring contracts in active engagements), monthly burn estimate (rolling average of last 3 months expenses, or rough estimate if pre-revenue), runway in months.
5. **Per-engagement margin.** For each live or expansion client: revenue collected − token spend. Flag any negative or trending negative.
6. **Apply watchdog triggers** (below). If any fired, lead the artifact with them.
7. **Write artifact** at `loops/finance/YYYY-MM-DD.md`.
8. **Slack summary** — 3 lines to `#yourco-charles`, signed "— Charles, YourCo Ops." If any watchdog fired, lead with it.

## Output artifact format
```
# Finance Pulse — YYYY-MM-DD

## Watchdogs fired
(If any — lead with these. Otherwise: "None.")

## Current state
- Cash: $X (as of YYYY-MM-DD)
- MRR: $X
- Estimated burn: $X/mo
- Runway: N months

## Logging gaps to fix this week
(List of entries that should be in ledger files but aren't)

## Per-engagement margin
(One line per live client; "no active engagements" if pre-revenue)

## What to do this week
(Specific actions — send invoice X, log expense Y, update runway.md, etc.)

## What I'd do differently next run
(Empty — for the Founder to fill before next Monday)

## What worked this run
(1-2 things that landed harder than expected. Future runs read this too — this is how wins get amplified, not just mistakes avoided.)

## Learnings applied this run
(The `/learnings/finance/` and `/learnings/ops/` entries that influenced this run. "None" if nothing applied.)
```

## Watchdog triggers
- Margin <50% on any client for 2 consecutive months → escalate
- Runway <6 months → escalate
- Token spend on a client growing faster than revenue from that client → escalate
- Any single client >40% of revenue (concentration risk) → flag
- Any week without entries logged in `revenue.md` or `expenses.md` while engagements are live → flag

## Pre-revenue handling
While YourCo is pre-revenue: report "no revenue yet"; focus on expense tracking, token spend on internal experimentation, and runway from cash on hand. Watchdogs still apply.
