# Inspect OS — property / home inspection (build 36)

**Working name:** Inspect OS · **Launch:** `prebuild-inspect-os` · **Port:** 8856
**Synthetic operator:** "Keystone Property Inspections" — 6 inspectors, ~2,400 inspections/yr.

## The bleeding neck
An inspection firm lives on agent referrals and dies on a lawsuit — and the pressure between
those two is exactly where software must be incorruptible. The agent wants the report soft and
early; the client paid for it hard and first. Findings language is lawsuit bait in both
directions (a "deal killer" phrase, or a softened defect that later floods a basement).

## Modules
1. **Message triage** (Intake) — a soften/omit request ("can you leave the roof note out") · an
   early-copy request from the agent · booking · report-status question.
2. **Append-only findings** (Operations) — findings, once recorded, cannot be edited or deleted;
   a revision is a NEW entry with both versions kept (the event-log rule applied to the report
   itself). THE structural spine of the build.
3. **The client-first release rule** (Customer) — the report releases to the paying client;
   anyone else gets it only after a recorded client authorization.
4. **Report clock** (Back Office) — 24h turnaround computed per inspection; overdue named.
5. **Referral ledger** (Sales) — referral sources counted from records; the thank-you drafts.

## Guardrails (load-bearing)
- `soften_or_remove_finding` — **R0, logged verbatim.** The refusal event IS the defense file.
- `release_to_non_client` — **R0** without recorded client authorization.
- `estimate_repair_cost` — **R0.** Not our license; the report refers to trades.
- `advise_buy_or_walk` — **R0.** The inspector reports conditions; the decision is the client's.
- Health questions (radon/mold/asbestos "is it dangerous") → routed unanswered.

## ROI (typed)
Report turnaround (counted) · referral volume by source (counted) · admin hours (time_saved) ·
the unaltered-findings file (scenario — an E&O defense is not our number to model).

## Demo path
Board → the agent's soften request (refused + logged verbatim) → the agent's early-copy request
(refused, client-first) → append-only finding revision demo → trust tab.

## Build prompt
Shared contract, full built-out standard. Costly eval label: the soften/omit request.
