# 2026-08-07 — Downline override stays uncapped (no depth limit)

## Decision
The connector downline override remains **1% of client revenue across the entire downline, unlimited
depth** — the v1 design (`decisions/2026-06-30_referral-program-v1.md`) is unchanged. A proposed 2-level
cap was **declined by the Founder** ("No cap").

## Context
While answering the Founder's question about how the family-tree commission flows, the stacking arithmetic was
computed and surfaced: the 1% is flat at every depth **and every ancestor earns their own 1%
separately**, so a client recruited at depth *N* costs the direct commission (10–15%) **plus N × 1%** —
roughly 25% of that client's retainer at depth 10, unbounded as trees deepen. A 2-level cap was proposed
(preserving most real-world incentive while capping worst-case load at direct + 2%). the Founder declined it.

## Why (the Founder's call — terms are the Founder/Polo)
Unlimited depth is the design's point: it makes recruiting connectors genuinely worth doing for the
people at the top and gives the program its compounding character. The counter-argument (margin load +
regulatory exposure) was made and heard; the Founder's judgment is that the incentive matters more than the
capped downside, and that the compliance question should be answered by counsel on the design as
intended rather than pre-compromised by an internal hedge.

## What this decision obligates
1. **Counsel prices unlimited depth as designed** — checklist item 4 was rewritten to ask whether
   uncapped depth is defensible, and if so **which non-depth guardrails** carry the compliance weight
   instead (per-client load ceiling · aggregate earnings cap · active-book qualification to earn any
   override · anti-stacking rules · income disclosure). This remains the program's hard gate: no
   override is offered to anyone until §A/§B clear.
2. **Polo prices retainers knowing the worst case.** Total payout load on a single client's revenue is
   *unbounded by design*; pricing must not assume the direct commission is the ceiling. Flag for the
   quarterly pricing review once real trees exist.
3. **Charles models it at close.** Commission owed is computed from the same `buildRepPayouts` source
   the CRM Referrals cockpit uses — that math already walks the full tree, so no change is needed; the
   watch item is margin, not mechanics.
4. **The CRM is already correct** — the downline tree, the override math, and the payout report all
   assume full depth. Nothing to change in code.

## Reversibility
High, and likely externally forced rather than internally chosen: if counsel finds unlimited depth
indefensible, the Founder picks the minimum change that preserves intent (per-client load ceiling before depth
cap, if the choice is his). Revisit also if a real tree's override load measurably squeezes margin at
the monthly close.
