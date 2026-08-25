# 10 · Home Health & Private-Duty Senior Care — **Shift OS**

*Pre-build. Not built, not sold, no client. See `../_README.md` for the shared build contract.*

## 1. The idea in one paragraph

A home-care agency's entire business runs through one recurring emergency: it is 6:12am, a caregiver just called out of a 7am shift with a client who needs help getting out of bed, and a scheduler has forty minutes to find someone qualified, available, close enough, and acceptable to that client and family. Do it well and the agency keeps the client and the caregiver. Do it badly and it loses both — caregiver turnover in this industry is famously brutal, and a family that gets a stranger with no notice starts shopping. **Shift OS** runs the fill as a ranked, explainable, cost-aware engine; watches the caregiver-retention signals that predict the *next* callout; keeps EVV and documentation exceptions from becoming billing problems; and closes the loop the family actually judges the agency on — a proactive update, before they call to complain.

## 2. Who buys it

The **owner or director of operations** of a private-duty / non-medical home care agency or a small home-health agency, $1.5M–$20M, 60–400 caregivers, running WellSky / AxisCare / ClearCare / AlayaCare. This is also the operated-B2B mirror of yourco's DTC **yourco Care** offering (`decisions/2026-06-16_caregiving-dtc-offering.md`) — the same domain, the same guardrails, sold to the agency instead of the family. Whichever validates first informs the other.

## 3. The bleeding neck

- **The callout.** The 6am scramble, solved by whoever the scheduler can reach, not by who fits best. Overtime cost is discovered on Friday.
- **Caregiver churn.** Turnover in this sector runs high, and every departure costs recruiting, onboarding, and often a client. The predictive signals — hours drift, cancelled shifts, longer commutes, no contact from the office — are all in the system and nobody watches them.
- **Referral-source response speed.** Hospital discharge planners and case managers send the referral to whoever answers. Slow response is lost census.
- **EVV and documentation.** Missed clock-ins, incomplete care notes, and visit exceptions that turn into billing denials and payroll disputes.
- **Family anxiety.** The family's confidence is built or destroyed by communication. Most agencies communicate only when something is wrong.

## 4. What we build

**Pillars:** Operations (5) + Intake (1) + Customer (4) + People (8). **Form factors:** headless automation (fill engine, watchtowers) + digital employee (referral intake) + embedded surface (the ops board + family view).

| Module | What it does | Autonomy start |
|---|---|---|
| **Fill engine** | On a callout, rank available caregivers by a defensible composite: certification and skill match to the care plan, client/family preference and history, travel time, continuity (has worked this client), **overtime cost impact**, and recent hours. Contact in waves with the reason for the ask, never a blast. Every ranking is explainable. | R2 within pre-approved caregiver/client pairings; **R1 for any new pairing** |
| **Retention watchtower** | Watches the predictive signals — hours below preference, cancelled shifts, commute creep, no office contact in N days, missed pay expectations — and surfaces a ranked weekly list of caregivers at risk with the specific signal, for a human conversation. | R1, always human contact |
| **Referral desk** | Answers referral sources (discharge planners, case managers, families) fast, captures the care need and payer/authorization basics, checks coverage feasibility, and books the assessment. Never clinical. | R2 for logistics; **R1 hard floor** on anything clinical |
| **EVV & documentation exceptions** | Missed clock-in/out, visits without notes, incomplete tasks, and authorization-vs-delivered-hours drift — each typed, with the billing and payroll consequence named. | R2 to flag, R1 to contact anyone |
| **Family loop** | A proactive, plain-language update on a guaranteed cadence — who is coming, what happened this week, what changed — approved by a human before it goes. | R1 |
| **Ops board** | Unfilled shifts in the next 72 hours with client risk, overtime exposure this week, caregivers at retention risk, EVV exceptions, authorization drift — counted or blank. | — |

**Integrations:** WellSky / AxisCare / ClearCare / AlayaCare (clients, caregivers, schedules, EVV), SMS, payroll seam, state EVV aggregator seam.

## 5. The ROI model (assumption-stated)

```
Fill value      = unfilled shifts/wk × fill% gained × revenue per shift × margin
Overtime        = OT hours/wk × premium × avoidable% (from ranked-fill choices actually taken)
Turnover        = departures/yr × replacement cost (recruit + onboard + lost client risk) × prevention%
Billing         = EVV/doc exceptions/mo × denial rate × avg visit value
```

Turnover prevention is the most seductive line and the least provable — it must be presented as a **scenario driven by their own departure history**, with the prevention percentage as a visible, editable assumption, and a plain statement that prevented departures cannot be counted.

## 6. The demo path (10 minutes)

1. Ops board at 6:12am: one unfilled 7am shift flagged high-risk (client needs transfer assistance), overtime exposure for the week, four caregivers at retention risk.
2. The fill: eleven candidates ranked with reasons — continuity, travel time, certification, **and the two that would trigger overtime shown with the cost** — wave one texted, filled in nine minutes, ranking explainable after the fact.
3. A message from a family asking whether mom's medication dose should change → clinical stop, routed to the nurse, visibly unanswered by the AI.
4. Retention list: a caregiver whose hours dropped 30% over three weeks and who has had no office contact in 26 days → conversation staged for a human.
5. EVV exceptions with the billing consequence named per line.
6. Event log, rungs, counted automation rate.

## 7. Guardrails

**No clinical advice of any kind** — no medication guidance, no dosing, no symptom interpretation, no care-plan changes. This is the highest-stakes vertical on the list and the guardrail is stricter than elsewhere: clinical content routes to a licensed nurse, over-routing is the deliberate bias, and **any crisis signal (fall, chest pain, confusion, self-harm, suspected abuse) routes to a human immediately with the emergency instruction shown**. Mandatory-reporting obligations are flagged to a human, never handled by the system. PHI under HIPAA with minimum-necessary access and an audit log; live deployment requires counsel and a BAA. EVV requirements are state-specific and the build must model them as configurable rules, never hardcode one state's. No caregiver is ever auto-assigned to a client pairing that has not been approved.

---

## 8. The prompt

> Copy everything below into a fresh chat in this workspace.

---

**Build a pre-built vertical AI OS prototype for private-duty home care and small home-health agencies. Working name: Shift OS.**

Build it into `Pre Build Ideas/home-health-care/build/`. This is an yourco pre-build: a demoable prototype on synthetic data, not a production system, never touching real patient or caregiver data. Read `CLAUDE.md`, `processes/ai-os-modules.md`, `processes/autonomy-matrix.md`, and `decisions/2026-06-16_caregiving-dtc-offering.md` (the DTC sibling of this domain — the guardrails there apply here), then read `Pre Build Ideas/property-management/build/core.py` and mirror its architecture and honesty rules exactly.

**The business you are modelling.** A private-duty agency: ~$6.5M revenue, 210 caregivers, 140 active clients, ~2,600 shifts/week including overnights and weekends, a mix of private-pay and Medicaid-waiver authorizations, running AxisCare. Model care plans with real task categories (transfer assistance, bathing, meal prep, medication *reminders* only, companionship, transportation), caregiver certifications and skills, client and family preferences, commute geography, pay and bill rates, overtime thresholds, and authorization limits. A scheduler should recognize their own Monday in the seed.

**The 6am callout is the product thesis. Build these six:**

1. **Fill engine.** On a callout, rank available caregivers by a defensible composite: certification and skill match to *this* care plan, client and family preference and history, continuity, travel time, recent hours, and **overtime cost impact shown explicitly**. Contact in waves with a personal reason for the ask — never a mass blast — and stop the moment it's filled. Every ranking must be explainable after the fact, and time-to-fill is a recorded metric. **A caregiver is never auto-assigned to a client pairing that has not been previously approved** — that is R1 and a test must prove it.
2. **Retention watchtower.** Watch the predictive signals already in the data — hours below the caregiver's stated preference, cancelled shifts, commute creep, no office contact in N days, shifts declined in a row — and produce a ranked weekly at-risk list with the *specific* signal, for a human conversation. The system never messages a caregiver about retention itself.
3. **Referral desk.** Answer referral sources fast (discharge planners, case managers, families), capture the care need and payer/authorization basics, check feasibility against caregiver coverage in that geography, and book the assessment. Response latency to a referral source is recorded, because that is what wins census.
4. **EVV and documentation exceptions.** Missed clock-in/out, visits without notes, incomplete tasks, authorization-vs-delivered-hours drift — each typed, with the **billing and payroll consequence named** on the line. Model EVV rules as configurable per state; never hardcode one state's requirements.
5. **Family loop.** A proactive plain-language update on a guaranteed cadence — who is coming, what happened this week, what changed — human-approved before sending.
6. **Ops board.** Unfilled shifts in the next 72 hours ranked by client risk, overtime exposure this week, caregivers at retention risk, EVV exceptions, and authorization drift — each counted from recorded events or shown blank with a reason.

**The clinical guardrail is the strictest on this list and must live in `core.py` as a rule, not a prompt string.** No medication guidance, no dosing, no symptom interpretation, no care-plan changes, no candidacy or condition opinions — all clinical content routes to a licensed nurse, unanswered, with the routing biased toward over-routing. **Any crisis signal — fall, chest pain, breathing difficulty, sudden confusion, self-harm, suspected abuse or neglect — routes to a human immediately and displays the emergency instruction**, and suspected abuse additionally raises a mandatory-reporting flag for a human, which the system never handles itself. Make both refusals visible in the demo; they are the product, not a limitation.

**Architecture.** Python stdlib only. `core.py` holds every rule: client, caregiver, care-plan, shift and authorization models; the fill-ranking composite with overtime math; approved-pairing enforcement; retention signal definitions and thresholds; EVV rule configuration; the crisis and clinical classifiers; and the autonomy matrix. `agents.py` holds the agents with a declared rung per action. `seed.py` generates the agency at any scale (`--caregivers 210 --clients 140 --weeks 26`) including callouts at realistic hours, caregivers at every stage of retention risk, EVV exceptions of every type, authorizations near their limits, and family messages including clinical and crisis phrasing. `data/` is a JSON store. `app/` is the surfaces on a stdlib server bound to `127.0.0.1`; add the `.claude/launch.json` entry and verify it responds.

**The two honesty rules, enforced in `core.py`:** (1) any number not computable from recorded events returns `None` with a `_missing` reason and renders as `unmeasured — <reason>`; (2) every state change appends to an immutable event log with actor and rung, and the automation rate is counted from it.

**ROI panel:** fill value, overtime avoided, turnover, and billing exceptions from the agency's own inputs, arithmetic on screen, labelled a MODEL. **Turnover prevention must be presented as a SCENARIO** driven by their own departure history, with the prevention percentage as a visible editable assumption and a plain statement that prevented departures cannot be counted. Overtime avoided should be computed from the ranked-fill choices actually taken, not assumed.

**Moat layer:** approval gate as the R1 floor on every family- and client-facing message and every new caregiver/client pairing; an eval harness scoring the clinical and crisis classifiers with **recall reported separately and prominently** (a missed crisis is the worst possible failure), plus fill-ranking quality against a labelled set you generate; audit log view; rung promotion only on a recorded streak, with clinical routing and new pairings permanently excluded from promotion.

**HIPAA posture:** minimum necessary, access audit log, and a README note that live deployment requires counsel review and a signed BAA — which this prototype does not need because every record is synthetic.

**Data:** synthetic only — invented client, caregiver and referral-source names, 555 phone ranges, no real addresses, no outbound network calls. Stub AxisCare/WellSky/ClearCare/AlayaCare, SMS, payroll and the state EVV aggregator behind adapter interfaces; a missing adapter reports `cannot-simulate`, a blocker, not a pass.

**White-label:** the demo agency's brand only — no yourco name, logo, or agent names on any caregiver-, client- or family-facing surface.

**Tests:** `test_shift_os.py`, stdlib asserts, pinning: a crisis phrase always routes to a human and never receives an AI answer; a clinical question is never answered; a caregiver is never assigned to an unapproved pairing by an agent; overtime cost appears on any ranked option that would trigger it; the retention watchtower never messages a caregiver; an uncomputable board metric returns `None` with a reason; EVV rules are configurable and no state's requirements are hardcoded; the event log is append-only.

**Deliverables:** the running build, the launch.json entry, a build `README.md` with the 10-minute demo script (6:12am ops board → a 7am shift filled in nine minutes with an explainable ranking and visible overtime cost → a medication question refused and routed → a crisis message escalated → the retention list with specific signals → EVV exceptions with billing consequences → event log), and an honest "what this does not do yet." Report the test count, the crisis-classifier recall, and everything it refuses to compute.

Do not send anything, do not deploy, do not use a real agency's, client's or caregiver's name.
