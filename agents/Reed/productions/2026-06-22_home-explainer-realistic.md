# Production — Home-page explainer (REALISTIC) · v1

**Producer:** Reed · **Date:** 2026-06-22 · **Brief/request:** `agents/Reed/requests/2026-06-22_home-explainer-realistic.md`
**Replaces:** the current animated home hero (`index.html` demo-frame → `share.descript.com/view/mIvvSqQZ5xk`).
**Status:** **Scaffold built — needs footage + VO + eval + approval before it goes on the site.**

## Done (2026-06-22)
- **Descript project created** from the approved ~90s script (9 beats): `yourco — home explainer (realistic)`.
  - URL: https://web.descript.com/6fc1f24c-2fea-4983-b6dd-27a5bbc65a96
  - Composition: `yourco home explainer v1` · 87.6s · 16:9 · project_id `6fc1f24c-2fea-4983-b6dd-27a5bbc65a96`.
  - Script laid out as the narration track across the 9 scene beats with per-scene visual notes; brand colors specified; **no baked-in text** (titles/overlays only); VO voice intentionally left **unassigned**.

## Real-footage bed — RENDERED ✅ (2026-06-22, $0 spent, free path)
OpenMontage project `quiet-after-hours` (on the Founder's Mac, `~/Documents/OpenMontage/projects/quiet-after-hours/`). Real Pexels footage (free license, no watermark) + royalty-free music. No paid AI generation (`FAL_KEY`/Seedance declined per the Founder). Real-footage-only path. 16:9 1080p, ~89s, no on-screen text, no narration, VO headroom — exactly the brief.
- **`renders/quiet-after-hours_picture-only.mp4`** — 89s · 1920×1080 · silent clean cut → drop into Descript for VO + conceptual beats.
- **`renders/quiet-after-hours_hero.mp4`** — 89s · picture + low music bed (for a quick "watch it" review).
- **`assets/music/quiet-after-hours_music-bed.mp3`** — 89s · separate music stem (full level, faded) for re-leveling under VO.
- *Finish note:* the staged `_assemble.py` had a bad ffmpeg filter option (`colorbalance=rshadows=…`, invalid in this ffmpeg build); fixed to `rs/bs/rm/bm` and re-ran cleanly. (The OpenMontage session had locked itself out of the folder by disabling its sandbox; finished from the yourco Cowork session, which retained access.)

## Remaining steps (in order)
1. ~~Real footage (OpenMontage).~~ **DONE** — the real-footage bed above. Covers the live-action beats (owner reality, audit/discovery, never-sleeps dusk→dawn, outcomes). Drop `picture-only.mp4` into the Descript composition.
2. **Assign the VO voice (Descript app — the known manual step, `02_build.md`).** Open the project → assign a calm, neutral AI voice → render the narration.
3. **Assembly polish + brand end card** (Descript): timing, overlays/titles, the Midnight-Indigo/Brass end frame + CTA.
4. **Kolby eval** against the realistic credibility gate: every workflow/outcome represents what yourco will actually build; **no fabricated metrics/testimonials/likenesses**; no AI-baked text; numbers real-or-labeled.
5. **the Founder approves.**
6. **Webb swaps the home embed:** in `index.html`, change the `<a class="demo-frame">` href to the new video's share URL; keep the component + brass play button.

## Credibility gate (load-bearing — `decisions/2026-06-17_Reed-realistic-video-openmontage.md`)
"produced realistically — every workflow + outcome shown represents what yourco will actually build and deliver." Pre-revenue → outcomes stay qualitative; no invented results. The "compounds / gets stronger over time" beat = the **operated** continuous-improvement loop (weekly iteration + `learnings/`), not autonomous self-rewrite.

## Closed-loop feedback (fill after first cut)
- What worked:
- What to change next cut:
- Reusable for future explainers:
