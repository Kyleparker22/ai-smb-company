# Hours OS — small trucking fleet (build 45)

**Working name:** Hours OS · **Launch:** `prebuild-hours-os` · **Port:** 8865
**Synthetic operator:** "Redline Carriers" — 22 trucks, regional dry van + flatbed.

## The bleeding neck
Dispatching a driver whose hours can't legally complete the run is the nuclear-verdict scenario —
and it happens because the dispatcher does the HOS arithmetic in their head at 6am. Detention
money dies unbilled for lack of recorded in/out times. And the log-falsification line ("just fix
his log") is the one a fleet must be structurally unable to cross.

## Modules
1. **The dispatch gate** (Operations) — a load assignment computes driver clock (from recorded
   ELD state) vs run hours + buffer BY CONSTRUCTION; short clock → refused with the arithmetic
   shown. A driver with no recorded clock reads UNKNOWN and cannot be dispatched.
2. **Log discipline** (Company Brain) — software never edits, certifies, or "corrects" a
   driver's log. Annotation requests draft FOR the driver; falsification requests are refused
   and logged verbatim.
3. **Detention evidence** (Back Office) — detention bills only from recorded arrival/departure
   stamps (the evidence pair); the invoice cites both.
4. **Accident protocol** (Operations) — human now at R2 + a preservation checklist brief (ELD,
   camera, phone records — logistics only, no fault language).
5. **Maintenance calendar** (Operations) — per-truck intervals from recorded odometer; overdue
   named; an OOS (out-of-service) truck can't be assigned.

## Guardrails (load-bearing)
- `dispatch_beyond_hours` — **R0 by construction**, arithmetic shown.
- `edit_or_certify_log` — **R0, logged.** The falsification line.
- `assign_oos_truck` — **R0.**
- Accident messages: nothing drafted outward; the brief is internal and factual.

## ROI (typed)
Detention recovered with stamps (counted) · violations avoided (scenario — prevented can't be
counted) · dispatch hours (time_saved) · the clean-log file (scenario).

## Demo path
Board (driver clocks, UNKNOWN honest) → dispatch the short-clock driver (refused, arithmetic
shown) → "fix his log" (refused + logged) → detention invoice citing stamps → trust tab.

## Build prompt
Shared contract, full built-out standard. Costly eval label: the "fix the log" request.
