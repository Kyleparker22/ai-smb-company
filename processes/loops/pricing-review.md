# Pricing Review Loop

> **Owner: Polo** (YourCo's Pricing Strategist — see `agents/polo/`). Runs and signs as Polo. Proposes only — vertical pricing locks and any external pricing communication require the Founder's approval. (Roster: quarterly pricing review.)

## Cadence
First Monday of each quarter (Jan / Apr / Jul / Oct). Plus on-demand per-vertical when a new vertical is being built.

## Goal
Keep YourCo's pricing honest against reality. Review the per-vertical pricing references against the close-rate, retention, and margin data that have accumulated — and recommend adjustments before they drift out of line with what the market and the math support.

## Inputs (read every run)
1. `pricing/v0/` — the canonical per-vertical pricing references + `pricing/README.md`, `pricing/CHANGELOG.md`
2. `clients/_pipeline.md` — close rates, stage movement, win/loss signal
3. Most recent `loops/finance/` artifacts + `finance/` ledgers — margin, per-engagement economics, token spend vs. revenue
4. Most recent prior artifact in `loops/pricing-review/`
5. `CLAUDE.md` — pricing model + token economics (YourCo absorbs model spend)

## Steps
0. **Read recent learnings.** Before anything else, read the most recent entries (last ~5, past 30 days) in `/learnings/pricing/` and `/learnings/ops/` for patterns that apply to this run, and apply what fits. List the entries you applied in the artifact's "Learnings applied this run" line. (An empty folder means nothing to apply yet — expected pre-launch.)
1. **Boot context.** Internalize the pricing model (build fee + monthly retainer + audit + add-on builds/retainer step-ups) and the principle that YourCo absorbs token/infra cost.
2. **Per-vertical read.** For each locked vertical: is the build fee + retainer still supported by close rate, retention, and margin? Is token spend on a vertical eating the retainer?
3. **Gap + risk scan.** Flag any vertical priced before there was data; any margin compression; any concentration risk; any retainer that no longer covers run cost.
4. **Propose.** Concrete recommendations (hold / raise / restructure), each with the data behind it. Proposals only — the Founder locks.
5. **Write artifact** at `loops/pricing-review/YYYY-MM-DD.md`.
6. **Slack summary** — 3 lines to `#yourco-polo`, signed "— Polo, YourCo Ops." Lead with any margin or retainer-coverage risk.

## Output artifact format
```
# Pricing Review — YYYY-MM-DD (Q#)

## Headline
(One line: pricing healthy / a vertical needs attention / not enough data yet.)

## Per-vertical read
(One block per locked vertical: current price, what the data says, recommendation.)

## Risks
(Margin compression, retainer under-coverage, concentration, priced-without-data. "None" if clean.)

## Proposals for the Founder to lock
(Specific changes + the data behind each. Empty if hold.)

## What I'd do differently next run
(Empty — for the Founder to fill)

## What worked this run
(1-2 things that landed harder than expected. Future runs read this too — this is how wins get amplified, not just mistakes avoided.)

## Learnings applied this run
(The `/learnings/pricing/` and `/learnings/ops/` entries that influenced this run. "None" if nothing applied.)
```

## Watchdog triggers
- Any vertical's retainer not covering its run cost (token + infra) → escalate.
- Margin <50% on a vertical for 2 consecutive quarters → escalate.
- A vertical still priced on assumption (no real close/retention data) after a full quarter live → flag.

## Pre-revenue handling
Until real close/retention/margin data exists, the review states that plainly and holds current pricing — it does not invent adjustments from no data. The first substantive review comes after the first engagements produce data.
