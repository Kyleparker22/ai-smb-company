# Sample Realty Home & Land, LLC

> **Stage:** `discovery` — mirrored from `crm/data.json`, which owns it. Do not edit this by hand; change the CRM and this follows. `runtime/consistency-check.py` fails if the two disagree.


**Boutique real estate firm — Yourtown & the Carolinas.** Broker/Owner **Sample Contact** (24+ yrs, licensed ST & SC, 100% referral-based); **Sample Contact** on the team. Seven agents, 70+ combined years (Kimi's correction, 2026-08-04). Site: `SampleRealtyteam.com` · `704-575-0714` · `KimiParkerRealtor@gmail.com`.

*(Name note: the humans **Kimi** and **Sample Contact** collide with yourco's internal agents Kimi/Kortney. In the CRM they are `kind: client` contacts under company `c30`. Don't confuse them in any automation.)*

## ⚠️ Stage: PROSPECT — not signed, not proposed
Folder created 2026-08-04 at the Founder's direction because real deliverables now exist and needed a home. **Delivery-loop Stage 0 (proposal sent / signed) has NOT fired** — no proposal, no pricing conversation, no engagement agreement. The scaffolded template docs (`01_discovery` / `02_build` / `03_eval` / `go-live` / `demo-kit`) are **unfilled scaffolding**, not an active build. Treat every `[[PLACEHOLDER]]` as open.

**Relationship:** warm network / family (the Founder). This is the real-estate-vertical proof case — work delivered to earn the conversation, not billed work.

## What's actually been delivered
- **`deliverables/Coleman-Listing-Presentation-A-Signature-Red.pdf`** — 7pp print listing presentation for sellers Gwynne & Scott Coleman (2304 Highland Forest Dr, Yourtown ST 28173). Sample Realty brand (site-sampled `#EF0004` / black / cream), Didot + Hoefler editorial system. **Option A = the dark/cream edition.**
- **`deliverables/Coleman-Listing-Presentation-D-White.pdf`** — identical 7pp content, **white-page palette**. Kimi picks A or D.
- Both are print-tuned: full-bleed letter, dark-page text at 100% white (not the original 62% cream — it muddied on toner), all small type raised ~1.5–2pt over the first draft, cover block centered and lowered.
- **`deliverables/Parker-Realty-Trust-Account-Review-2026.xlsx`** + **`deliverables/Trust-Account-Review-Findings.pdf`** — the PM "your year, reconciled" packet (2026-08-04): her trust-account journal regenerated into clean journal + per-property ledgers + NCREC trial balance + 5 owner statements, all live formulas; 2-page findings memo (10 findings incl. the −$1,830.51 Bexton cross-funding). Builder: `pm-module/build_packet.py`.

## Everything lives HERE now (consolidated 2026-08-05, the Founder: "organized by client")
The former `clients/_prospect-demos/sample-realty/` working source was merged into this folder — one client, one folder. Map:
- `site/` — the full website: all pages + tools + concierge + `listings-data.js` (single source for listings) + `assets/listings/` photos. Serve via `sample-realty-tour` (:8801) → `/site/`.
- `tour.html` + `assets/` — the cinematic AI tour demo (concept imagery, labeled).
- `listing-presentation/` — Coleman presentation sources + `build-variants.py` (4 palettes × 2 formats).
- `pm-module/` — the PM platform: `build_packet.py` (books engine), `source/` (her workbooks), `out/` (generated packet), `PLATFORM-SPEC.md`, `console/` (the Kimi cockpit demo → :8801/pm-module/console/).
- `narration-recording-kit.md` — Kimi's voiceover how-to for the narrated tours.
- `BUILD-NOTES.md` — the full build log & conventions from the demo sessions (honesty posture, buyer-side photo rule, data sources).
- `deliverables/` — finished, hand-over-able files only. **Rule:** edit source in the sibling folders, regenerate, copy the chosen output here. Never hand-edit a deliverable.

## How the OS works this client (agents across the whole process)
Per the Founder 2026-08-05: the agents help end-to-end on this engagement. Ownership map (internal names — never on client-facing surfaces):
- **David / CRM** — company `c30`, contacts, deal + activity log stay current; every session that ships something logs an activity row.
- **Bella** — runs the audit the moment Kimi says yes; the PM findings packet is her opening exhibit.
- **Polo** — prices it as an OS (PM module first), per the locked tier envelope. No prices on any client surface.
- **Sample Contact / Janice** — delivery scaffolding at Stage 0; the golden-template docs in this folder are theirs to fill.
- **Kolby** — eval pass on every demo surface that ships (site, console, packet numbers tie-outs).
- **Rafi** — compliance gates: MLS/ad rules on tours ("AI-enhanced" disclosure), NCREC trust-account posture, tenant-comms rules.
- **Ray** — counsel gate before the PM module touches live data (`processes/counsel-gates.md`).
- **Charles** — `cost.md` roll-up at weekly pulse + monthly close (ledger already has rows).
- **Atlas + runtime loops** — activation-gated at go-live per `runtime/activation-triggers.md`: rent watchdog (daily), books + reconciliation (monthly), owner statements (monthly), production error sweep.

## Open items
- **Facts to verify before any reprint:** the 3.9 / 2.3 months-of-supply stats are Kimi's own numbers, unverified — she should refresh against MLS at print time, and confirm Marvin vs Yourtown as the quoted sub-market.
- **Cover photo:** the cover has a built-but-hidden photo plate. Drop a rights-clean `cover-house.jpg` into `clients/sample-realty/deliverables/listing-presentation/` and the build flips it on automatically. Google Street View / Zillow images are **not** usable (ToS + photographer copyright) — declined three times; needs a photo Kimi or the Colemans own.
- **Cinematic tour clips:** chapters currently play a scripted animatic. Real Kling/Higgsfield clips drop in as `assets/*.mp4` with zero code change — blocked on the Higgsfield subscription (`grace_daily_limit_reached`).
- **Privacy flag for Kimi:** her **home address** is published on the live GoDaddy site's "Call or Visit" block. Removed from everything we produced; worth telling her.

## If this converts
Run the delivery loop properly: Bella's audit → proposal (Polo's locked OS-tier pricing) → Stage 0 → fill the scaffolded docs. The natural first module is **listing-launch automation** (Marketing pillar): new listing → tour + presentation + social cuts + syndication same day, with speed-to-lead intake behind it.


## Video: who does what
`video-editing-workflow.md` — **yourco runs the footage editing; Kimi does not touch Descript** (decided 2026-08-20). The split: photos → cinematic tour is hers in the Listing Kit Builder, which now exports MP4 directly; filmed footage → Descript, run by yourco off a shared Drive folder. Descript access is verified working end to end on the 2304 walkthrough.

## ⚠️ PII: the PM console is not shareable
`pm-module/console/index.html` carries **real tenant names, addresses, rent amounts, payment histories and security deposits**, plus owner names and balances. Fine to show Kimi on a laptop — it's her own data. **Never** publish it as an artifact, put it on a shared URL, or email it. Serve it locally (`sample-realty-tour`, :8801) and nowhere else. Same applies to the findings PDF and workbook, which name properties and owners.

**Three views, pick by audience:** `platform.html` = the OS with nothing loaded (what the product *is*) · `sample.html` = the same console on an invented portfolio (what it *looks like* full) · `index.html` = her real books (PII, laptop only).

**Use `pm-module/console/sample.html` or `platform.html` for anything that leaves the room** — same console, same layout, every name/address/figure invented. Verified zero real names, addresses or amounts. That's the version to share, screenshot, or put in a deck.
