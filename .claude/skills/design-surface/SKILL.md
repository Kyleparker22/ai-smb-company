---
name: design-surface
description: Design a visual surface before you build it — a page, dashboard, one-pager, deck, client console, demo. Use whenever you are about to write HTML/CSS or lay out a document that a human will look at. Covers the design-time decisions; `visual-brand-qa` checks the result afterwards.
---

# design-surface — decide the design before writing the CSS

## Canonical doc — read it, don't remember it
**`brand/DESIGN.md` is the source of truth for palette, type, and the brass rule. Re-read it every
run; never trust this skill's memory of it, and never copy its values into another file.** A palette
duplicated into a second document is the repo's #1 failure mode (change-one-sweep-all), and it has
already cost real time this year. This skill covers *how to decide*; DESIGN.md holds *what the values
are*.

## When
About to produce anything a person will look at: a site page, an HQ panel, a client console, a
one-pager, an audit report, a deck, a demo. **NOT** for checking a finished visual — that's
`visual-brand-qa`, which runs after. **NOT** for choosing a new brand direction — that's the Founder's call.

## Step 1 — calibrate the treatment (the decision most often skipped)
Design is not optional; the **treatment** is what varies. Name which one, in one line, before building:

- **Utilitarian** — a plan, memo, internal dashboard, cost ledger, runbook. Real typographic
  hierarchy, considered spacing, proper palette. **No giant hero, flourishes limited.** Most internal
  yourco surfaces are this. HQ is this.
- **Editorial** — the staged site, a client-facing demo, a proposal, anything carrying the "$50k
  agency" external bar. Opinionated calls; one real aesthetic risk where it serves the work.

Getting this wrong in either direction is the common failure: an over-designed internal tool wastes
effort and reads as unserious, and an under-designed client surface fails yourco's external bar.

## Step 2 — write the design plan before the code
Three lines. Do not skip to CSS.
- **Color** — 4–6 named values, taken from `brand/DESIGN.md`. Neutrals are *chosen*, not inherited: a
  pure mid-grey reads as unconsidered; bias it slightly toward the accent.
- **Type** — 2+ roles (display / body / utility-for-data). yourco's faces are in DESIGN.md.
- **Layout** — one or two sentences on the concept.

Then build from the plan, deriving every color and type decision from it.

## Step 3 — the technical rules that actually bite
- **Both themes, token-level.** Three viewer states, not two: explicit `data-theme="dark"` /
  `"light"`, and the default *unstamped* state where only `prefers-color-scheme` applies. Define the
  full palette on bare `:root`; redefine **only tokens** under
  `@media (prefers-color-scheme: dark){:root:not([data-theme="light"])}` and again under
  `:root[data-theme="dark"]`. **A color whose only definition sits inside a media or `[data-theme]`
  block never applies in the unstamped state** — that is the classic unreadable-page bug. `body` must
  paint an explicit token background; a transparent body borrows the host's ground.
- **Fonts.** Google Fonts is the only external host that loads under the artifact CSP; anything else
  must be inlined as a `@font-face` data URI or it silently falls back. Always declare a real fallback
  stack. **Verify a token, not a rule from the page's own inline `<style>`** — that is how you catch a
  silent font failure (`.claude/skills/show-surface/` §gotchas).
- **Layout does the spacing** — flex/grid with `gap`, not per-element margins that collapse or double.
  Wide content (tables, code, diagrams) gets its own `overflow-x: auto` container so the body never
  scrolls sideways. `font-variant-numeric: tabular-nums` wherever digits column up.
- **Watch selector specificity** — a type-based `.section` fighting an element-based `.cta` over
  padding silently undoes your spacing.
- **Structure must encode something true.** Numbered markers (01/02/03) only when the content really
  is a sequence. Eyebrows, dividers and labels are information, not decoration.
- **When it's a UI, not a document** — dashboards are scanned, not read. Summary before detail; encode
  state in *form* as well as number (pill, chip, severity stripe). Semantic color (good/warning/
  critical) is separate from the accent and does not count as your brass moment.
- **A control's edge is not a divider, and 3:1 is the bar.** WCAG needs **3:1 for UI components** —
  the border that makes an input look like an input. Divider tokens (`--line`, `--line-soft`,
  `--hairline`) are *correctly* faint at ~1.2–1.6:1 and must never be a control's border; use a
  dedicated control token (HQ's is `--control-edge`). A sweep of all 12 HQ doors on 2026-08-24 found
  **eight control types failing, every one from this single cause**, including a Board select at 109
  instances. **A state variant needs its own check** — a chip signalling through colour should use
  `border-color: currentColor`, so the semantic colour carries the edge and any state added later
  inherits a passing border for free.
- **The control with no styling at all is the one you will not notice.** That same sweep found a
  button with *no author rule*: native grey, Arial, padding zeroed by the `*` reset, and inherited
  cream text at **contrast 1.00 — an invisible label**. Nothing about an unstyled control looks
  deliberate enough to question, so check that every interactive element matched a rule you wrote.
- **Measure, don't look.** Contrast is arithmetic, and the browser will tell you: composite the
  colour over its real backdrop and compute the ratio. Two calls during that sweep looked wrong and
  measured fine (14.95:1), and one looked fine and measured 1.44:1.

## Step 4 — the yourco rules that override everything above
These are not style preferences; violating one is a real error.
- **No agent names on any external surface** — describe by function.
- **No prices on the public site** — Polo owns the bands; prices live in proposals.
- **Client-facing surfaces are white-label** — the client's brand only, no yourco mark unless the
  engagement co-brands. This bit us on Sample Product.
- **Public stats sourced from the last 12–18 months**, cited.
- **No fabricated proof** — no invented metrics, testimonials, logos, or endorsement. Pre-revenue means
  outcomes are stated qualitatively.
- **Real content, never lorem.** A placeholder that ships is a fabricated claim about a real client.
- Everything external stays behind the **launch-gate**.

## Step 5 — hand off
Register any new local surface in `.claude/launch.json` and verify it responds *before* sharing a link
(`.claude/skills/show-surface/`). Then run `visual-brand-qa` on the result.

## Gotchas
- **Copying DESIGN.md's values into your file.** The one thing this skill forbids outright. Reference,
  don't restate.
- **⚠️ yourco's palette sits inside a known AI-default cluster.** Warm cream + serif display + warm
  accent is *specifically* the combination a trained eye reads as machine-generated. yourco's cream is
  `#F4EFE6`, the display face is a serif, the accent is brass. **The brand is a deliberate, ratified
  choice and it wins** — a pinned direction always beats a generic guideline. But know that the
  differentiation has to come from *execution*: the indigo primary, oxblood reserved for signature
  moments, the parchment band, and disciplined use of the single brass moment. Reaching for the same
  cream-and-serif with none of that discipline produces the cliché, not the brand.
- **Over-designing an internal tool.** HQ, the CRM, the playground and the prototypes are utilitarian.
  Effort there belongs in information design, not hero treatments.
- **Designing blind.** If the browser pane is hidden, screenshots return blank while the DOM still
  answers — measure (`clientWidth`, bounding boxes, computed tokens) instead of looking, and say so
  rather than claiming a visual check you did not perform.

## Related
`visual-brand-qa` (the after-the-fact check) · `show-surface` (getting it on screen) ·
`brand/DESIGN.md` (the values) · `brand/writing-rules.md` (copy is design material — the em-dash cap
and the banned-phrase list apply to anything you write into a surface).
