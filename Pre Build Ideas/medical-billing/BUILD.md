# Claim OS — medical billing service (build 37)

**Working name:** Claim OS · **Launch:** `prebuild-claim-os` · **Port:** 8857
**Synthetic operator:** "Meridian Practice Solutions" — billing for 14 small practices, ~$3M fees.

## The bleeding neck
Denied claims die quietly: every payer has a timely-filing window, and a denial nobody works
before it closes is the client's money gone forever — the billing service's one unforgivable
failure. The opposite failure is worse: "fixing" a denial by upcoding is fraud with the service's
name on the 837.

## Modules
1. **Denial triage** (Operations) — appealable · needs-provider-documentation · miscoded
   (downcode/correct only) · true write-off candidate (a human decides). Typed by denial reason.
2. **Timely-filing calendar** (Company Brain) — per-payer windows (config names itself a default)
   computed per claim as DATE ALERTS; at-risk dollars counted.
3. **The upcoding refusal** (Back Office) — a code can never be changed to a higher-RVU code
   without a recorded provider-documentation reference. Correcting DOWN is R2; UP is gated on the
   record and still R1.
4. **Clean-claim gate** (Operations) — a claim missing required fields cannot be submitted; the
   refusal names each missing field.
5. **Appeal ladder** (Back Office) — drafted appeals citing the recorded denial reason + the
   documentation reference; bounded, deadline-aware.

## Guardrails (load-bearing)
- `upcode_without_documentation` — **R0.** The fraud line, structurally unexpressable.
- `submit_incomplete_claim` — **R0**, fields named.
- PHI discipline — outward drafts carry claim/account references, never full patient identifiers
  (tested: no DOB+name pairs in copy).
- Write-offs — a human decides, always (R1, never promoted).

## ROI (typed)
Denials worked before the window (counted × avg claim) · at-risk dollars surfaced (counted) ·
posting hours (time_saved) · the audit file (scenario).

## Demo path
Board (AR aging, at-risk timely-filing) → triage a denial → try to upcode (refused) → appeal
draft citing the denial → trust tab.

## Build prompt
Shared contract, full built-out standard. Costly eval label: the appealable denial approaching
its filing deadline.
