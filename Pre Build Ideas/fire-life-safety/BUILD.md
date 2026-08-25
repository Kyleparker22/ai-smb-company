# Code OS — fire & life-safety inspection (build 35)

**Working name:** Code OS · **Launch:** `prebuild-code-os` · **Port:** 8855
**Synthetic operator:** "Sentinel Fire Protection" — extinguishers, alarms, sprinkler inspections
across ~700 commercial sites, ~$8M.

## The bleeding neck
This business IS a calendar: every device carries a code-mandated inspection interval, and a
missed one is simultaneously lost revenue and a life-safety exposure with the company's name on
the last tag. The second leak: deficiencies found on inspection (the repair revenue) quoted once
and never chased. The catastrophic failure: software softening or sitting on an impairment.

## Modules
1. **Message triage** (Intake) — impairment report (sprinkler out, panel in trouble) · inspection
   due/scheduling · deficiency quote question · AHJ (fire marshal) contact.
2. **The device calendar** (Company Brain) — every device's next-due computed from its recorded
   last inspection + interval; a device with no record reads UNKNOWN, never "compliant."
3. **Impairment protocol** (Operations) — an impairment notifies the building owner NOW at R2
   with fire-watch language verbatim; software never downgrades severity, never closes one.
4. **Deficiency quote chase** (Sales) — bounded ladder; the copy cites the inspection finding and
   the code reference recorded with it.
5. **Compliance board** (Customer) — per-site: devices due, overdue, deficient — counted.

## Guardrails (load-bearing)
- `mark_compliant_without_record` — **R0.** No inspection record, no green check. Ever.
- `downgrade_impairment` / `close_impairment` — **R0.** A human closes after the fix is verified.
- `certify_inspection` — **R0.** The licensed inspector signs; software drafts the paperwork.
- AHJ contact → owner immediately; software never corresponds with the fire marshal.

## ROI (typed)
Overdue inspections recovered (counted × avg) · deficiency quotes chased (counted × their close
rate) · scheduling hours (time_saved) · the impairment log (scenario — never a saving).

## Demo path
Board → impairment message (R2 + fire-watch language) → try to mark the record-less device
compliant (refused) → deficiency chase copy citing the finding → trust tab.

## Build prompt
Shared contract, full built-out standard. Costly eval label: impairment.
