# Reserve OS — build

HOA management. Port **8887** (`prebuild-reserve-os`). Synthetic operator: Northgate
Community Management — 14 associations, ~2,300 doors.

```
python3 seed.py            # synthetic Northgate (one no-study assoc, one stale study)
python3 test_reserve_os.py # the suite
python3 server.py          # 127.0.0.1:8887
```

## The never-seen mechanism
- **Funding bands.** Reserve adequacy is never one number: the recorded balance and
  contribution are projected against the recorded reserve study's component replacements at
  bear/base/bull cost-inflation (recorded offsets, `_source`-named). The
  **special-assessment horizon is per band** — the first year the projected balance goes
  negative, or "beyond the study window," honestly. No study → **UNKNOWABLE** ("no study,
  no adequacy claim"). A study past the recorded staleness threshold flags every number it
  feeds.
- **One ledger, two doors.** The homeowner portal renders from the **same `board_view()`
  function** the board sees — structurally one read path; it removes only other homeowners'
  personal details, never a figure. The suite asserts the funding numbers and violation
  counts are identical through both doors. "Why did my dues rise" is answered by citation:
  the recorded line items verbatim plus the band math.

## The load-bearing refusals
- **No rule, no violation — structurally.** `create_violation` is the only writer to the
  ledger and cannot produce a row without resolving the cited CC&R section against the
  association's recorded rules list.
- **The fine clamp.** Fines are the recorded schedule's arithmetic; any other amount is
  refused (R0, logged, never approvable). The **hearing decision is a human act** — software
  assembles the file, cites the rule, and stops.
- **Safety first.** "The stairwell railing is loose" routes NOW, verbatim, at R2 — ahead of
  the queue; dismissal has no code path.
- **The horizon is always bands, never one date.** Outward everything (notices, replies,
  the monthly board packet) drafts R1.

## Honesty rules (from `_kit`)
Costly eval label `safety`. Counted week (escalations, human-sent notices, citation-answered
disputes, hearings decided). ROI typed; the avoided special-assessment shock and the
fairness-won contract are scenarios, never claimed savings. Automation counted from the
append-only log. White-label. Synthetic only.

**Nothing is sent.**
