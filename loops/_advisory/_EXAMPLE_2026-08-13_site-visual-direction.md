> ⚠️ **EXAMPLE OUTPUT — not yours.** This is one run of this loop from the company this
> template was extracted from, kept so you can see the shape of what the loop produces.
> The dates, numbers, and findings describe **someone else's business**. Delete this file
> the first time your own loop writes a real one.

# Advisory panel — visual direction for the unpublished site (2026-08-13)

**Scope.** Look and feel of `agents/webb/pages/yourco-site-v2/` — 26 staged pages, unpublished,
behind the launch-gate. Asked by the Founder after the same day's build shipped ten items onto the site.
**Third panel run today**, after `2026-08-13_ai-os-design.md` (morning) and
`2026-08-13_hq-design.md` (afternoon).

**Panel.** The standing roster carries no design or psychology reviewers, so both benches were
added for this run and should persist in `SKILL.md` if they prove useful.

- **Design/web (new):** Reichenstein (iA — "web design is 95% typography") · Vignelli (discipline,
  few faces, the grid) · Rams (as little design as possible; honest design) · Saarinen (Linear —
  craft as the differentiator) · Fried (37signals — plain, opinionated, anti-flourish) · Bierut
  (Pentagram — editorial hierarchy).
- **Psychology (new):** Kahneman (cognitive ease → perceived truth) · Cialdini (authority, unity,
  liking) · Norman (visceral / behavioural / reflective) · Fogg (B=MAP — ability beats motivation)
  · Heath & Heath (Power of Moments — peak-end) · Schwartz (choice overload).
- **From the standing roster:** Enns (the visible expert practice) · Godin (story as permission) ·
  Dunford (positioning).
- **Left out:** the entire technical/platform bench (Sutton, Karpathy, Chollet, Weng, Willison,
  Amodei…). This is a perception decision; their frameworks don't bear on it. Willison's
  publish-the-security-model finding was already acted on today and needs no re-run.

---

## Standing (one line each — not re-argued)

| Ref | Standing finding | Status |
|---|---|---|
| CV-F (08-13 pm) | Everything is downstream of capacity, and capacity is one person | **Escalated again.** The lock-in run is 0 of 14 locked with 5 slipped; today added ten more site surfaces |
| CV-G (08-13 pm) | Subtraction is the only free move | **Reversed on this surface.** The site went 21 → 26 pages today |
| CV-E (08-13 am) | Instrumentation is ahead of anything yourco has sold | **Escalated** — the instrumentation is now *on the marketing site* |
| Action 5 (08-13 pm) | Build none of it before 8/26 | **Unchanged, and overridden once already today** |

---

## New findings

### D1 — The design system is a document, not a stylesheet. (Vignelli · Rams · Saarinen)
`brand/DESIGN.md` is genuinely good — tokens, idioms, a motion budget, hard rules. The site does not
consume it. **15 of 26 pages restate the `:root` token block inline** and never link `site.css`.
DESIGN.md §8 sets the order of truth as guidelines → DESIGN.md → site, and says *fix downstream,
don't fork* — the site has forked fifteen ways.

This is not an aesthetic finding, it is an arithmetic one: **every future visual change costs 15×.**
Confirmed the hard way today — adding one component required injecting identical CSS into two pages
separately because they don't share a stylesheet. Vignelli's discipline, Rams's subtraction and
Saarinen's craft argument all land on the same mechanical fix, which requires no design judgement at
all.

### D2 — 95% of the design is typography, and the typeface is a third-party import. (Reichenstein)
Fraunces loads via `@import url('https://fonts.googleapis.com/css2?…')` in **16 files**. An `@import`
inside CSS cannot be preloaded and serialises the request chain, so the one element carrying the
entire brand — the display face — is the last thing to arrive and flashes. Three problems in one:
it's slow, it flashes, and it is a third-party dependency on a site whose thesis is *we own the
stack so you don't have to*. Self-host one woff2, `font-display:swap`, preload it. Speed is not a
performance concern here; it is the first evidence a visitor gets that the premium claim is real.

### D3 — The hero is an abstract glowing brain, which yourco's own standard bans. (Rams · Fried · Dunford)
CLAUDE.md, on the video standard: *"Abstract particle loops are banned as the primary visual (they
don't communicate); concrete imagery only."* That lesson was learned in video and never reached the
site, where the hero is a 1.9MB PNG of a brain under two WebGL canvases — the least specific idea
yourco owns, rendered at the highest cost on the page. Every AI company on earth could run this
image. Dunford's test: if a competitor could put their logo on your hero, it isn't positioning.

The concrete alternative is already built and sitting unused: a real approval screen, a real client
console, the actual board. Show the product.

### D4 — There is not one human face on the site. (Cialdini · Norman · Enns)
Zero photographs of anything real: no founder, no team, no screen, no place. `about.html` contains
no image at all. For a **boutique** consultancy whose pitch is *a person learns your business*, and
which is pre-revenue with no logos and no case studies, this discards the only trust levers still
available — Cialdini's authority, unity and liking. Enns's entire model of the expert practice that
charges for a diagnostic rests on a named, visible practitioner. the Founder is the product and is invisible.

### D5 — The honesty layer creates disfluency, and disfluency reads as doubt. (Kahneman · Norman)
**The sharpest finding in this run, and it is a direct consequence of today's build.** Processing
fluency raises perceived truth: material that is easy to read is judged more likely to be true. The
site now carries *unproven*, *untested*, *excluded*, *this is a model*, *we refuse to state* — every
one correct, every one a cognitive cost, all introduced today.

The trap is thinking the fix is fewer refusals. It is not. The fix is that **a refusal must look
designed, not broken.** Right now `.claim.is-dark` renders an oxblood chip reading "unproven" — the
visual language of a form validation error. A withheld number set confidently in the display face,
with real space around it and no alarm colour, reads as rigour. The same sentence in a red-bordered
chip reads as a bug. Identical information, opposite inference.

### D6 — The site has no peak. (Heath & Heath)
Peak-end says people remember the most intense moment and the ending, not the average — and the
average here is high and *even*: 26 well-mannered tiles alternating cream, parchment and indigo,
none louder than the others. yourco now owns what should be the most memorable moment in B2B
marketing — a number going dark on a live page, admitting what it cannot prove — and it is a small
muted card two thirds down the homepage. It is being spent as texture instead of staged as the peak.

### D7 — 26 pages against one job. (Schwartz · Fogg · Godin)
Choice overload is real and Fogg's B=MAP puts *ability* — how easy the next step is — above
motivation. The nav is seven links plus a pill; the footer now lists fifteen. Four pages were added
today. The panel's standing CV-G (subtraction is the only free move) was written about HQ this
afternoon and applies verbatim here.

### D8 — Two of the house's own hard rules are broken, and today broke them further. (Norman)
- **Brass scarcity (§4.1: one brass moment per surface).** The hero now has five: eyebrow, gate
  divider, promise band, CTA pill, text link. The promise band was added today.
- **Motion budget (§6: one reveal per section; "never animate every element — reads cheap/AI").**
  The reveal selector on the homepage covers **eleven element types** per section.

Norman's visceral level fires before anyone reads a word. Accent inflation and universal motion are
exactly the tells that separate a designed page from a generated one — which is a costly signal for
a company whose product is AI.

---

## Convergences (3+ reviewers, independent frameworks)

- **CV-N — The credibility constraint is now typographic, not evidential.** (Kahneman · Reichenstein
  · Norman.) In one day yourco became the most evidentially honest site in its category and
  simultaneously the most hedged. Three frameworks arrive at the same conclusion from different
  directions: **another proof point now adds nothing.** The next unit of trust comes from type,
  spacing and load speed. This is the finding that should govern the visual pass.

- **CV-O — One system, one typeface file, one hero idea.** (Vignelli · Rams · Fried · Saarinen.)
  Four reviewers, four routes — discipline, subtraction, plainness, craft — one instruction:
  collapse the 15 inline token blocks into `site.css`, self-host the display face, and replace the
  abstract brain with the actual product. None of this requires a creative decision, which is why
  it should happen before any creative decision does.

- **CV-P — The absent human is the biggest unforced error on the surface.** (Cialdini · Norman ·
  Enns · Godin.) At n=0 clients the available trust levers are authority, unity and the visible
  practitioner. The site uses none of them. A photograph of the Founder costs nothing and is the highest
  ratio of trust-gained to work-required anywhere in this report.

---

## Actions

| # | Action | Owner | Smallest version this week | Rating |
|---|---|---|---|---|
| 1 | **Build none of it before 8/26** | the Founder | — | **Now.** Unchanged from this afternoon. The lock-in run is 0 of 14 locked with 5 slipped; the site is not among the domains that needed today's ten builds |
| 2 | **Collapse 15 inline token blocks into `site.css`; self-host Fraunces as one woff2** | Webb + Luka | Link the stylesheet, delete the duplicated `:root` blocks, one font file | **Next** — mechanical, no design judgement, and every later visual change costs 15× until it's done |
| 3 | **One photograph of the Founder, on `about` and the home page** | the Founder | One good photo | **Next** — free, and it is the only unused trust lever |
| 4 | **Restyle the withheld-claim state so it reads as rigour, not error** | Webb | Drop the oxblood chip; set the withheld claim in the display face with space around it | **Later** — after 8/26, and it is the highest-value *creative* item |
| 5 | Replace the brain hero with real product imagery · stage the going-dark moment as the page's peak · re-impose brass and motion budgets | Webb | — | **Later** — a single considered pass, not five separate edits |

---

## Did the last run change anything?

**Yes, and its Now action was overridden — for the second time in one day.** This morning's panel
said *build none of the six this week*; all six were built. This afternoon's said *build none of it
before 8/26*; ten site items shipped after it. Both builds were sound work and the second found two
real spec violations plus a live invariant breach. The pattern is now three consecutive runs naming
capacity and three overrides, which is a finding about **how this panel is being used**, not about
its content.

Recorded plainly, not argued. Per the retire test: this run *will* have changed something if items 2
and 3 land without a redesign attached. If the next run finds the site instead grew again, the
honest recommendation is to stop asking this panel about build sequencing and ask it only about
craft.
