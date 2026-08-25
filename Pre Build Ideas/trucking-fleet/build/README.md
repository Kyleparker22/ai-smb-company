# Hours OS — build

Small trucking fleet. Port **8865** (`prebuild-hours-os`).

```
python3 seed.py          # synthetic Redline Carriers
python3 test_hours_os.py # the suite
python3 server.py        # 127.0.0.1:8865
```

## The load-bearing refusals
- **The HOS dispatch gate.** Run hours + 1h buffer vs the driver's RECORDED clock, by
  construction — the arithmetic is shown, and an unsynced clock reads UNKNOWN and cannot
  dispatch anything.
- **"Fix his log" is refused and preserved verbatim** — the falsification line; annotations
  draft FOR the driver, nothing is edited for them.
- **Detention bills only from the recorded stamp pair** — "we waited forever" is a feeling;
  stamps are an invoice.
- **After an accident, nothing outward drafts from software** — the preservation brief goes to
  the safety director and counsel drives.
- **An OOS truck gets fixed, not assigned.**

## Honesty rules (from `_kit`)
Costly eval label `log_ask`. Recovered-this-week counted. ROI typed; prevented violations and
the clean-log file are scenarios. Synthetic only; nothing is sent.
