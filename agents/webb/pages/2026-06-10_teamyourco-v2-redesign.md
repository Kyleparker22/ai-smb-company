# Webb — yourco.com v2 redesign + re-position

**Owner:** Webb · **Date:** 2026-06-10 · **Status:** 🟡 STAGED — Luka-passed, ported to deploy folder, **awaiting the Founder's go to deploy**.

## What changed
Full redesign + **re-position** of yourco.com from the old "two-week AI audit / Five Business Outcomes / 1–100 people, every industry" message to the current **digital-employee** strategy (matches brand v0.3, the OS, and the cold landing page). Decision to re-position: the Founder, 2026-06-10 ("audit offered as a service but not the main item").

## The site (5 pages, shared `site.css`)
- **index** — hero "Named digital employees. Live in 48 hours." → demo → how-it-works → moat → roster (employee shapes) → audit (secondary card) → close. Campaign lines placed: "the future doesn't clock in" + "hire once. scale forever."
- **positioning** (nav: "How it works") — the build (4 steps), employee shapes, 3 lessons. **Fabricated client case studies removed** (pre-revenue; integrity). Kept the true "we run on our own roster" story.
- **pricing** — explains the model, **no numbers**: optional audit (fixed) · build (fixed) · monthly retainer (runs employee + all infra) · add-ons (fixed + retainer step-up). "Complexity is ours" + "scope it on the call."
- **audit** — reframed as the secondary **one-week** (was two), fixed-fee "where to start" service; Days 1–2 / 3–4 / 5; ~3–5 hrs leadership time; ends in a first-employee recommendation.
- **about** — "a workshop, not a software vendor"; why yourco exists; 3 differentiators; "we run yourco on the employees we build"; honest fit.

Design: Apple-system discipline in locked brand colors (brass single accent, cream↔indigo tiles, tight display type, Eval Gate brass rules, locked wordmark lockup, paper-not-glass). Tagline locked: **"We learn your business. AI does the work."**

## Luka brand pass (2026-06-10)
PASS. One fix applied: removed "leverage" (banned word). No tech-blue, no pure white/black, no gradients, no drop-shadows-on-type, no italics-for-emphasis, lowercase wordmark, restraint held.

## Port
Source of truth: `agents/webb/pages/yourco-site-v2/` (OS repo, versioned). Ported (copied) to `~/Desktop/YourCo LLC/Website/YourCo-deploy/`; old pages → `_backup_pre_v2/`. Not a git repo, not deployed.

## Open / to-do before live
- **Deploy** — the Founder's go (Vercel). Also deploy the cold landing page to getteamyourco.com (Reilly campaign destination, needed ~June 22).
- Homepage still on inline CSS — fold onto `site.css` at deploy time (cosmetic active-state too).
- Case studies — deferred (add real ones if/when they exist).
- Legacy `diagnostic.html` now orphaned (no longer linked); decide keep vs retire.
