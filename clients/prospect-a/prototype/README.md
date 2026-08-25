# Storm-alert POC — Prospect A (Roofing, Florida)

A **give-first proof** of the system Nick wants: pull storm data from multiple
sources, have the AI **cross-verify accuracy**, and turn a confirmed storm into a
one-tap **approve → text-the-roofers** alert — replacing the manual daily
research + manual texting eating his time.

## Nick's spec (locked from discovery 2026-06-30)
- **Coverage:** Florida only.
- **Hazards:** hail + wind (+ tornado, e.g. the Fort Myers EF-0 worth traveling for).
- **Thresholds:** hail **> 0.75"**, wind **≥ 55 mph**. (Set as defaults.)
- **His sources (cross-references all):** **NOAA** (the insurance source of record for airport wind/hail), **HailTrace**, **Interactive Hail Maps**, a **predictive sales-AI weather tool**, and **Xweather** (`data.portal.xweather.com` — he has an API key; NOAA-verified live alerts).
- **Action:** door-knock the area after a large hail/wind event. **Speed is everything — first crew to the neighborhood gets paid.**
- **Delivery:** individual text + group text (depends on the company).
- **The whole ask:** cross-reference all these sites *every day*, spit out verified storm data by location — instead of his manual hour. **Live alerts are the key.**
- **Validation:** the engine reproduced most of a real week Nick cross-referenced by hand → `validation.md`.

## Show Nick this → `demo.html`
A branded, "see-yours" visual walkthrough built on **his real Florida data**:
the sources strip (live vs. ready-to-connect), the how-it-works flow, the
verified-storms grid (with the raw→verified→relevant funnel), a **Florida map**
of where they hit by county, and phone mockups of Nick's **approval screen**
(with a working **action selector** — door-knock all crews / area / monitor that
swaps the message) + what his **crew receives**. Open it directly (`demo.html`) or serve it (`nick-storm-demo` in
`.claude/launch.json`, port 8796). Refresh its data anytime:

    python3 storm_poc.py && python3 build_demo.py     # re-pulls NOAA → demo_data.js

`demo_data.js` is a committed real-data snapshot so the page opens standalone.

## What this proves (and what's real)
`storm_poc.py` runs **today, on live Florida data, at zero cost** off a **source
registry** (edit `SOURCES` to add/swap when Nick names the sites he trusts), and
scores confidence by cross-source agreement:

**Live now (free — NOAA is the insurance source of record):**
- **NOAA Local Storm Reports** *(primary)* — structured ground reports: hail size, wind, tornado, with county + lat/lon (drives the storm list + map).
- **NOAA SPC (national)** — compiled storm reports, used to corroborate.
- **NWS Live Alerts (`api.weather.gov`)** — official forecaster/radar warnings — the speed layer.

**Ready to connect (Nick's premium stack — add creds, flip `enabled=True`):**
- **Xweather** — Nick's NOAA-verified live-alerts API. Adapter built; add his `client_id`/`client_secret` to `.env` and it goes live (see below).
- **HailTrace** · **Interactive Hail Maps** — the hail-specific sources that catch the 1"+ hail NOAA ground reports miss (see `validation.md`).
- **Predictive weather guidance** — clarify which tool, then integrate.

- **Confidence:** `HIGH` when ≥2 signals agree (or a report + an official NWS warning); else `MEDIUM`. This agreement layer is **the yourco moat**.
- **Roofing filter (Nick's thresholds):** surfaces hail **> 0.75"**, wind **≥ 55 mph**, or tornado. Bare "wind damage" LSRs (a limb down) stay a flag but never alert. Marine/offshore zones dropped.
- **Configurable triggers (door-knock workflow):** each verified storm gets a recommended action — **Door-knock (all crews / area) · Monitor (reports pending)** — by hazard, magnitude, confidence (tornado / hail ≥1.25" / wind ≥70 → all crews). Nick overrides in one tap. Edit `TRIGGERS` to change copy.

### Integrating Nick's Xweather key
From `data.portal.xweather.com/account/developer` it's a **`client_id` + `client_secret` pair** (not one key). Put both in `.env` (`XWEATHER_CLIENT_ID`, `XWEATHER_CLIENT_SECRET`) and `storm_poc.py` turns Xweather on as a live source automatically — its reports flow into the same cross-verification. The adapter's field mapping is best-effort against Xweather's storm-reports endpoint; we confirm it against the first live response and tweak if their JSON nests differently on his plan. (the Founder adds the creds on the runtime — Nick never pastes secrets into chat.)

Run it: `python3 storm_poc.py`  ·  window/area: `DAYS=14 STATE=FL python3 storm_poc.py`
Output: a ranked digest with the recommended action + source attribution per storm, and `last_run.json` for the demo/pipeline.

**Real result (last run, FL, 14-day window):** 208 raw reports → 109 verified areas
→ 8 roofing-relevant, incl. a Duval County 60mph wind event (IEM + SPC) and a
Lee County tornado — auto-flagged "all crews."

## What production adds (the "best data possible" Nick asked for)
- **Nick's premium sources wired** (Xweather + HailTrace + Interactive Hail Maps) — just need creds. These carry the hail coverage NOAA's free ground reports miss (`validation.md`); the commercial leg carries a **data-licensing cost + redistribution terms**.
- **Dispatch:** approve → **SMS broadcast via Twilio** to his crew, grouped by individual / area / team. Approve-then-send is the autonomy-matrix approval gate (starts human-gated, earns toward auto-alert on proven accuracy).
- **Runs on the always-on runtime** (scheduled, like our other loops) — no laptop, no manual checking.

## Real dispatch (Twilio) — from demo to usable → `dispatch.py`
The last mile: approved storm + chosen action + target group → **texts Nick's roofers**.

- **Targeting:** `--to all | area:<X> | team:<X> | person:<name>` — matches Nick's own groupings in `roster.json`. (A Duval storm → `area:Jacksonville` → just those crews.)
- **Action:** defaults to the storm's recommended trigger; override with `--action canvass_all|canvass|dispatch|standby`.
- **Safety (the approval gate, in code):** DRY-RUN unless **all three** hold — creds present, `DISPATCH_DRY_RUN=0`, and `--send` passed. Dry-run prints the exact message + recipient list and sends nothing. No SDK dependency (raw Twilio HTTP).

```
cp .env.example .env            # Twilio creds (gitignored)
cp roster.example.json roster.json   # real roofers + numbers (gitignored)
python3 storm_poc.py            # produce last_run.json
python3 dispatch.py --to area:Jacksonville           # dry-run preview
python3 dispatch.py --to area:Jacksonville --send    # live (creds + DRY_RUN=0)
```

**Before it can send for real — the gating operational steps:**
1. **A Twilio account** + a Messaging Service (Account SID / Auth Token / MG sid).
2. **A2P 10DLC registration** (brand + campaign) — required for US business SMS or carriers filter it; takes a few days. Twilio auto-handles STOP/HELP opt-out.
3. **Nick's roster** — his roofers' numbers + how he groups them (area/team). We don't have this yet (his #4).

Runs as-is today in dry-run; flip to live the moment 1–3 are in place. Then it schedules on the always-on runtime behind Nick's one-tap approval.

## The daily loop → `run_daily.sh`
One command chains the whole thing: **pull every source → AI reads the reports → refresh Nick's visual → queue only the GO storms for approval.** Dispatch stays gated — the loop never texts anyone; it just makes sure only *real, verified* storms ever reach Nick's phone.

```
./run_daily.sh          # storm_poc.py → verify_ai.py → build_demo.py → approval queue
```

On the yourco always-on runtime this becomes a scheduled loop (systemd timer or cron) that fires each morning — and a **faster cadence in storm season**, because speed is the whole game. Every storm is AI-read *before* it can be dispatched, so Nick never wakes up to a false alert. The junk (e.g. the Palm Beach "pea-sized" hail) is filtered upstream; the GO list is what he taps to broadcast.

```cron
# storm season: check hourly during daylight; off-season: once each morning
0 12-23 * * *  cd /path/to/prototype && ANTHROPIC_API_KEY=… ./run_daily.sh >> loop.log 2>&1
```

## The full storm OS (modules)
Each is a runnable module — free data / deterministic logic where possible, adapter seams for paid feeds:

- **`watch.py`** — real-time watcher. Polls the sources on a short interval and fires the **instant** a new HIGH storm verifies (deduped). Speed = first crew to the door. `python3 watch.py --once`, or continuous via `WATCH_INTERVAL`.
- **`staging.py`** — pre-storm staging. NOAA SPC day-1/day-2 outlooks → which FL metros to position crews in *tonight* so they canvass as tomorrow's storm clears. Free NOAA.
- **`canvass.py`** — swath → optimized (nearest-neighbor) route → door-knock script with the NOAA proof baked in; surfaces the highest-ROI doors via `property.py`. `python3 canvass.py Duval`
- **`property.py`** — property overlay: score doors by roof age × home value × owner-occupied so crews knock the money doors first. Ready to connect a parcel feed (`PROPERTY_API_KEY`); deterministic demo scoring otherwise.
- **`claim.py`** — claim-assist packet. Auto-fills the storm-verification section of an insurance claim from the retained evidence (named ASOS/AWOS **measured** stations + NOAA source of record). `python3 claim.py Duval --address "123 Main St"`
- **`learning.py`** — the moat. Learns from field outcomes (`outcomes.json`) which storm profiles convert ($/door, close rate) and writes feed-forward priorities. In the seed data, **tornado + 1.25″ hail pay ~4× weak wind** — so crews chase what converts, not just what's biggest.
- **`roi.py` + `roi.html`** — ROI dashboard: revenue sourced, cost per job sourced (vs bought leads), wasted trips avoided. Served at `nick-storm-demo:8796/roi.html`.

## The crew-app — field capture + coverage (closes the loop)
The field half: what roofers use on the ground, and what makes `learning.py` / `roi.html` run on **real** results instead of seed data.

- **`crew.html`** — a mobile web app (roofers open a link, no install). **Roofer mode:** pick the active storm, tap "On it/Done", and log each door — Knocked / Not-home / Interested / Booked / Signed ($). **Coverage mode (Nick):** live tiles (doors / interested / signed $), a coverage dot-map, per-crew ack status (who's on it / done), and an activity feed — so no two crews hit the same street and nothing's missed. Works standalone via `localStorage`; uses the backend when it's running.
- **`crew_server.py`** — shared backend so every crew sees one live picture: `GET /api/state`, `POST /api/door`, `POST /api/ack`, persisted to `crew_state.json`. `python3 crew_server.py` → `localhost:8798` (or the `nick-crew-app` launch config).
- **`rollup.py`** — the wire: turns field logs into storm-level outcomes (`crew_state.json` → `outcomes_live.json`) so every **Signed** tap becomes a job + revenue attributed to its storm — feeding `learning.py` (what converts) and `roi.html` (what it made you). *Verified end-to-end: a signed door → $ in the ROI + a data point in the learning loop.*

**Why it's the keystone:** dispatch → **field outcomes (crew-app)** → learning → smarter dispatch → provable ROI. Without it the front half is sharp but blind to results; with it, storm-command gets more profitable every storm.

## Claim-date lookup — address → best storm date (added for Nick)
Type a property address, get the strongest verified storm over it in the last 12
months + the days left to file (you get ~1 year). For chasing claims after the fact.
- **`history.py`** — builds a 12-month NOAA storm-history cache for FL (chunked monthly → `storm_history.json`, ~1,360 reports, gitignored). Production swaps in Xweather historical.
- **`address.py`** — geocodes the address (free US Census geocoder), searches the cache within 15 mi, ranks by severity, returns the best date + claim-window countdown + evidence. `python3 address.py "400 Magnolia Ave, Panama City, FL"`
- **`address.html`** — the search UI (claim-date + "days left to file" in red when urgent). Live search via `crew_server.py`'s `/api/address`; seeded `address_data.js` for the static demo. Control-tower card "Claim-date lookup."

## Xweather webhook — push, not poll (added for Nick)
Real-time: Xweather POSTs storm reports + alerts the instant they're issued.
- **`xweather_webhook.py`** — the receiver: returns **202** immediately (Xweather's requirement), verifies a shared secret (`X-API-KEY`), filters to Nick's spec (**hail ≥ 0.75", wind ≥ 55 mph, tornado, all alerts**), queues approval-gated. Verified: 401 without secret; 0.9" hail + 62mph kept, 40mph dropped.
- **`XWEATHER_WEBHOOK.md`** — exactly what to hand Xweather (datasets: Alerts + Storm reports + Storm cells/Hail threats; FL coverage; the filters), plus go-live steps. Webhooks are a premium add-on registered by Xweather (not self-serve), so this is account setup + a public HTTPS URL — the polling `watch.py` covers real-time on free NOAA until then.

## Honest market note
Hail-mapping incumbents exist (HailTrace, Interactive Hail Maps, HailRecon,
CoreLogic) — but they're *data products you go look at*. None do the
**verified-alert → one-tap crew dispatch** workflow. That workflow + the
verification wrapper is the wedge, and it's productizable as an **operated
subscription** (same shape as Conduit / yourco Care — yourco builds & runs it,
the roofer gets an outcome, moat holds). Path: build for Nick as design partner,
prove accuracy, then productize.

## Open (from discovery)
- Which sites Nick uses now + trusts vs. distrusts (tunes the agreement set) — Nick to answer.
- What the alert triggers operationally (canvass an area? door-knock?) — Nick to answer.
- Roofer count + how groups map (individual / area / team).
- Commercial data budget + licensing terms.
- Dispatch/approval channel: SMS vs. a lighter rich-content channel for Nick's own review.

*Prototype only — not deployed. No texts send from this. Homed here like Sample Client's prototype (real materials to home).*
