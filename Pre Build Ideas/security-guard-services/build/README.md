# Post OS — build

Security guard services. Port **8862** (`prebuild-post-os`).

```
python3 seed.py         # synthetic Granite Shield Security
python3 test_post_os.py # the suite
python3 server.py       # 127.0.0.1:8862
```

## The load-bearing refusals
- **Incident narratives are append-only and verbatim.** No edit and no delete exist; a
  correction comes only from the reporting guard and keeps both versions; a client's adjust
  request is refused and preserved verbatim in the record.
- **The credential gate.** A post fills only with a guard whose recorded, unexpired credential
  set matches — the lapse is named; expiry drops the guard from fill lists by construction.
- **Use-of-force questions** go to a human supervisor, never software.

## Honesty rules (from `_kit`)
Costly eval label `incident`. Credential expiries as DATE ALERTS (45-day horizon). Recovered-
this-week counted. ROI typed; the unedited file is a scenario. Synthetic only; nothing is sent.
