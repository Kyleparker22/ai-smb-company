# Blackbox OS — build

HVAC & plumbing evidence-priced memberships. Port **8882** (`prebuild-blackbox-os`).

```
python3 seed.py             # synthetic Comfort First Mechanical (~1,400 homes)
python3 test_blackbox_os.py # the suite
python3 server.py           # 127.0.0.1:8882
```

## The never-seen mechanism
The maintenance membership **prices itself per-home** from the home's own black box —
recorded equipment ages and service history — and the customer sees the exact math:
every factor as `{label, dollars, why}` from a RECORDED pricing table (`_source`-named).
"Your furnace is 19 years old: +$9/mo; zero callbacks in 3 years: −$4/mo."

## The load-bearing refusals
- **An unrecorded age reads UNKNOWN.** It is never guessed (`invent_component_age`, R0):
  the quote goes PROVISIONAL at the flat recorded rate with the reason named — never a fake
  personalized price.
- **A locked price is locked.** `reprice_mid_term` is R0 *structural* — no function in this
  build writes a member's locked price mid-term; the endpoint exists only to show the refusal.
  Re-pricing happens at renewal, and the notice carries the exact factor deltas verbatim
  ("furnace crossed the 15-year band: +$6/mo") — in both directions.
- **The quote is the full enumeration or a refusal** (`hide_pricing_factor`, R0): the shown
  factors must sum to the price, to the cent.
- **A gas smell gets the evacuate script verbatim** (`dismiss_gas_smell`, R0) — never
  reassurance. The no-heat/no-cool emergency reads first in triage.
- **The fairness challenge** ("why is my plan more than my neighbor's") is answered with the
  asker's own factors — "market rates" is structurally forbidden language.

## Honesty rules (from `_kit`)
Costly eval label `emergency`. The honesty board counts members whose renewal price went
**DOWN** — the trust stat a flat-plan incumbent cannot print. This-week is counted (a human's
sent quote counts; an agent's gated draft does not). ROI is typed; the price-trust story is a
scenario line that stays blank until the operator owns a number. Events are append-only;
automation is counted from the log or refused. Synthetic only. **Nothing is sent.**
