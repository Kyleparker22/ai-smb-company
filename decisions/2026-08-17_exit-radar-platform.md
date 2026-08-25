# 2026-08-17 — Exit Radar: the exit-flip lane gets its platform

## Decision (the Founder)
Build the platform for the exit-flip targeting lane decided 2026-07-29: a
sourcing → triage → pitch-staging engine for SMBs whose owners are trying to
sell. the Founder's framing: *"a platform that will research and find me SMBs that
people are trying to sell, and we can then prospect them and pitch
AI/yourco to them."* Built same-day at `agents/sadie/exit-radar/`
(console :8814, launch name `yourco-exit-radar`; 36-assertion honesty suite).

## What it is / is not
- **Is:** the machine behind `2026-07-29_exit-flip-targeting-lane.md` —
  candidate store with mandatory provenance, signal-ranked triage (expired >
  relisted > listed > retirement-news), the two-sided pitch drafted per the
  decision's guardrails, routing by construction (anonymized → Bird as
  partner-category-9 input; sold/under-contract → the ETA lane), and export
  into the EXISTING cold pipeline (Sadie schema → `sourcing.py` → Reilly →
  CRM on reply). Not previously rejected — checked `rejections/`; the
  adjacent rejection (detection-evasion scrapers, 2026-07-05) is honored
  structurally: the platform contains no fetcher at all, and ToS-gated
  listing URLs require a human-read attestation to enter.
- **Is not:** a new offering (the sale is still Audit → OS), a parallel CRM,
  a scraper, or a send rail. All sends stay OtherVenture-gated; the Founder sends.

## Notes that update the 2026-07-29 decision's context
- **Targeting is horizontal** per 2026-08-05 (all industries, warm-first) —
  the beachhead-first line in the older decision is superseded; the lane
  filters by SIGNAL, not vertical.
- First sweep (2026-08-17) confirmed the sourcing posture empirically:
  open-web discovery routes to the ToS-gated platforms, so Google Alerts
  RSS + human-read listing sessions + the broker door carry the volume.
  Sourced 2026 stats for the copy (Axios Raleigh 02-24: ~half of ST small
  businesses have owners 55+; ~85% of those lack a succession plan).

## Trip-wire
- **Overturn if:** the platform is shelf-ware by the review date — the build outran the sourcing supply (alerts unset, brokers unworked) — evidenced by `agents/sadie/exit-radar/data/candidates.json` holding <10 non-dismissed candidates.
- **Review:** 2026-10-01
- **Check:** _none — the candidate-store count is not an instrumented tripwire fact (the engine's facts are commercial/system/gates/trust only, per `decisions/_TRIPWIRES.md`); this is a prose review at the 2026-10-01 date, checked by opening the exit-radar console._

## Reversibility
Cheap — a folder and a launch entry; the lane decision (2026-07-29) carries
its own kill signals and they apply here unchanged.
