# Production ledger — Sample Client platform demo video (live-driven v2)

**Asset:** `clients/sample-client/platform/demo/sample-client-design-studio-demo.mp4` — 2:25, 1600×1000, h264+aac, ~11 MB
**For:** the Founder + the Client Owner walkthrough (client-facing OK — white-label Sample Client, "built & run with yourco" end card)
**Produced:** 2026-08-18/19, directly in the Founder's Cowork session (no separate Reed run — logged here because video production is Reed's lane per the engagement agent map)

## What it is
A TRUE live screen recording — not a slideshow: a puppeteer-driven test run of the real platform (visible cursor, human-speed typing, real clicks/drag/file-uploads, Chrome screencast) acting out a full new project ("The Hendersons"): intake → site photos/Moasure/trace/grade → auto-drawn board → propose-layouts → patio drag → quote package flip → render uploads landing live in the client gallery → Night state flip → approvals gate to green → end card. ElevenLabs VO (Grady preset, via Higgsfield text2speech_v2) mixed at scene timestamps.

## Credibility gate
Holds: every frame is the actual product responding live; the renders shown were generated from the project's own site photo earlier in the engagement; no fabricated metrics (the accuracy badge visible in stills work runs on real Aspire history; the Hendersons project shows only what was entered on camera).

## Pipeline (repeatable)
`demo/drive.js` (committed) — deterministic re-takes: `node drive.js` → raw.webm + scenes.json → ffmpeg VO mix at scene offsets. VO clips + durations in session scratchpad; regenerate per-clip via text2speech_v2. Title/end cards: `demo/title.html`, `demo/end.html`.

## the Founder's verdict + open improvements (v3 backlog)
**B+, "90% there"** (2026-08-19). Known gaps to close:
- Filming found+fixed a product bug (render uploads now refresh client gallery live)
- Candidate v3 upgrades: slower/more deliberate cursor pacing on money moments · Subs tab scene · a real ⟳ regeneration on camera · light music bed under VO · human screen-recording polish (fade-ins between tabs)
- visual-brand-qa pass before it goes client-facing (was manually frame-checked only)
