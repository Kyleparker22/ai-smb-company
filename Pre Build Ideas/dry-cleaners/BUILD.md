# Garment OS — dry cleaning & laundry (build 49)

**Working name:** Garment OS · **Launch:** `prebuild-garment-os` · **Port:** 8869
**Synthetic operator:** "Lexington Cleaners" — 3 storefronts + wholesale hotel/restaurant routes.

## The bleeding neck
The wedding-dress claim is the reputation event: handled ad-hoc ("we'll give you $20") it becomes
a one-star story; handled procedurally it's a fair-claims calculation from the intake record. The
quiet leaks: the ready rack aging with finished work nobody picks up, stain promises the counter
can't keep, and the unclaimed-garment disposal clock that runs on state law.

## Modules
1. **Message triage** (Intake) — damage/loss claim · stain question (the promise trap) · pickup/
   ready status · wholesale account request.
2. **Claim protocol** (Operations) — a claim needs the intake condition record (tag notes — the
   evidence pair); the settlement DRAFTS from a recorded fair-claims schedule (garment class ×
   age depreciation, config-named default), never ad-hoc, never denied by software.
3. **The promise rule** (Customer) — stain-question replies are structurally "we'll try X,
   results depend on the fabric and the stain's age" — outcome promises can't be produced
   (guarantee-check pattern).
4. **Ready-rack ladder** (Back Office) — finished orders aged; bounded pickup reminders; the
   unclaimed-disposal clock per state as DATE ALERTS (config default named).
5. **Wholesale route board** (Operations) — route stops, counts recorded vs billed (the evidence
   for account disputes).

## Guardrails (load-bearing)
- `deny_claim` — **R0.** Software assembles the record and the schedule math; a human decides.
- `settle_off_schedule` — **R0**; the recorded fair-claims schedule or a human.
- `promise_stain_outcome` — **R0**, forbidden-language check on drafts.
- `dispose_before_clock` — **R0**; the state clock as DATE ALERT, disposal is a human act after it.

## ROI (typed)
Ready-rack cash released (counted) · claims settled on schedule vs ad-hoc (counted) · counter
hours (time_saved) · the claims file (scenario).

## Demo path
Board (rack aging, disposal clocks) → wedding-dress claim (record + schedule math, no denial) →
stain question (honest copy) → pickup ladder → trust tab.

## Build prompt
Shared contract, full built-out standard. Costly eval label: the damage/loss claim.
