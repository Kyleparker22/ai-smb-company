# The AI OS — module taxonomy (what an yourco OS is made of)

> The canonical vocabulary for what goes *into* a custom AI OS. Used three ways: (1) the **Audit's scoping checklist** (which pillars does this business need, in what order), (2) the **pricing unit** (price per module/pillar; `pricing/v0/`), (3) the **land-and-expand map** (land one → grow the department → grow the OS). Pairs with `processes/yourco-method.md` and `decisions/2026-06-18_offering-narrowing-os-first.md`. Owner: Brett (frame) + Kimi (build) + Polo (price).

## The frame
An yourco **AI OS** = a coordinated subset of the functional pillars below, **fit to one business**, sitting on the **cross-cutting moat layer**. The audit decides *which* pillars and the *sequence*. The "digital employee" is the **smallest unit** of a pillar — the on-ramp, still custom, never a menu SKU. A pillar says what a module *does*; the **form factor** (§below) says what shape it *ships in* — employee, headless automation, or embedded surface.

## The functional pillars (the modules)
| # | Pillar | What it does | Common first employee (the on-ramp) |
|---|--------|--------------|--------------------------------------|
| 1 | **Intake / Front Desk** | Capture + qualify every inbound (calls, forms, chat) → book / route | The intake/front-desk employee (the classic Tier-1 entry) |
| 2 | **Sales / Revenue** | Outbound, lead follow-up, pipeline/CRM hygiene, proposals/quotes, win-loss intel | Lead-follow-up or proposal-drafter |
| 3 | **Marketing / Demand** | Content, social, email, SEO/GEO/AEO, brand consistency | Content/marketing employee (Tier-2 "produce it") |
| 4 | **Customer / Retention** | Support triage, reviews, proactive health, cited customer Q&A | Support-triage or review employee |
| 5 | **Operations / Delivery** | Scheduling/dispatch, project status, vendor/sub coordination, the vertical's core workflow | The vertical's core-workflow employee (e.g. Sample Client proposal automation) |
| 6 | **Back Office / Finance** | Invoicing/AR, bookkeeping prep, receipts, reporting | AR/invoice-chaser or bookkeeping-prep employee |
| 7 | **Company Brain / Knowledge** | Institutional-knowledge capture + cited internal Q&A | Knowledge-capture employee ("don't lose the brain") |
| 8 | **People / Training** | Onboarding, sales role-play/coaching, SOPs | The AI sales coach (`offerings/sales-training/`) |

## Form factors (the three shapes a module ships in — added 2026-07-20)
Any pillar's module can take any of these shapes, and one module can blend them. All three run on the same moat layer; yourco itself runs all three internally, so this is the client-side mirror of an architecture already proven in-house.

| Form factor | What it looks like | yourco's own instances | Client-side examples |
|---|---|---|---|
| 1 · **Digital employee** | Personified — a name, its own email/phone, talks to people | Reilly, Jim, Sadie… (the roster) | The intake/front-desk employee — the classic on-ramp (the "common first employee" column above is form factor 1 throughout) |
| 2 · **Headless automation** | No face — trigger-fired workflow or loop | The runtime loops (Monday briefing, watchdogs, chasers) | Sample Client proposal automation (Aspire-signed → drafts, approval-gated) |
| 3 · **Embedded AI surface** | A product surface the client's staff *or their customers* touch; the AI is inside the tool, not wearing a name | Client console, demo kit, the CRM + HQ dashboards | Sample Client **Design Studio / Instant Range** (kitchen-table quote range, `clients/sample-client/04_instant-range-concept.md`); **Sample Product** — the same class at venture scale |

Three consequences worth stating:
- **"No agents built for it" is not a category problem.** A form-factor-3 module has the AI in the engine (vision, calibration, retrieval, generation). Most surface modules grow an agent limb later — the Instant Range's grey-area chaser (emails/texts open decisions until closed) is form factor 1 growing out of a form factor 3 module. Normal, not messy.
- **The moat layer binds per form factor.** For a surface, eval means product-grade calibration: the Instant Range's *range-vs-signed-price* tracking ("9 of 10 ranges held") **is** the eval-vs-reality record applied to pricing, plus human approval on any firm number. A quote surface with wrong numbers costs real dollars — which is exactly why the moat layer, not the tool, is what's being sold.
- **Positioning:** the offer's language should say the OS delivers through employees, automations, *and* customer-facing AI surfaces — a vocabulary addition, not a repositioning (the staged site's employee-led imagery under-shows form factor 3; Webb owns that pass). Any Sample Client asset shown publicly needs Client Owner's OK (white-label rule) and a signed engagement first.

## The cross-cutting layer (NOT a module you buy — the moat)
Under **every** OS, present by definition: **Reliability · Eval · Observability · Approval · Audit log.** This is what makes it *operated* (vs. DIY agents) and is the durable differentiator no-code can't deliver. It is never sold as a separate line; it's why the whole thing is trustworthy.

## How it maps to the rest of the system
- **Audit** → produces the scoped OS: which pillars, the sequence, the first module, the ROI math.
- **Pricing** → a single module/employee = entry ($1–5k setup + $1,500–2,500/mo); 3+ coordinated = an OS ($2–5k implementation + $3–10k/mo). Graduation + caps: `pricing/v0/vertical-ranges.md`.
- **Land-and-expand** (Bird) → land one pillar's first employee → add the rest of that pillar → add adjacent pillars → the full OS.
- **Named offering lines** (`processes/new-offering-lines.md`) are mostly *pillar-deep or vertical-deep* OSes — e.g. B6 sales-training = Pillar 8; Company OS = pillars 5/6/7 for an acquired firm; GEO = Pillar 3 for a vertical.

## Build-stage raw material
[msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents) (MIT, 232 persona prompts across 16 divisions) — a first-draft prompt/pattern library Kimi + the scaffolder can cannibalize when assembling a pillar's agents; always rewritten to the client and hardened through our reliability/eval/approval layer. It's the commoditized layer, not the moat — never shipped as-is.

Build-stage ingredients (from `decisions/2026-07-05_tool-triage.md`; instantiated per engagement, never pre-installed): **Supabase** — default backend when a build needs a real DB + auth + tenant isolation (RLS); **markitdown** — client-doc → markdown ingestion for the Company Brain pillar; **Firecrawl** (API) — prospect/client own-site → markdown for audit prep and AEO scans (compliance bounds in Rafi's scraping assessment); trigger-gated: **Chatwoot** (Customer pillar, support-desk need) and **Stirling PDF** (Back Office pillar, programmatic PDF ops) — see `runtime/activation-triggers.md` §Tool triggers.

## The one rule
We sell **the system (or its first module), built from the Audit and operated by us** — never an agent shopped off a menu. The pillars are how we *scope and assemble*, not a self-serve catalog.
