# Serve OS — build

Process serving agencies. Port **8877** (`prebuild-serve-os`).

```
python3 seed.py           # synthetic Docket Process Service
python3 test_serve_os.py  # the suite
python3 server.py         # 127.0.0.1:8877
```

## The load-bearing refusals
- **Software never signs and never attests.** The affidavit is a human's oath — `sign_or_attest`
  is R0, never-promotable, and never becomes an approvable row. A thousand clean runs cannot buy
  it.
- **Drafts assemble ONLY from the attempt log, verbatim.** An unlogged "fact" offered for the
  affidavit is refused and the request preserved verbatim in the record; if it happened, the
  server records it as a NEW log entry and the draft rebuilds.
- **The attempt log is append-only, recorded AT the attempt.** `edit_attempt` does not exist;
  a correction is a new entry pointing at the old one, and both remain. An attempt recorded more
  than 4h after the fact is labeled `late_recorded` forever — disclosed in the affidavit, never
  laundered.
- **Due diligence is the recorded rule against the log itself.** Substituted service refuses at
  2 of 3 attempts with the jurisdiction's rule cited and the gap named; it clears only when the
  log satisfies the recorded county rule (n attempts across distinct recorded hour-bands).

## Honesty rules (from `_kit`)
Costly eval label `deadline_risk` — a blown deadline collapses the case. The court deadline is
the master clock: the board and every server's day list rank by days-to-deadline, and a serve
with no recorded deadline is named, never guessed into the ranking. Status asks are answered
from the record (attempts + next window); outward drafts queue at R1. Recovered-this-week is
counted (serves completed, fees, deadline flags, late-record labels). ROI is typed; the
quashed-service file is a scenario the operator prices, never a claimed saving. Synthetic only.

**Nothing is sent.**
