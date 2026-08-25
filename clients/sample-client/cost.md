# Cost — Sample Client (the Client Owner)

> YourCo absorbs all token/model/infra spend; the client never sees it. Track it anyway so Charles can roll up margin (revenue collected − run cost) and Polo can sanity-check the retainer covers it. Log entries via the `log-build-cost` skill — at the end of any session that did real work for this client, and at Charles's monthly close.

**Pricing in effect:** build fee $0 (brotherhood kickoff) · monthly retainer $1,000 (proposed — **not signed**) · use case: **Design Studio / Field-to-Quote platform** (Installation Proposal Automation = earlier proposal, parked 2026-08-10)

## Ledger (append-only — one row per spend event)
Phases: **discovery** (audit/scoping/proposal) · **build** (implementation through go-live) · **tools** (third-party) · **run** (post-live).
Evidence: `metered` (console/invoice) or `est.` (session self-report).

| Date | Phase | What | Tokens | $ | Evidence |
|------|-------|------|--------|---|----------|
| 2026-07-06 | discovery | **Pre-ledger backfill** — proposal, dry-run prototype, mockup walkthrough set, demo kit config (multiple Cowork sessions, June 2026). Tokens not captured at the time; ledger starts today. | unknown | unknown | est. — pre-ledger, do not invent |
| 2026-07-05 | discovery | Client Owner follow-up video (59s, Higgsfield Soul stills + Kling clips + Maya VO) — credits drawn from yourco's shared Higgsfield Plus plan | — | ~shared-plan credits, not billed per-client | est. |
| 2026-08-07 | discovery | 8/6 in-person meeting digest + follow-up/data-request email draft + **Field-to-Quote platform v1** (measurement ground-truth registry, plan-calibration underlay, 2D board, quote engine w/ difficulty+tiers, SC-voice scope writer, Noah approval gate, catalog+labor JSON repositories) — one heavy Cowork session, built to close; still pre-signature CAC | ~1 heavy session | ~$15–25 | est. — session self-report |
| 2026-08-07 | discovery | Same session, continued: Design Studio merged into the platform (client-safe view) + the **six category-first features** (self-tuning engine + accuracy scoreboard, Moasure-trace auto-board + constrained layout generator, live confidence pricing, sub-quote autopilot, build journal, yard-grow render states) + subs/actuals data repositories; all functionally verified incl. client-view leak test | ~same heavy session (cont.) | ~$15–25 addl | est. — session self-report |
| 2026-08-07 | discovery | v2 layer: multi-project server + shared persistence (server.py + JSON API), Integrations hub (Aspire/HubSpot/SiteOne file adapters, API-ready), print/PDF client+internal exports, Higgsfield render pipeline live (night-state render generated: nano_banana_pro img2img) | ~same heavy session (cont.) | ~$10–20 addl | est. — session self-report |
| 2026-08-07 | tools | Higgsfield credits — first pipeline render (night state, sample project), from yourco's shared Plus plan | — | 2 credits | metered — MCP cost preflight |
| 2026-08-10 | tools | Higgsfield credits — first from-scratch design render (site photo → designed yard, sample project) | — | ~2 credits | metered — same model/params as preflighted night render |
| 2026-08-10 | tools | Higgsfield credits — first render on a REAL user-entered project (the Founder's front-yard test: porch + fountain + plantings from his photo) | — | ~2 credits | metered — same model/params |
| 2026-08-18 | tools | Google Gemini prepaid credits (render infrastructure for the platform's self-serve ⟳ button; dedicated 'YourCo Sample Client' GCP project — per-engagement metered) + first successful self-serve render (gemini-3.1-flash-image, ~pennies) | — | prepay top-up (the Founder; amount in Google console) | metered — Google billing console |
| 2026-08-18 | discovery | Demo video produced (2:23, 10 scenes, narrated): headless captures of the live platform + ElevenLabs VO via Higgsfield (10 clips) + ffmpeg assembly — `platform/demo/sample-client-design-studio-demo.mp4`, for the Founder + the Client Owner walkthrough | — | ~10 TTS credits (shared Higgsfield plan) | metered — Higgsfield |
| 2026-08-19 | discovery | Visit Mode batch: guided on-site tab (auto-design + auto-fired render set + completeness chips + voice-dictation hints), phase-grouped navigation (Pre-Meeting/On-Site/Back at the Shop), client add-on configurator w/ live +$ deltas, crew-availability/duration/lead-time cards fed by a new live Aspire install-calendar pull (1,224 scheduled tickets), "drop in your vision" inspiration references wired into the render pipeline as a style image | ~1 session (cont.) | ~$10–15 addl | est. — session self-report |
| 2026-08-19 | tools | First cinematic tour test — Veo 3.1 fast (8s, 720p) on Sample Client's Gemini prepay key, from the Hendersons day-1 render | — | ~$1 (Google prepay, metered in console) | metered — Google billing console |
| 2026-08-19 | tools | Render/tour spend during the feedback rounds — the Founder's Visit-Mode test sets (2 full sets + 2 angle re-fires ≈ 14 images), the Options-system verification set (4 images incl. the new screened porch), and ~5 cinematic tours; plus the consistency-fix re-fire of the Founder-Test (12 images — options now chain off one anchor render) | — | ~$3–5 (Google prepay, metered in console) | metered — Google billing console |
| 2026-08-21 | tools | Render spend fixing the option-consistency bugs on the Founder-Test: The Dream re-fires (2 × 3 images — court geometry), the full photo-first 4-option re-fire (12 images) + Option-1 auto-tour | — | ~$2 (Google prepay, metered in console) | metered — Google billing console |
| 2026-08-21 | discovery | Demo video v3 produced (~2:37, 10 scenes, live-driven puppeteer capture of the four-option platform, Grady VO via Higgsfield) — `platform/demo/sample-client-design-studio-demo-v3.mp4`, for Client Owner | — | ~10 TTS credits (shared Higgsfield plan) + 2 real option sets fired on camera (~$1 Gemini prepay) | metered — Higgsfield + Google console |

### Phase totals (Charles updates at monthly close)
| Phase | Tokens | $ | As of |
|-------|--------|---|-------|
| discovery | unknown (pre-ledger) + tracked from 2026-07-06 | | 2026-07-06 |
| build | — (not signed; build not started) | | |
| tools (one-time) | — | | |
| run (cumulative) | — | | |

## Monthly run cost
| Month | Model/tokens | Voice (ElevenLabs) | Telephony (Twilio) | Other tools | Total | Retainer | Margin |
|-------|--------------|--------------------|--------------------|-------------|-------|----------|--------|
| — (pre-live) | | | | | | | |

## Notes
- **Deal is at Proposal, not signed** — everything so far is discovery/CAC spend, useful to Polo as evidence of what winning an engagement costs even if it never converts.
- Planned stack is text-only (Aspire-signed → deposit/supplier/schedule drafts, approval-gated) — no Vapi/voice line expected; run cost should be model tokens + ~$0 marginal infra (shared VPS).
- At go-live: provision a **per-engagement Anthropic API key** so run tokens are `metered` from the console, not estimated.
