# Slip OS — marina & boat yard (build 48)

**Working name:** Slip OS · **Launch:** `prebuild-slip-os` · **Port:** 8868
**Synthetic operator:** "Harborview Marina & Boatworks" — 240 slips, 60-boat dry stack, full
service yard.

## The bleeding neck
Yard bills get disputed because work started on a phone call nobody recorded; the slip waitlist
is a shoebox of "call me when something opens" that never rings; storage billing runs past the
launch date; and a fuel-dock spill handled casually becomes a Coast Guard exhibit (the drift-
complaint pattern on water).

## Modules
1. **Message triage** (Intake) — SPILL/fuel incident (verbatim log, human now, regulator-grade)
   · work request · waitlist inquiry · billing.
2. **The work-authorization gate** (Operations) — a yard work order cannot start (clock in) 
   without recorded owner authorization for THAT scope + rate; verbal is a note, not a gate pass.
   Change-order pattern afloat.
3. **Storage clamp** (Back Office) — storage billing stops at the recorded launch/departure date
   by construction (Yard OS off-rent pattern).
4. **Waitlist engine** (Sales) — ranked offers when a slip opens (Visit OS waves pattern): 
   recorded beam/draft/length fit computed, first-refusal windows honest.
5. **Survey discipline** (Company Brain) — vessel-condition assertions route to a licensed
   marine surveyor; the yard reports work performed, never seaworthiness.

## Guardrails (load-bearing)
- `start_work_unauthorized` — **R0 by construction** (no clock-in without the authorization ref).
- `assert_seaworthiness` — **R0.** A surveyor's word, never software's.
- `bill_past_departure` — **R0 by construction.**
- Spill messages: verbatim + human now; software admits nothing, denies nothing (drift pattern).

## ROI (typed)
Waitlist conversions (counted) · disputed yard bills avoided at the gate (scenario) · storage
billed to the day (counted) · the spill log (scenario — a USCG file is not our number to model).

## Demo path
Board (open slips, waitlist depth, boats in yard) → spill message (verbatim protocol) → clock in
on the unauthorized work order (refused) → waitlist ranked offers → trust tab.

## Build prompt
Shared contract, full built-out standard. Costly eval label: the spill/fuel incident.
