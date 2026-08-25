# Fix OS — build

Appliance repair. Port **8878** (`prebuild-fix-os`).

```
python3 seed.py         # synthetic Reliable Appliance Service
python3 test_fix_os.py  # the suite
python3 server.py       # 127.0.0.1:8878
```

## The load-bearing refusals
- **An incomplete warranty claim cannot be submitted.** The claim builder names every missing
  field — serial, purchase-proof ref, failure code, parts, narrative-matches-parts — and there
  is no force-submit anywhere in the build. A denied claim is free work.
- **The COD clamp.** Work past the customer's recorded authorized amount has no path; the
  overage drafts back at R1 for the customer's approval — that is the only way the number moves.
- **The safety script leads.** Gas / spark / flood reads before everything, the customer's own
  words survive verbatim in the draft, and software never downgrades the symptom.
- **Narratives assemble from recorded diagnosis fields only.** An invented sentence on a claim
  form is fraud; the refusal says so.
- **The recall notice rides the ticket verbatim** — never summarized, never dropped.

## Honesty rules (from `_kit`)
Costly eval label `safety_symptom`. Parts-to-bring comes from the unit's own history + the
recorded likely-parts map — the first-visit fix is the margin, and nothing is guessed.
Recovered-this-week counted (claims paid, human releases, first-visit fixes). ROI typed; COD
disputes are a scenario that renders blank until the operator prices it. Warranty vs COD routes
from recorded coverage. Synthetic only. **Nothing is sent.**
