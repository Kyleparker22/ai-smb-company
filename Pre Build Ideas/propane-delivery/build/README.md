# Fuel OS — build

Propane delivery. Port **8863** (`prebuild-fuel-os`).

```
python3 seed.py         # synthetic Northline Propane
python3 test_fuel_os.py # the suite
python3 server.py       # 127.0.0.1:8863
```

## The load-bearing refusals
- **The leak-check gate.** An out-of-gas ticket cannot close without the tech's recorded
  leak-check result — the system was open to air, and relighting without the test is how houses
  explode. The customer copy states it as non-negotiable.
- **Gas smells get the evacuate script verbatim** and are never troubleshot by phone.
- **The contract clamp.** A contract customer's price IS the recorded contract price by
  construction.
- **The requalification gate.** An out-of-date tank gets requalified, not filled; no date reads
  UNKNOWN and is equally unfillable.

## Honesty rules (from `_kit`)
Costly eval label `gas_smell`. Runout board from recorded usage (no history → UNKNOWN, never
"fine"). Recovered-this-week counted. ROI typed; the leak-check file is a scenario. Synthetic
only; nothing is sent.
