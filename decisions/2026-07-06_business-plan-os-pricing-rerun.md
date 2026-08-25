# 2026-07-06 — Business-plan projections re-run on the locked OS-tier pricing

## Decision
`business-plan.md` §8 (and the `finance/yourco-financial-model.xlsx` inputs) now model the **OS tier ladder** (`pricing/v0/os-tiers.md`) instead of the retired Tier-1/Tier-2 employee pricing: headline path **0 → ~$670k ARR run-rate (Y1) → ~$4.4M (Y3) → ~$12M (Y5)**, replacing $240k / $2M / $7M.

## Context
The plan (last touched 2026-06-13) still assumed Tier-1 ~$4k build + $750/mo, Tier-2 ~$7k + $1.75k/mo, and an $850 blended retainer — ~3.5x stale against the OS-tier envelope Polo locked 2026-06-16 (Core floor $3,000/mo) and against the Founder's 2026-07-06 goals (`dashboard/goals.json`: $15k MRR / 5 live end-Q3; $36k / 12 by Dec-2026, anchored on the $3k Core floor). The goals commit (b7f8e55) explicitly flagged the plan model as needing a re-run.

## Stated assumptions (the new model)
- **Pricing input (not re-litigated):** the locked four-step ladder — Core $2–2.5k impl + $3–4k/mo · Suite $2.5–3.5k + $4.5–6k/mo · Operation $3.5–4.5k + $6.5–8k/mo · Command $4.5–5k + $8.5–10k/mo; on-ramp single employee $1–5k setup + $1,500/mo floor. `pricing/` untouched — Polo's lock is the input, not the subject.
- **Tier mix → blended retainer:** Y1 ≈ 20% on-ramp / 60% Core / 15% Suite / 5% Operation at band floors → **~$3,100/mo**; Y3 ≈ 10/45/30/12/3% mid-band → **~$4,400**; Y5 ≈ 5/35/35/18/7% → **~$5,200**.
- **Client counts:** fewer, larger logos than the pre-OS model (24/150/450 → **18/85/190**) — ACV is 3.5–4x, so the count trajectory scales down while revenue scales up. New-clients-added inputs: 18/30/45/60/75, retention 82→88% (unchanged band).
- **Upfront:** avg implementation ~$2,000 (Y1) → ~$3,500 (Y5) per client, net of the 100% audit credit.
- **Margin:** infra absorbed at $200–400/client/mo (multi-agent OS > the old single employee's $100–300) → **arithmetic gross margin ~91%**; the plan deliberately holds **~80–85%** (headroom for unmetered tools/voice/rework), consistent with the conservative 65/75/78% goal ramp in `dashboard/goals.json`.
- **Consistency check:** the Y1 row (~18 clients / ~$56k MRR at ~12 months post-launch) is the Founder's Dec-2026 target (12 / $36k) extended ~2 quarters at the same close rate.

## Options considered
- **Keep the old client counts (24/150/450) at new retainers** — rejected: implies $30M ARR by Y5, fabricated precision in the wrong direction.
- **Only patch the blended-retainer row** — rejected: mix, upfronts, margin, and counts all derive from the tier ladder; a partial patch would leave the table internally inconsistent.
- **Mark the plan stale and defer to Polo/Charles** — rejected: the plan is explicitly an assumption-stated model; re-running it with stated assumptions is exactly its contract. Polo/Charles still validate against real engagements.

## Why
An always-loaded plan quoting a retired price structure is exactly the change-one-sweep-all drift CLAUDE.md warns about — the Founder's goals, the CRM, and the pricing docs all spoke OS-tier while the plan spoke $850 blended. The re-run keeps the plan's "illustrative model, not a forecast" framing and simply swaps the pricing input for the locked one.

## Sweep (same commit)
- `business-plan.md` — §1/§2 offering language, §3 pricing, §8 assumptions + table, §9 milestone counts.
- `finance/yourco-financial-model.xlsx` — input rows (clients added, blended retainer, implementation fee, infra, opex, humans) + notes; formulas unchanged.
- `01_company.md` — stale 2026-06-07 pricing section marked superseded, sample math re-anchored.
- `agents/pickle/collateral/proposal.html` — sample proposal re-priced to the locked on-ramp ($2,000 + $1,500/mo).
- `agents/brett/premortem-2026-06-12.md`, `clients/_dryrun-commercial-path/2026-06-12_tabletop.md`, `decisions/2026-06-07_icp-and-pricing-v0.md` — dated point-in-time artifacts annotated (history preserved, price marked superseded).
- `dashboard/goals.json` — `_sources` margin notes updated to the plan's new margin language.
- Not touched: `pricing/` (the input); `_archive/`, `loops/` (history).

## Reversibility
Trivially revisable — it's an input-driven model. When the first ~10 real engagements land, Polo/Charles replace the mix/retention/margin assumptions with observed data (Polo's quarterly pricing review is the standing checkpoint); if the tier lock itself moves, re-run the same way.
