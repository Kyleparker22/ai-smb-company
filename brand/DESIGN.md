# DESIGN.md — yourco's machine-readable design system

> **The design-side twin of `writing-rules.md`.** Load this as a constraint block **before building any visual
> surface** — site pages, dashboards, client consoles, demo kits, decks, videos, one-pagers. It is the terse
> operational spec; the *why* behind every choice lives in `brand/v0/brand-guidelines.md` (canonical narrative,
> don't duplicate it). Owner: **Luka** (custodian) · primary consumers: **Webb, Reed, Pickle, Kimi + the
> scaffolder**. Pattern stolen from nexu-io/open-design's `DESIGN.md` brand systems
> (`decisions/2026-07-05_tool-triage.md` addendum).

## 1 · Tokens (copy-paste this `:root` — never restate hexes by hand)
```css
:root{
  --indigo:#161B33;      /* primary; dark bg, headers, wordmark-on-cream */
  --indigo-deep:#0F1226; /* darker context (video frames, deep panels) */
  --indigo-2:#1c2240;    /* raised dark surface */
  --cream:#F4EFE6;       /* page bg, text-on-dark */
  --cream-2:#E8E1D3;     /* hover / interactive secondary */
  --parchment:#EAE1CD;   /* alternate full-bleed band + footers (ratified 2026-06-23) */
  --brass:#B8965A;       /* THE accent — sparingly (see rule 4.1) */
  --brass-bright:#D4B27A;/* brass hover/highlight */
  --oxblood:#6B1E29;     /* reserved: eval-pass, "live" status, signature moments ONLY */
  --pewter:#6E7180;      /* neutral */
  --ink-muted:rgba(22,27,51,.62);        /* muted text on light */
  --on-dark:#F4EFE6; --on-dark-muted:rgba(244,239,230,.66);
  --hairline:rgba(22,27,51,.12); --hairline-dark:rgba(244,239,230,.16);
}
```
**Never:** pure black `#000`, tech-white `#FFF` as a surface, AI-purple/electric-blue gradients, neon, more than
one brass moment per view. (Guidelines §Never use.)

## 2 · Type
- **Display** (`h1`, section heads, pull quotes, big stat numerals): **Fraunces** (Google Fonts, variable) —
  wght ≈560, optical sizing on, tracking −1…−2%. Display only.
- **Body / UI / labels / the wordmark:** system-sans stack
  (`-apple-system,system-ui,BlinkMacSystemFont,"Inter","Segoe UI",Helvetica,Arial,sans-serif`) — never the serif.
- **Mono** (eval criteria, system status, code): JetBrains Mono.
- Body line-height 1.5–1.7 · no all-caps body (all-caps only ≤10pt labels, brass, sparingly) · no italics for
  emphasis (use weight) · **wordmark always lowercase `yourco`**, never set in the serif.

## 3 · The mark
- **Canonical lockup:** `.____ yourco ____.` — cream wordmark on indigo (indigo on cream for light surfaces),
  flanking hairline brass rules, brass diamond terminals. Clear space ≥ half cap-height beyond the rules.
- Small/circular slots (favicon, app, RCS): `brand/yourco-mark.png`. File map: `brand/LOGO.md`.
- Tagline lockups + variations: guidelines §Lockup variations. Primary tagline: *"We learn your business. AI
  does the work."*

## 4 · Component idioms (the house style — reuse, don't reinvent)
1. **One brass detail per surface.** Brass earns presence through scarcity: the CTA pill, *or* the eyebrow, *or*
   a tick — not all three shouting.
2. **Eyebrow label:** 13px · 600 · letter-spacing .08em · uppercase · brass. Opens a section.
3. **CTA pill:** brass bg, indigo text, 600, radius 9999px; hover → `--brass-bright`; ghost variant =
   transparent bg, brass text. One primary CTA per view.
4. **Sections as full-bleed tiles:** `padding:92px 0`, content in `.wrap{max-width:1040px;padding:0 28px}`.
   Alternate cream / parchment / dark-indigo bands so stacked sections read as chapters.
5. **Hairline dividers, not boxes:** `--hairline` (light) / `--hairline-dark` (dark). Cards are flat with a
   hairline border + generous padding — no drop-shadow soup (one soft shadow on hover is the ceiling).
6. **Brass tick motif:** a short 70×6px brass bar above headings/text blocks — the video/carousel/deck signature.
7. **Media frames:** 16:9, radius ~10px, 1px brass border, `--indigo-deep` fill. (The site's `.demo-frame`.)
8. **Sticky nav:** translucent cream + backdrop blur, hairline bottom border, wordmark left, links + pill right.
9. **Numbered value rows** (the how-it-works idiom): brass-outlined circled number + heading + muted body.
10. **Stats:** big Fraunces numeral in brass, small cream/muted caption, cited source line in small muted type.

## 5 · Surface recipes
- **Web pages:** idioms above; static HTML, semantic structure, JSON-LD where relevant; key facts never
  JS-gated (AEO). Local serving only via `.claude/launch.json` names.
- **Decks / carousels:** 1080×1350 portrait (social) or 16:9 (present); one idea per frame ≤25 words; big type;
  brass-on-indigo; slide 1 = hook, slide n = soft CTA (`processes/content/content-engine.md` §carousel).
- **Video:** per `agents/Reed/02_build.md` §Production standard v3 — concept-first, grounded/premium tone,
  brand palette, **all text as post overlays (never AI-rendered)**, title card + Eval-Gate end frame.
- **Docs/one-pagers (Pickle):** cream page, indigo headings, one brass rule, generous margins; reads as a
  commissioned document, not a flyer.
- **Client-facing surfaces:** **white-label** — client's brand only, no yourco mark unless co-branded; agents
  described by *function*, never internal names; no public prices; stats sourced ≤18 months (CLAUDE.md
  §External-surface rules).

## 6 · Motion (restraint is the brand — "precise, not animated")
Motion is seasoning, not the meal. The default is a single subtle scroll-reveal; anything louder needs a reason.
- **Scroll-reveal (the one default):** fade + rise — `opacity 0→1`, `translateY(16–24px)→0`. Fire **once** on
  enter (IntersectionObserver, ~−100px margin); never replay on scroll-back.
- **Timing:** 0.6–0.8s; up to 1–1.2s for a hero/cinematic moment. Ease-out — cinematic easing
  `cubic-bezier(.22,1,.36,1)`. If motion feels fast/jerky, lengthen + soften before adding more.
- **Animate `transform` + `opacity` only** — never width/height/top/left/margin (GPU-cheap, no layout thrash).
- **Respect `prefers-reduced-motion: reduce`** — no transitions/reveals, show the final state. Non-negotiable
  (accessibility + the premium bar). *(The live site already honors this — keep it that way.)*
- **Budget:** one reveal per section max; never animate every element (reads cheap/AI). No autoplay carousels,
  no looping bounce, no parallax that warps text.
- **Hero video** (per §5 Video / Reed): slow push-in lives in the file, not CSS; 25–35% `--indigo-deep`
  overlay under any text set over media.

Copy-paste recipe (vanilla — no Motion/Framer/JS-animation library; the stack stays hand-built static per
`decisions/2026-07-05_tool-triage.md`):
```css
@media (prefers-reduced-motion: no-preference){
  .reveal{opacity:0;transform:translateY(20px);
    transition:opacity .7s cubic-bezier(.22,1,.36,1),transform .7s cubic-bezier(.22,1,.36,1)}
  .reveal.in{opacity:1;transform:none}
}
```
```js
const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}}),{rootMargin:'-100px'});
document.querySelectorAll('.reveal').forEach(el=>io.observe(el));
```
*(Discipline distilled from Luke's "Build Premium Sites with AI" — the parameters, not its Next/Motion stack;
triage: `decisions/2026-07-05_tool-triage.md` §Addendum 07-20.)*

## 7 · Hard rules (fail the build if violated)
- Lowercase `yourco` everywhere the mark appears.
- No AI-rendered text in any generated image/video (gibberish rule) — text is always a real overlay.
- No fabricated metrics/testimonials on any surface; numbers real-and-cited or labeled illustrative.
- Oxblood only for its reserved moments; never decorative.
- External bar: premium "$50k-agency" feel — if a surface looks default-Bootstrap or AI-slop, it doesn't ship;
  for hero-grade visuals present 2–3 concrete options before iterating live.

## 8 · How agents load this
Step 0 of any surface-building task: read this file + (for copy on the surface) `brand/writing-rules.md`.
Inject §1 tokens verbatim into new CSS; pick idioms from §4 rather than inventing; check §7 before hand-off.
Changes to this file are Luka's call, logged in `brand/CHANGELOG.md`; if this spec and the live site disagree,
**guidelines → this file → site** is the order of truth (fix downstream, don't fork).
