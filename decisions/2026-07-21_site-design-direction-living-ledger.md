# 2026-07-21 — Site design direction: The Living Ledger (Concept B + hybrid)

**Decision:** The staged site's premium redesign follows **Concept B — "The Living Ledger"**: all-light editorial luxury (cream/parchment, Fraunces at cinematic scale, brass hairlines that draw themselves, the self-writing draft→approve→sent letter as the hero scene), with four elements folded in from the competing concepts:
- Concept A's **count-up stat numerals** (and stats laid side-by-side within upside/catch columns)
- Concept A's **8-department card grid** + the machined "◆ yourco. operated system" band for What-we-build
- One **dark "engine room" act** (#0F1226) with A's brass scan-beam
- Concept C's **living OS schematic** (8 nodes, reliability ring, approval port, pulse traffic, legend) living inside that dark act

**How it was chosen:** per the external-surface rule (2–3 concrete options before iterating live), three full art-direction prototypes were built in parallel — A "The Machined Object" (Apple product-page, light+dark act), B "The Living Ledger" (editorial all-light), C "The Glass Box" (Stripe-style dark-first living schematic) — all pure code motion (no libraries/images/canvas), all from the real homepage copy and locked brand tokens, so the comparison was direction-only. the Founder reviewed all three live and picked B with the A/C grafts above. Prototypes preserved at `agents/webb/pages/yourco-site-v2/_concepts/` (concept-a/b/c.html; b carries the merged v2).

**Motion standard set by this decision (applies to the production rebuild):** pure code motion (CSS + vanilla JS + inline SVG only); animate transform/opacity/clip-path/stroke-dashoffset only; easing cubic-bezier(0.16,1,0.3,1), slow assured timing; every animation must have a reason; full prefers-reduced-motion collapse; no horizontal overflow at 390px; no canvas particle fields.

**Next:** rebuild the production `index.html` in this direction on the Founder's sign-off of the v2 merge, then propagate the motion system across the funnel pages.

Owner: Webb (site) · the Founder chose 2026-07-21.
