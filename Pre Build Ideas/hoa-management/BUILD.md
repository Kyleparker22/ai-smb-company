# Reserve OS — the association that shows its math (build 67)

**Working name:** Reserve OS · **Launch:** `prebuild-reserve-os` · **Port:** 8887
**Synthetic operator:** "Northgate Community Management" — manages 14 associations, 2,300
doors total.

## Why this industry
HOA management is a trust desert: boards suspect managers, homeowners suspect both, reserve
studies rot in drawers until the six-figure special assessment lands as a surprise. The
management company that can PROVE fairness wins contracts.

## The never-seen mechanism
Reserve adequacy as live bear/base/bull FUNDING BANDS against the recorded reserve study
(Deal OS's bands aimed at a building), every violation and fee decision carried with
append-only evidence and the rule cited — and the radical part: **the homeowner portal shows
the same numbers the board sees.** One set of books, two doors, zero spin.

## Modules
1. **Reserve truth** (Operations) — per association: the recorded reserve study (components,
   remaining life, replacement cost, as-of date) vs actual recorded balances and contribution
   rates → funding trajectory as bear/base/bull bands (cost-inflation offsets recorded, not
   invented); the SPECIAL-ASSESSMENT HORIZON: the band-dated year contributions stop covering
   the curve. A study older than the recorded staleness threshold flags every number it
   feeds; an association with NO recorded study reads UNKNOWABLE — "no study, no adequacy
   claim," never a reassurance.
2. **The violation ledger** (Back Office) — append-only: every violation carries the recorded
   rule cited (CC&R section), photo ref, and the ladder stage (courtesy → notice → hearing →
   fine per the recorded policy); a violation citing no recorded rule cannot be created
   (structural); fines are the recorded schedule's arithmetic; the hearing decision is a
   human act on the record.
3. **Two doors, one ledger** (Customer) — the homeowner view renders from the SAME stores as
   the board view (structural: one read path, tested); homeowner asks answered by citation
   ("why did my dues rise" → the band math + the line items, verbatim).
4. **Board packet** (Company Brain) — monthly: funding bands, violation ledger summary,
   spend-vs-budget counted; drafted R1 for the manager, never auto-sent.
5. **Intake triage** (Intake) — costly label: the habitability/safety report ("the stairwell
   railing is loose" — common-area safety routes NOW) · dues/fee dispute · violation appeal
   (a recorded right; acknowledged with the hearing process cited) · amenity/general · human.

## Guardrails (load-bearing)
- `claim_adequacy_without_study` — **R0**; UNKNOWABLE, never reassured.
- `violation_without_recorded_rule` — **R0, structural**: no code path.
- `fine_off_schedule` — **R0**; the recorded schedule or a human hearing.
- `divergent_homeowner_numbers` — **structural**: one read path for both doors, tested.
- `dismiss_safety_report` — **R0**; common-area safety escalates verbatim.
- Outward drafts R1; the special-assessment horizon is always bands, never one date.

## ROI (typed)
Contract wins/retention on provable fairness (scenario + counted renewals) · special-
assessment shocks avoided (the horizon, counted early-warnings) · violation-dispute hours
(time_saved) · collection lift from citation-answered disputes (counted, operator lift).

## Demo path
An association's funding bands + special-assessment horizon → the no-study UNKNOWABLE refusal
→ a violation with rule + photo cited, ladder staged → the off-schedule fine refusal → the
homeowner door showing the board's numbers → dues dispute answered by citation → trust tab.

## Build prompt
Shared contract, full built-out standard. Costly eval label: the common-area safety report.
