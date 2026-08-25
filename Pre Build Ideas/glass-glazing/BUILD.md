# Pane OS — glass & glazing shops (build 59)

**Working name:** Pane OS · **Launch:** `prebuild-pane-os` · **Port:** 8879
**Synthetic operator:** "Clearview Glass Co." — storefront + shower + residential window work,
2 install crews, 1 fabricator relationship.

## Why this industry (the overlooked test)
Glazing shops live between fabricator lead times and customers with a hole in their wall — and
no AI product courts them. Every error is bespoke: a wrong measurement is a full remake at the
shop's cost plus two more weeks of an angry customer.

## The bleeding neck
The remake. Custom glass ordered off one hurried tape-measure reading is the margin killer —
the industry rule is measure twice, and the fix is structural: **no order goes to the
fabricator without two recorded measurements that match** (within recorded tolerance), taken as
recorded acts (who, when). The quiet leaks: safety-glass code locations (doors, tub/shower,
near-floor, stairs — recorded rule set) quoted as annealed to win on price; lead times promised
from hope instead of the fabricator's recorded dates; board-up emergencies (storefront smashed
at 2am) queued behind shower quotes; deposits uncollected before fabrication.

## Modules
1. **The measure-twice gate** (Operations) — orders carry measurement pairs; mismatched or
   single measurements refuse to release to the fabricator, naming the gap; tolerance recorded
   in config, cited in the refusal.
2. **Safety-glass rule** (Operations) — recorded hazardous-location rules; a quote for an
   annealed unit in a flagged location is refused with the rule cited — "we don't sell code
   violations cheaper."
3. **Order pipeline** (Back Office) — quote → deposit → fabrication (recorded promised date) →
   install; customer promises only cite the fabricator's recorded date + recorded install
   capacity; no deposit, no fabrication release.
4. **Intake triage** (Intake) — the costly label: break-in/board-up emergency reads first
   (storefront open to the street is a security event, dispatch the board-up); shower/mirror
   quote; status ask; warranty/seal-failure claim.
5. **Remake ledger** (Company Brain) — every remake recorded with cause (measure/fab/install/
   customer); the counted remake rate is the shop's own number, never an estimate.

## Guardrails (load-bearing)
- `release_order_without_matching_measurements` — **R0, structural**: no path.
- `quote_annealed_in_safety_location` — **R0**; the recorded rule is cited.
- `promise_undated_lead_time` — refused; promises cite the fabricator's recorded date.
- `release_fabrication_without_deposit` — structural; outward drafts R1.

## ROI (typed)
Remakes avoided (counted remake ledger × recorded cost, operator lift) · board-up capture
(counted) · deposit float (cash_timing) · office hours (time_saved).

## Demo path
Board → smashed-storefront intake → board-up dispatch first → shower order: one measurement →
refused, second mismatched → refused with tolerance cited, matched → released → annealed-in-door
quote refused → lead-time promise cites fabricator date → trust tab.

## Build prompt
Shared contract, full built-out standard. Costly eval label: the break-in / board-up emergency.
