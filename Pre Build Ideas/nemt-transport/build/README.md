# Ride OS — build

Non-emergency medical transport. Port **8866** (`prebuild-ride-os`).

```
python3 seed.py         # synthetic CareRoute Transport (no real PHI)
python3 test_ride_os.py # the suite
python3 server.py       # 127.0.0.1:8866
```

## The load-bearing refusals
- **A condition observation is never assessed.** "Grandma seems confused" goes verbatim to a
  human and the facility; the ack says plainly "we're drivers, not clinicians."
- **The trip-log billing gate.** Odometers, times, signature — or no invoice: an undocumented
  trip is free work with a Medicaid audit attached.
- **The never-bump rule.** Dialysis/chemo/radiation trips cannot be displaced by software; a
  conflict escalates to a human.
- **The credential gate.** No assignment without current license/background/CPR/securement — the
  lapse named.

## Honesty rules (from `_kit`)
Costly eval label `condition_change`. Recovered-this-week counted. ROI typed; the never-bump
record and securement file are scenarios. Synthetic only; nothing is sent.
