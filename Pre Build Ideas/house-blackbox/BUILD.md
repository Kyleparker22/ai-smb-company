# Blackbox OS — HVAC & plumbing membership pricing (build 62)

**Working name:** Blackbox OS · **Launch:** `prebuild-blackbox-os` · **Port:** 8882
**Synthetic operator:** "Comfort First Mechanical" — HVAC + plumbing, ~1,400 households.

## The never-seen mechanism
**The House Black Box:** every home carries a flight recorder — equipment make/model/install
dates, every repair, every reading — and the maintenance membership **prices itself per-home
from that record**. A 4-year-old system in a well-kept house pays less than a 19-year-old
furnace with three callbacks, and the customer sees the exact math. Every incumbent sells one
flat plan priced on hope.

## Modules
1. **The black box** (Company Brain) — per-home equipment ledger + service history; a home
   with unrecorded equipment ages reads UNKNOWN on those components, never guessed.
2. **Evidence-priced membership** (Sales) — price = recorded base + per-component age/history
   factors from a RECORDED pricing table (config, `_source`-named); the quote shows every
   factor and its dollar ("your furnace is 19 years old: +$9/mo; zero callbacks in 3 years:
   −$4/mo"). A home below the record floor (too few recorded components) gets a flat
   provisional plan with the reason named — never a fake personalized price.
3. **The re-price clock** (Back Office) — memberships re-price only at renewal, from the
   updated record; mid-term the price is locked (no surprise raises); a renewal price that
   moved carries the exact factor deltas that moved it.
4. **Intake triage** (Intake) — no-heat/no-cool emergency (costly label, safety script for gas
   smell) · membership quote ask · service booking · price-fairness challenge ("why is my
   plan more than my neighbor's" → the factors, verbatim, never "market rates").
5. **Membership honesty board** (Operations) — counted: members whose price went DOWN at
   renewal (the trust stat incumbents can't print), price-vs-claims per home.

## Guardrails (load-bearing)
- `invent_component_age` — **R0**; unrecorded reads UNKNOWN and prices provisional.
- `reprice_mid_term` — **R0, structural**: no code path changes a locked member price.
- `hide_pricing_factor` — **R0**; the quote enumerates every factor or refuses to quote.
- `dismiss_gas_smell` — **R0**; the evacuate script verbatim.
- Outward drafts R1; renewal notices carry the factor deltas verbatim.

## ROI (typed)
Membership conversion (counted quotes→joins, operator lift) · retention at renewal (counted)
· break-fix→recurring mix shift (counted) · the price-trust story (scenario).

## Demo path
A home's black box → the priced quote with visible factors → the neighbor-comparison challenge
answered with factors → provisional-plan refusal on a thin record → mid-term reprice refused →
renewal with factor deltas → trust tab.

## Build prompt
Shared contract, full built-out standard. Costly eval label: the no-heat / gas-smell emergency.
