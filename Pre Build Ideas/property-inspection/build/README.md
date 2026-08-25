# Inspect OS — build

Property / home inspection. Port **8856** (`prebuild-inspect-os`).

```
python3 seed.py            # synthetic Keystone Property Inspections
python3 test_inspect_os.py # the suite
python3 server.py          # 127.0.0.1:8856
```

## The load-bearing refusals
- **Findings are append-only.** There is no edit and no delete anywhere in the module — a
  revision is a NEW entry pointing at the old one, both kept. That absence is the rule.
- **The soften request is refused and preserved verbatim** — the request itself becomes part of
  the record (the E&O defense file).
- **Client-first release.** The report belongs to the paying client; anyone else needs the
  client's recorded authorization.
- **No repair costs, no buy/walk advice** — not our license; the trades quote, the client decides.

## Honesty rules (from `_kit`)
Costly eval label `soften_request`. The 24h report clock computed per inspection. Recovered-this-
week counted (delivered, refusals, bookings). ROI typed; the defense file is a scenario.
Synthetic only; nothing is sent.
