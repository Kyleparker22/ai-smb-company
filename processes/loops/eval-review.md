# Eval Review Loop

> **Owner: Kolby** (QA/Eval — see `agents/kolby/`). Runs and signs as Kolby. **Reports only** — scores and flags; never edits another agent's output or SOP. The weekly internal audit of every agent's quality.

## Cadence
Weekly, Sunday PM — so the scoreboard is fresh for the Monday briefing + the Founder's week.

## Inputs (read every run)
1. `processes/eval-rubric.md` — the six-dimension standard.
2. The week's loop artifacts in `loops/*/` (briefing, sales, finance, content, watchdog, advisor, finance-close, brand-audit, pricing-review, inbox-triage) — the subjects.
3. The corresponding loop SOPs in `processes/loops/*.md` — the bars each output is held to.
4. The prior `loops/eval-review/` artifact — last week's scoreboard, for drift.
5. `brand/v0/brand-guidelines.md` — voice (dimension 4).

## Steps
0. **Read recent learnings.** Before anything else, read the most recent entries (last ~5, past 30 days) in `/learnings/qa-eval/`, plus a scan of every other domain — Kolby is the meta-observer. Apply what fits this run; list applied entries in the artifact's "Learnings applied this run" line.
1. **Gather.** Pull each agent's most recent output from this week. If an agent didn't run, note it (a missing expected run is itself a flag).
2. **Error analysis, then score.** First *read* each output and note problems in plain language; group recurring problems into **failure modes** (a taxonomy) and count them across agents — this is the part that tells the Founder what to fix first. *Then* grade each output on the six rubric dimensions (binary-leaning 2/1/0, aligned to the Founder's taste — when unsure, fail it). Record every flag/fail with the specific line/reason. Any 0 = the output fails.
3. **Drift check.** Compare each agent's scores to prior weeks. A dimension trending down 2+ weeks, or a recurring flag, is drift — call it out even if the output still passes.
4. **Scoreboard.** Update the per-agent, per-week scoreboard.
4b. **Streak ledger.** Update the Streak ledger in `runtime/autonomy-matrix.md` per the streak rule (`processes/autonomy-matrix.md` §Advancement): for each climbing action, count this week's real uses and whether the week was clean. Clean week with ≥1 real use → streak +1 (and add the uses); zero real uses → streak unchanged (note "no uses"); any incident → **reset to 0** and record it in the ledger's incident column + a learning entry. When a streak crosses its threshold, flag it in the artifact and Slack — **promotion recommendation only; the rung change is the Founder's.** (Counts are the one edit Kolby makes outside his own artifacts — never the rungs.)
5. **Write learnings.** For each pattern worth carrying forward — a recurring failure mode, or a notable "what worked" — write a learning entry to the relevant `/learnings/<domain>/` (a sales-copy pattern → `/learnings/sales-copy/`, a brand-voice drift → `/learnings/brand-voice/`, a meta-pattern about evaluation itself → `/learnings/qa-eval/`). One entry per pattern, in the `/learnings/_README.md` format (Source / Pattern / Implication / Audience). This is the feed-forward step — how Kolby's findings reach the agents that need them. Kolby may write to any domain.
6. **Write artifact** at `loops/eval-review/YYYY-MM-DD.md`.
7. **Slack summary** — 3–5 lines to `#yourco-kolby`, signed "— Kolby, YourCo Ops": overall health, any **fails** (lead with these), and any drift. Reports only — name the owning agent so the Founder/that agent can fix.

## Output artifact format
```
# Eval Review — YYYY-MM-DD (week of …)

## Headline
(Overall agent-quality health in one line. Any fails up top.)

> ⚠️ **The scoreboard table below is machine-read.** `dashboard/loop_metrics.py` parses it for
> Kolby's owned number — outputs with no `0` on any of the six dimensions, over outputs scored. The
> column order and the `## Scoreboard` heading are a contract now; a pass is *no zero*, never a
> perfect 12, so an honest 11 must not be recorded as a fail. Change the shape and the metric
> reports a parse failure rather than a rate.

## Scoreboard (this week)
| Agent | Ground | Honest | SOP | Voice | Action | Loop/Gates | Total | Verdict |
(One row per agent that ran. "did not run" where applicable.)

## Failure modes (taxonomy + counts)
(Recurring problem types across this week's outputs, with counts — the error-analysis layer. "None observed" if clean.)

## Fails (any 0) — escalate
(Agent · dimension · the specific line/reason · suggested fix owner. "None" if clean.)

## Drift watch
(Dimensions trending down / recurring flags across weeks. "None" if stable.)

## Autonomy streaks
(Per climbing action: streak count after this week, uses added, any reset. Flag any action whose streak crossed its threshold — promotion is the Founder's call.)

## What I'd do differently next run
(Empty — for the Founder to fill)

## What worked this run
(1-2 things that landed harder than expected. Future runs read this too — this is how wins get amplified, not just mistakes avoided.)

## Learnings written this run
(The /learnings/<domain>/ entries Kolby created this run, and who they're for. "None" if nothing new.)

## Learnings applied this run
(The /learnings/qa-eval/ entries that influenced this run. "None" if nothing applied.)
```

## Watchdog triggers
- Any output scoring **0** on Honesty (fabrication) or Closed-loop/Gates (an unauthorized send/delete) → escalate at the very top; these are the cardinal failures.
- The same agent flagged 2 weeks running on the same dimension → escalate as drift.
- An expected weekly loop that produced no artifact → flag (silent failure).

## Pre-scale handling
With most loops honestly reporting "quiet / no data yet" pre-revenue, Kolby's main job now is verifying that honesty is *real* (the loop correctly found nothing) rather than a missed run or a fabrication. Grade the discipline, not the volume.
