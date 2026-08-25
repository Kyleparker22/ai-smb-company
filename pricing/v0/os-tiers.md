# AI OS tiers — priced rows (v0 proposal)

> ⚠️ **v0 proposal — Polo's draft for the Founder to lock. Pre-revenue positioning ranges, not validated or external prices.** No external pricing communication without the Founder's lock.
> Turns the **named/scoped tiers** (`decisions/2026-06-22_horizontal-positioning-and-os-tiers.md`, names 🔒 LOCKED) into **per-tier price points** — the artifact that decision assigned to Polo. This is a **split of the already-locked OS envelope** ($2–5k implementation + $3–10k/mo retainer, `vertical-ranges.md`, Polo-locked 2026-06-16), **not a new model.** Pairs with the 8-pillar taxonomy (`processes/ai-os-modules.md`). Owner: **Polo** · locks: **the Founder**.

## Principles carried forward (unchanged)
- **Price on scope + the reliability SLA — not per-agent count.** Agent count is the "what's included" guide, never the meter (CLAUDE.md: outcomes, not features).
- **The audit is the front door** that sizes which tier fits, and **credits 100%** toward the upfront on a 6-mo min engagement (`audit.md`).
- **No inversion with à-la-carte:** 3 individual employees cap at $2,500/mo, so the **Core floor ($3,000) is always a step up** (preserves Polo's 2026-06-16 lock).
- **Within-band placement** set by the same three levers as every vertical: **job/customer value · compliance lift · volume/complexity** (`vertical-ranges.md`). Lower-ticket trades sit at the bottom of a tier's range; compliance/multi-location sits at the top.

## The four priced tiers (the OS ladder)

| Tier 🔒 | What it runs | Agents (guide) | Pillars | **Implementation (one-time)** | **Retainer (/mo)** |
|---|---|---|---|---|---|
| *(on-ramp — single employee)* | One role; the entry rung — a good place to land, never the opener | 1 | 1st pillar's 1st agent | $1,000–5,000 setup¹ | **$1,500** floor² |
| **Core** | One core function automated | ~3 | 1–2 | **$2,000–2,500** | **$3,000–4,000** |
| **Suite** | A department runs itself | ~5 | ~3 | **$2,500–3,500** | **$4,500–6,000** |
| **Operation** | Multiple departments coordinated | ~7 | ~4–5 | **$3,500–4,500** | **$6,500–8,000** |
| **Command** | The whole company OS | up to 10 | most/all 8 | **$4,500–5,000** | **$8,500–10,000** |

¹ On-ramp single employee keeps the existing à-la-carte structure (`vertical-ranges.md`): $1–5k setup by complexity, +$500/mo each additional, **cap 3** → then graduate to an OS.
² $1,500 is the locked floor (landscaping anchor); scales to $2,000–2,500 for compliance/production employees.

**The whole ladder fits inside the locked envelope:** implementation spans $2,000 (Core floor) → $5,000 (Command top); retainer spans $3,000 (Core floor) → $10,000 (Command top). Same envelope Polo locked 2026-06-16, now resolved into four quotable steps.

## Command overage — agents beyond 10 (the Founder's structure, Polo's numbers)
Command includes **up to 10 agents.** Each additional agent is **case-by-case**, sized to complexity, and **discounted vs. its standalone price** — because at Command the cross-cutting moat layer (reliability/eval/observability/approval/audit-log), the runtime, and the integrations are **already built and operated**, so a marginal agent is mostly marginal build + run.

| Added agent | One-time implementation | Incremental retainer /mo |
|---|---|---|
| **Small / simple** (e.g. a templated drafter, a single-source Q&A) | **$500** | **+$500/mo** |
| **Medium** (e.g. a multi-step workflow agent, 1–2 integrations, a review/reputation agent) | **$750–1,500** | **+$625/mo** |
| **Large / complex** (e.g. new voice agent, new integration, compliance gating) | **$1,500–5,000** | **+$750/mo** |

**Discount anchor: ~50% off standalone** (substrate already built/operated). The discount lives in the **one-time implementation** — the moat layer, runtime, and integrations already exist, so a marginal agent is mostly marginal build (small builds drop to ~$500 vs. the à-la-carte $1–5k setup). The **incremental monthly reflects real recurring operate cost** (eval, observability, reliability load), which is why a complex agent (voice, compliance gating) can run at or above the base +$500 marginal. Expansion stays the obvious next step — this is where **land-and-expand (Bird)** lives.

## Graduation (individual employees → an OS tier)
Unchanged from `vertical-ranges.md`: **no second implementation fee.** Prior onboarding + per-employee setups credit 100% toward the OS implementation (effectively $0 for any 3-employee client); only net-new orchestration is chargeable (small, or waived to land it); the expansion is captured in the **retainer step-up** into the relevant tier band. A 3-employee à-la-carte client ($2,500/mo) graduating to **Core** is a clean +$500–1,500/mo step, no upfront.

## Worked examples (illustrative, within bands)
- **Landscaper, Core (front-of-house: intake → booking → follow-up, ~3 agents):** $2,000 implementation (the Audit is free, so nothing is credited — this is the full upfront) ~$1,000 net) · **$3,000–3,500/mo.**
- **Home-services firm, Suite (sales + intake department, ~5 agents):** $3,000 implementation · **$5,000/mo.**
- **Dental group, Operation (multi-dept + compliance, ~7 agents):** top of band → $4,500 implementation · **$8,000/mo** (the Audit is free; Pro return price $1,500 credited).
- **Multi-location operator, Command (whole OS, 10 agents) + 2 added agents:** $5,000 implementation + added builds ($500 small + $2,500 large) · **$10,000/mo** + one small (+$500) + one large (+$750) = **$11,250/mo.**

## Open items for the lock conversation (the Founder + Polo)
1. **Confirm the four retainer steps** ($3–4k / $4.5–6k / $6.5–8k / $8.5–10k) — are the gaps right, or should Suite/Operation compress?
2. **Confirm the overage discount %** (proposed ~50%) and the small-vs-large bands.
3. **Vocabulary reconcile:** retire/relabel the old "Tier-1/Tier-2" language in `pricing/` so only the on-ramp + Core/Suite/Operation/Command vocabulary remains customer-facing (Tier-2 = a production single employee at the top of the on-ramp band; say so explicitly).
4. **Site:** if locked, Webb folds a tiers section into `pricing.html` at launch (still number-free externally until the Founder clears).

> ⚠️ Ranges are internal proposal guidance. **Land → validate → lock** each number against a real engagement (Polo's quarterly review).
