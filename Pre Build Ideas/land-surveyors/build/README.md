# Plat OS — build

Land surveyors. Port **8873** (`prebuild-plat-os`).

```
python3 seed.py          # synthetic Meridian Land Surveying
python3 test_plat_os.py  # the suite
python3 server.py        # 127.0.0.1:8873
```

## The load-bearing refusals
- **Software never states where a boundary falls.** An unlicensed boundary opinion is
  practicing surveying without a license. The encroachment question is recorded verbatim in an
  append-only log, routed to the recorded PLS by name, and the draft reply is conclusion-checked
  structurally — no "encroach", no "the line is".
- **The seal gate.** A plat reads "sealed" only with its recorded seal reference — number and
  date — and only by the PLS's own act. There is no code path to sealed without them, and no
  Approve button either: it is not a slow yes.
- **A boundary without its chain is an opinion.** Drafting refuses until the deed book/page and
  prior plats are cited on the record.
- **Closing promises come from recorded stage clocks** — medians counted from sealed jobs'
  own logs, projected against the closing date, flagged to a human BEFORE closing week. No
  recorded clocks → a refusal, not a guess.
- **A quote is the median of recorded comparables** (type × acreage bucket, 3 minimum) — or a
  refusal.
- **Fieldwork without a same-day crew sheet reads incomplete** via unmeasured — never assumed.

## Honesty rules (from `_kit`)
Costly eval label `boundary_question`. The deadline board ranks by days-to-closing — the master
clock — with blockers named; jobs with no closing date rank last, never guessed. Recovered-this-
week counted (plats sealed, closings kept, boundary questions routed, alerts a human sent). ROI
typed; the lost title company is a scenario that renders blank until the operator prices it.
Synthetic only. **Nothing is sent.**
