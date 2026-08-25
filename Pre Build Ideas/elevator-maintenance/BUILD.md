# Cab OS — elevator & escalator maintenance (build 40)

**Working name:** Cab OS · **Launch:** `prebuild-cab-os` · **Port:** 8860
**Synthetic operator:** "Vertex Elevator Service" — ~380 units under contract across 90 buildings.

## The bleeding neck
An entrapment call is a human in a metal box — minutes matter and the words matter (a passenger
told to self-evacuate is the fatality scenario). Under that: per-unit code-test deadlines (AHJ),
maintenance-contract scope disputes ("that's billable" fights), and the red-tagged unit somebody
turns back on.

## Modules
1. **Call triage** (Intake) — ENTRAPMENT (human dispatch now, script verbatim) · unit down ·
   noise/ride complaint · inspection scheduling.
2. **The entrapment protocol** (Operations) — R2: mechanic dispatched, building contact called,
   and the desk script verbatim: stay in contact, never advise self-evacuation. Every word tested.
3. **Test calendar** (Company Brain) — per-unit code tests (cat-1/cat-5 style, config-named
   defaults) as DATE ALERTS; a unit with no test record reads UNKNOWN, never compliant.
4. **Scope engine** (Back Office) — Queue OS pattern: billable vs contract-covered decided by the
   cited clause or "ambiguous — a human decides"; never billable off silence.
5. **Red-tag discipline** (Operations) — shutting a unit down is a human decision recorded;
   RETURNING a red-tagged unit to service is R0 for software and gated on the clearing mechanic's
   recorded sign-off.

## Guardrails (load-bearing)
- `advise_self_evacuation` — **R0.** The words cannot be produced.
- `reactivate_red_tagged_unit` — **R0** without the mechanic's recorded clearance.
- `mark_test_compliant_without_record` — **R0.**
- `assert_billable_off_silence` — **R0** (clause or ambiguous).

## ROI (typed)
Callback rate counted (not asserted) · test deadlines kept (counted) · scope leakage recovered
(counted with clauses) · the entrapment log (scenario — never a saving).

## Demo path
Board → entrapment call (script + dispatch) → reactivate the red-tagged unit (refused) → scope
check citing a clause → test calendar (UNKNOWN vs due) → trust tab.

## Build prompt
Shared contract, full built-out standard. Costly eval label: entrapment.
