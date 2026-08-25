# YourCo Pipeline

> **Owned by David.** Lightweight, agent-readable **mirror of the sales pipeline** in `crm/data.json` (the source of truth; live editable view at `/crm/`). David keeps this in sync. **Sales deals only** — internal agent rollout/provisioning moved to `clients/_internal-rollout.md` (2026-06-11 reconciliation). Reilly, Jim, Bird, and Atlas read this.

> **Reconciled to `crm/data.json` (`meta.updated` 2026-08-13) by Atlas on 2026-08-17**, ahead of the 8/18 Sales lock — the mirror had drifted on both valued deals (stage + value inverted), still carried the pre-ladder stage vocabulary, listed Partner B as an active connector after he was parked/admitted as a partner (08-11), and counted 22 deals against the CRM's 21. When mirror and source disagree, the source wins. *(Normally David's edit; done here on the Founder's explicit "reconcile before locking the domain.")*

> **Since that reconciliation:** two pre-convo prospects added 2026-08-23 at the Founder's request — Sample Contact (`c31`/`p34`/`d31`) and Sample Contact (`c32`/`p36`/`d32`, dual-role with connector `ck4y2a`). Counts below include both — 23 deals, matching the CRM.

_Status: pre-revenue. Every row below is a **real, warm** record (`example: false` in the CRM). Per `decisions/2026-06-15_prospect-data-architecture.md`, the CRM holds only warm/relationship records; **cold sourced lists live in Instantly** and promote in on reply. Nothing signed or live yet. **Two deals carry firm value ($12k each): Sample Client (demo-proposal, $1k/mo) and Prospect A (discovery, $1k build + $2k/mo).** Sample Realty is in discovery (give-first stack delivered, value TBD pending the Bella audit); the remaining 20 are pre-convo warm prospects awaiting a first real conversation._

## Stage definitions (current ladder — matches `crm/data.json` `stages`)
- **pre-convo** — a real human, no conversation about the work yet → exit: a real conversation held, business + decision-maker identified
- **discovery** — walking the proof, then diagnosing + quantifying the bottleneck → exit: pain named + data shared + bottleneck quantified in $ (stale >14d)
- **demo-proposal** — showing the built thing, then the priced proposal → exit: signed (stale >7d)
- **signed-onboarding** — scaffold fired, kickoff held, access granted → exit: build scoped + access in hand
- **build-implementation** — inside the build window → exit: feature-complete against the scoped modules
- **testing** — shadow mode, running on real work, only we see the output → exit: eval gate PASS
- **live** — operating; weekly readouts (terminal; a new module is a NEW DEAL opened at demo-proposal as an expansion)
- **parked** — deliberately not now, with a reason → exit: re-open trigger fires

## Deals (mirror of `crm/data.json`)

| Company | Use case | Stage | Value | Owner | Last touch | Next action |
| --- | --- | --- | --- | --- | --- | --- |
| Sample Client | Re-scoping → AI OS (was single-agent proposal automation); Design Studio + AI quoting platform | demo-proposal | $0 build + $1k/mo (**$12k**) | the Founder | 2026-08-06 | Ship quoting-platform v1 for Colton (wk of 8/10) → 30–60min walkthrough → 2-wk test. **One step from signed; 11d past the 7d stale line; unsigned since June; no price named yet** |
| Prospect A | Storm-alert system (NOAA/NWS hail-date verify → Nick approves → one-tap SMS to roofers) | discovery | $1k build + $2k/mo (**$12k**) | the Founder | 2026-06-30 | Scope sources + geography + roofer list; build give-first POC on free NOAA data. **Discovery 42d stale (>14d); POC deadline (7/07) 41d past** |
| Sample Realty | Real-estate OS — PM back-office module first (trust-account books + Kimi console), listing-launch second | discovery | TBD (Bella audit → Polo-priced) | the Founder | 2026-08-07 | the Founder sit-down w/ Kimi: walk site + tours + 'reconciled year' packet + PM console → Bella audit → proposal. **Give-first stack of 6 artifacts delivered; ask not yet made** |
| Sample Company C | Inbound intake (TBD) | pre-convo | $0 | the Founder | — | Reach out — give-first personalized demo |
| Sample Contact | Inbound intake (TBD) | pre-convo | $0 | the Founder | — | Reach out — give-first personalized demo |
| Sample Contact | Inbound intake; also connector | pre-convo | $0 | the Founder | — | Reach out (give-first demo) + ask for intros |
| Josh Airforce | Inbound intake (TBD) | pre-convo | $0 | the Founder | — | Reach out — give-first personalized demo |
| Sample Contact | Inbound intake (TBD) — warm Audit candidate | pre-convo | $0 | the Founder | — | Reach out — give-first personalized demo |
| Sample Company 35 | Inbound intake; also connector | pre-convo | $0 | the Founder | — | Reach out (give-first demo) + ask for intros |
| Sample Contact — business (the Founder to fill) | TBD — start with the audit | pre-convo | $0 | the Founder | — | the Founder to add business name + contact, then book the audit |
| Sample Contact — Home Building | TBD — scope in discovery | pre-convo | $0 | the Founder | 2026-06-16 | Warm reach-out (friend) → discovery; get co. name + contact |
| Sample Contact — Smoothie Shop (Yourtown) | TBD — scope in discovery | pre-convo | $0 | the Founder | 2026-06-16 | Warm reach-out (friend) → discovery; get co. name + contact |
| Sample Contact — Peptide Testing | TBD — scope in discovery | pre-convo | $0 | the Founder | 2026-06-16 | Warm reach-out (friend) → discovery; get co. name + contact |
| Sample Contact — Painting | TBD — scope in discovery | pre-convo | $0 | the Founder | 2026-06-16 | Warm reach-out (friend) → discovery; get co. name + contact |
| Sample Company 45 (Sample Contact — the Founder's dad) | TBD — relationship; connector vs. opportunity | pre-convo | $0 | the Founder | 2026-06-16 | Clarify Brett's role + connector vs. opportunity |
| Staffing firm — Amazon warehouse setup (Sample Contact) | TBD — relationship; connector vs. opportunity | pre-convo | $0 | the Founder | 2026-06-16 | Warm reach-out → clarify firm, role, connector vs. opportunity |
| Sample Contact — Law Firm | TBD — scope in discovery | pre-convo | $0 | the Founder | 2026-06-16 | Warm reach-out (friend) → discovery; add firm name + contact |
| Sample Contact — Salon | TBD — scope in discovery | pre-convo | $0 | the Founder | 2026-06-16 | Warm reach-out (friend) → discovery; add salon name + contact |
| Sample Contact — family Insurance Agency | Insurance AI — use case TBD (intake / lead follow-up / renewals) | pre-convo | $0 | the Founder | 2026-06-22 | Get Max's contact + agency name; intro to principal → discovery |
| Sample Contact — small building/construction co. (Yourtown) | TBD — soft/relationship lead (builder, not owner); intro/referral path | pre-convo | $0 | the Founder | 2026-06-24 | Keep warm (family); get co. name + owner/decision-maker; explore fit later |
| Sample Contact | TBD — start with the audit | pre-convo | $0 | the Founder | — | the Founder to add business name + contact, then book the audit. **Whether Sample Contact referred him is unconfirmed — do not assume it from the surname** |
| Sample Contact | Social media ops + sports betting picks distribution — grow and scale | pre-convo | $0 | the Founder | — | Real conversation: what he runs, audience size, where it monetizes, which half he wants. **Dual-role (also connector `ck4y2a`). First gambling-adjacent prospect — no vertical precedent; picks stay human-authored, see the CRM note before any build** |
| Sample Contact | Connector — referral source | pre-convo | — | the Founder | — | Advice-ask → who do you know? |

**Open:** 23 active deals — 1 **demo-proposal** (Sample Client, $12k, one step from signed) · 2 **discovery** (Prospect A $12k; Sample Realty TBD) · 20 **pre-convo** (19 client-fit/relationship + 1 connector Sample Contact; all $0, most last-touched 06-16 = never a real conversation). **Closed:** none. **Total pipeline value: $24,000** ($12k Sample Client + $12k Nick; the other 21 are $0/TBD). **Firm-priced open value:** $1k/mo (Sample Client) + $2k/mo + $1k one-time (Nick).

## Parked / lost
- **Partner B** (was connector, d17) — **parked 2026-08-11.** Retired as a connector prospect: Partner B was admitted as a partner (35% member, the Founder 2026-08-10). A partner is not a connector on the bench; his standing is the OA, not a referral deal.

## Pipeline hygiene rules
- A deal in **discovery** more than 2 weeks (14d) → push to demo-proposal or park. *(Nick: 42d — fired.)*
- A deal in **demo-proposal** more than 1 week (7d) → close or park with a reason. *(Sample Client: 11d — fired.)*
- An engagement in **build-implementation** more than 5 days → the discovery scope was too loose; go back.
- A **live** client missing a weekly readout → watchdog signal, log and address.
- A **parked / lost** entry without a "why" is a missed learning — never let one through.
