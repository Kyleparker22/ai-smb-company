# Hook OS — towing & recovery (build 34)

**Working name:** Hook OS · **Launch:** `prebuild-hook-os` · **Port:** 8854
**Synthetic operator:** "Ironline Towing" — ~$6M, 14 trucks, police rotation + impound lot.

## The bleeding neck
The industry's reputation is "predatory," which makes provable discipline the differentiator:
rates that cannot exceed the filed rate card, storage that computes from the recorded impound
date, damage disputes settled by hookup photos, and the abandoned-vehicle lien clock that runs on
state dates — all against a police-rotation dispatch clock measured in minutes.

## Modules
1. **Call triage** (Intake) — police rotation (the clock starts NOW, R2 record) · breakdown ·
   price question · vehicle-release request.
2. **The rate-card clamp** (Back Office) — every quote/invoice computes from the recorded filed
   rate card BY CONSTRUCTION; there is no argument that produces a higher number. Per-state caps
   in a config that names itself a default.
3. **Storage arithmetic** (Back Office) — daily storage from the recorded impound timestamp;
   release stops the meter at the recorded release time.
4. **Damage evidence** (Operations) — a "your driver damaged it" dispute needs the hookup photo
   set; no photos → "cannot assert either way," a human calls.
5. **Lien calendar** (Company Brain) — abandoned-vehicle notice/lien steps per state as DATE
   ALERTS (default rules named replaceable); filing is R0, counsel files.

## Guardrails (load-bearing)
- `charge_above_rate_card` — **R0 by construction.**
- `assert_no_damage_without_photos` — **R0.** The photo pair argues, not the dispatcher.
- `file_lien` / `sell_vehicle` — **R0.** The calendar alerts; humans and counsel act.
- Release requires recorded ID + payment + release stamp — a gate, and the meter stops at it.

## ROI (typed)
Rotation calls answered inside the clock (counted) · storage billed to the day (counted) ·
dispute time (time_saved) · the rate-card defense file (scenario).

## Demo path
Board → rotation call (clock recorded) → try to bill above the card (clamped, named) → damage
dispute without photos (refused) → lien calendar (DATE ALERT) → trust tab.

## Build prompt
Shared contract, full built-out standard. Costly eval label: police rotation call.
