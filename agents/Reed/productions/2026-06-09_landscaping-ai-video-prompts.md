# AI-Video Production Package — Landscaping Intake Demo (Email 2)

**Created:** 2026-06-09 · Reed
**Pivot from:** Canva slide-export (read too deck-like) → AI cinematic video
**Tool (the Founder's pick):** Higgsfield (aggregates Veo 3.1, Kling 3.0, Sora 2). No MCP connector — browser-driven or run in the Founder's account.
**Script source:** `/agents/Reed/productions/2026-06-08_landscaping-intake-demo.md` (approved)
**Audio:** silent + captions overlaid in post (AI-baked text is unreliable — never let the generator render the on-screen captions; add them in the editor).

## The honest split (read first)
AI video is great at **realistic human/world scenes** and bad at **rendering your real product UI** (it fabricates dashboards and garbles text — which breaks the locked "every workflow shown represents what YourCo will actually build" gate).

- **Parts 1 & 3 (human/jobsite scenes):** ✅ generate with Higgsfield. This is where the cinematic upgrade lands.
- **Part 2 (the agent working — dashboard, calendar, SMS):** ⚠️ do NOT let AI gen invent the UI. Options: (a) stylized abstract UI motion (clean cards/fields animating, no fake product) with captions doing the work, or (b) real screen-capture / Canva motion-mock of the actual intake flow cut in. Recommend (b) for credibility; (a) acceptable for a v0 sizzle.

## Global style directives (apply to every human-scene prompt)
- Look: warm documentary realism, natural light, shallow depth of field, 35mm, slight handheld. Not glossy/ad-stocky.
- Palette bias toward brand: warm cream light, deep indigo shadows; brass/golden-hour accents. Subject: a real-looking owner-operator (40s, work clothes), a crew foreman, a residential yard.
- Aspect 16:9, 1080p, ~4–6 sec/clip. No on-screen text from the generator. No logos from the generator.
- Continuity: same owner + same truck across scenes (use Higgsfield Soul ID / character-reference to lock the character).

## Shot list — prompts

### Part 1 — the problem (generate in Higgsfield)
| # | Caption (add in post) | Prompt | Notes |
|---|---|---|---|
| 1 | 2:47pm tuesday | "Documentary handheld, golden afternoon light. A landscaping business owner in his 40s, work shirt and cap, stands on a green residential lawn talking with his crew foreman, gesturing at a freshly shaped hedge. His phone buzzes in his back pocket; he glances at it but keeps talking. Shallow depth of field, warm tones, realistic." | Lock this character (Soul ID) for reuse. |
| 2 | every missed call is a $4k–$15k job | "Close-up of a smartphone mounted on a work-truck dashboard, engine idling. A missed-call notification slides up: 'Unknown caller.' Out-of-focus green suburban street through the windshield. Natural light, realistic, shallow focus." | Don't render legible fake names — keep UI vague/abstract. |
| 3 | 7:14pm, still writing estimates | "Interior of a parked pickup truck cab at dusk, soft golden light through the windshield. The same 40s owner sits with a laptop on his lap, tired, a full coffee mug untouched in the cup holder. Quiet, intimate, documentary realism." | Same character. |
| 4 | monday morning | "A small landscaping company office, Monday morning. A whiteboard cluttered with overlapping sticky notes and crossed-out times. A crew foreman stands looking at it, head tilted, slightly overwhelmed. Natural window light, realistic." | No legible text needed. |

### Part 2 — the agent in action (do NOT pure-AI-gen the UI — see split above)
| # | Caption | Approach | Notes |
|---|---|---|---|
| 5 | picking up | Stylized clean UI motion OR real capture: an intake dashboard with an incoming-call card animating in. | If AI-gen: keep UI abstract/generic, never a fabricated "real" product screen. Real capture strongly preferred. |
| 6 | the call | Motion-mock: split view, caller bubble + qualification panel; text typed in post. | Captions carry the dialogue (Maria: retaining wall + regrade; agent: what zip?). |
| 7 | lead qualified, 38 seconds | Motion-mock: qualification fields populating one by one (zip 30327 · retaining wall + regrade · 200–400 sq ft · $8k–$15k · 2–3 weeks). | Build in editor/Canva, not AI gen — fields must be accurate. |
| 8 | he never touched his phone | Motion-mock: a calendar with a new event sliding in, Tue Jun 11 2:00pm, details attached. | Real Google Calendar capture is ideal. |
| 9 | confirmation sent | Motion-mock: a phone receiving a confirmation SMS (text added in post). | Keep the STOP line. |
| 10 | estimate scheduled · owner notified · crm updated | Motion-mock: status line + quiet checkmark. | — |

### Part 3 — the outcomes (generate in Higgsfield)
| # | Caption | Prompt | Notes |
|---|---|---|---|
| 11 | phone stays in the truck | "The same 40s landscaping owner walks across a backyard installation with his crew foreman, pointing at a graded slope, relaxed and confident. In the background his phone sits untouched on the truck's passenger seat, visible through the open window. Warm afternoon light, documentary realism." | Same character + truck. |
| 12 | booked while he was on site | "A clean weekly calendar view on a tablet held in work-gloved hands on a job site, several appointment blocks filled across the week. Natural daylight, realistic, shallow focus." | Keep calendar blocks abstract (no fake legible text). |
| 13 | requested automatically after every job | "A homeowner's hands holding a phone in a beautifully finished backyard at golden hour, tapping a five-star rating. Warm, satisfied mood, documentary realism, shallow depth of field." | — |

### End frame (build in editor, not AI gen)
- Cream `#F4EFE6` background, one line of Midnight Indigo `#161B33` text centered: **live in 48 hours from signed agreement**. Brass `#B8965A` lowercase `yourco` lower-right. Hold 5s. No other CTA.

## Assembly
1. Generate Part 1 + Part 3 clips in Higgsfield (lock character via Soul ID). 7 human clips.
2. Build Part 2 UI scenes via real capture or Canva motion-mock (NOT AI gen).
3. Cut together in order, ~74s. Add captions in post (brand font, cream on dark / indigo on light). Subtle notification/click SFX optional; no voiceover.
4. GIF preview: the Shot 4 → Shot 5 cut (chaos → clean intake), ≤2MB, 3–5s loop, brass play-button overlay.
5. End frame as specified.
6. Final cut → the Founder's publish approval → register in `_asset_registry.md` → hand GIF + Loom URL to Reilly.

## Execution options
- **A — I drive Higgsfield via Claude-in-Chrome:** connect your browser + log into Higgsfield (needs credits). I'll generate 2–3 hero scenes (1, 3, 11) as a look-test first, then the rest.
- **B — You run the prompts** in Higgsfield directly; I assemble + caption.
- **C — Hybrid build** for Part 2 (real capture) in parallel.

— Reed, YourCo Ops
