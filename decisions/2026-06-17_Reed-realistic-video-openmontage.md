# 2026-06-17 — Reed goes realistic; adopt OpenMontage; demos go full-blown

> **⚠️ PARTIALLY SUPERSEDED 2026-06-23 (`decisions/2026-06-23_Reed-higgsfield-not-openmontage.md`):** the **OpenMontage adoption is reversed** — Higgsfield is now the sole engine. **Still in force from this decision:** realistic video is allowed (not animated-only) and the **reframed credibility gate** below. Read the OpenMontage parts as historical.

## Decision (the Founder)
Two shifts, one goal — **make the prospect demos feel real enough that a prospect viscerally gets the outcome**:
1. **Reed's mindset/output shifts from "animated-only" → realistic.** The 2026-06-09 lock
   (`2026-06-09_Reed-higgsfield-animation-stack.md`) made demos *animated/conceptual only* (no real-footage,
   no realism) to avoid faking agent capture. **Superseded:** Reed may now produce **realistic video** —
   real/stock/archival footage, realistic scenes, true-to-life production — when that better shows the outcome.
2. **Adopt OpenMontage** (open-source agentic video — pulls real footage from Archive.org/NASA/Wikimedia/Pexels/
   Pixabay and assembles via Claude Code; `agents/brett/competitive-watch.md`) as the **real-footage production
   engine**, alongside Higgsfield (still useful for illustrative scenes) and the hyperframes pilot (data-viz). Three
   engines, picked per shot.
3. **Demos go full-blown, not minimal.** The current cold-outreach demos are thin/sample-grade. Upgrade them to
   **complete, realistic, outcome-first** pieces that let a prospect *feel exactly how this employee/OS produces
   their outcome* — the "I rebuilt your front desk with AI, here it is" hook (Logan Kilpatrick insight) only lands
   if the artifact is convincing, not a placeholder.

## Why
- **Realism converts.** A prospect feels an outcome more from a believable, real-feeling demo than a stylized
  cartoon. The animated-only constraint was protecting credibility; done well, realism *increases* it.
- **The cost of build is ~0.** OpenMontage + Veo-class realism make real-footage production cheap and fast — the
  reason animated-only was the safe default (realism used to be expensive/fake-looking) no longer holds.
- **The outreach hook demands it.** Personalized, full-blown demos are the cold-outreach weapon (Reilly/Michelle).

## The credibility gate — reframed, NOT dropped (this is the load-bearing part)
Realism raises the honesty bar, so the gate gets sharper, not looser:
- **Represents real yourco workflows + real, achievable outcomes.** Every demo still shows what yourco *will
  actually build* — no fabricated capabilities, no invented metrics, no "results" that aren't grounded.
- **No deception about what's real.** Do **not** present AI-generated or stock footage as genuine captured client
  work, and **never** fabricate a "real customer" testimonial/likeness. If a scene is illustrative, it stays
  clearly illustrative. AI-generated realism is fine as *production*; it must not manufacture *false evidence*.
- **No deepfakes / no real person's likeness or voice without consent.** (Brand + legal.)
- **Numbers are real or labeled illustrative** — same rule as everywhere (`brand/writing-rules.md`).
- Kolby evals demo claims; the Founder approves before any external send (unchanged).

> The old line "animated faithfully — every workflow shown represents what yourco will actually build" becomes:
> **"produced realistically — every workflow + outcome shown represents what yourco will actually build and deliver."**
> Honesty of *substance* is the constant; the *medium* (animated vs realistic) is now Reed's call per shot.

## What changes (docs)
- `agents/Reed/_README.md` + `02_build.md` — drop "animated-only," add the realistic mandate + OpenMontage +
  the reframed credibility gate. Higgsfield stays (illustrative scenes); OpenMontage = real-footage; hyperframes =
  data-viz. **Tool to set up:** OpenMontage is open-source — **the Founder/Reed install it** (agent can't); staged.
- Cold-outreach demo standard upgrades from "60–90s sample" to **full-blown, outcome-first, prospect-specific**.
- Connects to: the voice-agent landing experience + the demo kit (`clients/_yourco-template/demo-kit/`) — the demo
  kit gets the same "make it real" upgrade.

## Owners
**Reed** (produces; runs OpenMontage) · **Katie** (scripts) · **Kolby** (eval the realism + claims) · **the Founder**
(approves; sets up OpenMontage). Supersedes the animated-only clause of `2026-06-09_Reed-higgsfield-animation-stack.md`
(that stack doc stays valid for the tools; only the animated-*only* constraint is lifted).

## Status
Direction set 2026-06-17. Staged like all external content (launch-gate). OpenMontage install is the Founder/Reed's
next step; until then Higgsfield + hyperframes remain the live engines.
