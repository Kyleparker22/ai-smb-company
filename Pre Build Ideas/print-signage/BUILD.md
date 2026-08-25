# Proof OS — print & signage shop (build 39)

**Working name:** Proof OS · **Launch:** `prebuild-proof-os` · **Port:** 8859
**Synthetic operator:** "Meridian Print & Sign" — wide-format + offset, ~$4M, chronic rush jobs.

## The bleeding neck
Every eaten reprint traces to the same sentence: "they said go ahead." A job that reaches the
press without a RECORDED proof approval is a coin flip billed at margin. Meanwhile the jobs that
have money waiting are stalled on a customer who hasn't clicked approve — and nobody chases the
click. Rush work displaces scheduled work invisibly.

## Modules
1. **The proof gate** (Operations) — a job cannot move to production without a recorded proof
   approval (who, when, which revision). THE refusal. Verbal approval is a note, not a gate pass.
2. **Approval chase ladder** (Sales) — jobs-waiting-on-proof aged and chased; the copy says
   plainly that the clock starts at the click.
3. **Message triage** (Intake) — art inbound · proof approval/change · rush request · complaint.
4. **Capacity promise dates** (Operations) — Traveler pattern: a date computes from recorded
   press capacity or is refused; rush requests show what they displace.
5. **IP red flags** (Company Brain) — jobs whose art carries third-party marks (config keyword
   list) queue for a human authorization check; software never approves those to press.

## Guardrails (load-bearing)
- `produce_without_proof_approval` — **R0 by construction.**
- `promise_date_without_capacity` — **R0**; the arithmetic or nothing.
- `approve_trademarked_art` — **R0**; a human confirms the customer's right to print it.
- Color-match complaints — the reply cites the approved proof revision, or admits no approval
  exists (Crew OS two-shape honesty).

## ROI (typed)
Reprints avoided at the gate (scenario — prevented errors can't be counted) · proof-stalled
revenue released (counted) · scheduling hours (time_saved) · rush displacement made visible
(counted).

## Demo path
Board (jobs aging on proofs) → send the unapproved job to press (refused) → chase copy → rush
request showing displacement → trust tab.

## Build prompt
Shared contract, full built-out standard. Costly eval label: a proof-approval message misread
(the click that never got recorded).
