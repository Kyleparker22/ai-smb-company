# Decision — horizontal positioning (no verticals on the site) + tiered AI OS levels

**Date:** 2026-06-22 · **Owner:** the Founder (positioning) + Polo (tier pricing) + Webb (site) · **Status:** positioning set; tiers = direction for Polo to price

## 1. Positioning: horizontal, not vertical
**the Founder's call:** no verticals on the website. yourco's offer is **audit → custom AI OS for any business in any industry**, with whatever agents that business needs inside the OS. We do not segment the marketing by trade.

**Executed (this pass):**
- Parked the entire vertical funnel → `agents/webb/pages/yourco-site-v2/_parked/`: `verticals.html` (Industries hub), `vertical-template.html`, and `snapshot.html` (the Revenue Leak Snapshot was vertical-keyed off `snapshot-config.js` — it can't stay without verticals, so it's parked too; `snapshot-config.js` kept in repo for a possible future *generic* rebuild).
- Removed "Industries" from nav; replaced the home "Find your industry → Snapshot" section with **"We don't do one industry. We learn yours."** (any-business → audit).
- Retargeted all links → audit; **zero dead links** (verified). Cleaned the home footer (dropped the now-empty "Free tools" column + stale "Hire/Industries" labels).
- `llms.txt` "Industries served" rewritten to "any business, any industry."
- Live page count: 34 → **20**.

**The honest flag (decouple two things):**
- **Site positioning = horizontal** is fine and more honest about what the product is. ✅
- **GTM targeting** should *still* concentrate. The council and Brett's idea #1 ("own one vertical") argued focus wins for a solo pre-revenue founder — referral density, repeatable playbook, AEO concentration, sharper messaging. **Going horizontal on the *site* does not require going horizontal on *who you call first*.** Recommended: keep pointing the limited outbound time at a beachhead (the hardscaping/landscaping warm network — Sample Client, Sample Company C, etc.) to manufacture the first proof, even while the site says "any business." Don't let removing vertical *pages* silently delete the targeting *focus*. (Amends the beachhead language in `CLAUDE.md` and the spirit of `loops/brett-ideas/2026-06-17_ideas.md` #1 — focus moves from "vertical marketing" to "vertical *targeting* of a horizontal offer.")

## 2. Tiered AI OS levels (the Founder's idea + reframe for Polo)
**the Founder's proposal:** tier the custom OS by number of agents included — T1 = 3 agents, T2 = 5, T3 = 7, Top = 8+.

**The instinct is right** — good-better-best packaging anchors price, makes the OS easy to quote, and gives an upsell ladder. **One reframe before Polo prices it:**

> **Tier on outcome/scope, not raw agent count.** CLAUDE.md's first principle is "frame everything as outcomes, not features." Agent *count* is a feature/input metric — and pricing on it invites a "how many bots" race, misaligns value (one front-desk agent can be worth more than seven trivial ones), and reads as software, not an operated outcome. Keep agent count as the **"what's included" guide**, but lead each tier with the **scope of the business it runs.**

Suggested shape (Polo refines + prices, reconciling with the existing `pricing/` Tier-1/Tier-2 ranges):

| Tier | Headline (the outcome/scope) | Included (guide) |
|---|---|---|
| **Tier 1 — the wedge** | Automate one core function (e.g. front-of-house: intake → booking → follow-up) | ~3 agents |
| **Tier 2** | Run one department end-to-end (front + back office of an area) | ~5 agents |
| **Tier 3** | Coordinate multiple departments (sales + ops + admin) | ~7 agents |
| **Top — the company OS** | The whole operation, deepest integration + the strongest reliability/eval SLA | 8+ / effectively unlimited |

Notes for Polo:
- **Retainer scales with scope + the reliability SLA, not per-agent.** Offer "add an agent" as an in-tier upsell, but don't make agent-count the meter.
- The **audit is still the front door to all tiers** (sizing which tier fits is literally what the audit produces).
- This is the **custom-OS** packaging — distinct from the (now-parked) Ready-to-Hire single-employee catalog. The single employee remains the down-sell / entry; the tiers are the OS ladder above it.
- Reconcile with `pricing/` (existing Tier-1/Tier-2 production ranges) so we don't end up with two conflicting "tier" vocabularies.

### 2a. Refinement (the Founder, 2026-06-22): cap, overage, names, pillar-mapping
**Reconciled with the 8-pillar module taxonomy (`processes/ai-os-modules.md`):** an "agent" = the on-ramp unit of a pillar; tiers are counted in *agents* for customer simplicity but *scoped by pillars* in the audit. "Up to 10 agents" ≈ spanning most/all 8 pillars (some pillars carry >1 agent).

| Tier (name 🔒) | What it runs | Agents (included) | Pillars (approx) |
|---|---|---|---|
| *(on-ramp)* | One role — entry module / down-sell | 1 | the first pillar's first agent |
| **Core** (Tier 1) | One core function automated | ~3 | 1–2 |
| **Suite** (Tier 2) | A department runs itself | ~5 | ~3 |
| **Operation** (Tier 3) | Multiple departments coordinated | ~7 | ~4–5 |
| **Command** (top) | The whole company OS | **up to 10** | most/all 8 |

**Top-tier overage (the Founder's structure):** the top tier includes **up to 10 agents**. **Each additional agent beyond 10 is case-by-case** — a one-time **implementation fee** + **incremental monthly**, **sized to the agent's complexity** (big vs. small), and **discounted vs. its standalone price**. Rationale (real, not a giveaway): at the top tier the cross-cutting moat layer (reliability/eval/observability/approval/audit-log), the runtime, and the integrations are **already built and operated**, so a marginal agent is mostly marginal build + run cost. The discount makes expansion the obvious next step — the **land-and-expand engine** (Bird) lives at the top of the ladder. *(Polo sets the actual implementation-fee + monthly bands and the discount %.)*

**Tier names — 🔒 LOCKED (the Founder, 2026-06-22): Set A — `Core` · `Suite` · `Operation` · `Command`.** OS/executive register; reads as "yourco Command." (Rejected: Set B Core/Team/Operations/Company, Set C Cornerstone/Keystone/Capstone/Citadel.)

## Owners / next
**Polo:** turn §2 into priced tiers in `pricing/` (reframe applied) — incl. the top-tier overage bands + discount %. **Webb:** when the site rebuilds nav at launch, fold the lean set + reflect horizontal positioning + (if Polo's ready) a tiers section on `pricing.html`. **the Founder:** confirm the tier *definitions* (the table is a starting point, not locked). **Brett:** note the focus-discipline nuance above (horizontal offer, focused targeting).

## Status
Positioning executed + staged (launch-gate). Tiers = direction for Polo. Supersedes the "verticals deferred" line in `decisions/2026-06-22_website-dial-back.md`.
