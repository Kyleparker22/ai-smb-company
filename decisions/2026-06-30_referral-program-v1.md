# Decision — Referral program v1: two partner types + multi-level rep override

**Date:** 2026-06-30 · **Owner:** the Founder (locked the shape) + Polo (numbers) + Bird (program) + Charles (payouts) + **Ray (the MLM/legal structure — gating)** · **Status:** numbers LOCKED; **the multi-level override is a hard stop until counsel clears it** · **Updates** `decisions/2026-06-14_referral-program-tiered.md`. Full spec: `processes/partnerships/referral-program.md`.

## What changed (from the 2026-06-14 v0)
1. **Two partner types** (new): **(1) clients who refer clients** → **$100/mo credit** per active referred client, residual while live (stacks); **(2) sales reps** → the commission escalator.
2. **Rep tiers:** **10% / 12.5% / 15%** at **1–5 / 6–10 / 11+** active clients (thresholds were 3/5/10; rates softened from 10/15/20 same-day), on the whole active book.
3. **Override → full downline (multi-level):** a rep earns **1%** of the client revenue produced by their *entire* downline (was capped at one level). **the Founder's explicit call (chose "full downline" over "one level").**
4. **Equity track (new, internal — not marketed):** top reps can earn equity by trailing-12-mo referred revenue — **$500k → 0.5% · $750k → 1.0% · $1M → 1.5%**, with a **15%-of-company program cap**. Discussed 1:1, not on the site. ⚠️ **Securities-gated** — separate decision: `decisions/2026-06-30_rep-equity-track.md`.

## The math (the Founder's worked example)
| Person | Clients / MRR | Direct (tier) | Override (1% of downline MRR) | **Total/mo** |
|---|---|---|---|---|
| **Lucas** | 5 / $18,000 | $1,800 (10%) | $300 (1% of John+A+B = $30k) | **$2,100** |
| **John** (Lucas's recruit) | 3 / $10,000 | $1,000 (10%) | $200 (1% of A+B = $20k) | **$1,200** |
| **Sub-rep A** (John's recruit) | 2 / $10,000 | $1,000 (10%) | — | **$1,000** |
| **Sub-rep B** (John's recruit) | 2 / $10,000 | $1,000 (10%) | — | **$1,000** |
| **Total** | $48,000 network MRR | | | **$5,300/mo (~11%)** |

Per-client load: Lucas's clients 10% · John's clients 11% (10%+1%) · sub-reps' clients 12% (10%+1%+1%). *(Lucas's 5 clients are Tier-1 (10%) under the 1–5 band; 12.5% starts at 6. The whole network sits in Tier 1 here, so softening Tiers 2–3 to 12.5/15% doesn't move this example.)*

## ⚠️ The compliance reality (non-negotiable)
The one-level → full-downline change makes this a **multi-level marketing (MLM) structure.** It is **not offered to anyone** until **Ray + outside counsel** structure it properly:
- An **income-disclosure statement.**
- A **Partner/Referral agreement** with the downline terms.
- **Real-client-revenue-only** — never paid for the act of recruiting; no buy-in (these are what keep it out of pyramid territory).
- Any **depth / earnings caps** counsel requires (unlimited depth is the risk to bound).

What keeps it defensible: commission is on real product revenue, there's no pay-to-play, and no one earns for recruiting itself. Counsel bounds the depth.

## Still open (the Founder + Polo + Ray)
- Fast-start one-time build-fee bounty (5–10%) vs pure recurring.
- Clawback window + post-exit commission tail.
- **Net-margin-after-commission check** vs the financial model — the higher rates + multi-level override need a fresh look (Charles + Polo).
- **The MLM legal structure — Ray + outside counsel (the gating item before any recruiting).** Drafts ready for counsel: `processes/partnerships/legal/` (Partner Agreement · Income Disclosure · counsel-review checklist).

## Built
- CRM Referrals view updated: rates **10/15/20**, override now computed across the **full downline** (`downlineOf` recursion in `crm/index.html`); `D.meta.referralTiers` default updated. Client-referral ($100/mo credit) tracking = a CRM enhancement for activation.
- Spec rewritten to v1.

## Reversibility / launch posture
Staged — no rep recruited, no economics communicated. Lock the remaining numbers + **clear counsel** before recruiting. Once reps sign, rate changes apply going forward only.
