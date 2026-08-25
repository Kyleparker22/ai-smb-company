# Sample Client — engagement

> **Stage:** `demo-proposal` — mirrored from `crm/data.json`, which owns it. Do not edit this by hand; change the CRM and this follows. `runtime/consistency-check.py` fails if the two disagree.


**yourco's first real client engagement.** Proposal sent June 2026; **still at Proposal, not signed — pre-revenue.** **The engagement is the Same-Day Design Studio / Field-to-Quote platform — full stop** (the Founder 2026-08-10). The June Installation Proposal Automation concept was a different, earlier proposal — **parked**, revisit only if Client Owner raises it. the Founder committed a v1 walkthrough for the week of 2026-08-10.

## Who
- **Client:** Sample Client Design & Build — hardscaping / design-build, installation + maintenance + fencing. Yourtown, ST (15300 Holbrooks Rd). sampleclient.example.com. Runs on **Aspire** (core: pricing/job costing) + **HubSpot** (pipelines/reporting) + SiteOne, Moasure, VIP3D.
- **Decision-maker:** the Client Owner (owner). Warm network — the Founder's "brotherhood" relationship.
- **The team in the workflow:** Colton (design/estimating — the platform's daily user), Noah (operations — approves labor + means-and-methods), Charlene (intake/admin — collects surveys, enters labor), Corey (fencing sales, sells on-site).

## The deal (CRM: company c11, deal d11)
- **Lead use case (since 2026-08-06):** the Design Studio platform — photos + ground-truth measurements → scaled 2D + renders → ballpark quote on-site → Colton confirms in Aspire in 2–3 days (vs their 6–8 week cycle). Spec: `meetings/2026-08-06_design-sales-workflow-meeting.md`.
- **Parked (was the original June proposal):** Installation Proposal Automation — post-signature comms drafting. Not the focus (the Founder 2026-08-10); `prototype/` kept as historical dry-run only.
- **Pricing (brotherhood):** kickoff **$0** (standard $5,000), retainer **$1,000/mo** (standard $3,500); OS packaging per `decisions/2026-07-22_southern-cut-os-pricing.md`. In return: case study, testimonial, referrals.
- **Next:** send the data-request email (`meetings/2026-08-07_followup-email-draft.md`), run the walkthrough, close on the $1,000/mo start.

## The docs (this folder — one client, one folder)
- `01_discovery.md` … `03_setup-plan-and-tech.md` — original spec, June proposal, build plan
- `04_instant-range-concept.md` / `05_leadgen-postcards-concept.md` — concept modules (instant-range became the Design Studio; postcards pairs with it post-install)
- `06_os-module-roadmap.md` + `07_proposal-os.md` / `proposal-os.html` (:8800) — the full-OS pitch, `enterprise-value-builder.html`
- `meetings/` — meeting digests + send-ready follow-up drafts
- **`platform/`** — the merged **Design Studio + Field-to-Quote platform** (:8804): measurement ground truth, 2D board, quote engine, SC-voice scopes, Noah's approval gate, client-safe Design Studio view (`decisions/2026-08-07_southern-cut-one-platform.md`)
- `prototype/` — the June dry-run agent (10/10 tests, sample data) + mockup walkthrough (:8794); `prototype/design-studio/` — the cinematic pitch page (:8799, retired to sales-demo)
- `attachments/` — original PDFs (Client Owner's flowchart, proposal, setup plan, instant-range)
- `cost.md` — spend ledger (all discovery/CAC until signature)

## How the OS works this client (agents across the whole process)
Per the Founder 2026-08-07 (pattern set on Sample Realty): agents help end-to-end. Internal names — never on client-facing surfaces:
- **David / CRM** — c11 + d11 + activity log stay current; every session that ships something for Client Owner logs an activity row.
- **Polo** — owns the pricing posture (brotherhood terms locked; OS-tier packaging when modules stack). No prices on public surfaces.
- **Janice** — onboarding at signature: intake start items (Aspire API key, Workspace seat, Twilio, signed 1-pager), provision access.
- **Kimi** — delivery loop once live (weekly iteration cadence); **the Founder holds and runs engagement #1 personally until the playbook hardens.**
- **Kolby** — eval: platform QA before every Client Owner-facing walkthrough, and (once Aspire actuals land) the quote-accuracy loop — estimated-vs-actual becomes the platform's self-tuning benchmark, which is the moat demo.
- **Reed** — visual production: design renders, the follow-up videos (`agents/Reed/productions/`), Design Studio imagery. Credibility gate applies — nothing fabricated.
- **Rafi** — guardrails: the client-safe view boundary (no costs/margins ever client-side), approval gates (nothing sends without a human), NC811/utility disclaimers in scopes.
- **Ray** — counsel gate on the signed 1-page agreement before any live-data/production wiring.
- **Charles** — `cost.md` roll-up at weekly pulse + monthly close; watches CAC on this unsigned deal.
- **Atlas + runtime loops** — activation-gated at go-live per `runtime/activation-triggers.md`: production error sweep, then per-module watchdogs (quote-staleness/72h validity, sub-quote chase, availability-report ingestion).

## Open items (updated 2026-08-18)
- ✅ **Integration board ALL GREEN (2026-08-18):** HubSpot live (private app, contacts/deals r/w scopes) · **Aspire live** (dedicated read-only "Sample Client Design Studio" API record, Select-All-GET scopes — matched Client ID+Secret pair was the fix; write scopes added post-signature) · Shepherd's auto-pulling (public site) · SiteOne/Ewing/Latham/Kirk Davis credentialed (export→CSV paths) · availability inbox = colton@sampleclient.example.com (dedicated seat at go-live). Credentials in gitignored `platform/.env`; registry `runtime/connectors.md`.
- ⏳ Gemini render key: built+verified, waiting on Google crediting the prepayment (risk-flagged trial; watcher polling, fires first render automatically).
- Remaining data asks to Client Owner: labor benchmark list, stock rules, Moasure sample files, 2–3 priced designs (Aspire history can now come via API instead of manual export).
- Walkthrough call — close the $1,000/mo start on it; signed 1-pager opens Ray's gate for live data flows (Aspire actuals pull, HubSpot stage sync, write-back scopes).
- Next builds: Aspire actuals ingestion via the live API · "+ Custom" board element · render-queue drain loop.
