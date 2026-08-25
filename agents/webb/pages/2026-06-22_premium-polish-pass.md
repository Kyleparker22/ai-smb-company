# Premium polish pass — the "$50k feel" (2026-06-22)

> **Owner: Webb.** Sitewide craft pass on the staged `yourco-site-v2` site. Goal (the Founder): make it *feel* commissioned/expensive, clean up formatting, add standout moments — within Luka's quiet-luxury watch-notes (brass scarcity + motion restraint). Staged/internal only — not deployed (launch-gate). Committed in `d91a7e2` (swept into a runtime auto-commit), on `origin/main`.

## What shipped (four buckets, all approved by the Founder)

**① Editorial type voice.** Introduced a display serif — **Fraunces** (Google Fonts, variable opsz/wght) — on headlines (`h1`, `h2.sec`, `.close h2`, `.pullquote`, `.value h3`, `.ptier h3`, `.audit-card h3`). Body/UI stay system-sans (the editorial pairing). **The locked wordmark is untouched.** This is the single biggest jump in "commissioned" feel. ⚠️ **Brand-level addition — needs Luka/the Founder ratification** into `brand/v0/brand-guidelines.md` (see the Luka review). Easily swappable (one `@import` + the font-family list) if a calmer face (e.g. Spectral) is preferred.

**② Global polish.**
- *Material grain* — a faint film-grain `body::after` overlay (on-brand "paper-like craft"), ~1.5% effective, invisible on text.
- *Tactility* — resting shadow + hover-lift + brass edge on `.card`/`.ptier`/`.demo-frame`; an animated brass underline on nav links; a soft shadow-lift on `.pill`.
- *Section rhythm* — a soft seam between consecutive light tiles.
- *Scroll-reveal* — pure-CSS scroll-driven (`animation-timeline: view()`); each block reveals as it enters (naturally staggered). Reduced-motion and non-supporting browsers degrade to static (current behavior).

**③ Signature moment.** An animated **approval-gate** on the home moat section: `Awaiting you → ✓ Approved → ↗ Sent`, looping, pure CSS. Demonstrates the moat ("nothing external sends without a human say-so") *in motion*, and earns the brand's reserved **oxblood** for the hold state.

**④ Formatting cleanup.** `demos.html`: "see a digital employee work" → OS-first "see a piece of your system work" (title/og/h1); editorial headline applied.

## Architecture finding (important)
The site is **not** on a single stylesheet. Only **6 pages link `site.css`** (about, audit, audit-intake, build-your-os, positioning, pricing). The other **15 — including the flagship `index.html` — carry duplicated inline `<style>` blocks.** So the `site.css` changes only reached 6 pages; the polish + Fraunces had to be **injected into each standalone page's inline `<style>`** (idempotent script, one `@import` + one marked `/* PREMIUM POLISH */` block per page). All 21 pages now carry the pass.

**Deploy-time debt (recommended next):** consolidate all pages onto one shared `site.css` (and a single shared nav/footer) — already flagged in `site-ia.md` rollout status. Until then, any future global change must be applied to both `site.css` *and* the 15 inline blocks.

## Verification
Real home + `try-to-break-it` render with the new type, grain, and (home) approval-gate; **0 console errors**; injection idempotent (1 import + 1 polish block/page). Motion (hover, scroll-reveal, gate loop) reads live only — the preview tab backgrounds animation, and its eval context has a zero-size viewport (can't scroll-screenshot mid-page).

## Pending
- ✅ **DONE (2026-06-23) — Fraunces ratified + codified** in `brand/v0/brand-guidelines.md` (Typography → "Display headlines," v0.5). the Founder approved. Review: `agents/luka/reviews/2026-06-22_premium-polish-typeface.md`.
- **Self-host the font** before launch (currently Google Fonts CDN) — same note as any external dependency.
- **Stylesheet consolidation** (above).
