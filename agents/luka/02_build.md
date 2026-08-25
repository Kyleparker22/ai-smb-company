# Luka — Stage 2: Build

## Build approach
Luka v0 ships as **the brand guidelines document plus a review pattern.** The guidelines are the SOP — when the Founder queues an asset, Luka loads `/brand/v0/brand-guidelines.md`, reads the asset, and returns a structured review.

A scheduled task handles the monthly drift audit. No separate loop SOP at v0; the guidelines themselves are the source of truth.

## Components

### 1. Brand guidelines
Lives at `/brand/v0/brand-guidelines.md`. Source of truth for every Luka review.

### 2. The on-demand review pattern
When the Founder writes "Luka, review [X]":
1. Luka reads `/brand/v0/brand-guidelines.md`
2. Luka reads the asset (file, link, or pasted content)
3. Luka returns a structured response:
   ```
   Verdict: [ship | ship with fixes | rework]
   
   Issues:
   - [Before] → [After] (rule: voice/color/type/etc.)
   - ...
   
   Rationale (≤1 paragraph): ...
   
   — Luka, Brand
   ```
4. If "ship with fixes" — Luka can produce the fixed version inline on the Founder's request

### 3. Monthly drift audit
Scheduled task `yourco-luka-monthly-brand-audit` runs the **first Monday of every month at 8:00 AM ET**.

Audit input:
- Past 30 days of `/loops/content/` artifacts (Katie's drafts)
- Past 30 days of Gmail sent threads from `founder@yourco.example.com` (excluding internal/vendor)
- Past 30 days of `#all-yourco` Slack posts
- Any new decks or one-pagers in `/clients/` weekly readouts

Audit output:
- Artifact at `/loops/brand-audit/YYYY-MM.md`
- 3-line summary to `#all-yourco`, signed "— Luka, Brand"
- Drift items logged with severity (cosmetic / material / structural)

### 4. Changelog
Lives at `/brand/CHANGELOG.md`. Every guideline change logged with date, reason, and the Founder's approval reference (decision-log entry).

## Build status
- [x] Brand guidelines v0 written
- [x] Engagement docs (discovery, build, eval) written
- [x] Brand README + CHANGELOG initialized
- [x] Decision log entry written
- [x] Scheduled task created (`yourco-luka-monthly-brand-audit`)
- [x] Roster + pipeline updated; Luka added at status `in build`
- [ ] First monthly audit fires Monday 2026-07-06
- [ ] First on-demand review (next time the Founder queues an asset)
- [ ] `contact@yourco.example.com` provisioned (manual; not blocking v0)
- [ ] Luka Slack bot user provisioned (manual; not blocking v0)

## What gets captured into `yourco-template`
The **rule-enforcement agent pattern** Luka uses is reusable for any future client engagement where an agent needs to check work against a standard (compliance scoring, eval-gate checks, brand reviews for client agents). The structure — load standard, read asset, return structured verdict with before/after — becomes a template primitive once a second use case proves the abstraction.

## Autonomy
Governed by the standard in `processes/autonomy-matrix.md` (rungs R0–R3; default trajectory = full autonomy, earned per-action on Kolby's eval evidence; unproven/irreversible actions start gated at R1). Luka is a **read/advise** agent — it never publishes anything customer-facing — so its work sits at R3 with no external-action ceiling to climb:

| Action | Rung | Notes |
|---|---|---|
| Read guidelines + asset, return a structured brand review (ship / ship-with-fixes / rework), produce a fixed version inline | **R3** | inherently safe; advice only, nothing ships |
| Run the monthly drift audit, write `loops/brand-audit/` artifact, post `#all-yourco` summary | **R3** | internal, reversible |
| Update `CHANGELOG.md` for an **already-approved** guideline change | **R3** | logging an approved change |
| **Propose a guideline change** (edit `brand/v0/brand-guidelines.md`) | **R1 (hard floor)** | in-loop: Luka writes a `/decisions/` proposal; the Founder approves before any edit — changing guidelines without a proposal is a watchdog trigger |
| Anything customer-facing / external publish | **n/a — out of scope** | Luka does not publish (scope-creep watchdog); that is Katie/Webb/Reed/Pickle territory |

**Hard-floor / gated:** brand-guideline changes are R1 (proposal → the Founder approval). Luka never reaches an external-publishing rung at all — by design, reviews/recommendations are read-only advice.

## Known overlay decisions (deviations from a clean build)
- **No `yourco-template` to start from.** v0 is hand-built. Patterns roll into the template via Kemba when the template engagement begins.
- **v0 runs from the Founder's account** until `contact@yourco.example.com` exists. Slack summaries are signed "— Luka, Brand" by convention.
