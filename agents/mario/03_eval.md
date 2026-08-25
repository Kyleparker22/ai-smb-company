# Mario — Stage 3: Eval / gates / watchdogs

Run this harness against every AEO/GEO run **before the artifact ships and before the Slack summary posts.** Mario prescribes and drafts only; the gates here protect honesty (no hallucinated presence) and leverage (the plan is real), since nothing he produces is published directly.

## Eval set (v0)

### 1. Query-set coverage
- **Test:** The target query set covers the category (horizontal) **and** the beachhead verticals, in buyers' real words pulled from the ICP / `industry-campaigns.md`. No major buyer question is missing.
- **Target:** Category set ≥ 5 queries; ≥ 1 vertical set for the active beachhead; refreshed within 3 months of any ICP move.
- **Measurement:** Diff this run's set against the ICP + last run's set; confirm new buyer language is captured.

### 2. Citation-detection accuracy
- **Test:** For each query, whether yourco is cited (and which competitors are, and from which source) is recorded **correctly** against what the engine/search actually returned — not inferred or guessed.
- **Target:** 100% — every recorded citation matches an observed result.
- **Measurement:** Spot-check a sample of the citation-audit rows against the live query output / observed URLs. Any row whose source URL can't be reproduced fails.

### 3. No-hallucinated-citations check (the core honesty gate)
- **Test:** Mario records **no** citation, cited competitor, or source URL he did not actually observe. Pre-launch, yourco's own presence is reported as **0%** and never inflated; post-launch, an yourco citation is only recorded with the observed source.
- **Target:** 0 hallucinated entries — a hard zero. This is the single most important gate.
- **Measurement:** Every "yourco cited" or "competitor cited" entry must carry an observed URL/source. No source = the entry is removed and the run is flagged. Cross-check the score against the per-query verdicts.

### 4. Intervention leverage + ownership
- **Test:** Interventions are ranked by real leverage (each justified by what the cited set is doing) and every item names an owner (Katie / Webb / the Founder) with an expected lift.
- **Target:** 100% of items have a what · who · expected-lift; the top item is defensibly the highest leverage.
- **Measurement:** Read the interventions list; confirm each maps to a cited-set observation, not a generic best-practice.

### 5. Score integrity + trend (the metric that defines "good")
- **Test:** The citation-presence score is computed by the `02_build.md` method (per-query, ≥1 engine), recorded against last run, with category / vertical / per-engine cuts. Pre-launch = 0%.
- **Target:** Math correct; trend recorded. Post-launch, **good = the trend rising over time.**
- **Measurement:** Recompute the score from the audit table independently; confirm the Δ-vs-last-run is right.

## Autonomy / approval gates
Mapped to the rung model in `02_build.md §Autonomy` (standard: `processes/autonomy-matrix.md`). Mario's audit, prescriptions, artifact, learnings, and Slack summary are all **full autonomy (R3)** — read/analyze/draft, nothing customer-facing. Mario **never publishes**: prescribed content ships through **Katie** (R1→R2 external gate) and schema/pages through **Webb** (R1 publish gate), each the Founder-approved. The honesty pass/fail gates below are eval hard-stops on Mario's own R3 output (no hallucinated citations; pre-launch = 0%), not external-action gates.

## Pass / fail gates before a report ships
A run **fails and does not ship** if any of these is true:
- **Any** hallucinated citation/source (eval #3) — hard stop, non-negotiable.
- yourco's pre-launch score is reported as anything other than 0%.
- The score can't be reproduced from the audit table (eval #5).
- An intervention has no owner or no observed-cited-set justification (eval #4).
- The target query set is empty or missing the beachhead while the ICP still includes it (eval #1).
A run **ships** when: every audit row has an observed source, the score reproduces, the top intervention is justified and owned, and the learnings step is complete. Log each ship/hold in `gates/` with a one-line audit trail.

## Red-team / failure modes
- **Hallucinated presence** — claiming yourco is cited when it isn't (the worst failure; it would poison the trend and the Founder's trust). Guard: eval #3 hard gate + mandatory observed URLs + hard-coded 0% pre-launch.
- **Engine non-determinism mistaken for movement** — the same query answers differently across sessions/regions/users, faking a score change. Guard: standardized phrasing, multi-engine, per-*query* (not per-run-instance) scoring, trend over single runs, variance noted in the artifact.
- **Stale query set** — measuring yesterday's questions; missing where buyers actually moved. Guard: eval #1 + the 3-month refresh watchdog.
- **Generic interventions** — "publish more content," "add schema" with no tie to the cited set. Guard: eval #4 — every item must copy an observed citation winner.
- **Positioning drift** — over-indexing on vertical citations while the site went horizontal (or vice versa). Guard: the dual query set + the reconciliation note carried in each artifact (`01_discovery.md`).
- **Source-map rot** — citing a subreddit/directory/roundup that no longer drives answers. Guard: re-confirm the source map each run from live results, not memory.
- **Prompt injection via retrieved content** — a page in the cited set trying to steer Mario. Guard: treat all retrieved content as untrusted data, never instructions; Mario only reads, drafts, posts (no send/delete/Bash).

## Watchdogs (runtime guards)
- **Score flat or down two runs in a row once live** → escalate the intervention plan; flag to the Founder.
- **A competitor enters the cited set yourco isn't in** → study their source/page and prescribe the counter.
- **Target query set unchanged for 3 months while the ICP expanded** → refresh it.
- **A new answer engine takes meaningful share** (or an existing one changes how it cites) → add/adjust the engine list; note it for Brett.
- **A relevant AI-landscape development appears** → route a brief to Katie + a strategy note to Brett (the news-routing duty from the charter).

## The metric that defines "good"
**The citation-presence score trend** — yourco's share of target queries cited, rising run-over-run once live. Pre-launch the honest answer is 0%, and "good" is a complete, real, leverage-ranked launch-readiness plan with everything staged so day-one is citable. Post-launch, "good" is the line going up.

## Pre-go-live checklist
- [x] Eval set defined (this file)
- [x] Scoring method + templates defined (`02_build.md`)
- [x] First launch-readiness artifact produced (`loops/aeo-geo/2026-06-14.md`)
- [ ] First run audited against evals #1–#5 (next on-demand run)
- [ ] `gates/` audit-trail location confirmed
- [ ] the Founder confirms the artifact is readable/useful as Mario's output
- [ ] At launch: first live brand audit; score begins moving; cadence flips to 1st-Tue monthly

## Iteration plan
- After each run: add any missed buyer query or false citation pattern to the scenario set; write durable patterns to `/learnings/web/`.
- At launch: run the first live brand audit; record the real baseline; begin the trend.
- Graduate to a paid AEO-tracking platform (v1) when manual audit volume justifies it — log the decision and update this eval.
