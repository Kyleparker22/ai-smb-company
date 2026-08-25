# Vertical landing-page buildout brief — Sadie → Bella

> **STATUS: COMPLETE (2026-06-18).** All B2B intent-engine verticals now have a landing page + Revenue Leak Snapshot in `snapshot-config.js` — **57 verticals total** (was 13). Built in 9 batches; every stat live-sourced (real publisher, 2025-2026, working URL) or marked `[verify]`. The original priority-5 plan below is kept for the record. **Open follow-ups** (see bottom): one `[verify]` stat to backfill (Public Adjusters), and **Caregiving** still needs a bespoke DTC page.

**Created:** 2026-06-18 · **Owner of output:** Bella (curates `snapshot-config.js` — renamed from quick-audit-config.js) · **Sourcing:** Sadie
**Trigger:** The intent engine (`runtime/intent_verticals.json`) covers ~47 verticals with live Google Alerts feeds. The website per-vertical funnel (`snapshot-config.js` → `vertical-template.html?v=<slug>` + `snapshot.html?v=<slug>`) covered only **13**. This brief closed the gap — quality-first, a few at a time.

## The gap (as of 2026-06-18)
- **Website has 13:** landscaping, hardscaping, hvac, plumbing, electrical, roofing, restoration, garage-door, tree-service, septic-well, weddings, pet-care, waste-recycling.
- **Website-only (NOT in intent engine — leave as-is, flagged for awareness):** weddings, pet-care, waste-recycling.
- **Intent engine has 45.** ~32 intent verticals have no landing page / Quick Audit yet.

## Priority 5 (build these first)
Chosen on demonstrated live signal during the 2026-06-17 Alerts wiring + unit economics + web-signal density:

| Order | Vertical | Slug | Why prioritized (evidence) |
|---|---|---|---|
| 1 | Accounting / CPA | `accounting-cpa` | Alerts surfaced the exact pitch ("captures calls your CPA firm misses during tax season"); high-ticket, tax-season urgency hook. |
| 2 | Dental | `dental` | "When Your Dental Practice Is Busy But Your Team Is Breaking" surfaced live; high-ticket healthcare, recall/no-show angle. |
| 3 | Property Management | `property-management` | r/PropertyManagement buyer asking for an AI to talk to inbound leads; AppFolio/Yardi/DoorLoop validating market (also = competitors to watch). |
| 4 | Med Spa | `med-spa` | Competitor Ryvet.io running yourco's exact personalized "see yours" demo play — direct head-to-head; high-ticket aesthetic. |
| 5 | Real Estate | `real-estate` | Live answering-service competitor (AnswerRight.ai) + high lead volume; lead-response-time is the wedge. |

## What each block needs (match the existing schema in quick-audit-config.js)
Copy an existing block (e.g. `roofing`) and replace content. Each vertical needs:
- `name`, `eyebrow`, `heroPain`, `heroSub`, `probHead`
- `bottlenecks[]` (3 — title + desc), `osPitch`, `closeHead`
- `stats[]` (3) — **see STATS RULE below**
- `quickAudit.intro` + `questions[]` — keep the four leak-model keys present: **leads, missed (with `pct[]`), job_value, admin_hours**
- `report.firstBuild` etc. per the schema

## STATS RULE (non-negotiable — brand: no fabricated numbers)
- Every stat carries `src` + `url` — a **real, citable** source.
- **Recency:** published within ~12 months (2025–present). No decade-old studies.
- **Process:** Sadie sources + cites each stat → hands to Bella → Bella curates into the config.
- If a stat is added without a source, use `src: "[verify]"` (no url) — it renders visibly as unverified until cited. **Never invent a number.**

## Done = for each priority vertical
1. Sadie delivers 3 recent, cited stats matching the vertical's pain.
2. Bella writes the block into `quick-audit-config.js` with those stats.
3. Verify it renders: `vertical-template.html?v=<slug>` and `quick-audit.html?v=<slug>`.
4. Confirm the slug is added to the Industries hub (`verticals.html`) if it lists pages explicitly.

## After the priority 5
Work down the remaining intent verticals by cluster, highest unit-economics first: professional services (Law, Insurance, Wealth, Mortgage, Title & Escrow, Bookkeeping, Public Adjusters) → remaining healthcare (Vet, Chiro, PT, Ortho, Plastic Surgery, Dermatology, Family Medical, the clinics) → project trades (Concrete, Fencing, Painting, Window & Door, Flooring, Kitchen & Bath, Foundation, GCs, Home Builders, Excavation) → misc (Auto Repair, Pest Control, Cleaning, Pool, Solar, Moving, Commercial Cleaning, Hotels, Sports & Fitness, Funeral Homes, Caregiving, Recovery & Cold Plunge).

---

## Completion log (2026-06-18) — all 9 batches built
- **B1** (priority 5): accounting-cpa, dental, property-management, med-spa, real-estate
- **B2** (pro services): law-firms, insurance-agencies, mortgage-brokers, wealth-management, title-escrow
- **B3**: bookkeeping, public-adjusters, veterinary, chiropractic, physical-therapy
- **B4** (project trades): concrete-masonry, foundation-repair, flooring, kitchen-bath, fencing-decks
- **B5** (project trades): painting, window-door, general-contractors, home-builders, excavation
- **B6** (local service): auto-repair, pest-control, cleaning-services, pool-service, solar
- **B7** (healthcare): orthodontics, plastic-surgery, dermatology, family-medical, peptide-clinics
- **B8** (wellness): wellness-clinics, iv-therapy, hormone-trt, recovery-cold-plunge
- **B9** (misc): moving-storage, commercial-cleaning, boutique-hotels, sports-fitness, funeral-homes

Trades reused the repo's already-verified evergreen home-service stats (Invoca Dec 2025 + Jobber 2026) + one fresh market size each; healthcare/pro-services/hospitality each got 3 freshly-sourced stats.

## OPEN FOLLOW-UPS
1. **Public Adjusters — one `[verify]` stat (slot 3).** The only PA-specific settlement stat (747% higher recovery) traces to a 2010 OPPAGA study → fails the 12-month recency rule, so it's rendered `[verify]`. Sadie: source a recent (2025-2026) PA settlement-uplift or claim-recovery stat, or leave as-is.
2. **Caregiving — DTC, NOT built here.** Deliberately excluded from `snapshot-config.js`: the Revenue Leak Snapshot is a B2B model (leads × missed × job-value), which is nonsensical/tone-deaf for an adult child caring for a parent. It's the **yourco Care** DTC offering and needs its own page model (not the leak calculator). Stats already sourced & parked: AARP/NAC **63M** US family caregivers (Jul 2025), **78%** report burnout (A Place for Mom, Feb 2026), **+45%** caregivers in a decade (AARP, Jul 2025).
3. **A few stats lean on aggregator/vendor pages** (AgentZap, Aira, Gitnux, Dialzara) that cite a named primary source — they meet the literal rule (real page, in-window, claim present) but Sadie can upgrade to primary sources on the next refresh pass. All flagged in the per-batch commit messages.
4. **Recurring stat refresh** — the recency rule means these need re-checking on Sadie's cadence; IBISWorld figures in particular roll to new years.
