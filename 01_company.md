# YourCo LLC

## One-line
Boutique AI-implementation consultancy. **Audit first, then build and operate a custom multi-agent AI OS** fit to the business — billed as outcomes, not features.

## The model in plain English
Every engagement starts with a **free Audit** (no charge while yourco is getting started — the Founder 2026-08-16, `decisions/2026-08-16_audit-is-free.md`; the $1,000/$1,500 price is suspended, not deleted): YourCo diagnoses how the business really runs and quantifies the bottlenecks costing it money. Then YourCo **builds and operates a custom AI OS** — a multi-agent system shaped to that business from the Audit findings, scaffolded and delivered by Kimi, with the first capability live in ~48 hours. **The custom OS is the product and the primary revenue generator.** A single named digital employee (its own email in the client's tenant) still exists — but it's the **entry rung, offered last**, not the goal — and landing there is a good outcome, not a failed sale (`decisions/2026-08-10_lead-high-land-anywhere.md`). Offering hierarchy, high→low revenue: **custom AI OS > a few employees > single employee.** The client never sees the tokens, the model, the prompts, the infrastructure, or the eval harness — they see a system that shows up, does the work, and is held to a standard. (Motion: `decisions/2026-06-16_audit-first-os-as-product.md`.)

## The defining principle
The client never touches tokens, models, or infrastructure. YourCo owns reliability, security, and ongoing improvement. They just get an outcome.

This is what distinguishes YourCo from a no-code operator, a freelancer building automations, or a SaaS tool. Anyone with $20/mo and Zapier can wire a workflow. Almost nobody can prove the workflow did its job in front of an executive sponsor.

### The model-upgrade dividend
Because YourCo owns the stack and sells the outcome, **every improvement in the underlying AI flows through to the client as a free upgrade**. When models get better, cheaper, or faster, YourCo swaps them in underneath; the client's outcome improves and their invoice doesn't change. A client who buys a *tool* holds an asset that depreciates as AI advances; a client who buys an YourCo *outcome* holds one that appreciates. This is the standing answer to the objection every buyer has — *"won't this be obsolete in a year?"* — the tools underneath will be replaced, repeatedly, on purpose; the outcome and the reliability layer that proves it only get better.

## The thesis
The agent tooling layer is commoditizing fast. New frameworks, agent builders, MCP servers, and orchestration platforms ship every week. None of them are a moat.

The durable, defensible business is the one that:
1. proves an agent did its job
2. integrates into real enterprise systems
3. holds executive-level trust

The reliability / eval / observability / approval layer is where the margin lives — and it is exactly what no-code operators cannot deliver.

## The moat (in delivery terms)
- **Eval gates** — every digital employee has measurable criteria for success; YourCo knows when it's right and when it isn't
- **Watchdogs** — runtime guards that detect drift, error patterns, cost anomalies, and out-of-scope behavior
- **Approval flow** — human-in-the-loop where stakes are high; clean audit trail for the rest
- **Integration depth** — real ERP, CRM, ticketing, and finance system integration, not screen-scraping
- **Executive-readable artifacts** — every engagement produces reporting an executive sponsor can read in 60 seconds

## What's parked (and why)
**Self-serve SaaS.** The idea is parked because going self-serve deletes the moat: a self-serve product cannot credibly own reliability and approval flow for an executive customer. YourCo only revisits this if/when the moat layer becomes so productized that "serve yourself" no longer means "absorb all the eval risk yourself."

If the Founder ever feels pulled toward SaaS, that's the signal to re-read this section before acting.

## Engagement shape
- Named digital employee with its own email in the client's tenant
- Live on first use case within ~48 hours
- Framed around business outcomes, not features
- Strict scope discipline — no scope creep, ever

## Delivery loop
See `02_delivery_loop.md` for full SOPs. Six stages:
1. Discovery
2. Build (from `yourco-template`)
3. Eval / gates / watchdogs
4. 48h go-live
5. Weekly iteration
6. Account expansion

## Internal platform
See `03_internal_platform.md`. Two parts:
- `yourco-template` — golden client template; every engagement starts from this
- `Atlas` — ops agent; monitors, triages, tracks cost across all active engagements

## ICP (v0 — locked 2026-06-07)
- **Long-horizon:** any business, any size, any scope.
- **Initial target (updated 2026-08-05, `decisions/2026-08-05_horizontal-targeting-warm-first.md`):** all industries from day one — the sequencing filter is **relationship, not vertical**: warm intros and known relationships first, SMB-primary but never size-disqualifying. Industry depth is emergent-but-engineered: after each close, mine that client's industry for the next 2–3 intros (proof transfers best inside an industry). The former lead-vertical stance (Landscaping/Hardscaping, locked 2026-06-07) is superseded; its campaign kit and pricing lock remain live assets, pointed wherever traction lands.
- **Buyer profile:** owner-operator. Decision-maker is the founder/principal. Buying motion is fast (single sponsor, no procurement layer). Language for this buyer is "owner peace of mind" / "fits the software you already use" / "morning brief texted to your phone" — not the enterprise "executive trust" framing.
- Full ICP reasoning + alternatives considered: `decisions/2026-06-07_icp-and-pricing-v0.md`.

## Pricing — pointers only

**Canonical numbers live in `pricing/v0/`. Polo owns them. Nothing is duplicated here**, because the
previous version of this section kept a full Landscaping rate table under a "superseded" banner, and a
reader skimming found `$1,500/mo` before they found the warning.

- **The unit of sale is the OS tier ladder** — Core · Suite · Operation · Command → `pricing/v0/os-tiers.md`
- **The single-employee on-ramp** (entry rung, offered last; cap 3 → graduate to a tier) → same file
- **The Audit is free** while yourco is getting started (2026-08-16) → `pricing/v0/audit.md`
- **Per-vertical pricing** → `pricing/v0/<vertical>.md`; reasoning + alternatives in
  `decisions/2026-06-07_icp-and-pricing-v0.md`

Two rules that are *about* pricing rather than a price, so they belong here:

1. **Pricing is vertical-specific, not universal.** Same three-layer structure everywhere; the dollars
   move with the vertical's economics.
2. **No cold prospecting at unlocked prices.** Every new vertical gets its own locked pricing decision
   before Reilly's first cold campaign in it. ⚠️ **Open (Polo, flagged 2026-08-05):** whether the
   horizontal OS bands govern *warm* deals in unlocked verticals, which the warm-first motion now makes
   the common case.

⚠️ **Watchpoint, carried forward:** a low onboarding price can signal "automation gig" rather than
"boutique implementation." Revisit after the first 3–5 closes on close-rate and retention.

## Remaining open items
- Current pipeline state — who's in discovery, who's live, who's expanding? (see `clients/_pipeline.md`)
- Founder time allocation — what % of the Founder's week is on delivery vs. sales vs. platform improvement?
