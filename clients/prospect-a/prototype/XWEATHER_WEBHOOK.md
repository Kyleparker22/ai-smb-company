# Xweather webhook — setup + config

Push instead of poll: Xweather POSTs storm reports + alerts to us the instant
they're issued, so alerts fire in real time. `xweather_webhook.py` is the
receiver. Docs: https://www.xweather.com/docs/webhooks

## What to request from Xweather (Nick's list)
Webhooks are a **premium add-on** and **not self-serve** — you give Xweather (via
your account exec / support) the receiver URL + the datasets + coverage. Ask for:

| Dataset | Why | Filter we want |
|---|---|---|
| **Alerts** | official NWS watches/warnings | Florida; all severe-thunderstorm / tornado / hail alerts |
| **Storm reports** | ground-truth hail/wind reports | **hail ≥ 0.75"**, **wind ≥ 55 mph**, tornado |
| **Storm cells** (optional) | radar-tracked cells / hail size | hail-bearing cells over FL |
| **Hail threats** (optional) | real-time hail threat polygons | FL |

**Coverage:** Florida (state or a bounding box).
**Filtering note:** Xweather can pre-filter server-side; whatever it can't, our
receiver enforces anyway (**hail ≥ 0.75", wind ≥ 55 mph, tornado always, all
alerts**) — those thresholds live in `xweather_webhook.py` (`HAIL_MIN`/`WIND_MIN`).

## What to give Xweather
1. **Receiver URL** — a public **HTTPS** endpoint, e.g. `https://storm.yourco.com/xweather` (this receiver behind TLS).
2. **Shared secret** — they send it as `X-API-KEY` (or `?secret=`); set the same value as `XWEATHER_WEBHOOK_SECRET` on the receiver so only Xweather can trigger it.
3. **Datasets + coverage** from the table above.

## Receiver behavior (per Xweather's requirements)
- Accepts `POST` JSON, **returns 202 immediately**, processes async. ✅
- Verifies the shared secret. ✅
- Filters to Nick's thresholds, then queues an **approval-gated** alert (never auto-texts). ✅
- Kept events land in `xweather_events.json` for the alert feed / dispatch.

## Go-live steps
1. Contact Xweather to enable webhooks on Nick's account + register the URL.
2. Host `xweather_webhook.py` behind HTTPS (same box as the runtime; `storm.yourco.com`).
3. Set `XWEATHER_WEBHOOK_SECRET` to the shared secret.
4. Confirm the first real payload's field names and adjust the two `[CONFIRM]` spots in the parser if needed.

Until then, the polling watcher (`watch.py`) covers real-time off free NOAA — the
webhook is the upgrade that makes it instant and adds Xweather's hail precision.
