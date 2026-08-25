# Marquee OS — party & tent rental (build 55)

**Working name:** Marquee OS · **Launch:** `prebuild-marquee-os` · **Port:** 8875
**Synthetic operator:** "Fairfield Event Rentals" — tents, tables, chairs, dance floors; ~50
events on the book, 2 install crews.

## Why this industry (the overlooked test)
Event rental is logistics + weather + damage deposits run on whiteboards, and no AI vendor
courts it. Every weekend is a capacity crunch where one double-booked tent ruins a wedding —
the most reputationally radioactive customer there is.

## The bleeding neck
The wind call. A staked tent in a storm is a killer — the industry's fatal-accident case law is
all wind — and the decision to install, hold, or take a tent down against a forecast is
judgment carrying lives. Software surfaces the recorded forecast and the manufacturer's rated
limits; it NEVER makes the call. The quiet leaks: inventory double-books across the weekend,
tent permits (per municipality) missed, damage deposits refunded without the recorded
condition check, and site requirements (underground utilities located, surface type) unasked
until the crew is standing on the lawn.

## Modules
1. **Event board** (Operations) — the weekend as a capacity plan: every reservation's items
   against counted inventory; a double-book is structurally impossible (reserve from counted
   stock or waitlist, never oversell).
2. **The wind rule** (Operations) — per-tent recorded rated wind limits + the recorded forecast
   at the event's site/date; `make_weather_call` R0 — the board flags "forecast exceeds rated
   limit" and a human decides install/hold/strike, on the record.
3. **Site & permit checklist** (Intake) — utilities-located (the recorded 811 ticket), surface,
   power, per-municipality tent permit clocks as DATE ALERTS; an install without the recorded
   811 ticket is refused ("a stake through a gas line is the other fatal case").
4. **Damage deposits** (Back Office) — deposit math only from the recorded out-condition vs
   return-condition (photos referenced); a deduction without both records is refused; refunds
   drafted R1.
5. **Quote desk** (Sales) — packages priced from the recorded catalog; delivery windows from
   the crew capacity plan, never invented.

## Guardrails (load-bearing)
- `make_weather_call` — **R0, never-promote.** Software states the numbers; a human owns the sky.
- `oversell_inventory` — structural: reservations draw from counted stock.
- `install_without_utility_locate` — **R0**; the 811 ticket is a wall.
- `deduct_deposit_without_condition_records` — refused; refunds/deductions R1.

## ROI (typed)
Weekend utilization lift (counted inventory idle rate × operator lift) · deposit disputes
avoided (scenario) · permit fines (scenario) · office hours (time_saved).

## Demo path
Weekend board (capacity counted) → double-book attempt refused → wind flag on Saturday's 40x60
→ human call recorded → 811-less install refused → deposit math from condition records → trust.

## Build prompt
Shared contract, full built-out standard. Costly eval label: the weather/safety worry on a
booked event.
