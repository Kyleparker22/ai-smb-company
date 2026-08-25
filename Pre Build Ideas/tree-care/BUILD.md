# Canopy OS — tree care (build 32)

**Working name:** Canopy OS · **Launch:** `prebuild-canopy-os` · **Port:** 8852
**Synthetic operator:** "Hartwood Tree Company" — ~$4M, 4 crews, 1 crane, storm-season whiplash.

## The bleeding neck
Storm calls are triage or chaos — a tree ON a house is not a quote request. Estimates die
unfollowed (the industry's close rate problem is a follow-up problem). And the two ways a tree
company gets destroyed: working near energized lines without utility clearance, and telling a
customer a tree was "fine" before it fell.

## Modules
1. **Call/message triage** (Intake) — emergency (tree on structure/car/person, hanging limb over
   occupied) · hazard-assessment ask ("is my oak safe?") · quote request · schedule. Emergency first.
2. **The power-line gate** (Operations) — a job flagged `near_powerlines` cannot be scheduled
   without a recorded utility clearance reference. Structural, like the RUP gate.
3. **Hazard-assessment discipline** (Company Brain) — "is it safe / will it fall" questions route
   to the certified arborist UNANSWERED; assessments are drafted FOR the arborist, never issued.
4. **Estimate follow-up ladder** (Sales) — 3 touches, cooldown, silence-is-an-answer.
5. **PHC renewals** (Customer) — plant-health-care programs recalled on their recorded schedule.

## Guardrails (load-bearing)
- `assert_tree_safety` — **R0, never.** Neither "safe" nor "hazardous" leaves software; a
  certified arborist assesses. Both directions are liability.
- `schedule_near_powerlines_unclear` — **R0.** No utility clearance on file → the crew doesn't roll.
- `promise_no_damage` / felling-direction promises — **R0** in outward copy (tested).
- Emergency → R2 route + human now; the ack says a human is coming, nothing else.

## ROI (typed)
Estimates recovered by the ladder (counted × their close rate) · PHC renewals recalled (counted) ·
office hours (time_saved) · the storm-call answer speed (scenario).

## Demo path
Board → storm message triaged (emergency vs quote) → try to schedule the powerline job (refused) →
"is my oak safe" (routed unanswered) → estimate ladder with drafted copy → trust tab.

## Build prompt
Shared contract, full built-out standard. Costly eval label: emergency.
