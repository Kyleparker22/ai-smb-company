# Fix OS — appliance repair (build 58)

**Working name:** Fix OS · **Launch:** `prebuild-fix-os` · **Port:** 8878
**Synthetic operator:** "Reliable Appliance Service" — 5 techs, warranty-authorized for 3
manufacturers + COD retail work.

## Why this industry (the overlooked test)
Appliance repair sits under the AI radar — small shops squeezed between manufacturers' warranty
paperwork and consumers' "just fix my fridge." Half the revenue is warranty reimbursement that
dies on clerical errors nobody has time to prevent.

## The bleeding neck
The warranty claim. A manufacturer reimbursement is denied for a missing serial, wrong failure
code, absent proof-of-purchase date, or a narrative that doesn't match the parts — and denied
claims are simply eaten. The quiet leaks: second truck rolls because the eval didn't say what
part to bring (the fridge's model/serial and symptom were on file the whole time); COD repairs
started past the customer's authorized amount; recall/flagged units worked casually; parts
ordered by memory.

## Modules
1. **The claim gate** (Back Office) — a warranty claim assembles from recorded fields (serial,
   purchase-date proof ref, failure code, parts, narrative-matches-parts check) and REFUSES to
   submit incomplete, naming every missing field — "a denied claim is free work."
2. **Unit memory + parts-to-bring** (Company Brain) — every appliance's make/model/serial and
   history; triage turns symptom + model into the recorded likely-parts list so the first visit
   fixes (the entire margin).
3. **Authorization clamp** (Sales) — COD work carries the customer's recorded authorized amount;
   work past it has no path — the overage drafts back for approval first.
4. **Intake triage** (Intake) — the costly label: gas smell / sparking / flooding reads first
   (safety script); warranty vs COD routing from recorded coverage; status asks from record.
5. **Recall & safety flags** (Operations) — units matching the recorded recall list are flagged;
   a flagged unit's ticket carries the notice verbatim, never dropped.

## Guardrails (load-bearing)
- `submit_incomplete_claim` — **R0, structural**: the claim builder names missing fields and has
  no force-submit.
- `exceed_authorized_amount` — structural clamp; overage drafts R1.
- `dismiss_safety_symptom` — **R0**; gas/spark/flood language survives into every draft.
- `invent_failure_narrative` — **R0**; the narrative assembles from recorded diagnosis only.

## ROI (typed)
Warranty denial rate → recovered dollars (counted once claims flow) · first-visit-fix lift
(counted re-rolls × recorded cost) · COD overage disputes (scenario) · office hours (time_saved).

## Demo path
Board → fridge-not-cooling intake → parts-to-bring from unit memory → warranty claim refused
incomplete (fields named) → completed claim submits → COD overage clamp → gas-smell script →
trust tab.

## Build prompt
Shared contract, full built-out standard. Costly eval label: the gas/spark/flood safety message.
