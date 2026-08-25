# Pricing Changelog

**Every pricing change lands here** — per-vertical locks, the horizontal OS ladder, the Audit, and
any change to *what is being sold* rather than only what it costs. Dated, with reason and the Founder's
approval reference.

> The scope used to read "every pricing change **to a locked vertical**." That loophole is why the
> single largest pricing change in the company's history — 2026-06-22, when the unit of sale itself
> became the horizontal OS ladder — was never logged here: it wasn't a vertical, so it fell outside
> the sentence. Backfilled 2026-08-24, along with 2026-08-05. A changelog narrower than the thing it
> logs is a changelog that will miss the important entries specifically.

## 2026-06-07 — Landscaping / Hardscaping v0 (initial lock)
First vertical priced. Three-layer structure:
- $1,000 one-time onboarding
- $1,000–$2,000 one-time per-agent setup (scope-dependent)
- $1,500/mo first agent + $250/mo per additional agent

Approval: the Founder directed pricing in-session.
Decision log: `decisions/2026-06-07_icp-and-pricing-v0.md`.
Vertical pricing reference: `pricing/v0/landscaping-hardscaping.md`.
Pricing-agent owner assigned same day: Polo (`decisions/2026-06-07_polo-pricing-agent.md`).

---

## 2026-06-16 — Pricing model restructured: individual employees vs. AI OS

New two-path structure (the Founder-directed in-session):

**A. Individual employees (non-OS)**
- Per-employee setup: **$1,000–5,000** one-time each (was $1,000–2,000) — by build/complexity; production-grade at top.
- Retainer: **$1,500/mo** first employee · **+$500/mo** each additional (marginal raised from $250).
- **Cap: 3 individual employees.** 4+ coordinated = an AI OS.

**B. AI OS (the flagship)**
- Implementation/onboarding: **$2,000–5,000** one-time (one consolidated fee).
- Retainer: **$3,000–10,000/mo** consolidated.

**Polo's rationale + changes adopted:**
- Raised marginal individual retainer $250 → $500 **and** capped individual stacking at 3 — fixes a pricing inversion where 6 individual employees ($2,750/mo) would have undercut the OS floor ($3,000). At the cap (3 employees = $2,500/mo) the OS is always a step up.
- Folded the old "Tier-2 build $5k–10k" into the unified $1k–5k per-employee setup band (single-employee build now caps at $5k); Tier-2 value moves to the retainer (~$2–2.5k for production/compliance employees).
- Retired the old OS bundle table ($6–15k build / $5–7.5k mo) in `tier2-production.md` for the flat $2–5k implementation + $3–10k retainer.
- Per-vertical banding (bottom/middle/top of each range) recorded in `vertical-ranges.md`.

**Graduation policy (individual → OS):** a client moving from individual employees to an OS does **not** pay the implementation fee again. Prior onboarding + setup fees credit 100% toward the OS implementation (effectively $0 for any 3-employee client); only net-new orchestration work is chargeable (small, or waived to land the expansion); the expansion is captured in the retainer step-up to the OS band. Recorded in `vertical-ranges.md` ("Graduating individual employees → OS").

**Resolved 2026-06-16 (Polo's calls, the Founder delegated):**
- **Per-vertical individual-employee retainer re-locked off $1,500** (was stale $750-anchored). $1,500 floor (entry offer, never below anchor); scales to $2,000–2,500 for compliance verticals (dental/medical/legal/financial) and production single employees; +$500 marginal universal, cap 3. Table in `vertical-ranges.md`.
- **Audit credit applies to the full upfront** (onboarding + setup, or OS implementation), not build/setup-only. Real margin is the retainer, so crediting the full upfront is cheap and gives the cleanest "audit was effectively free" message; no spillover (upfront always exceeds the audit fee). `pricing/v0/audit.md`.

Approval: the Founder directed pricing in-session.
References: `pricing/v0/vertical-ranges.md`, `pricing/v0/tier2-production.md`, `pricing/v0/landscaping-hardscaping.md`.

---

## 2026-06-22 — The unit of sale becomes the horizontal OS ladder  *(backfilled 2026-08-24)*

**Not logged at the time.** Decision: `decisions/2026-06-22_horizontal-positioning-and-os-tiers.md`.
The largest pricing change to date, because it changed *what is being sold*, not a number.

- **Positioning went horizontal.** The offer is audit → custom AI OS for any business in any
  industry; yourco stopped segmenting the marketing by trade.
- **Four tiers named and 🔒 LOCKED by the Founder:** **Core** (~3 agents) · **Suite** (~5) ·
  **Operation** (~7) · **Command** (up to 10). Agent count is an *included* guide, never a meter.
- **Prices assigned to those names by Polo** in `v0/os-tiers.md` — a **split of the already-locked
  envelope** ($2–5k implementation + $3–10k/mo, locked 2026-06-16), not a new model. Core
  $2–2.5k + $3–4k/mo · Suite $2.5–3.5k + $4.5–6k/mo · Operation $3.5–4.5k + $6.5–8k/mo ·
  Command $4.5–5k + $8.5–10k/mo.
- **Tier names are locked; tier prices are NOT.** `os-tiers.md` remains a v0 proposal awaiting
  the Founder's lock — quoting it externally still needs that lock.
- **Guardrail carried in:** three à-la-carte employees cap at $2,500/mo, so the Core floor of
  $3,000 is always a step up. No inversion.
- **Same day, the Ready-to-Hire catalog was parked** (`decisions/2026-06-22_website-dial-back.md`),
  which is what makes `v0/ready-to-hire.md` a price list for a page that no longer exists.

## 2026-08-05 — Targeting goes horizontal; landscaping is no longer the lead vertical  *(backfilled 2026-08-24)*

**Not a price change — a change to which prices matter.** Decision:
`decisions/2026-08-05_horizontal-targeting-warm-first.md`.

- All industries from day one; the sequencing filter is **relationship, not vertical**.
- The landscaping/hardscaping lock (2026-06-07) **stays a live asset** — it still anchors the
  on-ramp $1,500 floor — but is no longer evidence of where yourco is aiming.
- ⚠️ **Left open by this change, and still open:** the house rule requires a locked pricing doc per
  vertical before *cold* outbound, but warm-first means most warm deals now land in unlocked
  verticals. Do the horizontal OS bands govern them? **Polo rules, before the first warm proposal
  in an unlocked vertical** (`06_business-plan.md` §4).

## 2026-08-16 — Audit fee suspended: the Audit is FREE
the Founder's call, overriding the 2026-06-16 lock. **No charge for an Audit** while yourco is getting started; the
$1,000 Standard / $1,500 Pro prices are retained in `v0/audit.md` as the **return price**, not deleted.
The **100% credit mechanic retires with it** — there is no fee to credit, so any surface saying "your audit fee
is credited toward implementation" now implies a fee that does not exist. The **founders' offer** (first 3
warm-network audits free) is retired into the general rule. Net effect is narrower than it looks: a converting
client always paid the same total, so what is given up is revenue from **non-converting** audits, upfront cash
float, and the **qualification filter** — the last being the one to watch. Trip-wire: revisit at 3+ completed
engagements with measured outcomes. Decision: `decisions/2026-08-16_audit-is-free.md`.

## 2026-06-16 — Audit fee locked + credit condition set

The Audit (mandatory diagnostic front door, `processes/audit-sop.md`) now has a locked fee:
- **Standard Audit — $1,000 flat** (universal across service-SMB verticals).
- **Pro Audit — $1,500 flat** (compliance verticals + multi-location).
- **100% credited** toward the build/implementation fee on a **minimum 6-month engagement** (replaces the earlier "credit within a 30-day window" idea).

Near-universal by design (not a per-vertical grid): the Audit is the qualifier + funnel, not the profit center. Open item: whether the credit applies to the full upfront (onboarding + setup) or only the per-employee build fee — flagged because Standard Audit ($1,000) now equals the Tier-1 onboarding fee ($1,000).

Approval: the Founder directed pricing in-session.
Reference: `pricing/v0/audit.md`. Site copy (number-free): `audit.html` + `pricing.html`.

---

## 2026-06-08 — Pricing pulled from Reilly's cold sequence (no price change)

No price change — pricing rules unchanged. Reilly's *cold copy* no longer surfaces price; pricing appears on first call only. Aligns to commission-breath-removal methodology.

Approval: the Founder directed methodology shift in-session.
Decision log: `decisions/2026-06-08_reilly-copy-structure-v2.md`.
Reilly methodology reference: `agents/reilly/copy-structure.md`.
Polo's role unchanged — still locks per-vertical pricing; Reilly still cannot quote unlocked verticals; quoting now happens on call instead of in cold.
