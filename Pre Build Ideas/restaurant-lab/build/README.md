# Lab OS — build

Multi-unit restaurant groups: your locations are your lab. Port **8889** (`prebuild-lab-os`).

```
python3 seed.py          # synthetic Blue Finch Hospitality (5 units)
python3 test_lab_os.py   # the suite
python3 server.py        # 127.0.0.1:8889
```

## The load-bearing refusals
- **TOO EARLY TO KNOW is a real verdict.** Below the recorded, `_source`-named sample floor,
  the verdict function's return *literally contains no winner, no lift, no direction and no z*
  — a 1800% fake lift on 100 tickets reads exactly the same as no data. Concluding early is
  refused; the confident fiction cannot be produced.
- **One lever per dial.** A new experiment whose metric overlaps a live experiment on any
  shared unit is refused at creation — two live levers on one dial make both unreadable.
- **The rollout gate has one door.** A rollout recommendation drafts at R1, stats attached,
  only from a concluded CLEAR verdict with treatment ahead. From a live experiment or a NOISE
  result there is no path — not a warning, a refusal.
- **The 86 ledger prices from the unit's own recorded pace** (median units/hr for that item
  and daypart × hours dark × price). No pace history → unmeasured: counted, never dollared.
- **The illness claim** ("your tacos made me sick") inherits the Unit OS rule exactly: logged
  verbatim, never answered in writing by software — human + counsel path only.

## Honesty rules (from `_kit`)
Costly eval label `illness`. Verdict confidence is a stated, deterministic z-approximation
bucketed clear / probable / noise — no library, no p-hacking surface. The menu graveyard keeps
killed items' recorded numbers so "let's bring it back" starts from facts. Weekly 86 cost and
the counted week come from the ledger and the event log, never asserted. ROI typed; the
bad-rollout-avoided line is a scenario and never a saving. Demo fixtures are `demo_tag`-skipped
by every sweep. Synthetic only. **Nothing is sent.**
