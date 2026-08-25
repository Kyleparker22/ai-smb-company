# Sample Realty — prospect demo / working source

> **This is the WORKING SOURCE.** Edit here, run `listing-presentation/build-variants.py`, then copy the
> chosen PDFs to `clients/sample-realty/deliverables/`. Never hand-edit a delivered PDF.
>
> **Client folder:** `clients/sample-realty/` was created 2026-08-04 (the Founder's call) to hold finished
> deliverables. Stage 0 (now: first-call-or-proposal-sent, rule updated 2026-08-07; at time of writing proposal-sent-or-signed) still has **NOT** fired — the scaffolded docs there are
> unfilled. Two locations on purpose: source here, deliverables there. Keep the split.

**Who:** Kortney + Sample Contact, Sample Realty (Yourtown) — the Founder's warm network. Real-estate vertical.
*(Name note: the humans collide with internal agents Kimi/Kortney — CRM keeps them separate as client-kind contacts.)*

**The pitch demo:** cinematic AI listing tour, anchored on 3524 Donovan Place, Yourtown 28215
(4bd / 2.5ba / 2,002 sqft / built 1967, Shannon Park — **now a LIVE rental listing of Kimi's**, MLS #4395709,
$2,600/mo, confirmed 2026-08-04; the tour imagery is still AI concept art, labeled).
Serve via `sample-realty-tour` (:8801) → `tour.html`.

**Real listings on the site (added 2026-08-04):** Kimi's actual book, pulled from her Canopy MLS
OneHome portal links (supplied by the Founder) — 5 active (1208 High Brook Dr Yourtown · 12727 Bullock Greenway
Blvd · 9725 Mattforest Cir · 1210 Sheldon Brook Ln Fort Mill SC · 11264 Hyde Pointe Ct), 1 lease
(Donovan), 2 sold (401 Wingfoot Dr $1.445M over asking · 7518 Meadowgate Ln $1.2M). Data + hero photos
(2048px, `site/assets/listings/`) are from Canopy MLS — Kimi is the listing agent, so the brokerage
holds the photo license; the page ribbon + footer say "listing data & photos via Canopy MLS, Aug 2026".
Note: the OneHome portal links are tokenized to the Founder's email and expire — never publish them on a page;
refresh listing data through Kimi's own portal/MLS access at engagement time.

**Site architecture (2026-08-04, Kimi's feedback round):** `site/listings-data.js` is the **single
source of truth** for every listing — one object per listing; the homepage band, the listings page,
and the per-listing detail page (`listings/listing.html?id=<slug>`) all render from it. **Add a
listing = drop photos in `site/assets/listings/<slug>/photo-0..N.jpg` + add one object** — that's the
"one-or-two-click" flow Kimi was promised (production version = the yourco listing-launch module
pulling from her MLS access). Donovan keeps its bespoke page (cinematic tour) + a real-photo gallery
(her rental photos are 296px — that's the max the MLS has). Also shipped this round: homepage
listings-first reorder (Kimi), 60+→70+ years, "small boutique"→"boutique" (swept incl. the Coleman
presentation source; **all 8 PDFs rebuilt**), detailed `services.html`, and `tools/mortgage.html` —
a **lead-gen mortgage calculator** (live payment top-line; full breakdown unlocks on contact capture;
demo stores to localStorage, production posts to CRM/intake).

**Buyer-side photo rule (Kimi, 2026-08-04):** for closed sales where Kimi represented the **buyer**,
the MLS photos belong to the listing side — **never use them.** Those render as photo-free cards
(`PR_BUYER_SOLDS` in `listings-data.js`, address + "Sold · Represented the Buyer" + closed price)
until Kimi sends her own shots. 2275 Whitebark Dr #148 (pending, $1,003,225 Toll Brothers new build,
buyer side) uses **her own construction-walk photos** (extracted from her texts). Every active-listing
detail page now carries a **cinematic tour** — a Ken Burns camera-movement-only player over the
listing's real photos (the honest, instantly-shippable version of the Donovan concept tour).

**Lead-gen build-out (2026-08-04 evening, the Founder's idea round):** the site is now a lead machine, all
demo-captured to localStorage with "at engagement → CRM/intake" comments at every capture point:
`tools/home-worth.html` (anti-Zestimate CMA magnet — THE seller hook), `results.html` (3 case studies
w/ real numbers + PR_STATS band: 19 closed / $6.9M+ / 4-day contract / +0.4% over ask, sourced),
`tools/carolina-compare.html` (NC-vs-SC border math — her unique both-states license), `neighborhoods.html`
(3 guides grounded in her actual deals), `tools/new-construction.html` (Whitebark photos as spine),
`tools/investor.html` (cap-rate/cash-flow analyzer prefilled w/ her listings → PM division loop), homepage
bands (market pulse strip fed by PR_MARKET — wire to a monthly runtime loop at launch; valuation band;
private-list capture; staging before/after slider with placeholder panes awaiting Kimi's ASP portfolio),
and **`concierge.js`** — the site-wide 24/7 assistant (FAB bottom-right): demo intent engine answers
listing/budget questions FROM listings-data.js, books showings via a 3-step capture, always framed
"drafted for Kimi's approval." At engagement the reply engine swaps to the operated Claude service —
this widget IS the digital-employee on-ramp demo.

**PM platform (2026-08-04, the Founder: 'set up a Property Management Platform — they have nothing'):**
spec at `pm-module/PLATFORM-SPEC.md` (buy-vs-build call: build the operated OS thin — books ✅,
rent roll, watchdog, maintenance flow, owner service, compliance calendar, Kimi console; buy only
screening + tenant payments if ever needed). v0 console demo at `pm-module/console/` (serve via
:8801 → /pm-module/console/) — white-label, seeded entirely from the real journal: rent board
(6 paying tenants, $14,215/mo), owners+held balances, real maintenance log, watchdog flags,
compliance calendar. Sit-down asks listed in the spec (lease dates, Capps/1138-Doveridge status,
which bank). Books engine + owner statements already shipped in `pm-module/out/`.

**Honesty posture (load-bearing):**
- All imagery = **AI concept art, labeled as such** on the page (ribbon + footer). We do NOT have their
  listing photos yet; the sit-down line is "with your real photos, this exact pipeline makes the real thing."
- **No Zillow scraping, ever** (ToS + photo copyright — photos are typically photographer/MLS-licensed).
  Production source = the listing's own licensed photography.
- Production rules shown on the page: camera-movement-only (never alter finishes/fixtures/views),
  eval vs source photos before publish, "AI-enhanced virtual tour" disclosure per MLS/state ad rules. Rafi gates.

**Asset pipeline (Higgsfield, locked stack):**
- `assets/exterior.jpg` — generated 2026-07-20 (nano_banana_pro), cropped to remove a hallucinated
  fake-brokerage watermark (**add "no text, no watermarks, no logos" to every regen prompt**).
- Remaining: 4 stills (living/kitchen/primary/backyard — prompts in the tour chapter labels + git history)
  + 3–5 Kling 3.0 camera-move clips + Descript assembly. **Blocked 2026-07-20: Higgsfield daily
  "grace period" limit — the Founder to check the Plus subscription state, then regenerate.**

**Pitch frame (offering hierarchy):** audit → real-estate OS; the tour is the wow opener for the
Marketing pillar (listing-launch automation). The page's "How every listing gets this" strip +
lead-capture form carry the actual yourco story: speed-to-lead, booked showings, operated pipeline.
