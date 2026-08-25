# Decision — Add "Conduit" (IEN immigration ops platform) as an YourCo offering

**Date:** 2026-06-18 · **Owner:** the Founder · **Status:** Offering added; pre-build (spec parked, no pilot signed)

## What it is
A vertical AI ops platform that runs the end-to-end pipeline for bringing an internationally-educated nurse (IEN) to the US on an employer-sponsored **EB-3 Schedule A** green card. It replaces the spreadsheets-and-email chaos that small immigration firms and boutique nurse recruiters run on today — a per-nurse 12-stage state machine (sourcing → credentials → English → NCLEX → licensure → VisaScreen → I-140 → visa-bulletin wait → consular/AOS → medical/civil → POE → onboard/retain) that monitors itself for deadlines, expiries, and visa-bulletin retrogression.

Working name **Conduit** (placeholder). Full build spec: [offerings/conduit/SPEC.md](../offerings/conduit/SPEC.md).

## Why it fits YourCo (and how it's framed)
This is the **custom AI OS** — YourCo's primary product — applied to a high-value vertical. It is offered as an **operated vertical platform**: YourCo builds *and runs* it (reliability, eval, observability, multi-tenant isolation, the UPL guardrail), and the firm gets an outcome. The buyer never touches tokens, models, or infra — the defining principle holds.

**On the "multi-tenant SaaS" language in the spec:** that describes the *asset shape* (one codebase serving many firms), not a self-serve go-to-market. Self-serve SaaS stays parked (`01_company.md`) because it deletes the moat by handing firms the eval risk. Conduit is operated, so the moat holds. If it ever drifts toward pure self-serve, that re-opens the parked-SaaS question — flag at that point.

**Moat alignment is unusually strong here:** the spec is dominated by exactly YourCo's defensible layer — UPL guardrails ("draft for attorney review," never a legal determination), eval/anomaly flags, reliability on a 2–4 year process, tenant isolation, full audit log, heavy-PII handling. This is precisely what no-code operators cannot deliver.

## How it runs through the delivery loop
Standard audit-first → build → operate. The **paid Audit** maps the firm's current pipeline chaos (where placements leak: missed license-expiry, visa-bulletin movement, document mismatches). The **build** is the platform; **operate** is ongoing monitoring + weekly iteration. The "holy crap" demo (per the spec) is the **Visa Bulletin monitor with auto-flagging** + the pipeline board replacing the spreadsheet — build that first.

## Stack note (vs. YourCo's locked stacks)
Spec stack: **n8n** (orchestration) · **Postgres** (system of record) · **Claude API** (extraction/drafting/next-action) · **MS Graph / M365** (email, SharePoint, calendar) · **React** (front-end). This is a text/ops platform — **no voice**, so the Vapi voice stack (`2026-06-08`) does not apply. **n8n is new** to the documented platform; if Conduit proceeds, decide whether n8n becomes a sanctioned orchestration tool or whether this maps onto the existing runtime pattern.

## UPL / compliance (non-negotiable)
Every legally-substantive AI output is a **draft for attorney review**, never advice to the nurse — baked into prompts and UI copy. Heavy PII (passports, immigration status, civil/medical-exam docs): encrypt at rest + in transit, strict RBAC, full audit log, retention policy, hard `firm_id` tenant isolation. Data sits adjacent to attorney-client material → respect confidentiality/conflict walls. Counsel review before any pilot that touches real client data (mirrors the yourco Care "counsel before launch" gate).

## Open decisions for the Founder (from spec §10)
1. **Multi-tenant SaaS vs. bespoke single-firm tool** — drives auth/isolation work. Spec (and this doc) assume multi-tenant/operated; collapse to single-tenant only if this is a bespoke internal tool for one firm.
2. **ICP wedge: recruiters vs. law firms** — same engine, different buyer. Recruiters optimize throughput/placement; firms optimize deadline/compliance. Pick the first wedge (shapes positioning + the demo emphasis).
3. **Pilot front-end: React vs. Retool** — React = sellable product (slower); Retool/Airtable = working pilot with Ana's firm in days to validate, then React once proven.

## Status / next steps
- Offering recorded; spec parked at `offerings/conduit/SPEC.md`.
- Pre-revenue, pre-pilot. Candidate pilot: "Ana's firm" (the Founder's domain SME is an employee there, per spec — interview to get workflow right; sell to the principal who owns P&L).
- No build until the Founder resolves the three open decisions above and a pilot is lined up.

## Related
[[2026-06-16_caregiving-dtc-offering]] (the other named non-core offering — also operated, also counsel-gated) · `01_company.md` (parked self-serve rationale) · `02_delivery_loop.md`.
