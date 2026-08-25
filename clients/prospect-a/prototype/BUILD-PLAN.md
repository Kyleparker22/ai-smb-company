# Sample Product — build plan (Nick internal test → potential market)

From the the Founder × Nick call, 2026-07-02. Product name: **Sample Product**
(supersedes the prototype's "Storm Command" working title). Goal: a build Nick
can **test internally for ~a month**, then decide on marketing.

## The plan (from the call)
- **Internal test first**, ~1 month, Nick's own crews. Then potentially market.
- **Free / open data first** — Nick to send his list of sites; the Founder checks open-source access before any paid API keys (hold on purchasing keys). xWeather dev webhook (~$3.99/mo) is a fallback only.
- **Legal before public** — data-reselling rights, API terms, third-party patents. Fine internally now; attorney required before any public launch / social / paid subscriptions.
- **Partnership:** one sells, one builds.
- **Pricing target:** $5–10k/yr per company (comps ~$3,500/yr). FL alone 2,000–5,000 roofers. (Economics: `PRICING.md`.)
- **Milestone:** initial build ready to test **~Thu Jul 9 / Fri Jul 10** (the Founder out Wed Jul 8 for mediation).

## Product spec (Sample Product) — from the call
1. Aggregate **5–6 weather sources** into one **AI-verified alert feed** — AI cross-references and **averages** wind/hail readings for accuracy; **flags + grades** severity; **learns close rates by storm type** over time.
2. **Pre-storm alerts** so crews prep before it hits.
3. **Property intelligence** — roof age, owner-occupancy, lead scoring → **optimized door-knock routes**.
4. **Crew tracking** — doors knocked, interest level, signed jobs, coverage map by member; kills double-knocking + "what did we hit yesterday?".
5. **One-tap verified alert** pushed to crew phones — replaces group chats.
6. **Storm verification reports** for insurance claim submissions.
7. **CRM integrations** (JobNimbus, AccuLynx) — later.

## What's already built (prototype → maps onto the spec)
| Spec item | Built |
|---|---|
| Aggregate + AI-verify + grade | `storm_poc.py` (IEM LSR + SPC + NWS, cross-verified) + `verify_ai.py` (reads reports, GO/HOLD/REJECT, claim-grade) → demo.html |
| Pre-storm alerts | `staging.py` + staging.html (SPC outlooks) |
| Property intel + routes | `property.py` + `canvass.py` → canvass.html ("where to knock") |
| Crew tracking + coverage | `crew.html` + `crew_server.py` (roofer / route / coverage) |
| One-tap alert to phones | `dispatch.py` (Twilio, approval-gated) + demo phone flow |
| Claim reports | `claim.py` → claim.html (adjuster-ready packet) |
| Address → best storm date | `address.py` → address.html (12-mo claim window) |
| Learns close rates | `learning.py` → learning.html + ROI dashboard |
| Real-time alert feed | `watch.py` + alerts.html; Xweather webhook receiver ready |
| Hub + narrated demo | index.html (control tower) + tour.html |

**~80% of the spec already has a working surface.** The internal-test build is
mostly: (a) hosting, (b) the free-source aggregation + averaging/grading refinement,
(c) making crew data real/persistent/mobile for a month of use.

## Open-source data plan (the Founder's action item — no paid keys)
5–6 free sources cover what HailTrace/Hail Maps do:
- **NWS API** (`api.weather.gov`) — alerts/warnings. JSON. ✅ live.
- **NOAA SPC** storm reports + convective outlooks (pre-storm). ✅ live.
- **IEM Local Storm Reports** — structured ground reports. ✅ live.
- **NOAA MRMS MESH** — radar-derived max hail size, CONUS, every ~2 min, `MESH_Max_1440min` (NCEP, GRIB2). **The radar hail layer that replaces HailTrace** (fixes "atmospheric vs ground"). Free; GRIB2 parsing is the one real lift. — *to add*
- **mPING** (NOAA/NSSL) — crowdsourced hail/wind reports. Free. — *to add*
- **CoCoRaHS** — community hail reports. Free. — *optional*
- **Property:** FL county property-appraiser open GIS/parcel (roof/build year, owner-occupancy) + free Census geocoding. — *to add per county*

## Live data — SOLVED via publish→read (Option 1), 2026-07-02
The hosted Worker blocks all outbound internet except Higgsfield's `fnf.internal`
(probed: Census/ArcGIS/SPC/weather.gov/example.com all fail). So the engine can't
run *in* the Worker. **Chosen + implemented: Option 1 — the engine runs where there's
internet (VPS/local) and PUBLISHES the feed to the Worker, which reads it from D1.**

```
storm_poc.py (NOAA + verify + grade) → storm_publish.py → POST /api/ingest
   (secret-gated) → D1 feed_cache → getFeed serves LIVE (no Worker egress)
```

**Proven live end-to-end** — published 8 real storms; the feed hero shows "LIVE — FL".
- `storm_publish.py` (prototype) — shapes `last_run.json` → StormFeed → POSTs it.
- Worker: `app/src/routes/api.ingest.ts` (secret `INGEST_SECRET`), `feed_cache` D1
  table, `getFeed` reads D1 first.
- VPS automation: `runtime/systemd/yourco-storm-publish.{service,timer}` (every 20m)
  + `runtime/storm-verified-setup.md` + `runtime/storm-verified.env.example`.
- **mPING/MESH** now fold in on the VPS side (Python), published in the same feed —
  no Worker changes needed.
- **Parcel/property**: stays a browser→data-source call (the roofer's phone has
  internet); `/property` has the lookup built + a note until that path is wired.

## LIVE hosted build (Cloudflare full-stack)
**Preview URL: https://sweet-opal-720.higgsfield.app** (React 19 + TanStack
Start on one Cloudflare Worker, **D1 database live**). Three routes:
- `/` — the verified alert feed (12 storms, grade badges, AI verdict pills, peak-vs-avg).
- `/crew` — the crew field log (log each door → **persists to D1**), mobile-first.
- `/coverage` — Nick's live rollup (doors/interested/signed/revenue by crew + county), from D1.

**Now live on the app (2026-07-02):** verified feed · crew field log (D1) · coverage (D1)
· **pre-storm staging** (`/staging`, SPC outlook) · **where-to-knock canvass** (`/canvass`,
swath route + proof script) · **claim packet** (`/claim`, NOAA source-of-record + evidence)
· **one-tap dispatch** (`/dispatch`, opens Messages pre-filled — approval-safe, Twilio is a
later upgrade) · **property lookup** (`/property`, REAL FL parcel data — client-side fetch:
OpenStreetMap geocode → FL Statewide Cadastral/FDOR → roof age, owner-occupancy, lead score;
works around the Worker egress block since the browser has internet). Each storm card links to
Dispatch/Canvass/Claim. **ROI + learning** now live too (`/roi`: real revenue, close
rate, and which storm grades/types convert — computed from the field log × storms).
Only remaining spec item: CRM push (JobNimbus/AccuLynx).

Repo is separate (Higgsfield-managed git); the storm snapshot is bundled from the
engine (`storm_poc.py → build_demo.py`). Persistence confirmed live via the D1
empty-state reads. **One thing to click-test:** log a door on `/crew`, then check it
lands on `/coverage` (the write path — standard D1 INSERT through the same binding).
To ship the public URL: `deploy_website env='production'` (only when ready).

## Gaps to close for the internal test
1. ~~**Hosting (the blocker).**~~ ✅ **DONE** — live at the preview URL above with a real D1 backend. Remaining: swap the bundled storm snapshot for a live engine fetch, and click-test the door-write path.
2. **Averaging + grading** in the engine (Nick's ask) — average wind/hail across sources, show peak vs consensus, assign a severity grade. → `storm_poc.py` refinement.
3. **MRMS MESH + mPING** sources — the radar-hail + crowdsource layer (the accuracy edge). → new adapters.
4. **FL parcel data** — real addresses/roof-age for the property layer (replaces demo stand-ins). → county open-data adapters.
5. **Persistent multi-crew** — crew app backed by a real DB so a month of field data holds + feeds learning/ROI for real.

## Milestones → Jul 9–10
- **Now → Jul 4:** ~~engine averaging/grading~~ ✅ · ~~Sample Product rebrand~~ ✅ · ~~open-source data audit (`DATA-SOURCES.md`)~~ ✅ · MRMS MESH adapter (radar hail — needs GRIB2 decision) · confirm hosting path.
- **Jul 5–7:** stand up hosted instance (real URL); persistent crew backend; mPING (free token) + one FL county parcel source; wire the aggregated feed.
- **Jul 9–10:** Nick's internal-test build live on a real URL, mobile crew app, real data — hand off.
- **Parallel:** Nick sends his site list (fold any new ones in); engage attorney for the pre-public review.

### Two open decisions (see `DATA-SOURCES.md`)
1. **Hosting** — Cloudflare full-stack (Worker + D1, real DB for crew/leads) vs simple static + a small API. Recommend full-stack for the persistent month-of-field-data need.
2. **MRMS MESH / GRIB2** — add one dependency (`pygrib`) on the hosted build to decode radar hail (recommended), or defer MESH to v2 and ship the internal test on the 3 keyless NOAA sources + free mPING token.

## Open decisions / dependencies
- **Nick's list of storm-data sites** (his action) — fold in any we're missing.
- **Hosting choice** — Cloudflare (full-stack, DB) vs simple static + small API. Recommend full-stack for the persistent crew/DB need.
- **Legal** — attorney on data-reselling + patents before public (not blocking internal test).
