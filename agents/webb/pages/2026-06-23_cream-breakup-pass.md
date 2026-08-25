# Breaking up the cream — section-rhythm pass (2026-06-23)

> **Owner: Webb.** the Founder: "some of the pages have too much cream color all run together." Fix applied across the staged `yourco-site-v2` site. Committed `02119b8`, on `origin/main`. Staged/internal — not deployed.

## Root cause
The full-bleed `.tile` pages stacked cream on cream and read as one flat field, for two reasons:
1. **The parchment alternate band was nearly identical to cream** (`#EFE8DA` vs `#F4EFE6`), so "alternating" sections didn't visibly alternate.
2. **Section boundaries were a near-invisible 1px hairline** — no real separation.

## Fixes
- **Deepened the parchment band: `--parchment` `#EFE8DA → #EAE1CD`** (a warmer light sand), applied **site-wide** (`site.css` + all 15 inline-styled pages, via a token replace). Now cream↔parchment alternation reads with a clear step; footers (parchment) also separate from the cream body. *(Brand-tone change — see Luka, below.)*
- **Soft "stacked-paper" separation** between same-tone light tiles: replaced the faint hairline seam with a subtle top inset-shadow (`box-shadow:inset 0 17px 28px -25px rgba(22,27,51,.5)`) in `site.css` + `index.html`'s inline copy. Resets to none at dark-tile boundaries (the colour change does the work there).
- **positioning.html** carried a three-cream run (hero → method → steps); made the **method** section `parchment` → clean `cream · parchment · cream · parchment · cream · dark` rhythm.

## Not touched (by design)
The **content pages** (`reliability`, `objections`, `compare`, `glass-box`, `manifesto`, `day-in-the-life`, `timeline-48h`, `eval-gated-seal`) already use **white cards on cream**, which breaks up the field on its own — left as-is.

## Verification
positioning + home render with clear tonal rhythm; deeper parchment confirmed (`rgb(234,225,205)`); 0 console errors.

## Open levers (offered, not done)
Dial parchment warmer/lighter; drop a dark indigo band into a long page for stronger punctuation; brass "gate" dividers between sections; panel/card treatment on a key section. Also: the same-tone inset-shadow seam is currently moot on these pages (everything alternates now) — it's a safety net for future same-tone runs.

## Cross-refs
- Luka brand note: `agents/luka/reviews/2026-06-23_parchment-tone.md`
- Brand guidelines updated (v0.4): `brand/v0/brand-guidelines.md` (Cream Linen → section band)
