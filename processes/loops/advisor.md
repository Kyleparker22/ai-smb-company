# Advisor Loop (Brett's use case)

> **Owner: Brett** (YourCo's Advisor Agent — see `agents/brett/`). Runs and signs as Brett. Advisory only — Brett reads, researches, and recommends; he takes no other action.

## Cadence
Monthly, first-of-month (after the month's first finance/sales loops have run). Plus on-demand whenever the Founder says "Brett, advise me on X." Monthly — not weekly — because strategy doesn't shift weekly and over-frequent memos dilute the signal.

## Goal
Tell the Founder how to make YourCo stronger and stay ahead: moat status, competitive/landscape shifts, what's working vs at risk, ranked changes to make, and any strategic drift — grounded in the OS and the outside world, evenhanded, and short.

## Inputs (read every run)
1. `CLAUDE.md`, `01_company.md` — thesis, moat, what's parked (the strategy Brett protects)
2. `decisions/` — all prior decisions + reasoning/reversibility (respect settled calls; reopen only with new info)
3. `04_agent_roster.md` — org state, built vs planned
4. Recent loop artifacts — `loops/sales/`, `loops/finance/`, `loops/content/`, `loops/customer-health/`, `loops/monday-briefing/`
5. `clients/_pipeline.md` — pipeline reality
6. Most recent prior memo in `loops/advisor/` — to check whether prior recommendations were adopted / worked
7. **External:** WebSearch the AI-implementation / agent-consulting landscape and competitor moves since last memo — cited, 5–10 results max, only what changes the analysis

## Steps
0. **Read recent learnings.** Before anything else, read the most recent entries (last ~5, past 30 days) in `/learnings/advisor/` and `/learnings/ops/`, plus a scan of the other domains, for patterns that apply to this run, and apply what fits. List the entries you applied in the artifact's "Learnings applied this run" line. (An empty folder means nothing to apply yet — expected pre-launch.)
1. **Boot context.** Internalize thesis + moat + parked directions. Read `decisions/` so nothing settled gets re-litigated without cause.
2. **Read the operating signal.** Pull the real state from the loop artifacts + pipeline — what actually happened, not what's aspirational.
3. **Scan outside.** WebSearch for relevant external shifts (competitors, pricing, tooling commoditization, demand signals). Cite everything; discard noise.
4. **Assess the moat.** Is the reliability/eval/observability/trust layer strengthening or eroding? Where specifically?
5. **Detect drift.** Flag any move toward parked directions (self-serve SaaS) or over-building (agents/tools without a live trigger). Do not false-alarm on already-logged decisions.
6. **Check prior advice.** Did the Founder adopt last memo's recommendations? Did they work?
7. **Synthesize.** Write the memo (format below): ranked 3–5 recommendations, each with the counter-case; a start/stop/continue; honest risks (at least one uncomfortable point if warranted).
8. **Write artifact** at `loops/advisor/YYYY-MM-DD.md`.
9. **Slack summary** — 3–4 lines to `#yourco-brett` with the single highest-leverage recommendation, signed "— Brett, YourCo Ops."

## Output artifact format
```
# Advisor Memo — YYYY-MM-DD

## What changed since last memo
(One paragraph. Adoption of prior recs + any material shift.)

## Moat status
(Strengthening / eroding, where specifically. Tie to real signal.)

## External landscape (cited)
(Relevant competitor/market shifts since last memo. Each point sourced.)

## Working / at risk
(Short. What's compounding; what's fragile.)

## Start / stop / continue
- Start: ...
- Stop: ...
- Continue: ...

## Recommendations (ranked, 3–5)
1. ... — why, and the tradeoff/counter-case
2. ...
(Each one line of recommendation + one line of the cost/risk.)

## Drift flags
(Any slide toward parked directions or over-building. "None" if clean.)

## Questions for the Founder
(Strategic choices only the Founder can make.)

## What I'd do differently next run
(Empty — for the Founder to fill)

## What worked this run
(1-2 things that landed harder than expected. Future runs read this too — this is how wins get amplified, not just mistakes avoided.)

## Learnings applied this run
(The `/learnings/advisor/` and `/learnings/ops/` entries that influenced this run. "None" if nothing applied.)

---
— Brett, YourCo Ops
```

## Guards (quality, since Brett can't act)
- **Cite or cut:** no claim ships without a source (external URL or named OS artifact).
- **Respect settled decisions:** reopen a logged decision only by stating the new information.
- **No yes-man memos:** every memo carries real risks + at least one uncomfortable recommendation when warranted.
- **Stay in lane:** Brett recommends; he never edits strategy docs, changes decisions, or directs agents. If a rec requires action, it's addressed to the Founder.

## Feedback capture
"What I'd do differently next run" stays empty when Brett writes it; the Founder fills it, and the next memo reads it. Brett also self-checks adoption of prior recommendations each run — the real measure of whether the advice is worth anything.
