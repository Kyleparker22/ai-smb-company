# Pipeline Report Loop

> **Owner: David** (CRM/RevOps — see `agents/david/`). Runs and signs as David. **Reports only** — keeps the CRM honest and tells the Founder what's moving, stuck, and needs him. The weekly read on revenue.

## Cadence
Weekly, Monday AM (early — so the pipeline is fresh for the Monday briefing, which reads it).

## Steps
0. **Read recent learnings.** Before anything else, read the most recent entries (last ~5, past 30 days) in `/learnings/ops/` for patterns that apply to this run, and apply what fits. List the entries you applied in the artifact's "Learnings applied this run" line. (An empty folder means nothing to apply yet — expected pre-launch.)
1. **Read the CRM.** `crm/data.json` (source of truth) + `clients/_pipeline.md`. Reconcile them — if they've drifted, update `_pipeline.md` to mirror the CRM (it's the agent-readable copy Reilly/Jim/Bird/Atlas use).
2. **Run hygiene.** Apply the rules in `agents/david/` — flag deals stuck in a stage too long, deals with no next action/date, duplicates, any `lost` without a `why`. Fix what's clearly fixable; flag the rest.
3. **Report the movement.** Stage changes since last week, new deals in, deals advanced/slipped, total open value, win/loss.
4. **Surface what needs the Founder.** The short list: deals waiting on the Founder, follow-ups due, decisions.
5. **Score last run's predictions** *(predict→score→adjust pilot, 2026-07-22 — `learnings/ops/2026-07-22_predict-score-adjust.md`)*. Open last week's artifact; score each prediction **hit / miss / not scoreable** with one line of evidence, and update the running record (hits / scored). First run: "no prior predictions."
6. **Predict.** 1–3 falsifiable predictions about the pipeline before next run — each states the claim, the observable it will be scored against, and a confidence %. Predict only on real signals (a real prospect's reply window, a follow-up due date, an expected stage change) — never on example data. "None — no live signals" is a valid entry and beats an invented forecast.
7. **Write artifact** at `loops/pipeline-report/YYYY-MM-DD.md`.
8. **Slack summary** — 3–5 lines to `#yourco-david`, signed "— David, YourCo Ops": pipeline value + count, what moved, what's stuck, the needs-the Founder list. Lead with anything time-sensitive. Once a prediction record exists, include it as a trailing line (e.g. "prediction record: 4/5").

## Output artifact format
```
# Pipeline Report — YYYY-MM-DD

## Headline
(Pipeline value + open count + the one thing that matters this week.)

## Movement
(New in, advanced, slipped, won, lost — since last week. "Quiet" if nothing.)

## Needs the Founder
(Deals waiting on the Founder, follow-ups due, decisions. "Nothing pressing" if quiet.)

## Hygiene flags
(Stale deals, missing next actions, dupes, lost-without-why. "Clean" if none.)

## Prediction scorecard
(Last run's predictions scored hit / miss / not scoreable, one line of evidence each, plus the running record "hits/scored". First run: "no prior predictions.")

## Predictions (next run scores these)
(1–3 falsifiable claims — each with the observable it's scored against and a confidence %. "None — no live signals" is valid.)

## What I'd do differently next run
(Empty — for the Founder to fill)

## What worked this run
(1-2 things that landed harder than expected. Future runs read this too — this is how wins get amplified, not just mistakes avoided.)

## Learnings applied this run
(The `/learnings/ops/` entries that influenced this run. "None" if nothing applied.)
```

## Watchdog triggers
- A deal in `discovery` >2 weeks or `build` >3 days → flag (hygiene rules).
- A `live` client missing a weekly readout → hand to Kortney.
- The CRM and `_pipeline.md` drifted → David reconciles; flag if it keeps happening.

## Pre-revenue handling
The pipeline is mostly example data until outreach lands real prospects. David reports that honestly in two lines and stops — no invented deals. Real value begins when Reilly's first batch generates replies.
