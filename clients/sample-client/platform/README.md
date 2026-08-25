# Sample Client — Design Studio + Field-to-Quote Platform (v1, staged)

Built 2026-08-07 from the 2026-08-06 meeting spec (`../meetings/2026-08-06_design-sales-workflow-meeting.md`).
Serve via launch.json name **`sample-client-platform`** (port 8804). Must be served over http — `fetch()` of the data files fails on `file://`.

**One platform, two audiences (decision: `decisions/2026-08-07_southern-cut-one-platform.md`):** the internal tabs are the Field-to-Quote engine; the **Design Studio ✦ tab is the client-facing presentation view** — renders, scaled plan, tier prices, ballpark range, scopes ONLY. Costs, margins, crew-days, difficulty math, and internal flags have no render path into that view; keep it that way (new features land internal-side by default). "Present full screen" is the on-site/in-office client mode. Photos + design renders upload in the Project tab (downscaled to ≤1400px JPEG for localStorage); the render *generation* pipeline attaches there in v2. The old standalone Design Studio page (:8799) is retired to sales-demo artifact status.

## The one architectural rule
**The AI never invents a dimension.** Every element dim traces to a source — Moasure / survey / manual-field-verify — and unverified dims are dashed + flagged all the way into the quote and the approval gate. This is the direct answer to Colton's takeoff test (12×16 rendered vs 14×21 actual).

## What v1 does (all client-side, localStorage persistence)
- **Project intake** — client/site, survey-on-file toggle (drives ballpark variance), consult notes.
- **Measurements** — registry with source tags; Moasure paste-import (real export parsing lands when Colton sends sample files); site-plan upload + 2-click scale calibration → scaled underlay on the board.
- **2D Board** — the product per Colton: scaled SVG grid (8px = 1ft), drag-drop elements (patio, walkway, wall, pergola, fire pit, turf, bed, steps), dims bound to the measurement registry, plan underlay.
- **Quote engine** — materials from `data/catalog.json` (SiteOne-basis pricing, in-stock-first, special-order badged), labor from `data/labor.json` benchmarks × access(1–10)/grade/hand-dig multipliers, 10% waste, sub allowances flagged as allowances, 3-tier strip, ballpark range widened when no survey, 72h validity, Aspire-format line items with cost/price/margin.
- **Scope writer** — Sample Client voice, best-practice defaults, editable/deletable per line.
- **Approval gate** — Noah's checkpoint: >$50k site walk, labor/means-and-methods, sub quotes vs allowances, special-order lead time, NC811, unverified dims. Gate stays LOCKED until all approved.
- **Catalog** — the repository Client Owner's master list lands in; prices editable in-browser (localStorage override).

## The six category-first features (built 2026-08-07, the Founder's greenlight — all verified working)
1. **Self-tuning quote engine + public accuracy scoreboard** (Actuals ⟳ tab): completed-job est-vs-actual history auto-tunes labor calibration (currently ×1.09 from 12 sample jobs) and difficulty math; the client view carries the badge — "Our last 12 ballparks landed within ±5% of final price" (honest "(sample history — staged)" tag until the real Aspire export replaces `data/actuals.json`). Log-a-job form re-tunes instantly.
2. **Moasure trace → auto-drawn board → designs inside the fence** (Measurements + 2D Board): paste a perimeter trace → property/house/features draw to scale, envelope registered as ground truth; "✦ Propose layouts" generates 3 options (Entertainer / Resort Lawn / Essentials) **geometrically constrained to the measured envelope** — setbacks, house clearance, nothing outside the fence, verified programmatically.
3. **Confidence pricing that visibly tightens** (Quote + client view): range = f(survey on file, % dims Moasure/survey-verified, track-record depth) — replaces the flat variance. Client view shows the animated certainty bar + the ●/○ "what tightens this" checklist: upload the survey, watch the range narrow live.
4. **Sub-quote autopilot** (Subs tab): sub-dependent lines auto-generate scoped RFQs (dims + scope + access; copy-button — **the Founder/Client Owner sends, approval-gated**); logged replies replace allowances in the quote and tighten each sub's learned price band (Kenny's seed band is Client Owner's own meeting number).
5. **The pitch becomes the build journal** (Project tab stage + journal): post-signature, the same Design Studio link grows a build timeline (crew photos), and at completion a maintenance calendar generated from the installed elements. Radius-postcard campaign (05_leadgen-postcards-concept) hooks on completion — internal, the Founder triggers.
6. **Watch your yard grow** (render states): renders upload tagged Day 1 / Year 1 / Year 3 / Autumn / Night; client gallery gets state tabs (unpopulated states show "soon" — never mislabeled). Generation via the Higgsfield pipeline is the v2 wiring.

Client-safe boundary held: automated leak test on the client view — no margins, crew-days, calibration, allowances, or supplier terms render there.

## v2 layer (built 2026-08-07 afternoon — the Founder's greenlight)
- **Multi-project + shared persistence:** `server.py` (stdlib, port 8804) serves the static app + a JSON API (`/api/projects` CRUD, `/api/actuals` shared history, `/api/render-queue`). Project switcher in the header; per-project state on disk under `data/projects/` (gitignored, machine-local); legacy single-project localStorage auto-migrates on first load. Frontend degrades gracefully to localStorage-only "local mode" if served without the API. launch.json entry now runs `server.py`.
- **Integrations hub (new tab):** every Client Owner system as a *file adapter today, API transport when credentials land* — Aspire (quote → line-item CSV export in Aspire import shape; actuals CSV import with column auto-match → re-tunes the engine), HubSpot (deal-sync JSON payload; note: his third party owns the Aspire→HubSpot bridge), SiteOne (price CSV import → catalog), Moasure (live via paste/trace), nursery availability (pending address), Higgsfield queue status. Status pills tell the truth per system.
- **Print / PDF export:** two documents from the same quote — client proposal (client-safe, leak-tested: badge + range + tiers + scopes) and internal estimate (full line items, margin, open allowances). Buttons on Quote tab + client view; browser print → PDF.
- **Higgsfield render pipeline (LIVE, proven):** "✦ Generate" per render state composes a geometry-faithful prompt from the project (elements, materials, state, no-invention constraint) → `/api/render-queue`. **First real generation shipped 2026-08-07:** the sample project's Night state (`assets/night1.png`) — nano_banana_pro image-to-image from the day render, same yard preserved, 2 credits. Runtime loop to drain the queue automatically = next wiring step.
- **Aspire write-back:** the export payload IS the write-back body; live API push flips on when Client Owner's API key (start item #2) arrives. Blocked on credential, not on build.
- **Self-serve render regeneration (built 2026-08-10):** "⟳ Update render" on the Project tab — for on-site iteration (add/delete/adjust on the 2D board → new render in ~90s while Client Owner talks plants). Server endpoint `/api/render/generate`: picks the base image (latest same-state render → any render → site photo, so edits chain img2img and the yard stays consistent), calls the image API directly (Google `GEMINI_API_KEY` in .env; `GEMINI_IMAGE_MODEL` override; Higgsfield Cloud slot reserved), saves the result into the project with versions kept for A/B. **No key yet → honest 503 → auto-falls back to the pipeline queue** (verified). Known prototype race: a client-side save PUT can theoretically collide with the server's render insert — acceptable until go-live hosting.

## Still blocked on Client Owner's email items
Real Aspire history (replaces sample `actuals.json`) · SiteOne export/login (replaces sample prices) · Moasure native file format (paste/trace works today) · labor benchmark list + stock rules + supplier master list · nursery report email address.

## Data files = the repositories
- `data/catalog.json` — materials, stock rules, plants, suppliers, stone regions. **Sample pricing — replace with SiteOne export.**
- `data/labor.json` — crew, production rates (only 500 sqft pavers/day is their real number so far), difficulty bands, markups, variance, validity.

White-label: Sample Client brand only, no yourco name on the surface (footer is internal-neutral).
