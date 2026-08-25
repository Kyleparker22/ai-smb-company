---
name: visual-brand-qa
description: Vision-model QA pass on any generated visual (Higgsfield/Nano Banana stills, video frames, carousels, one-pagers, site imagery) against brand/DESIGN.md + the credibility gate, BEFORE it routes to the Founder. Invoke at every producer hand-off (Reed, Pickle, Webb, Katie) and in Kolby's weekly eval pass for any week that shipped visuals. Binary pass/fail per criterion; reports only — the producer fixes, the Founder still approves.
---

# visual-brand-qa

## Canonical docs
`brand/DESIGN.md` (the spec — **source of truth, re-read it every run; never trust this skill's memory of it**) + `agents/Reed/02_build.md` §Credibility gate + CLAUDE.md §External-surface rules. Pattern stolen from the Isenberg×Cody Schneider marketing-agents episode ("put a vision model over the outputs — does this match brand style guides?"), `decisions/2026-07-05_tool-triage.md` §Addendum 07-29.

## When
1. **Producer hand-off** (the main gate): Reed finishes scenes/stills, Pickle a one-pager, Webb page imagery, Katie a carousel/social static → run this BEFORE the asset routes to the Founder. This gate is **in addition to** the Founder's human approval, never a replacement.
2. **Kolby's weekly eval-review**: any week where visuals shipped, spot-check them and record pass/fail in the scoreboard.
3. **Client-facing assets**: always — with the white-label criteria switched on.

## Steps
1. **Load the spec fresh**: Read `brand/DESIGN.md` (all sections) — the checklist below is the failure taxonomy; the *values* (hexes, fonts, idioms) always come from the file at run time.
2. **Read the visual(s)** with the Read tool (images render natively). Video: QA the stills/keyframes the producer already has (Higgsfield job frames, Canva export frames); full-motion deep QA is the gated claude-video-vision path (`runtime/activation-triggers.md`), not this skill.
3. **Score binary pass/fail per criterion** (Kolby's rubric style — no Likert scores):
   - **Palette** — only DESIGN.md §1 tokens; auto-fail: pure `#000`, `#FFF` surfaces, AI-purple/electric-blue gradients, neon; oxblood outside its reserved moments.
   - **One-brass rule** — at most one brass moment per surface/frame.
   - **Type** — Fraunces display-only; wordmark lowercase `yourco`, never serif; no all-caps body.
   - **Rendered-text check (the gibberish rule — auto-fail)** — ANY text baked into the generated image/frame (AI-rendered) fails; text must be a post overlay. Look closely: warped letterforms, pseudo-words, garbled UI labels.
   - **Idiom conformance** — matches a §4 idiom (eyebrow, CTA pill, hairlines-not-boxes, tick motif, media frame) rather than inventing.
   - **Credibility gate** — no fabricated metrics/testimonials/endorsements visible; any number real-and-cited or labeled illustrative; workflows shown = what yourco actually delivers.
   - **Premium bar** — would it pass as $50k-agency work? Default-Bootstrap or AI-slop texture = fail.
   - **White-label (client-facing only)** — client brand only, no yourco mark unless co-branded, agents by function never name, no prices, stats ≤18mo.
4. **Write the verdict block** (into the hand-off note / production ledger / eval artifact): per-criterion pass/fail, the specific fix for each fail (name the frame/region), and one overall line — **ship / fix-first**. Reports only: the producer applies fixes; never edit the asset yourself unless you are the producer.
5. **Feed forward**: a failure mode seen twice → write it to `learnings/video-production/` (or `learnings/design/`) so producers pre-empt it at their Step 0; a genuinely new failure class → flag to Luka as a candidate DESIGN.md §6 hard rule (Luka's call, his changelog).

## Gotchas
- **Re-read DESIGN.md every run** — the spec evolves (Luka's changelog); a cached checklist is how drift ships. If this skill and DESIGN.md disagree, DESIGN.md wins (guidelines → DESIGN.md → site is the order of truth).
- The rendered-text check is the highest-frequency catch (learned 2026-06-10, `agents/Reed/02_build.md` §Hard rule) — zoom in on anything that looks like UI text or captions.
- Don't let a pass here soften the human gate: the Founder approves everything external, always (HUMAN-MUST-APPROVE stays in every pipeline).
- Batch verdicts stay cheap: one verdict block per asset set, not an essay per image.
