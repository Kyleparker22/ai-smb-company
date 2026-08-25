# Unit OS — multi-unit restaurants (build 16)

**Working name:** Unit OS · **Launch:** `prebuild-unit-os` · **Port:** 8836

## The idea

A 4–10 unit restaurant group loses margin unit by unit: food-cost variance nobody computes until
the P&L lands six weeks late, complaints and reviews handled ad hoc per store, and — the one that
ends companies — an illness or allergen claim answered by whoever saw it first, in writing, with
an accidental admission. Unit OS counts the variance where counts exist, drafts the routine
responses, and hard-stops the dangerous ones.

**Buyer:** the owner/operator of the group. Thinks in food cost points and per-unit P&L.

## The bleeding neck

- Theoretical-vs-actual food cost: a 2-point gap on a $1.8M unit is $36k/yr, invisible without the
  discipline of counts.
- An illness claim answered by a shift lead ("so sorry OUR food made you sick") is an admission in
  a future lawsuit. An allergen question answered wrong by a bot is an ambulance.
- Reviews and complaints: response velocity is a counted number nobody counts.

## Modules

1. **Message & review triage** (Customer) — illness claims, allergen incidents, allergen
   *questions*, and health-department contact each hard-stop to a human with **no reply drafted at
   all**. Routine complaints and reviews get R1 drafts.
2. **Variance watchtower** (Back Office) — per unit-period theoretical vs actual food cost,
   computed **only where inventory counts exist**; a unit that skipped counts reads *unmeasured*,
   never estimated from last month.
3. **Unit scorecard** (Company Brain) — per-unit counted facts: variance, complaint velocity,
   response backlog — each refusing where its inputs are missing.

## Guardrails (load-bearing)

- `respond_to_illness_claim` — **R0.** No automated reply, no admission; a human calls with the
  insurer's language. The eval's costly class is an illness/allergen signal read as routine.
- `answer_allergen_question` — **R0.** Allergen safety is answered by trained staff, never by
  software.
- `respond_to_health_department` — **R0.** The owner, immediately.
- Variance is never estimated: no counts, no number.

## ROI model

Variance points recovered → revenue (their sales, counted variance) · response drafting hours →
time saved · illness-claim exposure → scenario (never a saving) · review velocity → their number.

## 10-minute demo

Board → triage the "food poisoning" message (no reply drafted, human + insurer) and the "is the
mole gluten-free" question (refused, manager) vs the cold-burrito complaint (R1 draft) → variance
board with the no-counts unit reading unmeasured → scorecard → ROI → trust.

## Build prompt (§8)

Build `Pre Build Ideas/multi-unit-restaurants/build/` on `_kit/`. Stdlib, JSON store,
127.0.0.1:8836, launch `prebuild-unit-os`. Seed "Verano Taqueria Group": 6 units, 12 months of
inventory periods with one unit skipping counts, messages incl. illness/allergen/health-dept
cases, reviews. Eval costly class = missed illness/allergen signal. Tests pin the three R0s, the
no-counts refusal, ROI blanks, counted automation.
