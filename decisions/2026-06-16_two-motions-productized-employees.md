# 2026-06-16 — Two motions: off-the-shelf employees AND audit → custom OS

## Decision (the Founder)
yourco runs **two go-to-market motions under one brand**, marketed in parallel:

1. **Off-the-shelf digital AI employees — productized, subscribe-and-go.** No forms, no quotes, no
   calls, no audit. You pick a pre-scoped employee from a catalog, subscribe, and it's live fast —
   **pause anytime.** Low friction, low time-to-value (TTV), the volume / self-serve-*purchase* entry.
   *Still fully operated by yourco* (see guardrail) — the client never touches tokens/models/infra.
2. **Audit → custom AI OS — consultative, bespoke, premium.** Unchanged from
   `2026-06-16_audit-first-os-as-product.md`: the Audit is the mandatory front door for a *custom
   build*, then Kimi + the scaffolder build the multi-agent OS. The high-ACV, high-stickiness motion.

This is the **DesignJoy/productized-services model** (Brett Williams interview, `agents/brett/competitive-watch.md`)
applied to the *entry tier*, sitting alongside yourco's consultative core. Lower TTV, wider funnel, two
front doors.

## Why
- **The off-the-shelf employee captures the buyer the audit loses:** the small/price-sensitive owner,
  the impulse/fast buyer, the one who won't sit for a diagnostic. Brett's whole thesis: productized,
  off-the-shelf, low-TTV wins because "companies value speed," and clients "pay before they ever talk
  to you." That's a market yourco currently has no SKU for.
- **It's the best distribution + proof artifact.** A subscribe-and-go employee (and the free Quick
  Audit) are launch-able on Product Hunt and shareable in a way a "book a call" consultancy is not
  (`processes/launch-runbook.md`). The "see yours" instant demo already exists as the top of it.
- **High margin, solo-scalable** — Brett does ~$1M/yr solo at ~$1k/mo expenses on exactly this shape.

## The hierarchy still holds
Offering hierarchy (revenue/value) is unchanged: **custom AI OS > a few employees > single employee.**
What changes: the **single employee now has two routes** — (a) a productized self-serve *purchase*
off the catalog (new), and (b) the down-sell at the end of an audit conversation (existing). The site
**leads with the OS** for high-intent/bigger businesses and **offers the off-the-shelf employee** as the
low-friction door for everyone else. Up-sell path: catalog employee → more employees → audit → custom OS.

## The guardrail that protects the moat (critical)
**Off-the-shelf ≠ self-serve operation.** "Subscribe-and-go" productizes the *purchase + onboarding*,
NOT the *operation*. yourco still builds it, runs it, evals it, gates approvals, and owns reliability on
an ongoing basis — the client subscribes to an *outcome*, they don't run software. This is the **same
carve-out** as yourco Care (operated DTC), and it is explicitly **NOT** the parked self-serve SaaS
(which = client absorbs the eval/reliability risk; that stays parked, `01_company.md`). If a request
needs real scoping/custom integration, it routes to the audit→OS motion — only **pre-scoped, known,
reliable patterns** (front desk / intake, follow-up, scheduling/recall, review-response, back-office)
become catalog SKUs (`clients/_yourco-template/employee-patterns*.md`).

## Amends the audit-first decision
`2026-06-16_audit-first-os-as-product.md` said the Audit is the mandatory front door for **every**
engagement. **Amended:** the Audit is mandatory for a **custom OS / bespoke build**. It is **not** required
to buy a pre-scoped catalog employee (the scoping is already done — that's what "productized" means).
Everyone who wants something *custom* still starts with the Audit.

## Resolved (2026-06-17)
- **Name:** customer-facing = **"Ready-to-Hire" employees / "Hire one today"** (internal name stays
  "off-the-shelf"). Framed as **hiring, not subscribing** — which keeps the "Hire, don't subscribe"
  manifesto intact even though billing is monthly (you hire an employee that happens to be billed monthly;
  you don't rent a tool). Catalog: `hire.html` (config `hire-config.js`); onboarding wizard:
  `hire-onboarding.html`.
- **Billing terms (the Founder):** **month-to-month, pause anytime (unused time rolls over), cancel anytime, NO
  minimum / no contract.** Low-friction is the whole point — a minimum kills the subscribe-and-go appeal.
  The custom OS keeps its 6-month minimum (different motion). Annual-commit discount optional (Polo).
- **Onboarding:** a **guided intake wizard** per employee (`hire-onboarding.html` renders each SKU's `needs`)
  that collects exactly what's required to build + integrate it — **plus** a "rather do a 10-min call?"
  fallback with a *have-these-handy* checklist (per-SKU `haveHandy`). Both, not either/or. **Owned by Janice**
  (the Onboarding Agent) — this productized wizard is the self-serve front of her onboarding job; the 10-min
  call routes to her too. (Janice → Kimi builds, same seam as the signed-deal flow.)
- **Transparent pricing:** **yes for the catalog SKUs** (the exception to the no-prices rule — needed for
  subscribe-and-go; DesignJoy/Off Menu both post). Audit + custom OS stay quote-on-call. Polo proposes the
  per-SKU prices (`pricing/v0/ready-to-hire.md`); until locked, `hire-config.js` `price: null` renders
  "Pricing at launch."

## Still open (platform)
- **Pause-anytime billing → runtime implication.** Pausing an *operated* employee means cleanly
  pausing/resuming that client's runtime + billing. Kemba: a clean per-client pause/resume in the
  always-on runtime. Not free — flag for the platform roadmap.
- **Productized build/onboarding SLA + live checkout.** "Live this week" needs a near-zero-touch build path
  for catalog patterns (scaffolder + Kimi's golden patterns) so a hire doesn't trigger a bespoke project,
  and a real **Stripe subscribe/checkout** flow on `hire.html` (currently the CTA goes to the onboarding
  wizard; checkout wires in at launch, same as the rest of the site).

## Owners
**Webb** (the catalog / subscribe flow / checkout on the site) · **Janice** (the onboarding wizard + intake +
the 10-min setup call) · **Polo** (SKU pricing + the transparent-pricing call) · **Kimi** (productized golden
build patterns) · **Kemba** (runtime pause/resume) · **Reilly/Michelle/Katie** (market both — the off-the-shelf
employee *and* the audit→OS). the Founder approves.

## Status
**Direction set 2026-06-16.** Staged like everything external (launch-gate + Polo pricing). The pieces
that already exist and feed this: `instant-employee.html` ("see yours"), `build-your-employee.html`
(configurator), the Tier-1 employee patterns, the Revenue Leak Snapshot. The new build is the **catalog → subscribe/
checkout → pause-anytime** flow + the productized SKU pricing — sequenced after the core SMB launch proves
out, so it doesn't pull focus (per the portfolio-focus memo, `loops/advisor/2026-06-16_offering-portfolio-focus.md`).
