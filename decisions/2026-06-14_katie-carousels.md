# Decision — add carousels to Katie's content engine (LinkedIn primary, Instagram repurpose)

**Date:** 2026-06-14 · **Owner:** the Founder + Katie · **Status:** settled

## Decision
Add the **carousel** as a standard format in Katie's weekly content output: a 6–10 slide deck published as a **LinkedIn document post** (primary) and an **Instagram carousel** (same deck, exported as images). Katie writes the **script** (slide-by-slide copy + structure); the rendered deck is a production step in **Canva** (brand kit, under Luka's voice/visual rules), or **Pickle** once that agent is built. Publishing stays Webb + the Founder-approval; internal-staged until the OtherVenture launch like all external content.

## Context
Katie's engine produced three written drafts per week (LinkedIn text post, X, newsletter) — no slide decks. the Founder wants carousels, both LinkedIn and Instagram. LinkedIn is already the #1 channel for the founder-led, B2B, proof-first strategy, and the LinkedIn document/carousel post is one of its highest-reach native formats (the swipe is the engagement signal) — so LinkedIn carousels are the higher-value half, with Instagram a free repurpose off the same asset.

## Why it fits (not a moat question, a format addition)
- **Same one-effort-many-assets discipline** the engine already runs: one carousel deck → LinkedIn doc post + IG carousel + a Reels cover + the spine of a newsletter section.
- **Reinforces the visual pillars** — teach-the-vertical (one leak per slide), reliability POV (the layers nobody sells), glass box (the 18-employee org chart), and the weekly franchise all carousel naturally.
- **Stays inside agent boundaries** — Katie = editorial/copy (the script); Pickle/Canva = the rendered static design; Luka = the brand rules they render within; Webb + the Founder = publish. A clean handoff, not a scope collision.

## Where it lives (the closed loop)
- `processes/content/content-engine.md` — carousel format spec (structure, specs, best-fit themes) + added to channels + the repurposing flow.
- `processes/loops/content.md` — carousel script is now the 4th weekly draft, with an output section, specs, and a carousel style rule; skip only for genuinely narrative-only themes (note why).
- `runtime/prompts/content.md` — Katie's runtime prompt now asks for the carousel script.
- `04_agent_roster.md` — Katie's scope updated to include carousel scripts.

## Reversibility
Trivial. It's a format added to an internal, staged, drafts-only loop — drop the carousel deliverable from the SOP if it doesn't earn its dwell time once we're publishing and reading engagement (the content loop's `learnings/` will tell us).
