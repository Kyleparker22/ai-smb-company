# YourCo — Brand Guidelines v0.2

*Maintained by Luka, YourCo's Brand Custodian.*
*Current version: v0.5 (2026-06-23) — see Changelog at the bottom.*

*The brand mark is described below in "The wordmark (locked v0.2)." The actual rendered wordmark asset lives in the Founder's Canva brand kit (kit ID `kAHMCKMxZN4`).*

This document is opinionated on purpose. v0 is meant to set a stake — a direction the company can argue with, then sharpen. Disagreements with it should be logged in `/decisions/` and end in either an update here or a written reaffirmation.

---

## Positioning, in one paragraph

YourCo is a boutique AI-employee implementation business. We deliver named digital employees who do real work inside a client's tenant within 48 hours — held to reliability, eval, and approval standards no one else delivers. The brand mirrors what we sell: precision, calm, executive-grade trust. Not the AI hype wave. Not generic consulting. A premium atelier that ships working agents.

The brand's job is to communicate *"this is built well"* before a single word is read.

---

## The emotional palette

What YourCo should feel like when an executive encounters it for the first time:

- **Calm** — the antidote to AI-category noise. Confident silence.
- **Considered** — every detail looks intentional. Nothing accidental.
- **Discreet** — we don't shout. Executive trust is earned by understatement.
- **Warm** — humans on the other side. Not cold tech.
- **Premium** — quality of craft. Not luxury-for-show.

If YourCo had a physical form, it would be a Milanese tailor's atelier outfitted with precision instruments. Small, deliberate, expensive without being loud. Not a startup loft. Not a glass office tower.

This emotional posture is the brand's competitive edge. Every other AI vendor is screaming; YourCo is the one in the room not raising its voice. That's what gets attention — by contrast.

---

## Color system

### Primary — Midnight Indigo
**`#161B33`** · darker context: **`#0F1226`**

- Use for: primary brand color, dark backgrounds, headers, the wordmark on cream surfaces
- Conveys: trust, depth, considered judgment, executive-grade
- Why this works: counter-positioned against bright AI-startup palettes. Almost-black but warm — never pure black. It reads as "decided" rather than "default."

### Secondary — Cream Linen
**`#F4EFE6`** · hover/secondary: **`#E8E1D3`**

- Use for: page backgrounds, body content, breathing room, contrast against indigo
- Conveys: precision, calm, paper-like craft
- Why this works: warmer than tech-white. Suggests real things, made with care.
- **Raised dark surface — `#1C2240`:** one step up from Midnight Indigo, for panels and cards that sit *on* a dark ground without becoming a second background. In live use across HQ, the CRM, the app shell and the partner walkthrough pages. *(Flowed upstream 2026-08-23: this token existed in `DESIGN.md` and in four shipped surfaces while the guidelines — the source of truth per DESIGN.md §8's guidelines → spec → site order — had never heard of it. Tokens are supposed to travel down, not up.)*
- **Section band — Warm Parchment `#EAE1CD`:** a slightly deeper, warmer cream for the *alternate* full-bleed band (and footer surfaces), so a page of stacked cream sections doesn't run together. Use as the every-other band on light pages; **not** for body text. Deepened from the original `#EFE8DA` on 2026-06-23 so the alternation actually reads. (`#E8E1D3` remains the hover / interactive-secondary cream.)

### Accent — Brass
**`#B8965A`** · darker: **`#9C7F4A`** · lighter highlights: **`#D4B27A`**

- Use for: small details — the dot on the "i" in the wordmark, thin rules, call-to-action accents, exec-grade emphasis
- Conveys: value, craftsmanship, lived-in quality
- Why this works: a warm metallic that's distinctly not tech-blue or AI-purple. Brass reads as "made by someone who knew what they were doing." It avoids gold-flash (cheap); brass is older, more sophisticated, more lived-in.
- **Use sparingly.** Brass earns its presence through scarcity. A single brass detail per surface is usually right.

### Reserved — Oxblood
**`#6B1E29`**

- Use for: premium moments only. Eval-pass signals. "Live" status on a digital employee's profile. The signature line on a contract.
- Why this works: a deep red that doesn't read as warning or error. Reads as premium leather chair.

### Neutrals
- **Slate Warm — `#2A2D3D`** — deep secondary text, charts, system status
- **Pewter — `#6E7180`** — body text on cream, metadata, secondary UI
- **Mist — `#C8C7C2`** — disabled, dividers, very light surface

### Never use
- Bright tech blues (`#0066FF` and family) — startup energy
- Neon greens, neon purples, magenta — AI hype energy
- Pure black `#000000` — too cold; use Midnight Indigo
- Pure white `#FFFFFF` — too cold; use Cream Linen
- Gradients — YourCo is precise, not animated
- Drop shadows on type — YourCo is paper, not glass

---

## Typography

### Recommended pairing (paid type)
- **Wordmark + headlines:** *Söhne* (Klim Type Foundry) — a precise grotesque with warmth. Reads as "expensive software made with care."
- **Body & long-form:** *Söhne Buch* — or *Tiempos Text* (Klim Type Foundry) when warmth in long-form essays is needed
- **Mono (eval criteria, system status, code):** *Söhne Mono* or *JetBrains Mono*

### Free alternative pairing (use until budget supports paid type)
- **Wordmark + sans UI/labels:** *Inter* (Google Fonts), medium weight — or the native system-sans stack (the live default).
- **Display headlines:** *Fraunces* — the editorial serif (see "Display headlines" below; ratified v0.5). *Supersedes the former "Inter for headlines."*
- **Body:** the system-sans stack / *Inter* regular for short copy; *Source Serif Pro* for long-form.
- **Mono:** *JetBrains Mono*

### Display headlines — editorial serif (ratified 2026-06-23, v0.5)
The live site sets **headlines in *Fraunces*** (Google Fonts, variable opsz/wght) over the system-sans body — a serif-display + sans-body pairing that reads *commissioned / atelier* and counter-positions against the geometric-sans AI-startup cohort. This is the brand's headline voice on the web.
- **Scope:** display only — `h1`, section heads, pull quotes, big stat numerals. **Not** body, small labels, or the **wordmark** (the mark stays in the locked humanist sans — the serif is a *voice*, never the logo).
- **Setting:** ~weight 560, optical sizing on, tracking −1% to −2% (per Type rules).
- **Easily swapped** (one `@import` + a font-family change) if a calmer serif (*Spectral* / *Newsreader*) is later preferred; a future paid upgrade can move to a licensed editorial serif (and/or pair the serif display with *Söhne* for body/UI).

### Type rules
- **Lowercase wordmark.** The brand is `yourco` — not `YOURCO` or `YourCo`. Lowercase signals craft and approachability. (Stripe, Notion, Linear — the modern premium-software cohort all do this.)
- **Tight letter-spacing on display.** -1% to -2% on headlines. Premium feel.
- **Generous body line-height.** 1.5 to 1.7. Breathing room is part of the brand.
- **No all-caps body.** All-caps reserved for very small labels (≤10pt), in brass, used sparingly.
- **No italics for emphasis.** Use weight (medium or semibold) instead.
- **Serif display, sans body.** Display/headlines = the editorial serif (*Fraunces*); body, UI, labels, and the wordmark = sans. Never set body in the serif, and never set the wordmark in the serif.

---

## The wordmark (locked v0.2 — 2026-06-08)

Primary: **yourco** set in a humanist sans (Söhne Buch, Cabinet Grotesk Medium, or Manrope SemiBold), lowercase, in **Cream Linen `#F4EFE6`** on a **Midnight Indigo `#161B33`** background.

### The signature lockup — "Eval Gate" rules

The locked wordmark is the **flanking brass-rules lockup**:

```
.____  yourco  ____.
```

- **The wordmark:** lowercase `yourco`, Cream Linen `#F4EFE6`, humanist sans semibold/medium weight, centered
- **Two horizontal thin brass rules** flank the wordmark (one left, one right) — color Brass `#B8965A`, hairline thickness, sized to roughly match the wordmark's width on each side
- **Brass diamonds** terminate each rule at the outer end — small filled square rotated 45° (diamond orientation), Brass `#B8965A`. These diamonds preserve the original v0 square-dot signature element, now relocated to the rule terminals.
- Generous breathing room — at least the full cap-height on all sides of the entire lockup

### Why this lockup works
- **The brass rules execute the Eval Gate motif directly into the wordmark.** "Brass thin rules as section dividers... suggests checkpoint passed" — now embedded in the brand mark itself.
- **The brass diamonds preserve the v0 square-dot element.** The original signature detail is conserved, just relocated from the dot of the "i" to the rule terminals. Continuity without literal repetition.
- **Restraint anchors the mark.** No tagline, no icon, no ornament beyond the rules and diamonds. The composition itself is the design.

### Lockup variations
- **`.____ yourco ____.`** — primary locked wordmark (Eval Gate lockup, this is the canonical mark)
- **`yourco`** — minimal lockup, no rules (small sizes, favicon-adjacent uses where the rules would not read clearly)
- **`yourco. boutique ai implementation.`** — primary tagline lockup
- **`yourco. named employees. 48-hour go-live.`** — descriptor lockup
- **`— yourco, in atelier`** — signature line for warm/personal surfaces
- **`We learn your business. AI does the work.`** — primary tagline for footers, proposals, and marketing (see Primary tagline section)

### Clear space
Minimum clear space around the lockup = half the cap-height of "yourco" on all sides (measured from the outer edge of the brass rules/diamonds, not from the wordmark itself). Never crowd it. The wordmark breathes; that's its strength.

### Inverse / light-surface treatment
For Cream Linen surfaces (light backgrounds):
- Wordmark: Midnight Indigo `#161B33` (instead of Cream)
- Brass rules and diamonds: unchanged — Brass `#B8965A`
- All proportions identical

---

## Themes & motifs

### The Atelier
YourCo is positioned as a *workshop*, not a factory. Imagery should evoke:
- Precision tools (rulers, brass instruments, watchmaker's loupes)
- Working surfaces (wood, leather, paper, linen)
- Considered light (soft, warm, never fluorescent)
- Quiet rooms

When choosing imagery: lean atelier. Pinned fabric over neon-circuit. Brass weights over chrome. Hands at work over screens.

### The Roster
YourCo's digital employees have names. The brand treats each as a small portrait card with a brass nameplate. The team page should feel like the staff page of a Milanese tailor's shop — not the "Meet the AI" page of a SaaS startup. Subtle individuality. Real names. Real roles.

### The Latin Nod
"YourCo" is Italian for *I learn*. Use Italian or Latin phrasing sparingly, for moments of emphasis. Never gimmicky — once per surface at most.
- **yourco** itself (always lowercase)
- **atelier** instead of *office* or *studio*
- **in service** or **live** instead of *active*
- **— yourco, in atelier** as a closing signature on essays and exec readouts
- *(the former* **a learning, I employ.** *wordplay line is retired; the primary tagline is now* **We learn your business. AI does the work.** *— see Primary tagline)*

### Primary tagline — *We learn your business. AI does the work.* (locked 2026-06-10, v0.3)

The brand's primary line. Two beats: **we learn your business** (custom-fit per client — and the "yourco = *I learn*" meaning, stated plainly, no acronym gimmick) and **AI does the work** (the outcome gets done). Sentence case; a period after each beat. On cream surfaces with brass available, the final period may be **brass `#B8965A`** (the small craft moment).

**Where it earns its place:**
- Website + landing-page footers (the seal spot)
- Email signature footer (after the Founder's contact lines)
- Close of a proposal, deck, or exec readout
- LinkedIn company bio one-liner (after the functional intro)

**Where it does NOT belong:**
- Above-the-fold hero slots — that's the functional value line (*Named digital employees. Live in 48 hours.*)
- Cold-email *subject* lines, ad headlines, SMS

**Conscious tradeoff (logged):** "AI does the work" re-centers the technology a notch versus the "employees, not tools" lane, and competes in a crowded space. Kept anyway for top-of-funnel clarity. The "employee, not a tool" differentiation still leads in body copy and the hero. Decision: `/decisions/2026-06-10_brand-tagline.md`.

**Retired:** *"a learning, I employ."* (v0.1 — the AI = *A-learning* + *I-employ* wordplay) read as too clever; retired 2026-06-10, on record only. The warm essay signature *"— yourco, in atelier"* is unaffected and still optional.

### Approved campaign lines (use sparingly — at most one per surface)
Sanctioned marketing hooks for Reilly (outbound), Katie (content), Webb (web), Reed (video). Never crowd the primary tagline.
- **The future doesn't clock in.** — the always-on angle (the employee never clocks in or out).
- **Hire once. Scale forever.** — the leverage angle (one hire, scaled without re-hiring).

### The Eval Gate
YourCo's moat is proving the work was done. Visual motif: a subtle threshold. **Brass thin rules** as section dividers in decks, dashboards, exec readouts. The rule suggests *checkpoint passed* — a quiet way to remind the reader that there's discipline behind the words.

---

## Voice & tone

> This section is the positioning layer (what to sound like). The sentence-craft layer — the banned phrases, the
> em-dash cap, the slop→human rewrites — lives in `brand/writing-rules.md`. Reilly, Katie, and Melanie read that
> at Step 0. Keep the two in sync; don't duplicate the rules here.

### Always
- **Concise.** Short sentences. Cut adverbs. Reading time matters.
- **Direct.** What's true. What we'll do. What we won't.
- **Confident through demonstration, not declaration.** *"Live in 48 hours"* is stronger than *"we're the fastest."*
- **Specific.** Real names. Real numbers. Real outcomes.
- **Warm.** There are humans on the other side.
- **Lowercase wordmark; sentence-case headlines.**

### Never
- AI buzzword salad: *leverage, synergy, harness the power of, unlock, revolutionize, transform, 10x, supercharge, cutting-edge*
- Hype emoji (🚀💯🔥)
- Vague claims without evidence (*enterprise-grade* without saying what makes it so)
- All-caps for emphasis
- Stock corporate (*solutions, platform, ecosystem*)
- Hedging on the moat (*just, simply, happens to*)

### Sentence patterns that work
- "Named [Name]. Lives in your tenant. Doing [outcome] within 48 hours."
- "We don't sell tools. We deliver employees."
- "Reliability you can prove. Eval gates. Watchdogs. Approvals. Live."
- "YourCo — Italian for *I learn*. Our agents do the same."

---

## Application examples (v0)

### LinkedIn header
- Background: Midnight Indigo `#161B33`
- Wordmark: **yourco** in Cream, brass square-dot on the *i*, centered-left
- One-line right of wordmark, Cream, small: *boutique ai employee implementation*
- No graphics. No glow effects. No gradients. The restraint is the point.

### Email signature
```
the Founder
yourco · founder
founder@yourco.example.com · yourco.com
```
- Set in Söhne / Inter Regular, Pewter `#6E7180`
- Brass middle-dot separators
- Three lines. Always three.

### Deck cover slide
- Full-bleed Midnight Indigo background
- Cream wordmark **yourco** top-left, small (~24pt)
- Document title large in Cream, sentence-case, generous line-height
- Single brass thin rule under the title
- Date and client name in small Pewter type, bottom-right
- No subtitle gradient. No tagline crowding the cover.

### Business card
- Front: Cream Linen card, Midnight Indigo wordmark centered, brass foil square-dot on the *i*
- Back: Midnight Indigo, name + title + email in Cream
- Heavy stock (32pt+). The card should feel expensive in hand.
- One detail (brass foil), one indulgence (heavy stock). Nothing else.

### Web (when site exists)
- Top section: Midnight Indigo. Below: Cream Linen.
- Söhne (or Inter) throughout.
- Brass thin rules as section dividers.
- A single hero line. No multi-column feature grid.
- Show the team (the agent roster). Show one outcome. Show how to talk to us. Nothing else.

---

## Sample first-touch copy

### Hero line options
- **A:** Named digital employees. Live in 48 hours. Held to evals you can read.
- **B:** We don't sell agents. We deliver employees who do the work.
- **C:** Boutique AI implementation. Built like an atelier, run like an operations team.

### Sub-line under hero
YourCo absorbs the tokens, the eval risk, and the watchdog cycle. The client just gets an outcome.

### Closing signature on essays and exec readouts
*— yourco, in atelier* (warm/personal essays)

— or, the primary tagline —

**We learn your business. AI does the work.** (analytical readouts, proposals, footers, marketing)

---

## Brand version & changelog

This is **v0.1**, June 2026. Significant changes get a `/decisions/` entry and a version bump (v0.1, v1.0). Drift is tracked monthly by Luka via the brand-audit loop.

### Changelog
- **v0** (2026-06-07) — initial brand system locked: Midnight Indigo + Cream Linen + Brass; Inter / Söhne typography; lowercase wordmark with brass square-dot signature element; voice + tone rules; atelier theming; `— yourco, in atelier` signature line.
- **v0.1** (2026-06-08) — Signature line `a learning, I employ.` added (see "The Signature Line" section). Decision log: `/decisions/2026-06-08_brand-signature-line.md`. No palette or typography changes.
- **v0.2** (2026-06-08) — Wordmark lockup locked: cream `yourco` flanked by two brass thin rules terminating in brass diamonds (the "Eval Gate lockup"). Original brass square-dot on the "i" replaced by brass diamonds at the rule terminals — continuity of the signature element, relocated. Decision log: `/decisions/2026-06-08_brand-wordmark-v02.md`.
- **v0.3** (2026-06-10) — **Primary tagline locked: "We learn your business. AI does the work."** Retired the v0.1 signature line "a learning, I employ." (too clever). Added an approved campaign-line library ("The future doesn't clock in." / "Hire once. Scale forever."). Decision log: `/decisions/2026-06-10_brand-tagline.md` (supersedes `/decisions/2026-06-08_brand-signature-line.md`).
- **v0.4** (2026-06-23) — **Section-band tone added: Warm Parchment `#EAE1CD`** (deepened from `#EFE8DA`) to break up runs of cream full-bleed sections on the site; applied site-wide to the alternate band + footer surfaces. A *derived* cream variant for layout rhythm, not a new core color — palette identity (indigo · cream · brass · oxblood) unchanged. the Founder-approved on review. Records: Webb `agents/webb/pages/2026-06-23_cream-breakup-pass.md`; Luka `agents/luka/reviews/2026-06-23_parchment-tone.md`.
- **v0.5** (2026-06-23) — **Display typeface ratified: *Fraunces*** (editorial serif) for headlines, over the system-sans body — a serif-display + sans-body web pairing. Supersedes the prior "Inter for headlines" fallback; the wordmark stays sans. Added a "Display headlines" subsection + a "serif display, sans body" type rule. the Founder-approved. Closes the pending item from the 2026-06-22 premium pass. Records: Luka `agents/luka/reviews/2026-06-22_premium-polish-typeface.md`; Webb `agents/webb/pages/2026-06-22_premium-polish-pass.md`.

The guidelines are a living document. They argue back. Bring evidence.
