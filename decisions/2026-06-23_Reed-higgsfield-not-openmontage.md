# 2026-06-23 — Reed: drop OpenMontage, standardize on Higgsfield

## Decision (the Founder)
Reed's video production runs on **Higgsfield (MCP-connected) as the sole generation engine** + **Descript** for assembly/VO/overlays. **OpenMontage is dropped** from the pipeline.

## Why
- **Higgsfield is the proven path.** This session validated the full premium pipeline on Higgsfield end-to-end: Soul Cinema stills (image-first) → Veo 3.1 / Cinema Studio 3.0 / Kling animation, MCP-driven from Cowork. It produced the approved grounded look + motion proof.
- **OpenMontage underdelivered + added friction.** Its stock-footage auto-assembly produced the "stock-soup" cut the Founder rejected; it only runs locally on the Founder's Mac (the VPS gate denies Bash), it locked itself out of its own folder mid-run (sandbox), and it needed a separate Slack bridge to drive. Higgsfield (MCP) removes all of that — Reed drives it directly, no local repo, no bridge.
- **One engine = simpler standard.** Concept-first + image-first + top-models, all in Higgsfield; assembly/VO/text in Descript. No third tool to maintain.

## What changes
- **Engine:** Higgsfield only (image: Soul Cinema / Nano Banana Pro / FLUX; video: Veo 3.1, Cinema Studio 3.0, Kling 3.0 — Turbo/720p for drafts). Assembly + VO + brand text overlays: Descript. Brand kit/end-frames: Canva. Hosting: Loom.
- **OpenMontage:** removed from the standing stack. `agents/Reed/openmontage-setup.md` and `runtime/montage_slack_bridge.py` are **deprecated** (kept for history, not used). The local `~/Documents/OpenMontage` install can be left or removed at the Founder's discretion.

## Supersedes / amends
- Supersedes the **OpenMontage adoption** in `decisions/2026-06-17_Reed-realistic-video-openmontage.md`. The rest of that decision **still stands**: realistic video is allowed (not animated-only), and the reframed **credibility gate** is unchanged.
- Consistent with the standing standard in `decisions/2026-06-22_Reed-premium-concept-first-video.md` and `agents/Reed/02_build.md` §"Production standard v3" (which was already Higgsfield-centric).

## Owner
**Reed** (production on Higgsfield + Descript) · **Kolby** (eval) · **the Founder** (approval). No agent action needed to "install" anything — Higgsfield is an MCP connector.
