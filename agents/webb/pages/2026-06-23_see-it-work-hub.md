# See it Work — one demo hub (combined live + production) (2026-06-23)

> **Owner: Webb.** Per the Founder: combine "See yours (live)" + "Production work" into a single **See it Work hub** (`demos.html`) with the existing 10-agent demo. Staged/internal.

## What changed
`demos.html` is now a **tabbed hub** with a segmented control under the hero:
- **Agents in action** (default) — the existing 10-agents-by-type chat demo, inline.
- **See yours · live** — the personalized "build one for your business" demo.
- **Production work** — the 8 Tier-2 production-agent pipelines.

### How it's combined (reliably)
The three are independent interactive widgets with overlapping class/IDs, so rather than a fragile inline merge, the two added experiences load as **chrome-stripped iframes**:
- Added an **`?embed`** mode to `instant-employee.html` and `demos-tier2.html` — hides nav/footer/grain, transparent bg, and **posts its height** to the parent (ResizeObserver + interval) so the iframe auto-sizes (no scrollbars, no double-nav).
- The hub **lazy-loads** each iframe on first tab open, **deep-links** via hash (`demos.html#yours`, `demos.html#production`), and sets iframe height from the `postMessage`.

### Retiring the separate pages
- The two files **remain** (they're the iframe sources, loaded with `?embed`), but are no longer standalone destinations. Home-footer "See it work" group repointed to the hub: **Agents in action → `demos.html`**, **See yours (live) → `demos.html#yours`**, **Production work → `demos.html#production`**. No other page linked them; the nav "See it work" already points to `demos.html`.
- Direct hits to `instant-employee.html` / `demos-tier2.html` (no `?embed`) still render the full standalone page — unlinked, but a redirect would break the iframe, so left as-is.

## Verification
All three tabs load; embeds render chrome-stripped and auto-size (yours ≈661px, production ≈743px); 10 / 8 agent chips intact; deep-links open the right tab; **0 console errors**. Aligned with the current site (function-only agents, premium polish, deeper parchment).

## Note for site-ia.md
`site-ia.md` should reflect that "See yours" + "Production work" are now **tabs of the See-it-work hub**, not separate pages (footer pattern updated). Flagged.
