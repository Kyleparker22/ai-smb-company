# Landscaping / Hardscaping — Pricing (v0)

**Locked:** 2026-06-07
**Owner:** Polo
**Decision doc:** `/decisions/2026-06-07_icp-and-pricing-v0.md`

> ⚠️ **The prices below are live; the *strategy* that chose this vertical is not.** Landscaping /
> hardscaping was yourco's lead vertical when this was locked. That stance was retired 2026-08-05
> (`decisions/2026-08-05_horizontal-targeting-warm-first.md`) — targeting is now horizontal, warm
> intros first, all industries from day one. **This lock stays a live asset** and remains the anchor
> the OS ladder's on-ramp floor is set from (`os-tiers.md` footnote 2); it is simply no longer
> evidence that landscaping is where yourco is aiming.

## Vertical snapshot
- **Average revenue per business:** $500k–$3M/yr (small to mid)
- **Buyer:** owner-operator
- **Typical software stack:** Jobber, Aspire, ServiceTitan, QuickBooks
- **Seasonal pattern:** March–November peak; off-season is a sales window
- **Major ops pain:** lead intake, estimating, scheduling, weather rescheduling, photo handling, follow-up, review collection
- **Competitive landscape (AI implementation):** near-zero direct competition. Indirect: DIY automation, freelance VA agencies, generic field-service software

## Pricing structure
| Line item | Amount | Notes |
| --- | --- | --- |
| Company onboarding | **$1,000 one-time** | Tenant access, brand/voice training, integration mapping with their stack, owner-sponsor alignment, eval criteria |
| Per-digital-employee setup | **$1,000–$5,000 one-time each** | Scope/complexity. Simpler agents (review harvester) → low end. Complex multi-integration / production-grade agents (estimate drafter, scheduler) → high end. *(Updated 2026-06-16; was $1,000–$2,000.)* |
| Monthly retainer | **$1,500/mo first employee; +$500/mo each additional** | Watchdog ops, weekly iteration, eval updates, monthly readout. Token spend absorbed by YourCo. *(Marginal raised $250 → $500, 2026-06-16.)* |
| **Individual-employee cap** | **max 3** | 4+ coordinated employees = an **AI OS** — priced as one system ($2k–5k implementation + $3k–10k/mo), not à-la-carte. See `pricing/v0/vertical-ranges.md`. |

## Sample engagement math (non-OS · updated 2026-06-16)
- **1 employee:** $1,000 onboarding + $1k–5k setup + **$1,500/mo**
- **2 employees:** + setup + **$2,000/mo**
- **3 employees (cap):** + setup + **$2,500/mo**
- **4+ employees → AI OS:** $2k–5k implementation + **$3k–10k/mo** (the flagship; replaces a small team + several vendors)

## Why these numbers
- **$1,500/mo first employee** reads as "less than a part-time VA but does more, doesn't sleep" — the comparison owner-operators will make
- **$500/mo marginal (raised from $250)** still rewards expansion, but no longer lets a client stack cheap individual employees *below* the OS floor — at the 3-employee cap they're at $2,500/mo, just under the $3,000 OS floor, so the OS is always a step up, never a penalty. Steers multi-employee buyers to the flagship per the offering hierarchy.
- **Cap at 3 individual employees** — beyond that the value is the *coordinated system*, priced as an OS, not à-la-carte agents.
- **$1,000 onboarding** is intentionally low to remove first-deal friction; explicit watchpoint logged for upward revision if it attracts price-sensitive churn

## Watchpoints
- High close + poor retention → onboarding too low (revisit upward)
- Low close → $1,500 entry over-priced for vertical (revisit downward or unbundle)
- Margin on additional employees <50% → $500/mo marginal needs revisiting
- Clients clustering at the 3-employee cap without graduating to the OS → the OS floor or the graduation pitch needs work

## Channels (locked 2026-06-07)

| Channel | Status | Notes |
| --- | --- | --- |
| **Email** | ✅ approved | Primary channel. Universal. Sent via Instantly. |
| **SMS** | ✅ approved | Owner-operators are mobile and text-native; SMS often outperforms email for this vertical. Sent via Instantly Hyper CRM tier. Requires 10DLC registration + FTSA legal review before first FL send. |
| **LinkedIn** | ⛔ not v0 | Landscaping owner-operators are less active on LinkedIn than other verticals. Revisit at v1. |
| **Phone call** | ⛔ not v0 | Reserve for replied/booked prospects, not cold. Revisit at v1. |

Owner-operator channel preference: **text > call > email**. Cadence design should reflect — SMS touches early in sequence (Day 3) often produce highest reply lift.

Per channel-selection framework: see `/decisions/2026-06-07_sms-channel-addition.md` for full rationale.

## Sourcing (locked 2026-06-07 — updated to multi-source)

**Source set:** **Outscraper + Instantly SuperSearch + Vibe Prospecting** — all three run in parallel; dedupe-and-merge into one canonical list per campaign.

Each prospect surfaces with a **cross-source match tag** indicating which tools found it:
- `all-three` → highest confidence; lead the campaign
- `two-source` → high confidence; mid-priority
- `single-source` (especially Outscraper-only) → wider coverage; lighter first touch. *Outscraper-only matches are the exact ICP profile for trade SMBs — weak digital footprint = true local owner-operator.*

### Why multi-source for this vertical
Coverage test (the Founder, 2026-06-07): national US landscaping at $1M+ rev / 5+ employees returned **~25–50 hits in Vibe** vs **~500 hits in Instantly SuperSearch**. Each tool has different blindspots. Outscraper's Google Maps coverage catches the truly local businesses neither commercial database tracks well. Combining all three yields the broadest deduplicated set.

### After sourcing
Vibe stays in the stack as the per-company enrichment + research layer (firmographics, technographics, funding signals) once a prospect is on the merged list.

### Watchpoint
Pre-campaign coverage threshold: ≥ 2,000 deduplicated US landscaping prospects in the merged set before launching a national campaign. Below threshold → expand filters or escalate.

Per sourcing framework: see `/decisions/2026-06-07_outbound-sales-stack.md` (multi-source amendment) and `/decisions/2026-06-07_multi-source-sourcing.md` for full architecture.

## Revision history
See `/pricing/CHANGELOG.md`.
