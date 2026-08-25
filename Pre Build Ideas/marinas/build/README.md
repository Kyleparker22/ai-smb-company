# Slip OS — build

Marina & boat yard. Port **8868** (`prebuild-slip-os`).

```
python3 seed.py         # synthetic Harborview Marina & Boatworks
python3 test_slip_os.py # the suite
python3 server.py       # 127.0.0.1:8868
```

## The load-bearing refusals
- **A spill is logged verbatim with cause never asserted** — a fuel-dock log entry is a USCG
  exhibit; the dockmaster hears NOW.
- **The work-authorization gate.** No clock-in without the owner's recorded scope + rate — a
  verbal go-ahead at the fuel dock is a note, not a gate pass.
- **The storage clamp.** Billing computes from recorded arrival to recorded departure by
  construction — the meter stops the day the boat splashes.
- **Seaworthiness is a surveyor's word, never software's.**
- **The waitlist is arithmetic**: recorded order, fit-checked on length/beam/draft, 48h first
  refusal — the shoebox retired.

## Honesty rules (from `_kit`)
Costly eval label `spill`. Recovered-this-week counted. ROI typed; the spill log and prevented
disputes are scenarios. Synthetic only; nothing is sent.
