# Deal OS — real estate investors (build 61)

**Working name:** Deal OS · **Launch:** `prebuild-deal-os` · **Port:** 8881
**Synthetic operator:** "Keystone Property Group" — a 5–50-door investor-operator screening
three markets. Companion to `Pre Build Ideas/property-management/build`: Deal OS finds and underwrites the
property; Property OS runs it after closing.

## Why this build (and the honest market read)
Deal-analysis tools exist (DealCheck, Mashvisor, AirDNA, PropStream) — this is NOT an
overlooked category. Its exploitable weakness is that **every incumbent flatters the deal**:
point predictions, hidden assumptions, appreciation that only goes up. The differentiated
version is the one that refuses to lie — honest-numbers-by-construction, yourco's entire
identity. The client is an SMB investor-operator, operated by yourco — not consumer SaaS
(the standing rejection stands).

## The bleeding neck
Trusting a stranger's number with six figures. An investor underwrites 50 deals to buy one,
every tool hands them fiction, and the spreadsheet they trust instead eats their nights. The
quiet leaks: STR revenue assumed from a listing screenshot, "it'll appreciate 5%" as a plan,
rates moving under a quote, and the deal that pencils at asking but not at the real all-in.

## Modules
1. **Underwriting engine** (Operations) — for any listing × strategy (LTR / MTR / STR):
   mortgage math + full amortization + payoff date, NOI with every opex line stated, cash
   flow, cash-on-cash, cap rate, DSCR, IRR at 5/10/30-year exits. **Every output carries its
   inputs (provenance) and the label THIS IS A MODEL.**
2. **The comp floor** (Company Brain) — rent / ADR / occupancy estimates require ≥ the
   recorded comp floor (count + recency) in that market; below it the strategy reads
   UNMEASURED and underwriting REFUSES it: "no STR comps here — we don't invent occupancy."
3. **Scenario bands, never points** (Operations) — appreciation and exit values computed at
   bear/base/bull (base = the market's recorded trailing history; offsets stated); any
   single-number long-horizon projection is refused. Sensitivity grid: rate ±2%, rent ±10% →
   DSCR/CoC matrix.
4. **Deal screen** (Sales) — ranked ONLY by the investor's recorded criteria (min DSCR, min
   CoC, max price, allowed strategies); no recorded criteria → no ranking ("we rank by your
   bar, not ours"). Every rank carries its why-trace.
5. **The advice line** (Customer) — "should I buy it?" is the costly intake label:
   `recommend_purchase` R0 — the reply is the arithmetic, the bands, and the NOT INVESTMENT
   ADVICE line, never a verdict. `guarantee_return` R0 (forbidden language structurally).
6. **Data freshness** (Back Office) — rates and comps carry as-of dates; stale (> recorded
   threshold) data flags on every number it touched, never silently used. Demo runs on a
   labeled synthetic market; real deployment pulls sanctioned APIs only (FRED, licensed MLS,
   AirDNA/Rentometer) — no scraping, per the anti-library.

## Guardrails (load-bearing)
- `recommend_purchase` — **R0, never-promote.** Arithmetic and bands, never a verdict.
- `guarantee_return` — **R0**; "guaranteed / can't lose / sure thing" cannot ship (tested).
- `project_point_estimate_long_horizon` — refused; bands only.
- `estimate_below_comp_floor` — refused with the floor and count named.
- `rank_without_recorded_criteria` — refused; the investor's bar is the only bar.
- Numbers trace to inputs structurally (provenance on every underwrite).

## ROI (typed — for the investor-operator client)
Underwriting hours returned (time_saved, counted deals screened) · deals screened →
offers made (counted funnel) · the bad-buy avoided (scenario — never a number) ·
rate-move exposure caught (counted flags).

## Demo path
Deal screen (ranked by recorded criteria, why-traces) → one property, three strategies
side-by-side with bands → the payoff schedule + extra-payment scenario → sensitivity grid →
"should I buy it?" → the advice-line refusal → STR with no comps → UNMEASURED → trust tab.

## Build prompt
Shared contract, full built-out standard. Costly eval label: the advice ask.
