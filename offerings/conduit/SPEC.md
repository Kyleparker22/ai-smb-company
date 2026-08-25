# International Nurse Immigration Ops Platform — Build Spec

**Working name:** Conduit (placeholder)
**Author:** the Founder
**Stack:** n8n (orchestration) · Postgres (system of record) · Anthropic Claude API (reasoning/extraction/drafting) · Microsoft 365 / Graph (email, storage, calendar) · React (front-end)
**Intended builder:** Claude Code / Cowork
**Status in YourCo OS:** offering parked — see `decisions/2026-06-18_conduit-ien-immigration-offering.md`. Offered as an *operated* vertical AI OS (YourCo builds + runs it), not self-serve SaaS.

---

## 0. What this is (and who pays for it)

A vertical ops platform that runs the end-to-end pipeline for bringing an internationally-educated nurse (IEN) to the US on an employer-sponsored EB-3 (Schedule A) green card. It replaces the spreadsheets-and-email chaos that small immigration firms and boutique nurse recruiters run on today.

**Customer = the firm's principal/owner**, not a coordinator. The buyer is whoever owns P&L and feels the pain of pipeline visibility, missed deadlines, and document chaos. The pitch is: *"You're tracking 80 nurses across a 12-stage, 2–4 year process in a spreadsheet. One missed license-expiry or visa-bulletin movement costs you a placement. This makes the whole pipeline self-monitoring."*

**Important constraints baked into the design:**
- **Build multi-tenant from day one.** Even if firm #1 is the pilot, the asset is SaaS sold to many small firms. Single-tenant only if you decide this is a bespoke internal tool.
- **The tool produces drafts and flags, never legal determinations.** Every AI output that touches legal substance is framed "for attorney review" to avoid unauthorized-practice-of-law (UPL) exposure. You are not the lawyer.
- **Your domain SME is an employee, not a partner.** Interview her to get the workflow right; sell to the principal. Don't design anything that depends on one employee funneling firm data.

---

## 1. The core object: the IEN pipeline state machine

Everything in the system hangs off a per-nurse state machine. These are the canonical stages (EB-3 Schedule A, employer-sponsored). Each stage has: required documents, responsible party, typical SLA, and blocker conditions.

| # | Stage | Key artifacts / gates | Owner | Long-pole? |
|---|-------|----------------------|-------|-----------|
| 1 | Sourced / Screened | RN license (home country), experience, English readiness | Recruiter | |
| 2 | Credentials Evaluation | CGFNS CES / ERES report (educational equivalency) | Coordinator | |
| 3 | English Proficiency | IELTS Academic or OET pass (~2-yr validity) — or exemption | Nurse | |
| 4 | NCLEX-RN | NCSBN registration → ATT → Pearson VUE seat → pass | Nurse | |
| 5 | State Licensure | Board of Nursing application (state-specific rules/timelines) | Coordinator | |
| 6 | VisaScreen | CGFNS/ICHP certificate (license + edu + English + NCLEX) | Coordinator | |
| 7 | I-140 Petition | Employer files (Schedule A Group I = no PERM); **priority date set** | Attorney | |
| 8 | Visa Bulletin Wait | Priority date must become current (**retrogression — the long pole**) | System monitors | ★ |
| 9 | Consular / AOS | DS-260 + NVC docs (consular) or I-485 (adjustment) | Attorney | |
| 10 | Medical + Civil Docs | Medical exam, police clearance, civil documents | Nurse | |
| 11 | Visa Issued → POE | Embassy interview → visa → travel → port of entry | Nurse | |
| 12 | Onboard / Retain | Relocation, licensure-by-state finalization, contract start, retention | Employer | |

**Design note:** stages are *not* strictly linear — credentials/English/NCLEX (2–4) run in parallel, and the I-140 (7) can be filed early to lock a priority date while licensure finishes. Model stages as independent state instances with dependencies, not a single linear status field.

---

## 2. Architecture

```
  React SPA  ───────▶  API layer (Node/Express or Next API routes)
  (coordinator +              │
   client + nurse            │
   portals)                  ▼
                       ┌───────────┐         ┌──────────────┐
                       │ Postgres  │◀───────▶│     n8n       │
                       │  (SoR)    │         │ orchestration │
                       └───────────┘         └──────┬───────┘
                                                    │ HTTP
                  ┌─────────────────────────────────┼─────────────────────┐
                  ▼                                  ▼                      ▼
          Anthropic Claude API              MS Graph (M365)         External sources
          (extract / draft /                email · SharePoint      Visa Bulletin,
           summarize / next-action)         OneDrive · Outlook      CGFNS/NCLEX status
```

- **Postgres** is the single source of truth.
- **n8n** runs all triggers, schedules, and orchestration.
- **Claude API** is called from n8n HTTP nodes (or a thin service) for every reasoning task.
- **MS Graph** handles email send/receive, document storage in SharePoint/OneDrive, and Outlook calendar for test/interview dates.
- **React SPA** is the human surface: pipeline board, nurse detail, document review, comms.

---

## 3. Data model (Postgres — core tables)

```sql
-- tenancy
firms            (id, name, plan, created_at)
users            (id, firm_id, name, email, role)  -- role: admin|coordinator|attorney|viewer

-- core entities
nurses           (id, firm_id, full_name, country_of_chargeability, dob,
                  email, phone, source, assigned_coordinator_id, attorney_id,
                  employer_id, destination_state, priority_date, current_summary)
employers        (id, firm_id, name, state, primary_contact, contract_terms)

-- pipeline
stage_defs       (id, code, label, sort_order, default_sla_days)
stage_instances  (id, nurse_id, stage_def_id, status,           -- not_started|in_progress|blocked|complete
                  started_at, completed_at, sla_due, blocker_reason)
tasks            (id, nurse_id, stage_instance_id, title, owner_id,
                  due_date, status, source)                      -- source: manual|ai|sla

-- documents
documents        (id, nurse_id, doc_type, file_ref,             -- file_ref = SharePoint/OneDrive URL
                  status, issue_date, expiry_date,
                  extracted_json, verified, uploaded_at)
-- doc_type enum: passport, diploma, transcript, home_license, cgfns_ces,
--   ielts, oet, nclex_att, nclex_result, state_license, visascreen,
--   i140_receipt, ds260, medical_exam, police_clearance, marriage_cert, other

-- visa bulletin
vb_snapshots     (id, month, category, country, final_action_date, filing_date, captured_at)

-- comms + audit
communications   (id, nurse_id, channel, direction, audience,   -- audience: nurse|employer|attorney|internal
                  subject, body, drafted_by_ai, sent_at, sent_by)
events           (id, firm_id, nurse_id, type, payload_json, actor, created_at)
```

---

## 4. AI modules (where Claude does real work, not CRUD)

Each is a discrete prompt pattern callable from n8n. Keep them small, typed, and reviewable.

1. **Document intake & extraction.** Nurse uploads a pile of PDFs → classify `doc_type`, extract structured fields (names, doc numbers, issue/expiry dates), and **cross-validate** (name spelling/order consistent across passport, license, diploma — a top real-world failure point). Output JSON → `documents.extracted_json`. Flag mismatches and missing/expiring docs.
   - *Prompt skeleton:* "You are a document analyst for an immigration ops system. Classify this document and return ONLY JSON: {doc_type, fields:{...}, expiry_date, name_as_written, confidence, flags:[...]}. Do not infer beyond the document."

2. **Visa Bulletin monitor + impact analysis.** On each monthly bulletin, parse final-action/filing dates by category+country, write to `vb_snapshots`, then compare every nurse's `priority_date` + `country_of_chargeability` → flag who just became **current**, who's within ~90 days, and draft the notification. (Retrogression is the long pole — this is the single highest-value automation.)

3. **Next-best-action engine.** Given a nurse's stage_instances + outstanding docs/tasks, output the blocking item and the recommended next step, per stage. Powers the "what do I do today" coordinator view.

4. **Tri-audience status drafting.** Generate the same update in three registers — for the **nurse** (plain, encouraging), the **employer** (milestone + timeline), the **attorney** (precise, doc-level). Marked draft-for-review.

5. **Document-chase comms.** Draft outreach to nurses for missing/expiring docs, tone-matched, optionally in the nurse's language. Queue to `communications`, send via Graph on approval.

6. **Risk/anomaly flags (scheduled).** License expiring before PD likely current · IELTS/OET past ~2-yr validity · passport expiry inside processing window · NCLEX ATT window closing · stage past SLA. Each flag → task + notification.

---

## 5. n8n flows to build

- `flow:doc_uploaded` — webhook on upload → call module 1 → write `documents` → fire flags.
- `flow:visa_bulletin_monthly` — scheduled (monthly) → fetch/parse bulletin → module 2 → notifications.
- `flow:daily_sla_expiry_sweep` — cron daily → module 6 → create tasks + Teams/email alerts.
- `flow:inbound_email` — Graph subscription → parse nurse replies/attachments → attach to nurse record.
- `flow:status_update_request` — on demand → module 4 → draft three updates.
- `flow:chase_missing_docs` — on flag → module 5 → draft + queue.

---

## 6. Integrations

- **MS Graph (M365):** email send/receive, SharePoint/OneDrive doc storage, Outlook calendar (NCLEX/embassy/medical dates), Teams alerts.
- **Visa Bulletin:** scrape/parse travel.state.gov monthly (or a structured mirror). Store snapshots.
- **CGFNS / NCLEX / state boards:** mostly no clean public API — model as **status fields + document uploads + manual confirmation**, not live integrations, for MVP. Don't over-engineer this.

---

## 7. Phased build plan

**Phase 1 — replace the spreadsheet (the wedge / demo).**
Multi-tenant auth · nurse + employer records · the 12-stage state machine · document repository with AI intake/extraction + expiry tracking · pipeline board (every nurse by stage, blockers visible) · **Visa Bulletin monitor with auto-flagging**. This alone is the "holy crap" demo for a firm on spreadsheets.

**Phase 2 — make it move work.**
AI comms drafting (chase + tri-audience updates) · task engine + SLAs · two-way M365 email sync · next-best-action coordinator view.

**Phase 3 — scale + sell.**
Employer (client) portal · nurse self-service upload portal · analytics (time-in-stage, bottleneck reporting, cohort throughput) · billing/seats for multi-firm SaaS.

---

## 8. Security, compliance, UPL

- **Heavy PII:** passports, immigration status, civil docs, possibly medical-exam data. Encrypt at rest + in transit, strict RBAC, full audit log (`events`), defined retention policy.
- **Tenant isolation:** enforce `firm_id` scoping on every query; never let cross-tenant data leak. This is non-negotiable for SaaS.
- **Law-firm adjacency:** data sits next to attorney-client material. Respect confidentiality and conflict walls; isolate per firm.
- **UPL guardrail:** every legally-substantive AI output is a **draft for attorney review**, never advice to the nurse. Bake this into prompts and UI copy.
- Not classically HIPAA (you're not a covered entity), but treat the data with equivalent seriousness.

---

## 9. Claude Code kickoff

Drop this spec in the (Conduit build) repo root as `SPEC.md` and start with:

> "Read `SPEC.md`. Scaffold Phase 1 only: a multi-tenant Postgres schema per §3, a Node API with `firm_id`-scoped RBAC, and a React pipeline board showing nurses by stage with blockers. Stub the Claude API document-intake module (§4.1) and the Visa Bulletin monitor (§4.2) as n8n-callable HTTP endpoints with typed JSON contracts. Use environment variables for all secrets. Don't build Phases 2–3 yet."

Then iterate module-by-module. Build the Visa Bulletin monitor early — it's the highest-value, most demoable piece.

---

## 10. Open decisions for you

1. **Multi-tenant SaaS vs. bespoke single-firm tool** — drives the auth/data-isolation work. Spec assumes multi-tenant; say the word to collapse it.
2. **Recruiters vs. law firms as ICP** — same engine, different buyer and emphasis (recruiters care about throughput/placement; firms care about deadline/compliance). Pick the first wedge.
3. **Front-end speed vs. control** — React (this spec) gives you a sellable product; Retool/Airtable gets a working internal pilot in days. If the goal is a fast pilot with Ana's firm to validate, consider Retool for Phase 1, React once it's proven.

## 11. Watch — reference for the drafting layer
- **Mike** ([mikeoss.com](https://mikeoss.com), `Open-Legal-Products/mike`, OSS, self-hostable — Harvey/Legora alternative; Will Chen) — a legal-AI platform doing document review, grounded citations, case-law research, and end-to-end contract drafting/editing. **Reference, not a dependency:** when Conduit builds its "for attorney review" drafting layer (the UPL-guardrailed core, §"produces drafts and flags, never legal determinations"), Mike is worth reading for how a self-hostable legal-AI stack structures grounded/cited drafting — the same shape as our draft-for-review requirement, and self-hostable fits the tenant-isolation/PII posture. **Does not change the stack** (still Claude API for reasoning/drafting); it's a design reference for the drafting + citation pattern. **UPL guardrail unchanged** — counsel gate #9 (`processes/counsel-gates.md`) governs any real-data pilot; Mike is not legal advice and does not relax the "not the lawyer" rule. Triaged 2026-07-20 (`decisions/2026-07-05_tool-triage.md` §Addendum 07-20 11-repo batch).
