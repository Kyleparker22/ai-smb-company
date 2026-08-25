# Gate OS — build 23

Pre-built vertical AI OS for self-storage operators.
Spec: [`../BUILD.md`](../BUILD.md) · shared engine: [`../../_kit/`](../../_kit/).

```bash
python3 seed.py            # 3 facilities, ~1,900 tenants (~140 delinquent)
python3 test_gate_os.py    # 36 assertions
```

Launch name **`prebuild-gate-os`** (port 8843, 127.0.0.1 only).

## What it is

"Summit Ridge Storage" — 3 facilities, $3.2M. Four modules: **delinquency ladder**,
**the SCRA stop**, **message triage**, **occupancy board**.

## The refusal it is organised around

**No lien step runs against a military-flagged or unverified tenant.** A lien step against a
servicemember is a federal violation with statutory damages — and against an *unverified* tenant
it is a gamble with the same downside, so both are refused with the stake named. A deployment
signal in a message ("I'm deployed until March", "PCS orders") flags the tenant, voids stale
verification, freezes the ladder at R2, and queues human SCRA verification. Eval costly class =
missed military signal, recall 1.0.

Also load-bearing:
- **The lien calendar is date alerts under replaceable per-state rules** — a state with no rule
  set is refused, not defaulted; swapping the rules moves the dates (tested).
- `initiate_auction` / `cut_lock` / `sell_contents` — **R0.** A human runs a sale off a
  counsel-reviewed checklist; software alerts dates.
- **Dunning is bounded and structurally cannot threaten** — 3 gentle touches, then a person; the
  forbidden-language check refuses "auction", "final warning", "sell your".
- Occupancy refuses any facility whose unit count is missing.
- The ROI panel's SCRA line is the operator's number or blank — statutory damages are not ours
  to quote.

## 10-minute demo

Board → Inbox (the deployment message: ladder frozen, verification queued) → Delinquency & liens
(lien step on all three demo tenants: military — refused; unverified — refused; verified — the
date-alert calendar) → ROI → Trust.

## What this does not do yet

- **No integrations.** FMS (SiteLink/storEDGE-class), gate systems, payments are adapter seams.
- **Triage is deterministic pattern-matching** — a real deployment puts a model behind the routine
  path and leaves the SCRA stop exactly as it is.
- **Lien rules are simplified shapes, not law** — counsel replaces them per state; SCRA
  verification itself is a human process against the DMDC database.
- **Nothing is sent.**
