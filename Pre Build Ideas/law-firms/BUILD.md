# 6 · Law Firms (Personal Injury · Family · Small Litigation) — **Case OS**

*Pre-build. Not built, not sold, no client. See `../_README.md` for the shared build contract.*

## 1. The idea in one paragraph

A plaintiff's firm loses money in two places that have nothing to do with lawyering. The first is the **first ten minutes**: injured people call several firms, and the one that answers, screens, and gets a retainer in front of them first usually keeps the case. The second is the **records chase**: a personal-injury case cannot be valued or demanded until the medical records and bills are in hand, and getting them means months of faxes, portals, per-provider quirks, prepayment demands, and follow-ups that a paralegal does by hand. **Case OS** runs both — a 24/7 intake with conflict check and criteria-based screening that ends in an e-signed retainer, and a records engine with a per-provider playbook that requests, tracks, pays, escalates and receipts every record until the file is complete — plus the third thing every bar association complains about most: **clients who don't know what's happening**, fixed by automatic status updates drawn from case events.

## 2. Who buys it

The **managing attorney** of a 2–15 attorney contingency-fee firm — PI, workers comp, mass tort intake, or a family-law practice with the same intake dynamics. $1M–$10M in fees, running Filevine / Litify / Smokeball / MyCase / Clio. They already spend heavily on lead acquisition, which makes speed-to-lead an easy arithmetic conversation, and they feel the records chase as *the* reason cases take two years.

## 3. The bleeding neck

- **Speed to signed retainer.** The lead is shopped. Nights and weekends are when accidents happen and when firms are closed.
- **Screening quality.** Intake staff either sign cases the firm can't win or turn away good ones, because the criteria live in a partner's head.
- **The records chase.** Per-provider request formats, HIPAA authorization requirements, prepayment, custodial delays, incomplete productions that nobody notices until the demand is being drafted. This is the single biggest schedule risk in a PI case.
- **Client silence.** The #1 source of bar complaints is failure to communicate. Cases sit for months with no client contact, and a client who feels ignored is a client who switches firms.
- **Demand assembly.** Building the demand package — records index, bills summary, treatment chronology, lost-wage documentation — is days of paralegal assembly per case.

## 4. What we build

**Pillars:** Intake (1) + Operations (5) + Customer (4). **Form factors:** digital employee (intake) + headless automation (records + status) + embedded surface (the case board).

| Module | What it does | Autonomy start |
|---|---|---|
| **Intake** | 24/7 call/text/form. Runs a **conflict check** first, then screens against the firm's written criteria (case type, jurisdiction, statute-of-limitations proximity, liability facts, treatment status, insurance coverage), captures the incident narrative, and sends the retainer for e-signature. Declines are referred out with a documented reason. | R2 to screen and book; **R1 hard floor** on anything legal |
| **Records engine** | Per-provider playbook: correct request format, authorization requirements, prepayment handling, expected turnaround. Tracks every request through a state machine, follows up on its own schedule, verifies the production against what was requested, and flags gaps (missing date ranges, missing billing, illegible pages). | R2 for standard requests, R1 for anything with money or authorization |
| **Chronology + demand assembly** | Builds the treatment chronology and bills summary from received records, indexes exhibits, and drafts the demand's factual sections **for attorney review**. | R1, permanently drafting |
| **Client status** | Turns case events into plain-language updates on a guaranteed cadence, so no client goes dark — with the attorney approving anything substantive. | R1 → R2 for the "nothing has changed, here's why" update |
| **Case board** | Every case, its stage, its blocker, days since last client contact, records completeness %, and statute-of-limitations proximity — the last two in red where the data is missing rather than assumed fine. | — |

**Integrations:** Filevine / Litify / Clio (matters, contacts, docs), e-signature, phone/SMS, fax-to-digital for records, and a records-retrieval vendor seam.

## 5. The ROI model (assumption-stated)

```
Speed-to-lead     = after-hours leads × incremental sign% × avg case fee
Screening quality = declined-but-qualified rescued + signed-but-unqualified avoided (both counted, not assumed)
Records cycle     = avg days to complete file reduced → cases resolved per year per attorney
Paralegal time    = requests + follow-ups + chronology hours × loaded rate
```

Case-fee assumptions in contingency work are wide and lumpy. The panel must present avg case fee as an **editable input with the firm's own number**, must never use a published settlement statistic, and must state plainly that faster cycle time changes *when* fees arrive as much as *whether* they do.

## 6. The demo path (10 minutes)

1. Case board: 62 open cases, four past their client-contact threshold, two with statute proximity under 90 days, one records-completeness figure blank and labelled.
2. A 11:40pm call after a rear-end collision → conflict check → screened against criteria → retainer e-signed before morning.
3. A caller asking "do I have a case?" → refused and routed to an attorney, visibly.
4. The records board: 140 open requests across 38 providers, six flagged as incomplete productions with the specific gap named.
5. A demand package draft with the chronology assembled and every fact cited to an exhibit page.
6. Event log, rungs, counted automation rate.

## 7. Guardrails

**No legal advice, no case-value opinions, no fee discussions beyond the published fee agreement, no guarantees.** This is the UPL rule from `offerings/conduit/SPEC.md` applied to a plaintiff's practice: the system drafts *for attorney review* and routes anything substantive to a licensed attorney, unanswered. Conflict check runs **before** any substantive intake, and a potential conflict is a hard stop. Statute-of-limitations proximity is **flagged, never calculated as advice**. Client PII and PHI (records are PHI) are handled under minimum-necessary with an access log; live deployment requires counsel review, and the prototype is synthetic-only. No recording without state-appropriate consent language.

---

## 8. The prompt

> Copy everything below into a fresh chat in this workspace.

---

**Build a pre-built vertical AI OS prototype for plaintiff-side law firms (personal injury, with family-law intake as a secondary mode). Working name: Case OS.**

Build it into `Pre Build Ideas/law-firms/build/`. This is an yourco pre-build: a demoable prototype on synthetic data, not a production system, never touching real client data. Read `CLAUDE.md`, `processes/ai-os-modules.md`, `processes/autonomy-matrix.md`, and the UPL constraint in `offerings/conduit/SPEC.md`, then read `Pre Build Ideas/property-management/build/core.py` and mirror its architecture and honesty rules exactly.

**The business you are modelling.** A six-attorney personal-injury firm: ~$4M in annual fees, ~310 open matters, ~90 new leads/month across phone, web form and text with a heavy nights-and-weekends skew, four paralegals, running Filevine. Model auto, premises and dog-bite case types with written intake criteria, a provider universe of ~40 medical facilities each with its own records quirks, and matters at every stage from intake to demand. A managing attorney should recognize their own docket in the seed.

**Two bottlenecks are the product; a third is the retention insurance. Build these five:**

1. **24/7 intake.** Handles call, text and form at any hour. **Runs the conflict check first** — a potential conflict is a hard stop before any substantive conversation. Then screens against the firm's *written* criteria (case type, jurisdiction, statute proximity, liability facts, treatment status, available coverage), captures the incident narrative in the caller's own words, and sends the retainer for e-signature. Declines are referred out with a documented reason so the firm can audit its own screening later.
2. **Records engine.** A per-provider playbook: request format, authorization requirements, prepayment handling, expected turnaround, escalation contact. Every request is a state machine (drafted → sent → acknowledged → prepaid → produced → verified → complete) that follows up on its own schedule. Verification is the valuable part: compare what arrived against what was requested and flag gaps — missing date ranges, missing billing, illegible pages, wrong patient — rather than marking it complete.
3. **Chronology and demand assembly.** Build the treatment chronology and bills summary from received records, index exhibits, and draft the demand's factual sections **for attorney review**, with every fact cited to an exhibit and page. A fact that cannot be cited is omitted and listed as unsupported — never written anyway.
4. **Client status.** Turn case events into plain-language updates on a guaranteed cadence, including the honest "nothing has changed this month, and here is why that is normal at this stage" update. Track days-since-last-client-contact as a first-class metric.
5. **Case board.** Every matter: stage, blocker, days since client contact, records completeness percentage, statute proximity. Where completeness cannot be computed, show it blank with the reason — never assume a file is complete.

**The UPL guardrail is load-bearing and must live in `core.py` as a rule, not a prompt string.** The system gives no legal advice, no case-value opinions, no liability assessments, no fee discussion beyond the published agreement, and no guarantees. "Do I have a case?" is routed to a licensed attorney *unanswered*, and that refusal must be demonstrable in the demo. Statute-of-limitations proximity is flagged as a date-based alert, explicitly not as legal advice. Every AI output touching legal substance is labelled for attorney review.

**Architecture.** Python stdlib only. `core.py` holds every rule: the matter and stage model, intake criteria evaluation, conflict-check logic, the provider playbook and records state machine, production-verification rules, chronology construction, contact-cadence thresholds, and the autonomy matrix. `agents.py` holds the agents with a declared rung per action. `seed.py` generates the firm at any scale (`--matters 310 --months 24`) including leads arriving at 2am, borderline screening cases, providers that stall, incomplete productions, and matters that have gone quiet with clients. `data/` is a JSON store. `app/` is the surfaces on a stdlib server bound to `127.0.0.1`; add the `.claude/launch.json` entry and verify it responds.

**The two honesty rules, enforced in `core.py`:** (1) any number not computable from recorded events returns `None` with a `_missing` reason and renders as `unmeasured — <reason>` — records completeness especially must never be assumed; (2) every state change appends to an immutable event log with actor and rung, and the automation rate is counted from it.

**ROI panel:** speed-to-lead, screening quality, records cycle time, paralegal hours — from the firm's own inputs, arithmetic on screen, labelled a MODEL. Average case fee is an editable input using the firm's own number; never use a published settlement statistic. State plainly that cycle-time gains change *when* fees arrive as much as whether they do.

**Moat layer:** approval gate as the R1 floor on every outward message and every records request that involves money or an authorization; an eval harness scoring intake screening against the written criteria and production-verification against a labelled set you generate, reporting the false-"complete" rate separately because that error causes a bad demand; audit log view; rung promotion only on a recorded streak.

**Confidentiality posture:** client PII and medical records are PHI. Minimum-necessary handling, access log, and a README note that live deployment requires counsel review and appropriate agreements — which this prototype sidesteps by using synthetic records only.

**Data:** synthetic only — invented client, provider and insurer names, 555 phone ranges, no outbound network calls, no fax. Stub Filevine/Litify/Clio, e-signature, telephony and the records-retrieval vendor behind adapter interfaces; a missing adapter reports `cannot-simulate`, a blocker, not a pass.

**White-label:** the demo firm's brand only — no yourco name, logo, or agent names on any client-facing surface.

**Tests:** `test_case_os.py`, stdlib asserts, pinning: the conflict check runs before any substantive intake and a hit is a hard stop; "do I have a case" is always routed unanswered; a records production with a missing date range can never be marked complete; a demand fact without an exhibit citation is omitted and listed; records completeness returns `None` when unknowable; the event log is append-only; no outward action executes above its declared rung.

**Deliverables:** the running build, the launch.json entry, a build `README.md` with the 10-minute demo script (case board → 11:40pm intake to e-signed retainer → a legal question refused → records board with six flagged productions → a cited demand draft → event log), and an honest "what this does not do yet." Report the test count and everything it refuses to compute.

Do not send anything, do not deploy, do not use a real firm's, client's or provider's name.
