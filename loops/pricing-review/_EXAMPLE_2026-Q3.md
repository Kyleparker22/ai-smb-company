> ⚠️ **EXAMPLE OUTPUT — not yours.** Describes the source company. Delete once your own loop runs.

# Quarterly Pricing Review — 2026-Q3

**Run:** 2026-07-06 (first pricing-review run) · **By:** Polo, Pricing · **Verdict:** No adjustments. Insufficient data to test any prediction — YourCo is pre-revenue.

## Scope
One locked vertical: **Landscaping / Hardscaping** (`pricing/v0/landscaping-hardscaping.md`, locked 2026-06-07, structure updated 2026-06-16). No other vertical is locked; `vertical-ranges.md`, `os-tiers.md`, `ready-to-hire.md`, `tier2-production.md`, and `audit.md` are directional ranges / packaging, not campaigned locked prices, so they're out of scope for predicted-vs-actual review.

## Landscaping / Hardscaping
- **Close rate:** No data. Reilly has 2 campaign artifacts (national batch, 2026-06-08/09) but **0 tracked closes, 0 proposals out, 0 human replies logged** in `loops/sales/`. Pipeline is 21 open deals, all TBD/unpriced. Predicted range (eval target: within ±20% after 5 deals each) — **cannot be tested; 0 of 5 deals.**
- **Retention:** No data. Zero live engagements; `finance/revenue.md` MRR = $0. Predicted range (no >25% deviation after 6 months) — **cannot be tested; no client has reached month 1.**
- **Margin:** No data. Only near-live account is Sample Client (unsigned, in discovery, re-scoping single-agent → AI OS); `clients/sample-client/cost.md` is empty. Margin watchdog (<50% sustained) — **no engagement cost to measure.**
- **Flag:** None warranted. Nothing has diverged because nothing has closed. Holding all landscaping prices as locked.
- **Proposal decision doc:** None. No divergence → no adjustment cycle opened.

## Why no adjustment
Per Polo's discovery doc (`clients/polo/01_discovery.md`, "Pre-revenue thinness") and the locking decision (`decisions/2026-06-07_icp-and-pricing-v0.md`), the first quarter of operation is theoretical by design — real close-rate/retention/margin signal only starts after the first 3–5 deals per vertical. Adjusting locked prices now would be fitting to noise. The locked numbers stand.

## Adjacent watchpoints (informational, no action)
- The landscaping watchpoints in the pricing file (onboarding-too-low churn signal, $1,500 entry over/under-priced, marginal <50%, cap-3 clustering) all require post-go-live data — none exists yet.
- Sample Client is re-scoping away from the single-agent landscaping price toward a banded AI OS deal. If it signs as an OS, its economics test the **OS tiers** (`os-tiers.md`), not the landscaping per-agent lock — worth pricing-tracking separately once scoped.

## What fills in next quarter (2026-Q4)
- **First close** → the first real close-rate data point for landscaping (target: 5 deals to test ±20%).
- **First signed engagement's `cost.md`** → first margin signal (via Charles's finance loops).
- **Sample Client resolution** → either the first landscaping proposal converts, or the first OS-tier deal opens a separate pricing-track.
- Until then, the review remains a coverage-and-hygiene check, not a predicted-vs-actual analysis.

## Eval self-check (Polo)
- Coverage: 100% — every campaigned vertical (landscaping only) has a locked price. ✅
- Quarterly hygiene: this artifact satisfies the Q3 review requirement. ✅
- Close-rate / retention / margin alignment: **N/A — pre-revenue.** First measurable next quarter.

---

## What I'd do differently next run
_(the Founder to fill — the closed-loop feedback hook. Left empty by design.)_
