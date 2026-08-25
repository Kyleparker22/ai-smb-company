# Decision — the /learnings/ continuous-improvement substrate

**Date:** 2026-06-10 · **Decider:** the Founder (directed in chat) · **Status:** 🟢 implemented

## What
Add `/learnings/` — a shared substrate where agents record operational patterns observed in practice, and read their domain's recent entries at the start of each run (a new "Step 0"). It completes the closed loop CLAUDE.md already calls for: scheduled task → artifact the next run can read → feedback capture → **feed-forward into the next run.**

## Why now
Kolby (QA/eval) exists and grades every loop weekly — but the findings had nowhere to go that changed behavior on the next run. `/learnings/` is the missing channel: Kolby (and any agent) writes a pattern; the relevant agents read it next run and adjust. It makes Kolby's existence pay off and is squarely on-ethos (reliability + eval + observability + continuous improvement is the moat).

## The contract (full spec in `/learnings/_README.md`)
- Entries: `YYYY-MM-DD_short-slug.md`, format Source / Pattern / Implication / Audience.
- 12 domains mapped to agents (brand-voice, sales-copy, video-production, pricing, content, finance, ops, web, delivery, advisor, qa-eval, compliance).
- Any agent writes its own domain; Kolby + Brett (cross-cutting) write any domain.
- Every loop reads its domain's last ~5 entries as Step 0 and applies what fits.
- Entries never deleted; `[absorbed]` after ~90 days if internalized.
- **learnings/ = operational/behavior-adjusting; decisions/ = settled calls.** No overlap.

## SOP retrofit (applied to all 11 actual loops)
Each loop SOP got: a **Step 0 "Read recent learnings,"** plus two new artifact sections — **"What worked this run"** (amplify wins, not just avoid mistakes) and **"Learnings applied this run."** Loops retrofitted: advisor, brand-audit, content, customer-health, eval-review, finance, inbox-triage, monday-briefing, pricing-review, reilly-outbound, sales. Reilly's `copy-structure.md` also got Step 0. Kolby's `_README` + `eval-review.md` now include writing learnings after scoring.

## Correction note
This was proposed via a build prompt written against an assumed/older OS structure. Implemented the design **adapted to the real structure**: the prompt referenced files that don't exist (`agent-health.md`, Kolby's `01_discovery.md`/`02_build.md`, a Reilly "pipeline" section) and missed 5 of our 11 actual loops. The corrected build wires all 11 loops, points Kolby's update at `_README` + `eval-review.md`, and added a `compliance/` domain (Rafi). Same design, correctly mapped.

## Revisit conditions
- If any single domain exceeds ~50 entries, restructure that folder (e.g. sub-index or archive `[absorbed]` entries).
- Re-confirm the substrate is earning its keep after the first quarter of real volume; if loops read empty folders indefinitely, the value hasn't landed yet (expected pre-launch).
