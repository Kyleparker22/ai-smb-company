# Production ledger — Sample Client platform demo video v3 (live-driven, four-option studio)

**Asset:** `clients/sample-client/platform/demo/sample-client-design-studio-demo-v3.mp4` — ~2:37, 1600×1000, h264+aac
**For:** the Client Owner — "see exactly how the platform works, in real time." the Founder sends (house rule: agents draft, the Founder sends).
**Produced:** 2026-08-21 in the Founder's Cowork session (Reed's lane — video production; logged here). Supersedes v2 (2026-08-19, B+).

## What it is
A TRUE live screen recording — the real platform driven by puppeteer with a visible cursor, human-speed typing, real clicks, real uploads, real project creation, and a real render-set firing — narrated by the Grady ElevenLabs voice (Higgsfield text2speech_v2, 10 clips). Ten scenes: title → Visit Mode (reps, the four want-levels typed live) → site capture (photo, tape dims, grade, access + why) → Auto-design fires four options → Design Studio on a finished project (four named, described, priced option cards + the cinematic fly-through; "Go with this one") → Build it together (live toggle, budget-fit line) → studio step sign-off → 2D board locked to the chosen option → Subs RFQs → quote → approvals + proposal gate → Present mode → end card.

## Credibility gate
Holds. Every frame is the product responding live. The four options shown are the real renders on the the Founder-Test project (generated earlier from its real site photo); the new "The Millers" project created on camera fired a real 12-image set during the take. No fabricated metrics: the accuracy badge on screen (±5%, 21 jobs) is computed from real Aspire history. The VO's "a few minutes later" honestly covers the ~9-minute render wait via a cut to the finished project.

## Pipeline (repeatable)
`demo/drive3.js` (committed) + `scenes-v3.json` + `vo-durations-v3.json`. Re-take: `node drive3.js` → `raw.webm` + scene timestamps → `mux.py` (ffmpeg adelay/amix at scene offsets) → mp4. VO clips regenerate via text2speech_v2 (variant elevenlabs, voice Grady preset). Title/end cards: `demo/title.html`, `demo/end.html`. Each take creates a "The Millers" project and fires one real option set (~$0.50 on the client's Gemini key) — delete the extra project after.

## QA
Frame-by-frame check at 8 scene points + a hard assert on every critical step (photo uploaded, options fired, 4 option cards, board lock text, present-mode class). Take 1 failed the present-mode frame check (click timing) → driver patched with assert + fallback → take 2.

## Known limits / v4 backlog
- No music bed (no licensed track on hand — the Founder's v2 note still open)
- No fade transitions between tabs (raw screencast)
- The Millers' own renders don't appear in the video (they finish after the take) — the cut to the Founder-Test is the honest substitute
- visual-brand-qa pass before external send if the Founder wants belt-and-suspenders
