# 2026-06-07 — ICP + Pricing v0

> ⚠️ **Pricing superseded:** the $4k-build/$750-mo-era numbers below were re-anchored 2026-06-16 (`pricing/v0/vertical-ranges.md`) and resolved into the OS tier ladder (`pricing/v0/os-tiers.md`); the business-plan model was re-run against them 2026-07-06 (`2026-07-06_business-plan-os-pricing-rerun.md`). The ICP reasoning stands.

## Decision

### ICP (Ideal Customer Profile)
- **Long-horizon:** any business, any size, any scope. YourCo's model is meant to scale across the full B2B landscape.
- **Initial target (v0):** SMB services businesses. Specifically:
  - Real estate / brokerage
  - **Landscaping / Hardscaping** ← lead vertical
  - Roofing
  - Insurance / adjusting
  - Wealth management
  - Law firms
  - Adjacent services businesses fitting the same operator-buyer pattern

### Lead vertical (v0)
**Landscaping / Hardscaping.** First vertical YourCo will sharpen `yourco-template` against. Reilly's outbound, Katie's content, Reed's demos all bias to this vertical until the Founder decides to expand.

Concrete digital-employee shapes that fit landscaping immediately:
- Lead intake / qualifier (answers inbound calls/texts, qualifies, books estimates)
- Estimate drafter (intake notes + property photos → quoted proposal)
- Schedule coordinator (crews, weather rescheduling, customer notifications)
- Follow-up / collections (chases unpaid invoices, re-engages cold leads pre-season)
- Review harvester (texts customers post-job for Google reviews)

### Pricing framework (v0)
Pricing is **vertical-specific**, not universal. All verticals use the same three-layer structure (onboarding + per-agent setup + bundled MRR with marginal pricing on additional agents). Dollar amounts vary by vertical to reflect that vertical's economics, willingness-to-pay, and competitive landscape.

**Rule:** every new vertical YourCo prospects gets its own pricing decision doc locked **before** Reilly's first outbound campaign in that vertical. Pre-locking prices for verticals not yet validated is a spreadsheet exercise; locking based on first prospect conversations is evidence-based.

### Landscaping / Hardscaping pricing (v0 — the only locked vertical)

| Line item | Amount | Notes |
|---|---|---|
| Company onboarding | **$1,000 one-time** | Covers tenant access, brand/voice training, integration mapping with their stack (Jobber/Aspire/QuickBooks), exec-sponsor alignment, company-level eval criteria |
| Per-digital-employee setup | **$1,000–$2,000 one-time each** | Scope-dependent. Simpler agents (review harvester) → lower end; complex multi-integration agents (estimate drafter, scheduler) → higher end |
| Monthly retainer | **$1,500/mo** for the first digital employee; **+$250/mo** per additional digital employee on the same account | Includes watchdog ops, weekly iteration, eval updates, monthly readout. **Token spend absorbed by YourCo.** Marginal pricing rewards account expansion (delivery loop stage 6) |

### Other verticals — directional ranges (NOT locked; will be set per-vertical when Reilly approaches)
For reference only — do not quote externally. Lock via decision doc before prospecting.

| Vertical | Onboarding (range) | Per-agent setup (range) | First agent (range) | Each +agent (range) |
| --- | --- | --- | --- | --- |
| Roofing | $1,000 | $1k–$2k | $1,500/mo | +$250/mo |
| Real Estate / brokerage | $2,000 | $1.5k–$3k | $2,000/mo | +$300/mo |
| Insurance / Adjusting | $2,500 | $2k–$3k | $2,500/mo | +$400/mo |
| Law Firms | $3,500 | $2k–$4k | $3,500/mo | +$500/mo |
| Sample Contact | $5,000 | $3k–$5k | $4,000/mo | +$600/mo |

Spread rationale: tighter-margin owner-operator businesses (landscaping, roofing) get accessible pricing; high-WTP regulated verticals (wealth management, law) get premium pricing that reflects compliance complexity and revenue per advisor/attorney.

### Pricing math reference (landscaping/hardscaping baseline)
- 1 agent client → $2,500 upfront + $1,500/mo = **$20,500 Y1**
- 2 agent client → $4,000 upfront + $1,750/mo = **$25,000 Y1**
- 3 agent client → $5,500 upfront + $2,000/mo = **$29,500 Y1**
- 15 clients × ~2 agents avg → **~$375k Y1 revenue**

Higher-WTP verticals (law, wealth mgmt) materially shift this math upward once unlocked — a 5-client wealth-mgmt portfolio could rival 15-client landscaping portfolio revenue.

## Context
The OS reached the point where the bottleneck is no longer infrastructure (7 agents scaffolded, brand v0 live, loops running, decision logs filed) — it's pipeline. Without an ICP and pricing locked, Reilly couldn't fire, Katie's content had no defined target reader, and "land first client" stayed vague. This decision unblocks all three.

## Options considered

### On ICP
- **Mid-market (200–2,000 employees)** — most-aligned with thesis language ("executive trust") but slower sales cycles, harder to land as a solo founder pre-track-record. Rejected for v0; revisit at v2 once SMB case studies exist.
- **Startups (under 50)** — the Founder's initial pick. Refined out: startup founders are usually AI-savvy builders themselves; willingness-to-pay is constrained; thesis fits poorly. Replaced with SMB services as the better-fitting "smaller customer."
- **SMB services (chosen)** — owner-operator buyers feeling acute ops pain, fast decisions, AI-vendor competition is minimal in this space, recurring software-stack profile is consistent (QuickBooks + field service software + CRM).

### On lead vertical
- **Legal / lawtech** — saturated with AI vendors already; high competition.
- **Healthcare ops** — heavy compliance bar (Rafi-territory pre-revenue), slower cycles.
- **Real estate / proptech** — viable; in the second-tier list to expand into after landscaping proof.
- **Landscaping / Hardscaping (chosen)** — almost zero AI-vendor competition, real and concrete ops pain, owner-operators are reachable, ROI is direct (time-back = labor margin).

### On pricing
- **Flat $2,500/mo per agent (originally recommended)** — cleaner, higher per-engagement value. Rejected as too high for SMB landscaping entry tier.
- **Setup + retainer (chosen)** — matches the SMB mental model (one-time + monthly subscription). The hybrid that locked.
- **Pure project-based** — rejected; eliminates the moat (no watchdog ops, no iteration).
- **Outcome-based** — rejected; hard to measure in SMB, operationally messy.

## Why this won
The combination is **counter-positioned-on-counter-positioning**: YourCo's brand is premium and counter-positioned against AI-startup loudness, while the ICP is counter-positioned against where every other AI consultancy fishes (Sequoia portcos, VC-backed startups, enterprise procurement). The pricing is low enough to land first deals fast and prove the model on real engagements; the bundled MRR structure incentivizes account expansion, which is exactly stage 6 of the delivery loop. Velocity > per-deal-margin at v0.

## Reversibility
- **Pricing:** Easy to raise after the first 3-5 deals if close rate is high and retention holds. Harder to lower; locking too high here risks chasing too-few prospects.
- **Lead vertical:** Easy to expand into adjacent SMB services (roofing, hardscaping siblings). Hard to switch entirely to a different industry shape (e.g., enterprise) without rebuilding template patterns.
- **ICP:** Long-horizon plan to scale to any business size makes this directional, not absolute. SMB is the v0 wedge.

## Watchdog flag (Charles / Brett)
- **Margin/churn watchpoint:** $1k onboarding undervalues the moat work. If close rate is high *and* retention holds, the price is right. If churn spikes in the first 90 days post-go-live, the entry was too low and attracted price-sensitive buyers. Charles should flag this in the monthly close once data exists; Brett should flag it as a strategic risk in the first monthly advisory memo.

## What this unlocks
- **Reilly** — outbound campaign can now target landscaping/hardscaping owners specifically with the pricing in hand. **Reilly workflow addition:** before launching a campaign in any new vertical beyond landscaping, lock that vertical's pricing via a fresh decision doc (`/decisions/YYYY-MM-DD_pricing-<vertical>.md`).
- **Katie** — content briefs can speak directly to landscaping owners' ops pain
- **Reed** — demo can be set in the landscaping context, showing realistic digital-employee work
- **Luka** — brand guidelines stay valid; the SMB owner-operator framing layered on top doesn't require palette/type changes, just voice adjustments (less "executive" phrasing, more "owner" phrasing)
- **`01_company.md`** — three open items resolved (target verticals, pricing model, ICP)

## Amendment 2026-06-07 (same session)
the Founder correctly pushed back: pricing should be **vertical-specific**, not universal. Original draft of this decision implicitly treated the landscaping numbers as YourCo's universal pricing. Amended:
- Framework principle added: every new vertical gets its own pricing decision before Reilly campaigns into it
- Landscaping pricing scoped to landscaping only
- Directional ranges added for the five adjacent verticals (roofing, real estate, insurance/adjusting, law, wealth mgmt) — **NOT locked**, for internal reference only, do not quote externally
- Reilly's workflow gets the new step: lock vertical pricing before campaigning that vertical
