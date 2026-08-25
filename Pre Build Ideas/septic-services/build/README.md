# Pump OS — build

Septic & portable sanitation. Port **8853** (`prebuild-pump-os`).

```
python3 seed.py         # synthetic Clearline Septic & Site Services
python3 test_pump_os.py # the suite
python3 server.py       # 127.0.0.1:8853
```

## The load-bearing refusals
- **The manifest billing gate.** A pump-out bills only with gallons + disposal site + manifest
  reference — an unmanifested load is unprovable work AND a DEQ exhibit.
- **No phone diagnosis.** "Is it the baffle?" gets a tech visit, never a guess.
- **No unpermitted land application.** A permit is a paper fact, not a verbal one.
- **A backup is an emergency, not a booking** — truck window + human now.

## Honesty rules (from `_kit`)
Costly eval label `emergency`. Interval recall ladder: 3 touches, 30-day cooldown; a system with
no recorded pump date reads unknowable, never assumed. Recovered-this-week counted. ROI typed;
the DEQ audit is a scenario. Synthetic only; nothing is sent.
