# Sample Product — data sources

**Policy update (2026-07-03): the "hold on paid keys" is lifted — paid data sources
are approved.** Free NOAA sources still run the baseline (zero cost); Nick's paid
sources layer on top and auto-enable when their key/creds are set in the engine
environment (the engine runs server-side on the VPS, so keys stay private).

## Nick's connect list (2026-07-03)
| Source | What it gives | Env var(s) to enable | Adapter status |
|---|---|---|---|
| **api.weather.gov** (NWS) | Warnings / alerts | none (free) | ✅ live |
| **Xweather** (xweather.com) | NOAA-verified storm reports (hail/wind) | `XWEATHER_CLIENT_ID` + `XWEATHER_CLIENT_SECRET` | ✅ adapter built — needs creds |
| **Visual Crossing** (visualcrossing.com) | Historical/forecast wind gusts + severe risk (no hail size) | `VISUALCROSSING_KEY` | ✅ adapter built — needs key |
| **HailTrace** (hailtrace.com) | Radar-verified hail size + swaths | `HAILTRACE_KEY` | ⏳ scaffold — needs HailTrace's **API docs/endpoint** + key |

**To connect each:** drop the key(s) into the VPS engine env (`/home/claudeops/.config/storm-verified.env` or the systemd unit) and the source lights up in the published feed automatically. **HailTrace also needs their API documentation** (partner/enterprise API — endpoint + response shape) before the adapter can map it; everything else is just the key.

## Free baseline (always on, $0)
| Source | What it gives | Access | Status |
|---|---|---|---|
| **NOAA SPC** | Storm reports + day-1/2/3 outlooks | HTTP CSV/geojson | ✅ live |
| **IEM Local Storm Reports** | Structured ground hail/wind | HTTP geojson | ✅ (mesonet blocks CF Worker egress; runs in the Python engine) |
| **NOAA MRMS MESH** | Radar-derived max hail size | HTTP GRIB2 | ⏳ needs `pygrib` on the VPS + `MESH=1` |
| **mPING** (NOAA/NSSL) | Crowdsourced hail/wind | HTTP JSON | ⏳ free token (register) → `MPING_TOKEN` |
| **FL Statewide Cadastral** (FDOR) | Roof year / owner / value | ArcGIS (public) | ✅ live (client-side on /property + /canvass) |
| **US Census / OSM** | Address → lat/lon | HTTP JSON | ✅ live |

## The two things that need a decision (not a purchase)

### 1. MRMS MESH → needs a GRIB2 reader
MESH is free and public, but the files are **GRIB2** (a compressed binary grid
format). Our prototype is pure-Python-stdlib, which can't decode GRIB2. Options:
- **(A) Add one dependency** — `pygrib` or `cfgrib`/`eccodes` on the hosted
  build. Cleanest; the "stdlib-only" purity mattered for a zero-install laptop
  prototype, not for a hosted service. **Recommended.**
- **(B) Hand-write a minimal GRIB2 decoder** for just the MESH product. No deps,
  but fragile and a real time-sink under the Jul 9–10 deadline.
- **(C) Defer MESH to v2** — ship the internal test on the 3 keyless NOAA sources
  + free mPING token; add radar hail after the test proves the workflow.

MESH is the accuracy edge (fixes "atmospheric estimate vs ground truth"), so (A)
is worth the one dependency — but it's the Founder's call whether to add it now or defer.

### 2. mPING → needs a free registration
Free forever, but requires registering for a token at
`mping.ou.edu/registration/register/` (Developer/Research license, $0). Someone
has to sign up once; then it's a keyless-feeling HTTP call. Not a purchase.

## Bottom line for the Founder
- Nothing needs to be **bought** to run Nick's month-long internal test.
- Two free-but-not-instant steps: register mPING (5 min) and decide the GRIB2
  approach for MESH (recommend: add `pygrib` on the hosted build).
- Xweather/HailTrace stay parked as paid fallbacks we've now confirmed we don't need.
