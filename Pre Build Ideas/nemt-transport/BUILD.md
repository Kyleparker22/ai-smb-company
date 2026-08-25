# Ride OS — non-emergency medical transport (build 46)

**Working name:** Ride OS · **Launch:** `prebuild-ride-os` · **Port:** 8866
**Synthetic operator:** "CareRoute Transport" — 18 vehicles (wheelchair + ambulatory), Medicaid
broker + facility contracts.

## The bleeding neck
A missed dialysis pickup is medical harm, not a late ride — those trips can never be bumped by
scheduling software. Medicaid pays only on complete trip logs (odometer + times + signatures),
so an undocumented trip is free work. And the moment a driver texts "grandma seems confused
today," the company is one bad automated reply away from practicing medicine.

## Modules
1. **Message triage** (Intake) — patient-condition change (human now, NEVER assessed) · schedule
   change · billing · complaint.
2. **The trip-log billing gate** (Back Office) — a trip bills only with its complete recorded
   log (pickup/dropoff odometer, times, signature ref). As-applied pattern; fields named on
   refusal.
3. **The never-bump rule** (Operations) — trips flagged dialysis/chemo/dialysis-standing cannot
   be displaced by the scheduler; a conflict escalates to a human instead. Structural.
4. **The credential gate** (Operations) — a driver assigns only with current recorded
   credentials (license, background, CPR, wheelchair-securement training). RUP pattern; expiries
   as DATE ALERTS.
5. **Tomorrow board** (Operations) — trips by run, unbillable trips (missing logs) counted,
   credential lapses.

## Guardrails (load-bearing)
- `assess_patient_condition` — **R0.** "Confused today" goes to a human and the facility, verbatim.
- `bill_without_trip_log` — **R0**, fields named.
- `bump_dialysis_trip` — **R0 by construction.**
- `assign_uncredentialed_driver` — **R0**, the lapse named.

## ROI (typed)
Unbillable trips recovered (counted) · no-load runs reduced (counted vs their baseline) ·
dispatch hours (time_saved) · the securement/credential file (scenario).

## Demo path
Board → condition-change message (verbatim, human) → bill the log-less trip (refused) → bump the
dialysis trip (refused) → assign the lapsed driver (refused) → trust tab.

## Build prompt
Shared contract, full built-out standard. Costly eval label: the patient-condition change.
