# Site Information Architecture — yourco-site-v2

> **Owner: Webb.** The staged site is **21 lean HTML pages (~20)** — core journey + a differentiation/proof kit — led by the **audit** and positioned **horizontally** (audit → custom AI OS for *any* business, no per-trade funnel). This is the canonical structure so it's *navigable*, not a pile. Implemented as the reference on `index.html`; Webb applies the same nav + footer template to every page at deploy. **Last updated 2026-06-22** — full pass: nav, footer, **page-tier table, cross-links, and rollout status all reconciled to current truth** against the three dial-back/positioning decisions (below). Staged/internal — nothing deployed (launch-gate).
>
> **Decisions this reflects:** `decisions/2026-06-22_website-dial-back.md` (34→~20 pages; parked the Ready-to-Hire catalog, org-chart/team, ROI calculator, build-your-employee, redundant diagnostics, refer) · `decisions/2026-06-22_horizontal-positioning-and-os-tiers.md` (no verticals on the site; per-vertical funnel parked; OS tiers Core/Suite/Operation/Command) · `decisions/2026-06-18_offering-narrowing-os-first.md` (one motion — the unit of sale is the OS or its first module; the single "digital employee" is the on-ramp, not a menu SKU).
>
> **Parked** (in `agents/webb/pages/yourco-site-v2/_parked/`, fully reversible — *not* part of this IA): `hire.html`, `hire-onboarding.html`, `employees.html`, `build-your-employee.html`, `roi-calculator.html`, `quiz.html`, `refer.html`, `missed-money-meter.html`, `leak-index.html`, `org-chart.html`, `team.html`, `verticals.html`, `vertical-template.html`, `snapshot.html`.

## Page tiers
| Tier | Pages | Where it lives |
|---|---|---|
| **Primary** (the visitor journey) | Home (`index`) · How it works (`positioning`) · What we build (`build-your-os`) · See it work (`demos`) · Pricing (`pricing`) · About (`about`) | **Top nav** |
| **Convert** (the front door) | Start with the audit (`audit` → `audit-intake`) | nav CTA pill + every page |
| **Proof / depth** | `instant-employee` (See yours) · `demos-tier2` (Production work) · `try-to-break-it` · `day-in-the-life` · `timeline-48h` · `objections` (Honest answers) · `compare` · `reliability` · `glass-box` · `manifesto` · `eval-gated-seal` | **Grouped homepage footer + contextual links** (not the top nav) |
| **Compliance** | `privacy` · `sms-terms` | footer meta + linked from forms |

**Rule:** keep the top nav lean — primary journey only; the convert action is **the audit** (the paid front door, not "book a call"); everything else lives in the footer + contextual links, never crammed into the nav.

## Canonical primary nav (every page) — current
`Home · How it works · What we build · See it work · Pricing · About · [Start with the audit →]`
(The current page gets `class="active"`. "How it works" → `positioning.html`; "What we build" → `build-your-os.html` (the OS-first explainer); "See it work" → `demos.html`. The CTA pill → `audit.html` — the audit is the single front door, per the OS-first / dial-back decisions; "Book a call" survives only as the footer **Company → Contact** link, not the primary convert action.)
*Updated 2026-06-22: added "What we build" + "About"; CTA is now the audit (was "Book a call") — supersedes the earlier 5-item nav.*

## Footer — two patterns (current, 2026-06-22)
**Home (`index.html`) — rich 4-group `.fnav`** (centered, `repeat(4,1fr)`, max-width 840px):
- **Product** — How it works · What we build · The audit · Pricing
- **See it work** — See yours (live) · Demos · Production work · Try to break it · A day in the life · 48 hours, documented
- **Why yourco** — Honest answers · Compare · Reliability · The glass box
- **Company** — Manifesto · Eval-Gated · About · Contact
- + the tagline lockup + **Book a call**

**Other pages — flat `.fgrid`** (single centered row of links + lockup + meta).

*Updated 2026-06-22: dropped the old "Explore" group + "The team" (org-chart / team / ROI-calculator / build-your-employee parked in the dial-back); removed "(Tier 2)" jargon. Fixed the home grid (was `repeat(5,1fr)` for 4 groups → off-center).*

## Contextual cross-links (the funnel)
Every path lands on **the audit** (`audit.html`) — the single convert action. All targets below are live pages (parked pages removed).
- **Home** → hero CTAs to *See it work* (`demos`) + *Start with the audit* (`audit`); the horizontal "We don't do one industry. We learn yours." block → `audit`; the grouped footer surfaces the proof kit (no separate "Explore" strip needed).
- **How it works** (`positioning`) → `timeline-48h` ("see a real 48-hour build") + `glass-box`.
- **What we build** (`build-your-os`) → `pricing` (the Core/Suite/Operation/Command tiers) + `audit`.
- **See it work** (`demos`) → `try-to-break-it` + `demos-tier2` (Production work) + `instant-employee` (See yours).
- **The glass box** → `try-to-break-it` + `manifesto`.
- **Every proof/depth page** → ends in *Start with the audit*.

## Rollout status
- ✅ Canonical nav + grouped footer **implemented on `index.html`** (the reference).
- ✅ Page-tier table, cross-link map, and this status **reconciled to the ~20 live pages** (parked pages dropped; horizontal/OS-first positioning applied) — 2026-06-22 full pass.
- 🔲 Webb applies the same nav + footer template to the other ~20 pages at deploy (mechanical — copy the `index.html` nav + `<footer>` blocks). Per the dial-back's "known cosmetic debt": the deploy pass also rebuilds a **single shared nav** and cleans any retargeted-label copy.
- 🔲 If Polo's tiers are ready at launch, fold a **tiers section** (Core/Suite/Operation/Command) into `pricing.html` (per the horizontal-positioning decision).
- Staged/internal — nothing deployed until the launch-gate clears (`processes/launch-runbook.md`).
