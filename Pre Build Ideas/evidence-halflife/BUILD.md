# Halflife OS — the evidence half-life ledger (build 64)

**Working name:** Halflife OS · **Launch:** `prebuild-halflife-os` · **Port:** 8884
**Synthetic operator:** "Merrick & Vance" — 4-attorney PI/litigation firm, ~70 open matters.
(Distinct from build 6 Case OS, which runs intake/records-chase — Halflife OS treats evidence
as PERISHABLE INVENTORY with expiry clocks.)

## The never-seen mechanism
Every case's evidence is inventoried with its decay clock: surveillance footage retention
(30–90 days, per recorded custodian policy), witness memory (contact-freshness), vehicle EDR
data, records destruction schedules. The firm's work queue re-orders by WHAT DIES FIRST, and
preservation letters draft the day of intake. Cases are lost to evaporated evidence
constantly; no product treats evidence as inventory with expiry dates.

## Modules
1. **Evidence inventory** (Company Brain) — per matter: items typed (footage / witness / EDR /
   records / physical), each with source, custodian, and a decay clock from the RECORDED
   retention table (config `_source`-named defaults per custodian type; a custodian with no
   recorded policy reads UNKNOWN-EXPIRY and sorts FIRST — unknown decay is the scariest).
3. **The dies-first queue** (Operations) — firm-wide, every matter's evidence merged and
   ranked by days-to-expiry; the day's work IS this list; expired items are marked LOST with
   the date it died and who was on notice — the ledger does not forgive.
2. **Preservation desk** (Back Office) — intake auto-drafts preservation/spoliation letters
   per evidence item (R1, citing the item + custodian + clock); a sent letter (human act)
   pauses that item's LOST label but not its clock ("a letter is notice, not possession").
4. **Witness freshness** (Customer) — witnesses carry last-contact dates; a statement not yet
   taken decays; the take-the-statement task ranks with footage.
5. **Intake triage** (Intake) — new matter (starts the inventory NOW — every day of delay is
   evidence gone) · costly label: the evidence-exists tip ("the gas station probably has it
   on camera") — must never be routed casually; deadline ask; status; human.

## Guardrails (load-bearing)
- `assert_evidence_secured` — **R0**; only possession (recorded receipt) is secured — a sent
  letter is "on notice", never "secured".
- `extend_clock_without_policy` — **R0**; clocks come from the recorded retention table or
  read UNKNOWN — hope is not a retention policy.
- `legal_advice_to_nonclient` — **R0** (the Case OS line holds).
- Outward letters/drafts R1 always; the dies-first queue is R2 (ranking is arithmetic).

## ROI (typed)
Evidence preserved before expiry (counted, the ledger's own stat) · matters where footage
made liability (scenario — never a promised win) · paralegal chase hours (time_saved) ·
the malpractice shield (scenario).

## Demo path
Dies-first queue (footage at 9 days, unknown-policy custodian at top) → intake spawns
inventory + drafted preservation letters → "secured" refused for a letter-only item → an
expired item marked LOST with dates → witness freshness decay → trust tab.

## Build prompt
Shared contract, full built-out standard. Costly eval label: the evidence-exists tip.
