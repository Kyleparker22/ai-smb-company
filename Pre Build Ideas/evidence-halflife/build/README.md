# Halflife OS — build

Evidence half-life ledger for small law firms. Port **8884** (`prebuild-halflife-os`).
Synthetic operator: Merrick & Vance, 4-attorney PI/litigation, ~70 open matters.

```
python3 seed.py             # synthetic Merrick & Vance
python3 test_halflife_os.py # the suite
python3 server.py           # 127.0.0.1:8884
```

## The never-seen mechanism
Every case's evidence is inventoried as PERISHABLE with a decay clock from the recorded
retention table (gas-station CCTV 30d, municipal cameras 14d, EDR 60d, witness memory a
120d freshness window from last recorded contact…). The firm-wide work queue re-orders by
WHAT DIES FIRST — and a custodian type with **no recorded policy reads UNKNOWN and sorts
first**, because unknown decay is the scariest. Preservation letters draft the day of
intake, per item, in the same call.

## The load-bearing refusals
- **Only a possession receipt is "secured."** A sent preservation letter sets *on notice* —
  and the clock keeps running. A letter is notice, not possession. Marking an item secured
  without a recorded receipt is refused at R0 and can never become an approvable row.
- **Nothing extends a clock.** Clocks come from the recorded retention table or read
  UNKNOWN — hope is not a retention policy (`extend_clock_without_policy`, R0; the function
  does not exist).
- **LOST is permanent.** Expiry passed → LOST with `died_at` and whether we were on notice.
  There is no resurrect path anywhere in the codebase; a late copy is a NEW item and the
  loss stays on the record. The ledger does not forgive.
- **The evidence-exists tip is never routed casually.** "The gas station probably has it on
  camera" spawns an inventory item (clock running from the *incident*, not the message) and
  a preservation-letter draft in the same pass — the costly eval label.
- **No legal advice.** Deadlines, case value, liability — routed to a licensed attorney
  unanswered (the Case OS line holds).

## Honesty rules (from `_kit`)
Costly eval label `evidence_tip`. All outward letters/drafts R1 (a human approval IS the
send); the dies-first ranking is R2 arithmetic. ROI typed — the scenario lines ("footage
that made liability," the malpractice shield) stay blank, never a promised win. This-week
stats counted from the ledger and event log with a baseline delta. Append-only events.
White-label — the firm's name only. Synthetic only. **Nothing is sent.**
