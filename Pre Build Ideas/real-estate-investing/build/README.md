# Deal OS — build (real estate investors)

Run: `python3 seed.py && python3 server.py` → http://127.0.0.1:8881 (launch name
`prebuild-deal-os`). Suite: `python3 test_deal_os.py` (84 assertions, incl. hand-checked
mortgage fixtures). Synthetic "Keystone Property Group" screening three invented markets.
Companion to `Pre Build Ideas/property-management/build`: Deal OS underwrites the buy; Property OS runs it after.

## The market read, stated honestly
Deal calculators are NOT an overlooked category (DealCheck, Mashvisor, AirDNA, PropStream).
Their shared weakness is that every one flatters the deal — point predictions on hidden
assumptions. This build is the one that refuses to lie.

## The load-bearing refusals

- **Never a verdict.** "Should I buy it?" is the costly triage label; `recommend_purchase` is
  R0 never-promote. The reply is the arithmetic, the bands, and the not-advice line — "a yes
  from a tool is someone else's judgment wearing math."
- **Bands, never points.** Long-horizon projections only exist as bear/base/bull bands, with
  base growth computed from the market's own recorded trailing history ("an appreciation guess
  with no history is astrology"). A 10-year point estimate is refused outright, on the record.
- **The comp floor.** Rent/ADR/occupancy need ≥5 recorded comps within 180 days (config-named
  floor) or the strategy reads UNMEASURED — "we don't invent occupancy." Maplewood deliberately
  has no STR comps so the refusal is live in the demo.
- **Provenance on every number.** Each underwrite carries its full input set — price, rate +
  as-of date, comp count and basis, every assumption (all defaults visible and overridable) —
  and the label THIS IS A MODEL. Cashflow ≡ NOI − debt service and CoC ≡ cashflow / cash-in
  are pinned by test.
- **Stale data flags, never silently used.** Cedar Falls' rate is seeded 44 days old; every
  underwrite it feeds carries the stale flag.
- **Ranked by THEIR bar.** The deal screen ranks only by the investor's recorded criteria (min
  DSCR / min CoC / max price / strategies) with a why-trace per row and the skipped counts
  shown; no recorded criteria → no ranking ("we rank by your bar, not ours").
- **No guarantees.** "Guaranteed / can't lose / risk-free" structurally cannot ship (tested);
  a deal alert is drafted R1 — a six-figure nudge never sends itself.

## What the engine computes
All three strategies (LTR / MTR / STR) side-by-side on the same stated assumptions: payment,
full amortization + payoff date (with the extra-principal scenario), NOI with every opex line,
cash flow, cap rate, cash-on-cash, DSCR, and 5/10/30-year exit IRRs per band (bisection IRR,
fixture-tested). Sensitivity grid: rate ±2% × rent ±10% → DSCR/CoC — "if the deal only works
in the bottom-right corner, the deal doesn't work."

## What this does not do yet
- **No live data.** The market is synthetic and labeled. Real deployment pulls sanctioned APIs
  only (FRED for rates, licensed MLS/listing feeds, AirDNA/Rentometer) — no scraping, per the
  anti-library.
- **No tax modeling** (depreciation, cost seg, 1031) — real CPA territory, deliberately out.
- **Not investment advice, structurally** — and the disclaimer ships on every surface.
- **Nothing is sent.**
