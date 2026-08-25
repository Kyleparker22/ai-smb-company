# One referral rate card — a referring client IS a connector (2026-08-13)

**Decided by:** the Founder. **Supersedes** the Type 1 / Type 2 split in `decisions/2026-06-30_referral-program-v1.md`.
**Locks:** referral economics

## The problem

Two programs paid different money for identical work.

- **Type 1** — a client refers → flat **$100/mo credit** off their own retainer, per active referred client.
- **Type 2** — a connector refers → **10% / 12.5% / 15%** of referred MRR by active-client count.

The flat $100 was calibrated to a ~$1,000/mo engagement — it is exactly 10% of one. It was never
re-based when the **$3,000/mo Core floor** was set. So by August 2026 the *same referral* paid a
connector **$300/mo** and a client **$100/mo**.

Nobody chose that. It is an artifact of a number that stopped tracking the thing it was derived
from — and it was invisible to everyone except the person on the wrong end of it. the Founder spotted it
from the other direction: *if a client refers someone, that client is a connector.*

## The decision

**One rate card. Everyone who refers earns the escalator.** The only difference is how it is paid.

| Who refers | Paid as |
|---|---|
| A client | **credit against their own bill**, floored at $0 — then **cash** above it |
| A connector who is not a client | cash |
| A client who churns | cash — they keep earning on referrals still live |

A client becomes a **full connector on their first referral**, including the downline and the 1%
override.

## Why credit-then-cash rather than a cap

A credit is bounded by the bill, so overflow needs an answer. Three were considered:

1. **Cap at the bill.** Simplest, never creates a payee. Rejected: a $1,000/mo client hits the
   ceiling at ~3 referrals, so the 6+ and 11+ tiers are unreachable for exactly the person you
   most want referring. A mechanism that stops rewarding your best referrer is self-defeating.
2. **Carry the excess forward.** No cash, no 1099, but it accrues an open-ended liability and
   reads as funny money to the client.
3. **Credit to $0, cash the overflow.** ← chosen. Most client-connectors never overflow, so most
   never become a 1099 payee; the ones who do are earning more than their own bill and the
   paperwork is obviously worth it.

At the top tier the overflow case is the *design target*, not an edge case: a client referring
eleven $3,000/mo clients earns **$4,950/mo**, which exceeds any plausible bill.

## Churn

A churned client keeps earning, in cash, on referrals that are still live. The referred clients
still pay yourco; cutting someone off the day they leave is how a referral source becomes a
detractor. In the implementation this needs no special case — a churned client has no live deal,
so their bill is $0 and the whole commission falls through to cash.

## ⚠️ What this widens, stated plainly

Under `decisions/2026-08-11_connector-program-v2.md` connectors **recruit** connectors from R1 and
earn a **1% full-downline override** — already the counsel gate's second hard stop (**item 4c**:
bounty on non-revenue events + recruit-at-R1 + uncapped depth).

Making every referring client a connector **automatically enrolls the client base into that
structure**. A happy customer getting a discount and a downline recruiter are different legal
objects, and this decision converts the first into the second on one referral.

Claude recommended making the *rate* automatic but *recruiting* an explicit opt-in at signature.
**the Founder chose full connector on first referral.** Recorded as the founder's call, not a finding —
and recorded so the counsel gate reflects the actual scope rather than the narrower one it was
written against. See `processes/counsel-gates.md` item 4c.

Two characterisation questions ride the existing gate rather than opening a new one:

- A **bill credit** is a price reduction (reduces yourco revenue; generally not income to the
  client). A **cash commission** is 1099 income. The same obligation is now delivered both ways
  depending on size, and the credit portion is likely safer described as a *discount* than a
  *commission*.
- Charles needs the revenue model: a client riding to a **$0 net bill** while referring is
  plausibly the best customer yourco has, and shows on the P&L as $0 MRR.

## Consequences already applied

- `crm/index.html` — `buildRepPayouts()` is now the single engine: both referral link styles
  (`referredByCompany` id, `referrer` name) resolve to one key; each row carries
  `isClient · bill · credit · cash · netBill · churned`. `clientReferralCredits()` and the
  `CLIENT_CREDIT` constant are **deleted**, not left returning empty — a dead function that still
  computes something is how a retired rate quietly comes back.
- Payouts (section 10) splits **Connectors (cash)** from **Client-connectors (credit)** and shows
  the arithmetic per row — bill, commission, credit, overflow, net bill. A client told their
  invoice is $250 must be able to reconstruct why.
- **Copy payout summary** now splits by *how* someone is paid, because Charles hands the cash list
  to a payment run and the credit list to invoicing — two different actions in two systems.
- Self-referral rule restated: no commission on your own bill; the engine drops self-referring rows.
- `crm/connector_statements.py` still carries `CLIENT_CREDIT = 100` — **open**, see below.

## Open

- [ ] `crm/connector_statements.py` — port to the unified engine (still computes the retired flat credit).
- [ ] Charles: model the $0-net-bill client in the revenue plan.
- [ ] Ray: characterisation of credit-vs-cash, and the widened 4c scope.
- [ ] Polo: confirm the escalator is still the right rate now that it applies to clients too — it
      was priced for a sales force, not for a customer base.

## Trip-wire

Revisit if **any** of these becomes true:

- A client-connector's credit exceeds their bill for **3 consecutive months** — the cash-overflow
  path is now load-bearing and needs the payee process actually built, not assumed.
- **5+ clients** become connectors before counsel clears item 4c — the exposure is real and
  accruing, not theoretical.
- The Core floor moves again — the escalator is a percentage so it self-adjusts, but confirm no
  other flat number was left behind the way the $100 was.
