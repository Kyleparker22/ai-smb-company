# Claim OS — build

Medical billing service. Port **8857** (`prebuild-claim-os`).

```
python3 seed.py          # synthetic Meridian Practice Solutions (no real PHI)
python3 test_claim_os.py # the suite
python3 server.py        # 127.0.0.1:8857
```

## The load-bearing refusals
- **The upcoding refusal.** A code cannot move to a higher-RVU code without a recorded provider-
  documentation reference — the fraud line, held shut structurally. Downcoding is mechanical (R2).
- **The clean-claim gate.** Incomplete claims cannot submit; the refusal names each field.
- **Write-offs are always a human decision** (R1, never promoted) — it's the client's money.
- **PHI discipline.** Outward drafts carry claim references, never identifiers — appeal copy runs
  the scrub check structurally.
- **The timely-filing window** computed per claim from each payer's own contract as DATE ALERTS;
  at-risk dollars counted.

## Honesty rules (from `_kit`)
Costly eval label `needs_provider_doc`. Appeal ladder: 2 touches then a human call. Recovered-
this-week counted. ROI typed; the audit file is a scenario. Synthetic only; nothing is sent.
