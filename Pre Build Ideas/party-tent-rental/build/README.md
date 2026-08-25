# Marquee OS — build

Party & tent rental. Port **8875** (`prebuild-marquee-os`).

```
python3 seed.py             # synthetic Fairfield Event Rentals
python3 test_marquee_os.py  # the suite
python3 server.py           # 127.0.0.1:8875
```

## The load-bearing refusals
- **Software never makes the weather call.** It states two recorded numbers — the forecast on
  file against the tent's recorded rated wind limit — and a human decides install, hold, or
  strike, on the record. `make_weather_call` is R0 and never promotable; the wind reply is
  tone-checked structurally and can state numbers but never reassure.
- **An oversell has no code path.** Reservations draw from counted stock per weekend or go to
  the waitlist honestly — there is no force flag and no override argument; the absence is the
  guarantee.
- **The 811 ticket is a wall.** An install without the recorded utility-locate ticket is
  refused — a stake through a gas line is the other fatal case.
- **The deposit is never touched without both condition records.** Deduction and refund alike
  draft only from the recorded out-condition vs return-condition pair (photos referenced),
  at R1; a missing record is named, never papered over.
- **Permit clocks are DATE ALERTS**, per municipality from a table that names itself a DEFAULT
  — not legal advice; filing is a human act.

## Honesty rules (from `_kit`)
Costly eval label `weather_worry` — the wind worry on a booked event reads first. Recovered-
this-week counted (a draft is not a send). ROI typed; disputes avoided and permit fines are
scenarios and render blank without the operator's own inputs. Automation is counted from the
append-only event log, never asserted. Synthetic only; the server binds 127.0.0.1.

**Nothing is sent.**
