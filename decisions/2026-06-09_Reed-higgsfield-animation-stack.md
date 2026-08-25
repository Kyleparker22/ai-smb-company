# Decision — Reed: Higgsfield is the animation engine (supersedes Canva)

**Date:** 2026-06-09
**Owner:** the Founder (decision) · Reed (execution)
**Status:** ✅ Locked
**Supersedes:** `/decisions/2026-06-08_Reed-production-stack.md` (Canva Pro animated-only) — for the *animation generation* layer only.

## Decision
Reed's demo videos are produced with **Higgsfield** (AI animated video generation, MCP-connected to the workspace), not Canva. Canva's AI presentation-to-MP4 route read as a slide deck, not an animated video. Higgsfield generates genuinely animated, conceptual workflow scenes.

## Scope of the video (the Founder's direction, 2026-06-09)
Fully **animated and conceptual** — NOT realistic humans, NOT a literal product-UI screen capture. Show what the agents look like from a **workflow standpoint**: the problem → the agent doing the work → the outcomes, as clean animated motion (e.g., a friendly animated intake-assistant character moving a call → qualification → calendar → confirmation flow). Because it's overtly animated, the "faithfulness" risk that blocked real-UI depiction disappears; the "animated faithfully" credibility gate still applies (every workflow shown must represent what YourCo will actually build).

## Stack
- **Animation engine:** Higgsfield (MCP). Default model Seedance 2.0 (reference-driven, consistent identity, silent); Veo 3.1 / Kling 3.0 available for specific shots. ~22–25 credits per ~5s 720p clip.
- **Style/consistency:** lock a character + palette via a reference frame (or Soul ID), reuse across scenes for a single consistent animated look.
- **Captions / assembly / end-frame:** lightweight editor (Canva retained for brand kit + captions + the cream/indigo/brass end frame). Captions added in post — never baked by the generator (AI text is unreliable).
- **Hosting:** Loom (free).
- **Brand:** Cream `#F4EFE6`, Midnight Indigo `#161B33`, Brass `#B8965A`, lowercase `yourco`. Silent + captions.

## Ownership
This is **Reed's job**. Reed runs Higgsfield (now an available tool), generates the scene set, assembles + captions, and brings the final cut to the Founder's publish gate. Reilly consumes the registered asset for Email 2. Atlas monitors credit spend.

## Voiceover added (2026-06-09 — amends the silent posture)
the Founder's call 2026-06-09: the demo gets a **calm, professional male voiceover** narrating throughout — overriding the prior "silent + on-screen captions, no voiceover" posture (from copy-structure v2 / Reed 02_build). Rationale: reads more produced/professional. Guardrail: the VO must stay **consultative, not announcer/hype** — a salesy VO would fight the brand harder than silence. VO script: `/agents/Reed/productions/2026-06-09_landscaping-vo-script.md`. Generated via ElevenLabs-class TTS, mixed under the stitched clips. With VO carrying narration, on-screen captions reduce to key labels + the end-frame line. The VO script drives the edit (lock VO → time scenes to it).

## Unchanged
Animated-only (no real-agent capture, no live B-roll). Reed's publish gate (the Founder approves final cut → register in `_asset_registry.md` → hand to Reilly). The 06-08 script + story arc still drive the scenes.
