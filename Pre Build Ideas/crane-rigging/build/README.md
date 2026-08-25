# Rig OS — build

Crane & rigging. Port **8867** (`prebuild-rig-os`).

```
python3 seed.py        # synthetic Blue Iron Crane & Rigging
python3 test_rig_os.py # the suite
python3 server.py      # 127.0.0.1:8867
```

## The load-bearing refusals
- **Software never approves a lift plan** — it only checks that a recorded plan and its signer
  exist. The lift director signs.
- **The certification gate per crane class** — a TSS card doesn't swing a lattice boom.
- **The wind gate by arithmetic** — forecast vs the configuration's recorded chart limit; a
  human may only agree with a stand-down. No recorded limit → no dispatch.
- **A critical-flagged RFQ cannot be quoted as taxi work** — the flags force the engineering
  path (Traveler pattern), and the copy calls it a compliment to the job.
- **No firm quote without site data** — a wrong radius is a change-order fight or a tipped crane.

## Honesty rules (from `_kit`)
Costly eval label `critical` (the routine lift that wasn't). Recovered-this-week counted. ROI
typed; the lift-plan file is a scenario. Synthetic only; nothing is sent.
