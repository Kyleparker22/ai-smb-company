# Code OS — build

Fire & life-safety inspection. Port **8855** (`prebuild-code-os`).

```
python3 seed.py         # synthetic Sentinel Fire Protection
python3 test_code_os.py # the suite
python3 server.py       # 127.0.0.1:8855
```

## The load-bearing refusals
- **No record, no green check.** A device with no inspection record reads UNKNOWN — marking it
  compliant without an inspector's recorded result is structurally refused.
- **An impairment is never downgraded or closed by software.** The owner is called NOW with
  fire-watch language; a human verifies the fix.
- **Software never certifies** — the licensed inspector signs; it drafts the paperwork.
- **The fire marshal talks to the owner**, never to software.

## Honesty rules (from `_kit`)
Costly eval label `impairment`. Deficiency ladder: 3 touches, 10-day cooldown, honest exit
("another contractor fixed it — send the record, that's a fine outcome too"). Recovered-this-week
counted. ROI typed; the impairment log is a scenario. Synthetic only; nothing is sent.
