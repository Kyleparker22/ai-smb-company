# Decision — payment collection rail → Stripe

**Date raised:** 2026-06-12 (gap audit) · **Decided:** 2026-06-12 — **Stripe** (the Founder) · **Status:** ✅ settled; remaining = the Founder's account/banking setup · **Owner:** Charles (operate) · the Founder (setup)

> **Decision: Stripe.** Operating SOP → `processes/payments.md`. Build fee via Stripe payment link (deposit on signing) + retainer via Stripe ACH subscription. "Deposit due on signing via Stripe" wired into `processes/contracts/proposal-sow.md`. Remaining action is the Founder's only (create account, connect bank, enable ACH — the agent cannot) per the setup checklist in `payments.md`. Books reconcile into `finance/revenue.md`; QuickBooks later.

## The gap
The Engagement Agreement states payment *terms* (deposit on signing, retainer on receipt, card/ACH) and `finance/revenue.md` logs invoices — but there's **no mechanism to actually collect money.** QuickBooks was deferred (Intuit returned 403 / no account). Launch-critical: day 1 with a paying client, you must take a deposit + start a recurring retainer, and today you can't, cleanly.

## What the rail has to do
1. **One-time build fee** (the deposit) — a clean invoice / payment link at signing.
2. **Recurring monthly retainer** — automated subscription billing, not a manual invoice every month.
3. **ACH preferred for the retainer** — card fees (~2.9%) on a $1.5–3k/mo retainer add up; ACH is ~0.8% or flat.
4. **Professional feel** — enterprise buyers expect a real invoice / portal, not a Venmo request.
5. **Books reconcile** — feed `finance/revenue.md` (and QuickBooks later, when accounting is set up).

> Note: setting up the account + entering banking credentials is **the Founder's to do** (prohibited for the agent). This doc is to pick the rail; the assistant can then write the operating SOP and the per-invoice/checkout templates.

## Options
| Option | Build fee | Recurring retainer | ACH | Setup effort | Notes |
|---|---|---|---|---|---|
| **A · Stripe** *(recommended)* | Invoices + payment links | ✅ Subscriptions (native) | ✅ ACH Direct Debit | Low | Cleanest for one-time + recurring in one place; payment link drops into the proposal; great APIs if we later automate. |
| **B · QuickBooks Payments** | Invoices | Recurring invoices | ✅ | Medium | Unifies billing + accounting — but it's the deferred path (no account yet); heavier; earlier auth failed. |
| **C · Square / PayPal Invoicing** | Invoices | Recurring (lighter) | Square ✅ / PayPal limited | Low | Simple, but less polished for recurring/enterprise; PayPal feel is consumer. |
| **D · Manual invoice + ACH/check/wire** | PDF invoice | Manual each month | bank ACH | None | Zero processor, zero fees — but fully manual, slow, no automation, no card option for clients who want it. Fine as a stopgap. |

## Recommendation
**Option A — Stripe.** It's the only one that does the one-time build fee *and* the automated recurring retainer cleanly, supports ACH to protect margin on the retainer, gives you a payment link to embed in the proposal/SOW, and leaves the door open to automate billing later. Books still reconcile into QuickBooks when you stand up accounting. **Stopgap if you want zero setup before the first deal: Option D** (manual ACH invoice), then move to Stripe.

## Next step once the Founder picks
Assistant writes: the payment SOP (`processes/payments.md` — deposit on signing → retainer subscription → reconciliation into `finance/revenue.md`), the invoice/checkout language, and wires "deposit due on signing" into the proposal/SOW. the Founder sets up the account + banking (his to do). Then this doc moves to a settled `decisions/` entry and off the launch-runbook blocker list.
