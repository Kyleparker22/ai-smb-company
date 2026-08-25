# Sample Product — live feed publisher (VPS setup)

> **Status: LIVE — client infrastructure, not an yourco loop.** `yourco-storm-publish.timer` is active on the VPS and fired 2026-08-23. Counted as `client-infra` in loop health, deliberately outside yourco's own loop scoring.

The hosted Sample Product app (Cloudflare Worker) **can't fetch NOAA itself** — that
host blocks all outbound internet except Higgsfield's own API. So the engine runs
here on the VPS (which has internet + Python + pygrib for MESH), and **publishes**
the verified feed to the Worker, which stores it in D1 and serves it. This is the
"Option 1" architecture (VPS publishes → Worker reads a binding).

```
storm_poc.py (NOAA fetch + verify + grade)  ──►  storm_publish.py  ──POST──►
   /api/ingest (Worker, secret-gated)  ──►  D1 feed_cache  ──►  getFeed serves LIVE
```

## One-time setup on the VPS
1. Secret file (not in git):
   ```
   mkdir -p /home/claudeops/.config
   cp /home/claudeops/yourco-os/runtime/storm-verified.env.example /home/claudeops/.config/storm-verified.env
   # edit it: set INGEST_SECRET to the Worker's INGEST_SECRET value
   chmod 600 /home/claudeops/.config/storm-verified.env
   ```
   The `INGEST_SECRET` must match the Worker secret (set via the website-builder
   secrets tool). Rotate by updating both.
2. Install the units:
   ```
   sudo cp /home/claudeops/yourco-os/runtime/systemd/yourco-storm-publish.{service,timer} /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable --now yourco-storm-publish.timer
   ```
3. Test once: `sudo systemctl start yourco-storm-publish.service && journalctl -u yourco-storm-publish -n 20`
   Expect: `published N storms -> 200 {"ok":true,...}`.

## Cadence
Every 20 minutes (`yourco-storm-publish.timer`). NOAA SPC/LSR refresh on that order;
adjust `OnCalendar` if you want it tighter during active weather.

## Manual publish (any host with internet)
```
INGEST_URL=https://sweet-opal-720.higgsfield.app/api/ingest \
INGEST_SECRET=xxxxx  DAYS=8  python3 clients/prospect-a/prototype/storm_publish.py
```

## Notes
- The publisher sends a browser-like User-Agent — the preview host 403s default
  UAs at the edge.
- MESH radar hail: install `pygrib` on the VPS + set `MESH=1` in the env file to
  fold radar-derived hail into the published feed (see `mrms_mesh.py`).
- Production URL: when the app ships to production, point `INGEST_URL` at the prod
  origin's `/api/ingest`.
- Parcel/property lookup stays a **browser→data-source** call (the roofer's phone
  has internet); it is not part of this feed publish.
