# AEO / GEO — Answer-Engine Visibility Loop

> **Owner: Mario** (YourCo's Answer-Engine Visibility Agent — see `agents/mario/`). Runs and signs as Mario. Drafts and prescribes only; nothing publishes without the Founder. Webb implements the schema/pages Mario specs; Katie writes the content Mario briefs.

## Cadence
Monthly, first Tuesday, 8:00 AM ET — once yourco is live. Pre-launch it runs on demand to produce and maintain the launch-readiness plan.

## Goal
Get yourco into the set of brands AI answer engines cite for its category, and measure whether it's working. Each run audits where yourco stands, finds who's winning the citations and why, and prescribes the next interventions ordered by leverage.

## Inputs (read every run)
1. `CLAUDE.md` and `01_company.md` — what yourco is and the moat (the entity definition the engines should learn)
2. The most recent prior artifact in `loops/aeo-geo/` — last run's plan and the citation-presence score, so this run measures movement
3. `processes/outbound/industry-campaigns.md` and the ICP — the verticals and the language buyers actually use (drives the target query set)
4. `brand/writing-rules.md` — any content Mario briefs must follow it

## The target query set
The questions yourco wants to be the answer to. Maintain these in the artifact; they're the thing measured every run.
- **Category:** "done-for-you AI agents for small businesses," "AI employee implementation consultancy," "how do I add an AI agent to my business without hiring a developer," "alternatives to building AI agents in-house."
- **Per-vertical (one set per ICP vertical):** "AI receptionist / front desk for a [landscaping / dental / roofing / HVAC / law] business," "AI to answer after-hours calls for a [vertical]," "AI intake for a [vertical]."

## Steps
0. **Read recent learnings.** Read the last ~5 entries (past 30 days) in `/learnings/web/` and `/learnings/strategy/` and apply what fits. List what you applied in the artifact.
1. **Audit (live runs).** For each target query, ask each engine (ChatGPT, Claude, Gemini, Perplexity, Google AI Overview) and record: is yourco cited? who is cited instead? which source did the engine pull from (a Reddit thread, a directory, a roundup, the brand's own page, YouTube)? Pre-launch, skip the yourco-cited check (it's zero by definition) and audit the **category** instead — the cited-set and the sources, which is the intelligence that drives the plan.
2. **Read the cited set.** For the brands winning citations, name *why*: what page or source the engine pulled, what makes it citable (it directly answers, it's structured, it sits in a source the engine trusts). That's the playbook to copy.
3. **Map the citation sources.** List the specific places AI pulls answers in this category — the subreddits, the directories (G2/Capterra/Clutch-type), the roundup/"best X" listicles, the YouTube channels. These are where yourco needs a presence, not just its own site.
4. **Prescribe interventions, ordered by leverage.** Group into: (a) content yourco should publish (answers, comparison/alternative pages) → brief for Katie; (b) schema + page structure → spec for Webb (Organization, Service, FAQ, Product); (c) off-site presence → where to show up in the source list; (d) citations/mentions to earn. Each item: what, who owns it, expected lift.
5. **Score.** Compute the citation-presence score: share of target queries where yourco is cited (0% pre-launch by definition — the score starts moving at launch). Record it so the next run measures movement.
6. **Write artifact** at `loops/aeo-geo/YYYY-MM-DD.md`.
7. **Slack summary** — 3–5 lines to `#yourco-mario`, signed "— Mario, YourCo Ops": the score, the single highest-leverage intervention, and anything that needs the Founder or a handoff to Katie/Webb.

## Output artifact format
```
# AEO/GEO Audit — YYYY-MM-DD

> ⚠️ **This heading and the `**N%**` line under it are machine-read** by
> `dashboard/loop_metrics.py` for Mario's owned number on HQ → Agents. Keep both exactly; the score
> must be the first thing under the heading and must carry a `%`.

## Citation-presence score
X% of target queries cite yourco (was Y% last run). Pre-launch: 0% by definition — baseline plan below.

## Target query set (this run)
(category + per-vertical, with the cited/not-cited result per query once live)

## The cited set — who's winning, and why
(brands the engines cite + the specific source/page each pulled + what makes it citable)

## Citation sources map
(the subreddits, directories, roundups, YouTube channels AI pulls from in this category)

## Interventions, by leverage
1. Content (→ Katie): ...
2. Schema / structure (→ Webb): ...
3. Off-site presence: ...
4. Citations to earn: ...

## Handoffs
(what goes to Katie, what goes to Webb, what needs the Founder)

## Learnings applied this run
(entries from /learnings/web/ and /learnings/strategy/, or "None")
```

## Watchdog triggers
- Citation-presence score flat or down two runs in a row once live → escalate the intervention plan; flag to the Founder.
- A competitor enters the cited set yourco isn't in → study their source and prescribe the counter.
- Target query set unchanged for 3 months while the ICP expanded → refresh it.
