# Well OS — build

Well drilling & water treatment. Port **8872** (`prebuild-well-os`).

```
python3 seed.py          # synthetic Blue Ridge Well & Water
python3 test_well_os.py  # the suite
python3 server.py        # 127.0.0.1:8872
```

## The load-bearing refusals
- **Software never declares water safe.** A potability verdict is a recorded lab report —
  id, date, result, quoted verbatim — or it does not exist: "we don't know yet, the lab
  does." The system quotes the report; it never adds to it.
- **A contamination worry is never soothed.** "My water smells like rotten eggs" gets a
  procedure: verbatim record, sampling visit to the top of the route, a human same-day.
  The copy runs the soothe check structurally — "probably fine" cannot ship.
- **"Protected" is never claimed past the clock.** A UV lamp past its recorded interval
  still glows; it just stops sterilizing. Overdue reads overdue; an unrecorded clock reads
  unmeasured, never current.
- **We measure, then we price.** A quote with no recorded well log (depth, casing, yield,
  static level) is refused — a number without the log is a guess in writing.
- **County permit clocks are DATE ALERTS**, computed from a config-named DEFAULT rules
  table that says replace-before-go-live — dates, never legal advice.

## Honesty rules (from `_kit`)
Costly eval label `contamination` (the health stake, reported separately). Reminder
ladder: 3 touches, 14-day cooldown, then silence is an answer. Recovered-this-week
counted (human sends count; agent drafts don't). ROI typed; the permit-fines line is a
scenario that stays blank until the operator puts a number on it. Automation % counted
from the append-only event log.

## What this does not do yet
No real messaging, telephony, or lab integration — lab reports are typed records, not a
LIMS feed. No state e-filing; the permit table is a default to replace per county. No
payments, no scheduling backend. Synthetic data only. **Nothing is sent.**
