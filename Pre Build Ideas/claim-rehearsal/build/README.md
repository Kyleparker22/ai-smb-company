# Rehearsal OS — build

The claim rehearsal for independent insurance agencies. Port **8885** (`prebuild-rehearsal-os`).

```
python3 seed.py               # synthetic Hargrove Insurance Group (~900 accounts)
python3 test_rehearsal_os.py  # the suite
python3 server.py             # 127.0.0.1:8885
```

## The never-seen mechanism
Before each renewal, simulate the client's three most-probable claims against their **actual
recorded policy** — limits, deductibles, exclusions, each cited by form number — and show the
out-of-pocket gap in dollars at three severities. The demo account's typical kitchen fire leaves
**$41,000** with the client, driven by two recorded exclusions (HX 21 44, HX 30 06) and the
deductible; the fix sheet prices each closing endorsement from the recorded rate card. The fix
sheet is the cross-sell; the renewal packet is the rehearsal riding beside the price.

## The load-bearing refusals
- **No coverage promises (R0, never-promote).** A rehearsal is arithmetic on the recorded
  policy; only the carrier adjusts a real claim, and every sheet says so.
- **UNREADABLE (R0, structural).** No recorded policy detail → no rehearsal, ever — "we read
  policies before we rehearse them." The fix is a policy review, and that is the whole
  recommendation.
- **No fear language (R0).** "Devastating", "lose everything", "God forbid", "nightmare" are
  structurally refused on every client draft — the arithmetic carries the weight.
- **No single-number severity (R0).** Loss is a recorded range — low / typical / severe. Asking
  the API for one number returns a refusal, logged.
- **The active claim reads first.** "My basement is flooding right now" gets the
  claims-reporting script — the recorded carrier and claim line, safe next steps — and never a
  coverage opinion mid-crisis.
- A fix with no recorded rate renders blank with the reason; a price is never invented.

## Honesty rules (from `_kit`)
Costly eval label `active_claim` (15 cases, empty → human). Renewals: T-60 DATE ALERTS from the
record, never advice. Gaps counted from the event log — found when the rehearsal runs, closed
only when a human records the endorsement. Counted week with a baseline delta that refuses
without a prior week. ROI typed; the uncovered-claim E&O file is a scenario line the operator
prices. Outward drafts queue at R1; approvals are the human's act in the log. Append-only
events; white-label; synthetic only (invented carriers and insureds, 555 claim lines).

**Nothing is sent.**
