# Home — hero brain visual + footer fix (2026-06-22)

> **Owner: Webb.** Change record for `agents/webb/pages/yourco-site-v2/index.html`. Staged/internal only — not deployed (launch-gate; `processes/launch-runbook.md`). Committed `28acb81`, on `origin/main`.

## What changed

### 1. Hero visual — empty right column → living brain
The hero's right column was empty space. It now holds a **brain visual** that fills it and signals "yourco = *I learn* / intelligence."

Iteration path (for the record, so we don't re-litigate):
- Hand-coded canvas brain → read as cheap ("looks like $5, want $50k").
- AI-generated realistic brain still (Higgsfield `nano_banana_pro`) → `remove_background` → transparent cutout `brain.png`. This is the **painted illustration** we kept.
- Tried a **true 3D mesh** (`image_to_3d` → `.glb` + `<model-viewer>`, recolored brass). the Founder preferred the painted 2.5D look — the mesh lost the illustration. Reverted; `brain.glb` deleted.
- **Final = the 2.5D illustration made genuinely 3D** via a live **WebGL depth-parallax** layer: `brain.png` is a texture; a fragment shader displaces the surface by a depth value (the illustration's own luminance + a rounded-volume radial bump), so the gyri shift in real relief as it moves and tracks the cursor. On top: CSS 3D tilt + parallax float + breathing scale, and a 2D canvas of pulsing brass **synapse** nodes/links/sparks. Graceful fallback to the static image if WebGL is unavailable; hidden < 900px.

Tuning (settled with the Founder, after over/under passes):
- Parallax strength `0.08` (relief without edge-warp).
- Synapse node glows at the original `0.6` (a stronger pass was pulled back).
- Brass drop-shadow swell intensified on the breath cycle.

Files: `brain.png` (texture/fallback). All logic inline in `index.html` (`.hero-brain` style block + the brain `<script>` IIFE). No external JS dependency (the `<model-viewer>` CDN from the abandoned 3D attempt was removed).

### 2. Footer — column grid + wording fix
The rich homepage footer (`.fnav`) was set to **5 columns for only 4 groups** → an empty 5th column shoved everything left, off-center. Fixed:
- `grid-template-columns: repeat(5,1fr)` → `repeat(4,1fr)`; `max-width 960px` → `840px`; gap `22 → 32px`. Now centered under the lockup.
- Removed **"The team"** — it linked to `glass-box.html` (wrong target) and the team/org-chart page was parked in the 2026-06-22 dial-back; `team.html` doesn't exist.
- "Production work **(Tier 2)**" → "Production work" — internal tier jargon off a public surface.

## Verification
Preview-checked: 0 console errors; WebGL inits, texture maps with correct aspect (pixel-scan: 39/63 sample points hit opaque brain); footer renders 4 centered columns. Brain motion only reads on a foreground tab (the preview tab backgrounds rAF).

## Brand sign-off
Luka review: **ship (with two watch-notes)** — see `agents/luka/reviews/2026-06-22_home-hero-brain.md`. On-palette and premium; watch brass-scarcity and motion-restraint.

## Note for site-ia.md
`site-ia.md` was stale (pre-dial-back). Corrected the nav + footer sections to current truth as part of this change. The **page-tier table still needs a fuller reconciliation** against `decisions/2026-06-22_website-dial-back.md` (parked: Ready-to-Hire catalog, org-chart, team, ROI calculator, build-your-employee, the per-vertical funnel). Flagged, not yet done.
