# Rebid OS — the graveyard re-bid desk (build 68)

**Working name:** Rebid OS · **Launch:** `prebuild-rebid-os` · **Port:** 8888
**Synthetic operator:** "Ridgeway Precision Machining" — 12 machines, ~40 quotes/mo, a
graveyard of ~300 lost quotes.
(Distinct from build 29 Traveler OS, which runs the shop floor — Rebid OS sells the shop's
idle hours to its own lost quotes.)

## The never-seen mechanism
Every lost quote becomes a STANDING ORDER that watches the shop's counted idle capacity; when
idle spindle-hours cross the marginal-cost floor the OS computes, the lost job re-bids itself
at a price the shop can defend. Lost-quote files and capacity boards both exist everywhere —
nothing has ever connected them.

## Modules
1. **The graveyard** (Company Brain) — every lost quote recorded with its loss reason (price /
   lead time / capability / silence), the machine-hours it would consume, material cost, and
   the price it died at; a quote with unrecorded hours reads UNREBIDDABLE — no hours, no
   marginal math.
2. **The capacity truth** (Operations) — idle hours per machine class per week, COUNTED from
   the recorded schedule (booked jobs vs available shifts), never estimated; below a recorded
   confidence floor (schedule not maintained that week) capacity reads unmeasured and the
   desk stands down — "we don't sell hours we can't count."
3. **The marginal floor** (Back Office) — per machine class: recorded variable cost/hr
   (labor, tooling, power) + material + the recorded minimum-margin line = the floor; the
   floor's arithmetic prints on every re-bid; a re-bid below the floor has NO PATH.
4. **The re-bid desk** (Sales) — when counted idle hours ≥ a graveyard job's hours AND the
   defensible price (floor + recorded margin) ≤ the price it died at: the re-bid drafts R1 —
   honest copy: "we have open capacity the week of X; same part, $Y — here's why the price
   moved." A job lost on capability never re-bids (the machine didn't change). Bounded: one
   re-bid per quote per quarter, silence is an answer.
5. **Intake triage** (Intake) — costly label: the hot RFQ with a deadline ("need 200 by
   Friday, can you?" — answered from counted capacity, never optimism) · re-bid reply ·
   quote-status · spec change · human.

## Guardrails (load-bearing)
- `bid_below_marginal_floor` — **R0, structural**: no path; the floor's math prints on
  every re-bid.
- `sell_uncounted_capacity` — **R0**; unmeasured week → the desk stands down.
- `rebid_capability_loss` — **R0**; the machine didn't change, the bid doesn't either.
- `promise_capacity_optimism` — **R0**; deadline answers cite counted hours only.
- Re-bids R1, bounded (1/quarter/quote, cooldown, silence-exit).

## ROI (typed)
Graveyard revenue recovered (counted re-bids won × recorded margin) · idle-hour absorption
(counted before/after) · the defensible-price story (scenario) · quoting hours (time_saved).

## Demo path
The graveyard (loss reasons counted) → this week's counted idle hours → a re-bid fires with
the floor's math printed → below-floor refusal → capability-loss refusal → uncounted-week
stand-down → the hot RFQ answered from counted capacity → trust tab.

## Build prompt
Shared contract, full built-out standard. Costly eval label: the deadline RFQ.
