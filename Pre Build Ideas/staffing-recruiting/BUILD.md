# 9 · Staffing & Recruiting Agencies — **Redeploy OS**

*Pre-build. Not built, not sold, no client. See `../_README.md` for the shared build contract.*

## 1. The idea in one paragraph

A staffing agency's most valuable asset is the database it already paid for — every candidate it sourced, screened, placed, and then forgot. Meanwhile it sources fresh candidates for every new req, submits too slowly to win the ones it does fill, and lets assignments end without a redeployment conversation, which is the single cheapest revenue in the industry. **Redeploy OS** flips the default: when a req lands, it mines the agency's own ATS first and produces a ranked shortlist with reasons within minutes; it screens and schedules conversationally so submissions go out in hours not days; it watches every active assignment's end date and starts the redeploy motion three weeks out; and it tracks credential and compliance expiries so a placed worker is never pulled off site for an expired document. Every ranking is explainable, and **the AI never rejects anyone** — it ranks with reasons and a recruiter decides.

## 2. Who buys it

The **owner or ops lead** of a 5–60 person staffing agency — light industrial, healthcare, skilled trades, IT contract, or admin — $2M–$40M in revenue, running Bullhorn / JobDiva / Crelate / Avionté. They live on submission-to-interview ratio, time-to-submit, and redeployment rate, and they know their database is a graveyard.

## 3. The bleeding neck

- **Sourcing what they already have.** Recruiters go to the job boards because searching their own ATS is worse than starting over. Every re-source is money spent twice.
- **Time to submit.** In contingent staffing the first credible submission frequently wins. Hours matter, and screening + scheduling + packet assembly takes days.
- **Assignment-end blindness.** An assignment ends Friday and nobody talked to the worker on Monday. That worker takes a job elsewhere and the agency re-sources a replacement it already had.
- **Credential expiry.** In healthcare and regulated industrial work, an expired certification means a worker pulled off site, a billing gap, and an unhappy client.
- **Candidate ghosting.** Poor communication cadence during the process; candidates disappear between screen and start date.

## 4. What we build

**Pillars:** Sales (2) + Intake (1) + Operations (5) + People (8). **Form factors:** headless automation (mining, watchtowers) + digital employee (the screener/scheduler) + embedded surface (the desk board).

| Module | What it does | Autonomy start |
|---|---|---|
| **Database-first shortlist** | On a new req, search the agency's own ATS before any external source: skills, verified experience, geography, pay-rate history, availability signal, prior client fit and performance notes. Produces a **ranked list with a stated reason per candidate**, plus an explicit "and here is who we do *not* have" gap statement. | R1 (recruiter decides), always |
| **Screen & schedule** | Conversational screening against the req's must-haves, availability and rate expectation capture, interview scheduling against the client's calendar, and reminder cadence to stop ghosting. | R2 for scheduling and logistics, R1 for anything evaluative |
| **Submission packet** | Assembles the submittal — formatted résumé, screening notes, rate, availability, credential status — in the client's preferred format. Time-to-submit is a first-class metric. | R1 |
| **Redeploy watchtower** | Every active assignment carries an end date; at T-21 days it opens a redeploy record, starts the worker conversation, and searches open reqs for a fit. Redeployment rate is measured. | R1 → R2 for the initial outreach |
| **Credential tracker** | Certifications, licenses, screenings and client-specific onboarding requirements with expiry dates; escalates before the lapse, not after. | R2 to warn, R1 to contact a client |
| **Desk board** | Open reqs with time-to-submit, submissions in flight, assignments ending in 30 days, credentials expiring in 30 days, redeployment rate — counted or blank. | — |

**Integrations:** Bullhorn / JobDiva / Crelate (candidates, reqs, submissions, placements), SMS + email, calendar, background/credential vendor seam.

## 5. The ROI model (assumption-stated)

```
Redeploy value   = assignments ending/mo × redeploy% gained × gross margin per placement × avg duration
Source savings   = reqs/mo × external sourcing cost avoided × database-fill%
Speed value      = time-to-submit reduced → win% (from THEIR OWN submission history)
Compliance       = lapses/yr avoided × cost per lapse (billing gap + client remediation)
```

Redeployment is the honest headline: it is the highest-margin revenue in staffing because the candidate is already sourced, screened and proven. Speed-to-win must be computed from the agency's own submission history or shown blank.

## 6. The demo path (10 minutes)

1. Desk board: 18 open reqs, average time-to-submit, 11 assignments ending in 30 days, 4 credentials expiring, redeployment rate.
2. A new req at 4:50pm → database-first shortlist in seconds, seven candidates ranked **with a reason each**, plus the honest gap statement ("we have nobody with the forklift certification within 25 miles").
3. The screening conversation, the scheduling, the packet — with time-to-submit stamped.
4. The redeploy board: an assignment ending in 19 days, the worker conversation started, two matching open reqs surfaced.
5. A credential expiring in 12 days → escalation before the lapse.
6. Event log, rungs, counted automation rate, and the ranking explainability view.

## 7. Guardrails

**The AI never rejects a candidate and never makes a hiring decision** — it ranks with explicit, inspectable reasons and a recruiter decides. Ranking inputs are restricted to job-related factors, and the code must exclude protected characteristics and their obvious proxies by construction, with a written note that a real deployment needs an adverse-impact review and counsel sign-off (EEOC/Title VII exposure is real, and several states now regulate automated employment decision tools). Pay-rate history is used for candidate fit, never to suppress an offer where salary-history use is restricted. Every ranking is auditable after the fact — that audit trail is the product's defense and its selling point.

---

## 8. The prompt

> Copy everything below into a fresh chat in this workspace.

---

**Build a pre-built vertical AI OS prototype for staffing and recruiting agencies. Working name: Redeploy OS.**

Build it into `Pre Build Ideas/staffing-recruiting/build/`. This is an yourco pre-build: a demoable prototype on synthetic data, not a production system, never touching real candidate data. Read `CLAUDE.md`, `processes/ai-os-modules.md` and `processes/autonomy-matrix.md`, then read `Pre Build Ideas/property-management/build/core.py` and mirror its architecture and honesty rules exactly.

**The business you are modelling.** A 19-person light-industrial and skilled-trades staffing agency: ~$14M revenue, ~340 workers on assignment, an ATS of ~11,000 candidates of whom maybe 2,000 are genuinely reachable, ~45 open reqs at a time, ~30 assignments ending each month, running Bullhorn. Model credentials (forklift, OSHA 10, welding certs, background and drug screens) with expiry dates, client-specific onboarding requirements, pay/bill rates and gross margin per placement. A staffing owner should recognize their own desk in the seed.

**The database is the asset. Build these six:**

1. **Database-first shortlist.** When a req lands, search the agency's own ATS *before* anything external: skills, verified experience, geography and commute, pay-rate history, availability signal, prior client fit and recorded performance. Output a ranked list with **a stated reason per candidate**, plus an explicit gap statement naming what the database does *not* contain — because "we have nobody within 25 miles with that certification" is more valuable than a padded list.
2. **Screen and schedule.** Conversational screening against the req's must-haves, capturing availability and rate expectation; interview scheduling against the client's calendar; a reminder cadence designed to stop ghosting between screen and start date.
3. **Submission packet.** Assemble the submittal in the client's preferred format — formatted résumé, screening notes, rate, availability, credential status. **Time-to-submit is a first-class recorded metric** from req receipt to submission.
4. **Redeploy watchtower.** Every active assignment carries an end date. At T-21 days open a redeploy record, start the worker conversation, and search open reqs for a fit. Measure redeployment rate as a counted number.
5. **Credential tracker.** Certifications, licenses, screenings and client-specific onboarding requirements with expiries, escalating *before* the lapse with the billing impact named.
6. **Desk board.** Open reqs with time-to-submit, submissions in flight, assignments ending in 30 days, credentials expiring in 30 days, redeployment rate — each counted from recorded events or shown blank with a reason.

**The employment-decision guardrail is load-bearing and must live in `core.py` as a rule, not a prompt string.** The system **never rejects a candidate and never makes a hiring decision** — it ranks with explicit, inspectable reasons and a recruiter decides. Ranking inputs are restricted to job-related factors by construction: exclude protected characteristics and their obvious proxies (name-derived inference, age or graduation-year inference, ZIP-code-as-proxy beyond genuine commute distance, gaps interpreted as character). Build a **ranking explainability view** that shows exactly which factors moved each candidate, because that audit trail is both the legal defense and the sales pitch. Write into the README that real deployment requires an adverse-impact review and counsel sign-off, and note that automated employment decision tools are regulated in a growing number of jurisdictions.

**Architecture.** Python stdlib only. `core.py` holds every rule: candidate, req, assignment and credential models; the matching and ranking scorer with its permitted-factor list enforced in code; commute math; the redeploy trigger calendar; credential expiry logic; submission state machine; and the autonomy matrix. `agents.py` holds the agents with a declared rung per action. `seed.py` generates the agency at any scale (`--candidates 11000 --months 24`) including stale records, candidates with mixed performance notes, assignments ending across the next 60 days, credentials at every expiry distance, and a submission history rich enough to compute time-to-submit against outcomes. `data/` is a JSON store. `app/` is the surfaces on a stdlib server bound to `127.0.0.1`; add the `.claude/launch.json` entry and verify it responds.

**The two honesty rules, enforced in `core.py`:** (1) any number not computable from recorded events returns `None` with a `_missing` reason and renders as `unmeasured — <reason>`; (2) every state change appends to an immutable event log with actor and rung, and the automation rate is counted from it.

**ROI panel:** redeploy value, sourcing savings, speed value and compliance value from the agency's own inputs, arithmetic on screen, labelled a MODEL. The speed-to-win line must compute from **their own submission history** or render blank — no industry statistic. Redeployment is the honest headline; say why (candidate already sourced, screened and proven) in one line on the panel.

**Moat layer:** approval gate as the R1 floor on every evaluative action and every client-facing message; an eval harness scoring shortlist quality against a labelled set you generate — and separately reporting whether excluded factors ever influenced a ranking, which must be zero; audit log view; rung promotion only on a recorded streak, with evaluative actions explicitly excluded from promotion.

**Data:** synthetic only — invented candidate, client and certification-body names, 555 phone ranges, no real résumés, no outbound network calls. Stub Bullhorn/JobDiva/Crelate, SMS/email, calendar and the background/credential vendor behind adapter interfaces; a missing adapter reports `cannot-simulate`, a blocker, not a pass.

**White-label:** the demo agency's brand only — no yourco name, logo, or agent names on any candidate- or client-facing surface.

**Tests:** `test_redeploy_os.py`, stdlib asserts, pinning: no agent action can set a candidate to rejected; excluded factors never influence a ranking score; every ranked candidate carries a reason; the gap statement appears when the database genuinely lacks a match; a credential inside its expiry window always escalates; the speed-to-win ROI line returns `None` without recorded outcomes; the event log is append-only.

**Deliverables:** the running build, the launch.json entry, a build `README.md` with the 10-minute demo script (desk board → a 4:50pm req shortlisted from the database with reasons and an honest gap → screen/schedule/packet with time-to-submit stamped → a redeploy opened at T-19 → a credential escalation → the ranking explainability view → event log), and an honest "what this does not do yet." Report the test count and everything it refuses to compute.

Do not send anything, do not deploy, do not use a real agency's, candidate's or client's name.
