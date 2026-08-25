# Brand Changelog

Every change to `/brand/v0/brand-guidelines.md` (or successor versions) lands here. Dated, with reason and the Founder's approval reference.

## 2026-08-23 — DESIGN.md wired in, and a token flowed back upstream

Not a guideline change. A **wiring** change, from a review of the whole folder.

**DESIGN.md was an orphan.** Its own §8 declares *"Step 0 of any surface-building task: read this
file"* — and **no loop prompt referenced it**, including `brand-audit`, Luka's own monthly loop, which
read only `brand-guidelines.md` and this changelog. So a surface could violate every component idiom in
§4 and every hard rule in §7 and still pass the brand audit. The only thing loading it was the
`visual-brand-qa` skill.

Now read by `brand-audit` (Luka — audit against tokens AND narrative) and `content` (Katie — anything
that becomes a rendered visual). The set is deliberately small: over-wiring a check is noise, not safety.

**`#1C2240` (raised dark surface) travelled the wrong way.** It lived in DESIGN.md §1 and in four
shipped surfaces — the app shell, the CRM, and both partner walkthrough pages — while these guidelines,
which §8 names as the source of truth, had never heard of it. Added under Primary. All 10 spec tokens
now exist upstream.

**Both are now invariant-checked** (`runtime/consistency-check.py`), and the check was proven by
breaking it in each direction rather than by passing.

Approval: the Founder, 2026-08-23 (review of `brand/`).

## v0 — 2026-06-07
**Initial brand standard published.** Direction set by the Founder: sleek, stylish, not crazy; attention-catching by counter-positioning; psychological/emotional weight via colors and themes.

Key choices:
- Counter-positioned against AI-startup palette (bright purples, electric blues) with a deep Midnight Indigo + Cream Linen + Brass system
- Lowercase wordmark `yourco` with a brass square-dot on the *i* as the signature design element
- Atelier metaphor — Milanese tailor's workshop, not startup loft
- Italian/Latin nods sparingly for moments of emphasis (literal: *yourco* = "I learn")
- Voice rules formalize the Founder's existing posture (concise, direct, confident through demonstration)
- Reserved Oxblood for premium moments only

Approval: the Founder directed the build in-session; this file constitutes the first version of record.
Decision log: `decisions/2026-06-07_luka-brand-agent.md`.

## 2026-07-05 — DESIGN.md added (machine-readable design spec)
- New `brand/DESIGN.md`: the agent-loadable constraint layer over the v0 guidelines — live site tokens (`:root`),
  type system (Fraunces display / system-sans body / JetBrains Mono), 10 component idioms from the staged site,
  surface recipes (web/deck/video/docs/client-facing), hard rules (lowercase mark, no AI-rendered text, no
  fabricated numbers, oxblood reserved, premium bar), and the order of truth (guidelines → DESIGN.md → site).
- Pattern stolen from nexu-io/open-design's brand `DESIGN.md` systems — the design-side twin of the 2026-06-22
  Voice-DNA move (`writing-rules.md` as an injectable constraint block).
- Approval: the Founder directed in-session ("yes draft it now"). Triage verdict + provenance:
  `decisions/2026-07-05_tool-triage.md` §Addendum (open-design + agent-reach).

## DESIGN.md §6 Motion — 2026-07-20
**Added a Motion section to `brand/DESIGN.md`** (new §6; Hard rules → §7, How agents load → §8; no external refs broken — verified only §1/§2 are cited elsewhere). Codifies the house motion discipline as a reusable spec + copy-paste vanilla recipe (IntersectionObserver + CSS): single subtle scroll-reveal, `translateY(16–24px)` + opacity, 0.6–0.8s (1–1.2s cinematic), easing `cubic-bezier(.22,1,.36,1)`, transform/opacity only, `prefers-reduced-motion` honored, one reveal per section. Reinforces the brand's "precise, not animated" restraint; **no animation library** — the stack stays hand-built static.
- Reason: distilled the *parameters* (not the Next/Motion/Vercel stack) from Luke's "Build Premium Sites with AI" guide; every surface Webb/Luka/Kimi builds now inherits consistent, accessible motion instead of re-deriving it.
- Approval: the Founder directed in-session ("yes"). Triage verdict + provenance: `decisions/2026-07-05_tool-triage.md` §Addendum 2026-07-20 (Build Premium Sites with AI).
