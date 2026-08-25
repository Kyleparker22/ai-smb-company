# Remit OS — the reimbursement autopsy (build 66)

**Working name:** Remit OS · **Launch:** `prebuild-remit-os` · **Port:** 8886
**Synthetic operator:** "Lakeside Pharmacy" — independent pharmacy, ~310 scripts/day, three
PBM contracts.

## Why this industry
Independent pharmacies are cash-bleeding and utterly unserved: every PBM remittance carries
underpayments, DIR-fee drift, and contract-vs-paid gaps that nobody has time to audit. The
tooling exists only as expensive consultants. This is Claim OS's logic aimed at the other
direction of the money.

## The never-seen mechanism
Every remittance line reconciled against the RECORDED contract terms — rate basis, dispensing
fee, DIR schedule — and every underpayment lands in a recoverable ledger with the appeal
draft attached, citing the contract clause and the delta to the cent.

## Modules
1. **Contract register** (Company Brain) — per PBM: recorded rate terms, dispensing fees, DIR
   schedules, appeal windows (DATE ALERTS); a PBM with unrecorded terms reads UNAUDITABLE —
   "we can't audit against a contract we haven't recorded," never a guessed benchmark.
2. **The autopsy** (Operations) — remittance lines vs contract arithmetic; each variance:
   expected (per the clause, cited) vs paid vs delta; variances classify (underpaid /
   DIR-drift / correct / contract-ambiguous — ambiguous goes to a HUMAN with both readings
   shown, never auto-resolved in either direction).
3. **The recoverable ledger** (Back Office) — every confirmed underpayment aged against the
   recorded appeal window; appeals draft R1 with clause + delta; recovered dollars counted
   from remittance corrections, never estimated.
4. **Margin truth board** (Operations) — per-script margin from recorded acquisition cost vs
   paid; the counted list of scripts DISPENSED AT A LOSS (the number every owner suspects
   and never sees); no recorded acquisition cost → that script reads unmeasured.
5. **Intake triage** (Intake) — costly label: the patient safety message ("I think I got the
   wrong pills" — pharmacist NOW, never a queue) · PBM/insurance question · refill ask ·
   price complaint · human. NO PHI in any outward draft (the scrub, tested — patients are
   invented, but the pattern is structural).

## Guardrails (load-bearing)
- `audit_without_recorded_contract` — **R0**; UNAUDITABLE, gap named.
- `auto_resolve_ambiguous_clause` — **R0**; both readings to a human.
- `estimate_recovered_dollars` — **R0**; recovered = counted corrections only.
- `wrong_med_message_queued` — **R0**; the pharmacist-now script is the whole reply.
- `phi_in_outbound` — **R0, structural** scrub (the medical-billing pattern).
- Appeals and outward drafts R1.

## ROI (typed)
Recovered underpayments (counted from corrections) · loss-dispensing caught (counted × the
recorded cost) · appeal-window saves (counted DATE ALERTS) · owner audit hours (time_saved).

## Demo path
A remittance autopsy: the underpaid line with clause + delta cited → the appeal draft → an
ambiguous clause going to a human with both readings → the dispensed-at-a-loss board →
UNAUDITABLE PBM refusal → wrong-pills script → trust tab.

## Build prompt
Shared contract, full built-out standard. Costly eval label: the wrong-medication message.
