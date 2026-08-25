# Shine OS — build

Car wash & detailing. Port **8858** (`prebuild-shine-os`).

```
python3 seed.py          # synthetic Brightline Wash Co.
python3 test_shine_os.py # the suite
python3 server.py        # 127.0.0.1:8858
```

## The load-bearing refusals
- **Software never denies a damage claim.** Verbatim log + footage pull + a manager calls with
  the footage in front of them. "Our brushes couldn't do that" cannot be produced.
- **The cancellation clock starts at the request.** The save offer is a separate row; processing
  never waits on it, and a charge after the recorded request is structurally impossible.
- **Dunning never threatens** — three stepped touches with the forbidden-language check, and
  touch 3 offers same-day cancel as the honest exit.
- **Weather reschedules are honest drafts**, not voicemails.

## Honesty rules (from `_kit`)
Costly eval label `damage_claim`. Recovered-this-week counted. ROI typed; the claims file is a
scenario. Synthetic only; nothing is sent.
