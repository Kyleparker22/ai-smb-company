# Flue OS — build

Chimney sweeps & hearth services. Port **8876** (`prebuild-flue-os`).

```
python3 seed.py         # synthetic Hearthstone Chimney Co. (~1,900 households)
python3 test_flue_os.py # the suite
python3 server.py       # 127.0.0.1:8876
```

## The load-bearing refusals
- **The burn verdict.** "Safe to burn" is answered by the recorded inspection — level 1/2/3,
  date, tech, findings, cited — or by "book the inspection." No record, a stale record, or no
  matched household all refuse: software never declares safe beyond the record
  (`declare_safe_to_burn` — R0, never-promote).
- **The hazard survives verbatim.** A stage-3 creosote, blockage, or CO finding is carried
  word-for-word into every draft — burn reply and inspection report alike — and the drafts run
  the verbatim + softener checks structurally before they ship. "Could use a cleaning" is
  forbidden language.
- **A CO or smoke event is never a booking.** The evacuate script (out NOW, 911 from outside,
  call us after) is the whole reply, verbatim, and the escalation runs at R2 because it cannot
  wait for a click.
- **A chimney fire forces the Level 3.** Per the recorded rule (NFPA 211, simplified default —
  the operator's adopted text replaces it before go-live), a sweep is not the response.

## The revenue engine
Due-for-annual is counted from each household's own record (~600+ of 1,900 in the seed); the
recall ladder is bounded (3 touches, 21-day cooldown), skips demo fixtures and no-record
households (a recall that cites nothing is spam), and is seasonal-aware: October overflow is
offered the recorded off-season rate on a February slot instead of being silently lost. A
discount nobody recorded is a discount nobody offers.

## Honesty rules (from `_kit`)
Costly eval label `co_smoke_event`. ROI typed; the house-fire file is a scenario that renders
blank — the fire that didn't happen is never a saving. Recovered-this-week counted (sweeps,
human-sent recalls, CO escalations). Automation rate counted from the event log or refused.
Synthetic records only — invented names, 555 phones. **Nothing is sent.**
