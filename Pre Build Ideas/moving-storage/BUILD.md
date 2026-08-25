# Move OS — moving & storage (build 22)

**Working name:** Move OS · **Launch:** `prebuild-move-os` · **Port:** 8842

## The idea

The moving industry's reputation problem is a pricing problem: the lowball quote that grows on
moving day, the "pay more or we keep the truck loaded" hostage pattern, and damage claims that
dissolve into he-said-she-said. A reputable mover's competitive weapon is *provable* discipline:
a binding estimate that required a real survey, final charges that structurally cannot exceed the
estimate plus signed change orders, and claims resolved on condition records with a clock.

**Buyer:** the owner. Thinks in trucks, crews, claims ratio, and review scores.

## The bleeding neck

- A binding quote issued off a phone guess is either lost margin or a moving-day fight.
- Every dollar charged above the estimate without a signed change order is a complaint, a
  chargeback, or a regulator letter.
- Claims that sit unacknowledged breed one-star reviews and, interstate, regulatory exposure.

## Modules

1. **Quote desk** (Sales) — a **binding estimate cannot be issued without a recorded survey**
   (onsite or virtual, with an inventory). Non-binding quotes carry their nature on their face.
2. **The charge clamp** (Back Office) — final charges = binding estimate + recorded signed change
   orders, **by construction**. A charge above that does not exist; the clamp names itself.
3. **Claims desk** (Customer) — a damage claim needs the load AND delivery condition records for
   the item; the acknowledgment clock is computed under a rule set that names itself a default.
4. **Message triage** (Intake) — claim reports are the costly class: routed and clocked
   immediately; quotes, date changes, and complaints draft at R1.

## Guardrails (load-bearing)

- `issue_binding_without_survey` — **R0.** A guess is not a binding number.
- `charge_above_estimate` — **R0**, structural: the invoice function clamps.
- `condition_delivery_on_extra_payment` — **R0.** The hostage load is the industry's shame; this
  system cannot express it.
- Claims acknowledgment dates are DATE ALERTS under configurable rules.

## ROI model

Moving-day disputes avoided → scenario · survey-backed margin → their number · claims hours →
time saved · review-driven bookings → their number.

## Build prompt (§8)

Build `Pre Build Ideas/moving-storage/build/` on `_kit/`. Stdlib, JSON store, 127.0.0.1:8842,
launch `prebuild-move-os`. Seed "Beacon Hill Moving & Storage": ~300 moves across 12 months
(binding and non-binding, with/without surveys, change orders), condition records, claims at every
age, messages incl. claim reports. Eval costly class = missed claim report. Tests pin the
no-survey refusal, the charge clamp, the hostage R0, the evidence pair, the clock, ROI blanks.
