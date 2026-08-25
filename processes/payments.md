# Payments — how money moves (Stripe)

> **Rail: Stripe** (decided 2026-06-12, `decisions/2026-06-12_payment-collection.md`). Closes the launch-critical gap from the gap audit. Owner: **Charles** operates the flow + reconciles; **the Founder** owns the account + banking setup (account creation and entering bank details are the Founder's to do — never the agent's). **The client enters their own card/bank details into Stripe's hosted page — YourCo never keys or stores a client's payment numbers.**

## The two charges
1. **Build fee (the deposit)** — one-time, due on signing. A Stripe **payment link** (or invoice) sent with/after the signed proposal.
2. **Retainer** — recurring monthly, as a Stripe **subscription**, **ACH Direct Debit preferred** (card accepted). ACH (~0.8%/flat) protects margin vs card (~2.9%) on a $1.5–3k/mo retainer. Starts at go-live.

## Credits owed to the client (added 2026-08-24 — Charles)

Two clauses can reduce what a client owes. Both are **counsel-gated** (`counsel-gates.md` #19) and
neither is live until Ray clears them — but when they go live they are Charles's to compute, not
something to discover at the monthly close.

| Credit | Trigger | Amount | Applied |
|---|---|---|---|
| **Acceptance credit** | Go-live acceptance unmet **for reasons within yourco's control** | the retainer does not start, or that period is credited | on the next invoice |
| **SLA credit** | Availability or response target missed (`sla.md` §4) | per the SLA table, combined cap **[[50%]]** of that month's retainer | against the **following** month |

- The client claims an SLA credit in writing within **[[30]] days** of the monthly report; yourco does
  not wait to be asked where its own report already shows a miss.
- **An unmeasured month counts as a miss** (`sla.md` §6). If monitoring was down, the credit is owed —
  the side holding the logs carries that burden.
- Three consecutive missed months gives the client an **immediate termination right** with no notice-period
  liability (`sla.md` §4). That affects the final invoice; read it before prorating.

## The flow (per engagement)
1. **Signed proposal/SOW** (DocuSign) lands → David flags Charles.
2. **Collect the build fee** — send the Stripe build-fee link/invoice; **due on signing**. **The 48h clock starts at "go-ready" (signed + access granted + deposit *authorized*) — NOT at deposit *cleared*.** ACH takes 1–4 business days to clear; gating go-live on clearing would let the payment rail blow the 48h promise. So: start the build on authorization; if a client needs literal instant settlement for a same-day start, take the deposit by **card**. (Resolves the tabletop dry-run finding #4, `_archive/2026-06-12_commercial-path-tabletop.md`.)
3. **Start the retainer subscription** — create the Stripe subscription (ACH preferred) effective **go-live**; billing **on receipt / net 0** per the Engagement Agreement §2.
4. **Reconcile** — log every payment in `finance/revenue.md` (`invoice_date`, `paid_date`, `status`). Charles. Sync to QuickBooks later, when accounting is stood up.
5. **Dunning / late** — Stripe auto-retries failed charges. Per the Agreement: amounts >10 days past due accrue interest; YourCo may suspend after **15 days past due** with written notice + a 5-day cure period. Keep dunning consistent with the contract.
6. **Refunds** — Fees are **nonrefundable except as expressly stated** in the Agreement. No ad-hoc refunds without the Founder.
7. **Per-unit add-ons** (RE listings, vehicles, SKUs, proposals — Tier 2) — bill as metered usage or monthly invoice items on top of the base subscription.
8. **Offboarding** — stop the subscription on the effective date; final/prorated invoice (see `processes/offboarding.md`).

## Privacy / security (hard rules)
- YourCo and the agent **never enter, view, or store** a client's card or bank numbers. The client enters them on Stripe's hosted checkout/link.
- No payment data in our repo, CRM, or logs — only Stripe's tokens/IDs + the reconciliation status.
- PCI scope stays with Stripe by using hosted links/checkout (no card fields on our side).

## the Founder's setup checklist (his to do — agent cannot create accounts or enter banking)

> **Prepped 2026-08-16.** Every value Stripe will ask for is below, so the session is typing, not
> deciding. Account creation, bank connection and any card/bank number stay the Founder's by rule — the
> agent never touches them. Budget ~30 minutes once §0 is answered.

### §0 — Decide these BEFORE opening Stripe (this is where the setup stalls)
- [ ] **Business address.** Stripe requires one on the application. **This is the same unmade
      decision as counsel gate #3** (CAN-SPAM postal address — home vs PO box vs registered agent),
      so answering it here clears both. Do not start the application without it.
- [ ] **Statement descriptor** — what a client sees on their card/bank statement. Suggest `YOURCO`
      (≤22 chars, must be recognisable or it drives chargebacks).
- [ ] **Payout schedule** — daily / weekly / monthly to the business bank. Default daily is fine.

### §1 — Account + banking (the Founder only)
- [ ] Create the Stripe account. **Legal name: `YourCo LLC`** — *not* "YourCo LLC".
      The IRS CP-575G reads YOURCO LLC and Stripe validates the name against the **EIN**, so the
      state-filed name will fail verification. Both names and the EIN are in
      `finance/legal-docs/business-info.md` (sensitive — read it there, never paste it into chat).
      Entity type: **single-member LLC, Florida**.
- [ ] Connect the YourCo business bank account for ACH payouts.
- [ ] Enable **ACH Direct Debit** *and* card. ACH (~0.8%, capped) protects margin against card
      (~2.9%) on a $3,000–10,000/mo retainer — on a $5,000 retainer that gap is ~$105/mo.

### §2 — Products (create all three; amounts are per-deal, these are the Polo-locked bands)
| Product | Type | Amount | Source |
|---|---|---|---|
| **Audit** | one-time | **$1,000** Standard · **$1,500** Pro (compliance + multi-location) | `pricing/v0/audit.md` |
| **Implementation** (the build fee / deposit) | one-time | **$2,000–5,000** by tier — Core $2,000–2,500 → Command $4,500–5,000 | `pricing/v0/os-tiers.md` |
| **Retainer** | recurring monthly | **$3,000–10,000** by tier — Core $3,000–4,000 → Command $8,500–10,000 | `pricing/v0/os-tiers.md` |

- Create each as a product with a **custom/per-deal amount** rather than fixed prices — the bands
  are ranges Polo sets per engagement, and fixed prices would go stale on the next pricing pass.
- Two documented exceptions that must not become the default: **warm-network Audits run at $0** for
  the first three (100% credited if they proceed), and **Sample Client is $0 kickoff / $1,000/mo**,
  below the Core floor, on Brotherhood terms.

### §3 — Reusable templates
- [ ] A **payment-link template** for the Audit and for the Implementation fee (hosted checkout —
      the client enters their own details; PCI scope stays with Stripe).
- [ ] A **subscription template** for the Retainer, ACH-preferred, billing **on receipt / net 0**
      per Engagement Agreement §2, starting at **go-live** (not at signing).
- [ ] Set dunning to match the contract, not Stripe's defaults: interest past **10 days**,
      suspension available after **15 days** with written notice + a 5-day cure period.

### §4 — Hand off to Charles
- [ ] Grant Charles access to send links/invoices and read the dashboard for reconciliation.
- [ ] Record the resulting link URLs + product IDs in `finance/` (not here, and never a key) so
      Charles can send them without asking, and so `finance/revenue.md` reconciliation has the IDs.

Once set up: this moves off the launch-runbook blocker list, and the proposal/SOW's "deposit due on signing via Stripe" line goes live. **Until then a signed client cannot pay, and the Audit — the front of the entire motion — cannot be sold.**
