# Yard OS — equipment rental (build 15)

**Working name:** Yard OS · **Launch:** `prebuild-yard-os` · **Port:** 8835

## The idea

An independent rental house ($5–20M, mixed contractor/homeowner) burns trust and margin in three
places: invoices that keep running after the customer called the machine off rent (the dispute
machine), damage charges asserted without evidence (the churn machine), and equipment that is off
rent but never picked up — deployed, not earning, invisible. Yard OS makes billing stop at the
recorded call, makes damage a matter of evidence pairs, and puts the pickup queue on a board.

**Buyer:** the owner / rental manager. Thinks in dollar utilization and disputes.

## The bleeding neck

- The off-rent call taken on a cell phone at 4:50pm that never reached billing. Every such invoice
  is a dispute, a credit memo, and a customer shopping the competitor.
- "You bent the boom" with no checkout photo is a $4,000 argument the store always loses.
- Off-rent, not picked up: the unit earns nothing and can't be re-rented.

## Modules

1. **Off-rent integrity** (Back Office) — billable days are computed from the rental record and
   **structurally stop at the recorded off-rent call**. A bill past the call cannot be produced.
   Disputed rows show both sides.
2. **Call triage** (Intake) — off-rent requests (the costly miss), breakdowns (billing-stop clock
   plus swap), extensions, new rentals. Eval ships with the build.
3. **Damage evidence** (Operations) — a damage charge requires the checkout AND check-in condition
   records. Missing either, the system says **"cannot assert damage"** — a refusal, not a weaker
   claim.
4. **Yard board** (Operations) — pickup queue aging, utilization per class counted from the fleet
   file (refusing where fleet counts are missing), dollar utilization where rates are recorded.

## Guardrails (load-bearing)

- Billing past a recorded off-rent call is impossible by construction — tested, not promised.
- `assert_damage_charge` without both condition records → refused with the missing record named.
- Waivers/credits carry a **standing limit**: small ones execute at R2 and log; above the limit the
  action demotes to the approval gate (the autonomy matrix's limit pattern, visible in the demo).
- `backdate_off_rent` — **R0.** The record is the record.

## ROI model

Disputed-invoice credits avoided → scenario · pickup-queue days recovered → revenue (their rates)
· billing-audit hours → time saved · damage recovery with evidence → revenue (counted claims).

## 10-minute demo

Board → take the 4:50pm off-rent call (watch billing clamp to the call) → try to bill past it —
impossible → damage claim with the missing-checkout refusal vs the evidenced one → pickup queue
aging → the waiver limit demo → ROI → trust.

## Build prompt (§8)

Build `Pre Build Ideas/equipment-rental/build/` on `_kit/`. Stdlib, JSON store, 127.0.0.1:8835,
launch `prebuild-yard-os`. Seed "Blue Heron Equipment Rental": ~650 units in 8 classes, ~900
rentals across 12 months incl. off-rent-called-still-out rows, damage cases with and without
evidence pairs, calls incl. the 4:50pm off-rent. Eval costly class = missed off-rent request.
Tests pin the billing clamp, the evidence refusal, the waiver limit demotion, the R0, utilization
refusals, ROI blanks, counted automation.
