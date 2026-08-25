# Content / Marketing Cadence Loop

> **Owner: Katie** (YourCo's Content/Marketing Agent — see `agents/katie/`). Runs and signs as Katie. Drafts only — nothing publishes externally without the Founder's approval. Atlas reads the output for the Monday briefing but no longer owns this loop. (Handoff logged: `decisions/2026-06-07_katie-content-agent.md`.)

## Cadence
Every Friday at 7:00 AM ET.

## Goal
Produce a weekly content brief and ready-to-post drafts anchored on YourCo's thesis. Currently YourCo's primary growth lever — until pipeline lands, content compounds.

## Inputs (read every run)
1. `CLAUDE.md` — especially the thesis and moat sections
2. `01_company.md` — for narrative anchors
3. Most recent prior artifact in `loops/content/`
4. The most recent sales artifact in `loops/sales/` — for any topical hooks from the week (e.g., a prospect's objection becomes a public post)
5. (Optional) WebSearch for AI-implementation industry chatter from the last 7 days — at most 3-5 results, only if it changes the angle

## Steps
0. **Read recent learnings.** Before anything else, read the most recent entries (last ~5, past 30 days) in `/learnings/content/` and `/learnings/brand-voice/` for patterns that apply to this run, and apply what fits. List the entries you applied in the artifact's "Learnings applied this run" line. (An empty folder means nothing to apply yet — expected pre-launch.)
1. **Boot context.** Internalize the thesis: agent tooling is commoditizing, the moat is reliability/eval/observability/approval/integration/trust, 48h go-live, named digital employees, never self-serve.
2. **Pick a theme for the week.** One sharp angle anchored on the moat or thesis. Not generic AI content. Examples:
   - "The difference between a workflow and a digital employee"
   - "What an eval gate looks like in practice"
   - "Why we won't sell self-serve (and won't apologize for it)"
   - "A digital employee's first 48 hours"
   - "How we know our agent did its job (and how the client sees it)"
3. **Draft four pieces in the Founder's voice (concise, direct, minimal formatting, no emoji unless natural):**
   - **LinkedIn post** — 1200-2000 chars, conversational, ends with a one-line provocation or question. Ready to copy-paste.
   - **X/Twitter** — short version or thread.
   - **Newsletter-style piece** — 400-700 words for longer-form publication.
   - **Carousel script** — a 6–10 slide deck for **LinkedIn (document post)** and **Instagram (image carousel)** — same deck, both channels. You write the *script* (slide-by-slide copy + structure), not the visual; production is Canva/brand-kit (or Pickle once built). Structure: slide 1 = hook (scroll-stopper, ≤12 words), slides 2…n−1 = one idea per slide (≤25 words each, builds the argument), slide n−1 = the payoff, slide n = a soft CTA. Skip the carousel only when the theme is genuinely narrative-only (no list/teach/proof spine) — note why in the artifact.
4. **Suggest 3-5 follow-up angles** — next themes that build on this one.
5. **Write artifact** at `loops/content/YYYY-MM-DD.md`.
6. **Slack summary** — one line to `#yourco-katie`: "Content brief ready, theme: <X>." Signed "— Katie, YourCo Ops."

## Output artifact format
```
# Content Cadence — YYYY-MM-DD

## Theme
(One sentence)

## Why this theme this week
(One paragraph anchoring it to thesis/moat/timing)

## LinkedIn draft
(Ready to copy-paste)

## X/Twitter draft
(Ready to copy-paste)

## Newsletter-style piece
(Ready to copy-paste or stage for blog)

## Carousel script (LinkedIn document + Instagram)
(Slide-by-slide, ready to drop into Canva. "Skipped — narrative-only theme: <reason>" if not applicable this run.)
- **Slide 1 (hook):** ...
- **Slide 2:** ...
- **Slide 3:** ...
- ...
- **Slide n (CTA):** ...
(Caption: 1–3 lines to post alongside the deck. Channels: LinkedIn document post + Instagram carousel.)

## Follow-up angles
1. ...
2. ...
3. ...

## What I'd do differently next run
(Empty — for the Founder to fill)

## What worked this run
(1-2 things that landed harder than expected. Future runs read this too — this is how wins get amplified, not just mistakes avoided.)

## Learnings applied this run
(The `/learnings/content/` and `/learnings/brand-voice/` entries that influenced this run. "None" if nothing applied.)
```

## Style guide (apply rigorously)
First, the canonical writing rules: `brand/writing-rules.md` (banned phrases, the em-dash cap, prose vs. display copy, the read-aloud test). On top of those, for content:
- Outcomes framing, not features framing
- Never sell the tooling; sell the moat layer
- Real examples > abstract claims
- No emoji unless it's organic in flow
- If the post could have been written by anyone selling AI consulting, rewrite it
- **Carousels:** one idea per slide, phone-readable, no slide a screenshot of the last. Hook slide must stop the scroll on its own. Big type, brand colors (brass-on-indigo), lots of whitespace. The deck should make sense muted and tiny — if a slide needs a paragraph, it's two slides.

## Watchdog triggers
- Same theme used 2 consecutive weeks → vary it next run
- No follow-up angles created → flag
- Drafts read like generic AI content → reject and redraft
