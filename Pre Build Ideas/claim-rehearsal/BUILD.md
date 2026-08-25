# Rehearsal OS — the claim rehearsal (build 65)

**Working name:** Rehearsal OS · **Launch:** `prebuild-rehearsal-os` · **Port:** 8885
**Synthetic operator:** "Hargrove Insurance Group" — independent P&C agency, ~900 accounts.
(Distinct from build 4 Renewal OS, which works the renewal pipeline — Rehearsal OS runs the
CLAIM before the client ever has it.)

## The never-seen mechanism
Before each renewal, simulate the client's three most-probable claims against their ACTUAL
current policy — recorded limits, deductibles, exclusions — and show the out-of-pocket
surprise in dollars: "here's what your kitchen fire costs you today: $41,000, because of
these two recorded exclusions." The fix becomes the cross-sell. Agencies sell renewals on
price; nobody sells them by rehearsing the claim.

## Modules
1. **Policy record** (Company Brain) — per account: recorded coverages, limits, deductibles,
   exclusions (each with the policy-form citation); an account whose policy detail was never
   recorded reads UNREADABLE — a rehearsal cannot run on a policy we haven't read, and says
   so instead of guessing.
2. **The rehearsal engine** (Operations) — claim scenarios from a RECORDED scenario table per
   account type (homeowner: kitchen fire / water damage / liability slip; commercial: the
   trade's top three — config `_source`-named severity ranges). For each: walk the recorded
   policy → payout arithmetic → THE GAP in dollars, every exclusion/deductible cited by name.
   Severity is a RANGE (low/typical/severe), never one number — bands, not points.
3. **The fix sheet** (Sales) — each gap maps to the endorsement/limit change that closes it,
   priced from the recorded rate card; the draft leads with the rehearsal, not fear language
   (forbidden: "devastating", "lose everything", "God forbid" — tone-checked structurally).
4. **Renewal integration** (Back Office) — rehearsals run at T-60 before renewal (DATE
   ALERTS); the renewal packet = price + the rehearsal; counted: gaps found, gaps closed.
5. **Intake triage** (Intake) — costly label: the ACTIVE claim ("my basement is flooding
   right now" — claims-reporting script, carrier cited from the record, never coverage
   opinions mid-crisis) · rehearsal ask · quote ask · policy question · human.

## Guardrails (load-bearing)
- `promise_coverage` — **R0, never-promote.** Only the carrier adjusts a claim; the rehearsal
  is arithmetic on the recorded policy, and every sheet says so.
- `rehearse_unread_policy` — **R0, structural**: no recorded policy detail → UNREADABLE, no
  rehearsal, the gap named ("we read policies before we rehearse them").
- `fear_language` — **R0**; the tone check on every client draft (tested).
- `single_number_severity` — refused; ranges from the recorded table only.
- Outward drafts R1; the fix sheet cites every exclusion by its recorded form number.

## ROI (typed)
Retention lift at rehearsed renewals (counted, operator lift) · endorsement revenue (counted
gaps closed × recorded commission) · the uncovered-claim E&O file (scenario) · CSR hours
(time_saved).

## Demo path
An account's rehearsal: kitchen fire → $41k gap, two exclusions cited → the fix sheet priced
→ UNREADABLE refusal on an unrecorded policy → active-claim script → tone check refusal →
renewal packet with the rehearsal → trust tab.

## Build prompt
Shared contract, full built-out standard. Costly eval label: the active claim.
