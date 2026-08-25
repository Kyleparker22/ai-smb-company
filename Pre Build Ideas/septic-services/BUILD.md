# Pump OS — septic & portable sanitation (build 33)

**Working name:** Pump OS · **Launch:** `prebuild-pump-os` · **Port:** 8853
**Synthetic operator:** "Clearline Septic & Site Services" — ~$5M, pump trucks + portable fleet.

## The bleeding neck
Pump-out intervals live in customers' heads (a 3-year cycle nobody recalls = the quiet revenue
leak), sewage-backup calls are emergencies handled like bookings, and the regulated half —
disposal manifests, land-application permits — is exactly where a missing record becomes a fine
with the company's name on it.

## Modules
1. **Message triage** (Intake) — backup emergency (sewage in the house) · due-service ·
   quote · portable-unit event order. Emergency first.
2. **The manifest billing gate** (Back Office) — a pump-out bills only with gallons + disposal
   site + manifest reference recorded. The as-applied pattern: unprovable work is a dispute, and
   here it's also a regulatory exhibit.
3. **Interval recall** (Customer) — pump-outs recalled from each system's own recorded interval;
   bounded ladder, honest copy (no scare language about system failure).
4. **Phone-diagnosis refusal** (Operations) — "is it the baffle or the field?" → a tech visit,
   never a guess; drafted booking instead.
5. **Portable-event board** (Operations) — units out, service schedule, event returns.

## Guardrails (load-bearing)
- `bill_without_manifest` — **R0.** Gallons, site, manifest — or no invoice.
- `diagnose_by_phone` — **R0.** A system nobody has opened is a system nobody diagnoses.
- `schedule_land_application_unpermitted` — **R0** without the recorded permit reference.
- Backup emergency → R2 + human now; the ack promises a truck window, not a diagnosis.

## ROI (typed)
Recalled pump-outs (counted × avg ticket) · portable event capture (counted) · office hours
(time_saved) · the manifest file (scenario — a clean DEQ audit is not our number to model).

## Demo path
Board → backup message (emergency route) → bill the job with no manifest (refused, fields named)
→ recall ladder copy → trust tab.

## Build prompt
Shared contract, full built-out standard. Costly eval label: backup emergency.
