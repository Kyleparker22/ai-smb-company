# Decision — Billing + rep-commission cadence: 1st / 3-day buffer / 2nd-Friday payout

**Date:** 2026-07-05 · **Owner:** the Founder (locked the cadence) + Charles (runs billing + payouts) + Polo (terms) + Ray (agreement language) · **Status:** locked; staged with the rest of the referral program (nothing pays out until reps exist + counsel clears the program).

## Decision
yourco clients **auto-pay their monthly retainer on the 1st of each month** (for that month, in advance). A **3-day collection buffer** (through end-of-day the 4th) absorbs ACH settlement and failed-card retries. **Rep commissions are paid on the 2nd Friday of the same month**, computed on revenue actually **collected by the end of the buffer**. Anything that collects after the buffer (late retry, mid-month signup) **rolls into the next 2nd-Friday payout** — no proration, no partial runs.

## Context
the Founder set the cadence while building the rep packet ("clients pay the 1st, 3-day buffer — fair? — pay reps the 2nd Friday"). The prior placeholder term was "monthly, in arrears, net-30," which was vaguer and slower.

## Options considered
- **Net-30 in arrears** (the v1 placeholder) — safe but slow; a rep waits up to ~6 weeks after a client's payment to see the commission, and "net-30" is a mushy promise.
- **Pay immediately on collection** — fastest, but creates dribbling micro-payouts all month and no clean reconciliation point.
- **1st + buffer + fixed 2nd-Friday payday (chosen)** — one billing day, one reconciliation window, one payday.

## Why
- **Timeline works:** the 2nd Friday falls on the 8th–14th, so Charles gets 4–10 days after the buffer to reconcile collected revenue, compute tiers + downline overrides, and run payouts.
- **Safe by construction:** commissions are only ever paid on cash already collected (never booked/unpaid), and the existing **60-day clawback** covers refunds after a fast payout.
- **A rep-experience win:** "paid the second Friday of every month" is concrete and *faster* than net-30 — a genuine recruiting line that costs yourco nothing extra.
- **Ops-simple:** one auto-pay date + one payday = a monthly close rhythm Charles can automate (billing run on the 1st, reconciliation the 4th–5th, payout file the 2nd Friday).

## Mechanics (for Charles)
1. **1st:** retainer auto-charge (card/ACH) for the current month.
2. **1st–4th:** retries/settlement window. End of the 4th = the collection cut for this month's payout.
3. **2nd Friday:** payout run — each rep's tier from active-client count, direct % on collected retainers, + the (counsel-gated) 1% full-downline override; statement issued with book/tier/next-tier nudge.
4. **Collected after the 4th:** included in the *next* month's 2nd-Friday run. Mid-month signups: their first payment (whenever collected) lands in the following payout.
5. Clawback per program terms (refund/chargeback ≤60 days deducts from the next payout).

## Reversibility
Cadence-only — fully reversible before any rep exists; after reps sign, changes apply prospectively (same rule as rate changes). Client billing-date exceptions (a client who can't do the 1st) are allowed per-engagement; their collections simply map to whichever payout window they clear in.

## Updated by this decision
- `processes/partnerships/rep-packet.md` + `rep-packet.html` — "net-30 in arrears" → the concrete schedule.
- `processes/partnerships/referral-program.md` §Terms — same.
- Client billing norm (pay-the-1st, auto-pay) becomes the default in proposals/engagement agreements — Ray folds into the agreement drafts (`processes/partnerships/legal/`, engagement agreement).
