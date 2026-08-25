# Function-only / no-vertical alignment sweep (2026-06-23)

> **Owner: Webb.** After reworking See it Work (demos.html) to agents-by-type, the Founder: "update so everything aligns." Audited all staged pages for named agents (proper names) and vertical-specific framing; fixed every user-facing instance. Consistent with the function-only-naming decision and horizontal positioning. Staged/internal.

## Pages fixed
- **demos.html** — (done earlier, `e848f79`) 12 named/vertical employees → 10 agents by type.
- **demos-tier2.html** (Production work) — 11 named, vertical "Tier-2 employees" (Sloane/real-estate, Lux/med-spa, Counsel/law, …) → **8 production-agent types**: Listing & Catalog Marketer · Campaign Manager · Proposal Builder · Document Packet · Review-Prep Analyst · Reactivation Engine · Reputation Manager · Progress Reporter. Pipelines kept; "employees" → "agents" in copy/legend/closer/meta.
- **instant-employee.html** (See yours / live demo) — the result now shows the **agent by role** ("Front desk & intake", "Intake & consultation coordinator", …) instead of a person name (Reese/Quinn/Sage/…). Removed all person-name display + lead-capture refs; stripped the now-inert `emp:"…"` data fields. "employee" → "agent" (h1, lede, meta, result label). "pick an industry" → "preview an example." The personalize-to-your-business mechanic is unchanged (on-brand for horizontal — example businesses demonstrate "any business").
- **timeline-48h.html** — the example build was **"Sage," an intake employee for a landscaping company** → **"an intake agent"** (no name, no vertical); "employee" → "agent" throughout + meta.
- **about.html / manifesto.html** — dropped "**named** digital employee" → "digital employee" (the "named" wording conflicted with no-names; identity is still conveyed by "its own email").

## Left as-is (correct)
- **build-your-os.html** — already function-based (module names) + horizontal ("type your business"); its vertical-flavored flow text is *personalization*, not segmentation.
- **try-to-break-it.html** — already function-worded ("yourco intake agent").
- Content pages (reliability/objections/compare/glass-box) — function-worded already.
- CSS source comments naming "Webb/Luka" — build attribution, not user-facing; left.
- The per-vertical funnel (verticals/snapshot/etc.) — already parked.

## Verification
demos / demos-tier2 / instant-employee re-tested live (type chips, role-based render, full play/pipeline, 0 console errors). Final grep: **no displayed proper-name agents remain** anywhere.
