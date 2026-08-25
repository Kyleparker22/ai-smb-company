# 2026-08-03 — PROPOSAL: rule on italic captions, the gradient ban, and a `--surface` token

**Status: proposed by Luka — awaiting the Founder. Guidelines are not edited until this is ruled.**

## Why this exists
The 2026-07-06 brand audit raised these three questions *inside the audit artifact*, which violates Luka's own rule (proposals go to `/decisions/`, never into an audit). Nothing could act on them, so all three drift patterns are unchanged 30 days later (`loops/brand-audit/2026-08.md` §Structural). This file is the same three questions, filed where they can be ruled.

## 1 · Italic captions and footnotes — permit or ban?
Guidelines §Type: *"No italics for emphasis. Use weight instead."* That plainly bans inline `<i>word</i>` (5 live pages — a real fix either way). It is **silent on small italic captions/footnotes** — `.note`, `.analogy`, `.osb-note`, `.ground`, disclaimer lines (6 live pages).

- **(a)** Permit italic for ≤13px captions/footnotes as a distinct editorial voice — add the carve-out to §Type + DESIGN.md §2.
- **(b)** Confirm the ban is absolute — recolor/resize captions with `--pewter` + smaller size instead.

Pick one so the fix is unambiguous. Note: the new `_concepts/` direction (07-21) uses an italic serif signature (`concept-b.html:323`) — option (b) makes that a rework.

## 2 · Reconcile the gradient rule between the two specs
They disagree, and `DESIGN.md` is downstream of the guidelines (order of truth: guidelines → DESIGN.md → site).

- Guidelines §Never use: **"Gradients"** — flat ban.
- DESIGN.md §1 Never: **"AI-purple/electric-blue gradients"** — tech-color only.

Every gradient on a live page is a hairline brass/cream fade-to-transparent used as a functional device: `timeline-48h.html:38`, `build-your-os.html:72`, `index.html:97-98,338`. Not the animated color-wash the ban was written against.

- **(a)** Amend guidelines §Never use to *"**Decorative / color-wash gradients** (esp. AI-purple / electric-blue). Hairline brass or cream fade-to-transparent as a functional mask/rule is permitted"* — matches DESIGN.md, live pages become compliant.
- **(b)** Uphold the flat ban — the 4 live instances become fixes, and `_concepts/concept-c.html:57` (radial-gradient hero glow) is a rework.

## 3 · Add a `--surface` warm-white token to DESIGN.md §1
Pure white `#fff` is the card surface on 14 live pages because *there is no sanctioned alternative to reach for* — the guidelines say "use Cream Linen," but cream is the page background, so a card on cream needs a lighter tone. `instant-employee.html:71` already improvises the right answer (`#fbfaf7`).

**Proposal:** add `--surface:#FBFAF7;` to the DESIGN.md `:root` block as the standard card/input/raised-surface fill, then sweep `#fff` → `var(--surface)` site-wide.

This one is a DESIGN.md addition, which is Luka's call under the eval — filed here for visibility rather than approval, and held until #1 and #2 are ruled so the sweep happens once.

## If approved
Guidelines version bumps to v0.6 with a `brand/CHANGELOG.md` entry referencing this file; DESIGN.md updated in the same commit; Webb runs the site sweep (change-one-sweep-all).
