# 3 · Dental Practices & Small DSOs — **Chair OS**

*Pre-build. Not built, not sold, no client. See `../_README.md` for the shared build contract.*

## 1. The idea in one paragraph

A dental practice's single largest asset is sitting inside its own software, unscheduled: treatment that was diagnosed, presented, and never booked. Alongside it sit two daily wounds — the hole that opens in tomorrow's schedule when a patient cancels at 7am, and the front-desk hours burned verifying insurance benefits on hold. **Chair OS** attacks all three: a reactivation engine that works the unscheduled-treatment report as a ranked revenue queue, a same-day fill engine that refills a canceled slot from a ranked ASAP list before the chair goes cold, and a benefits pack that assembles tomorrow's verifications before the office opens. The measure is one number the owner already knows: **production per chair-hour**, and how much of tomorrow's is at risk.

## 2. Who buys it

The **owner-dentist** or the operations lead of a 1–6 location practice, $1.2M–$8M production, running Open Dental / Dentrix / Eaglesoft. Open Dental in particular has a genuine API, which makes it the right first target. This buyer is fee-conscious and has been sold to heavily by recall-postcard vendors — the differentiator is that ours computes from their ledger and refuses to invent numbers.

## 3. The bleeding neck

- **Unscheduled treatment.** Every practice's practice-management system holds a report of diagnosed-but-unscheduled procedures. In most offices it is printed occasionally and worked never. It is the highest-margin revenue in the building because the diagnosis and the presentation are already paid for.
- **The 7am cancellation.** A canceled crown seat is production that cannot be recovered later — chair-hours don't bank. Refilling it requires calling the right patient in the right order in the next twenty minutes, which nobody has time to do.
- **Insurance verification.** Hours on hold per week confirming eligibility, frequency limitations, remaining maximums and waiting periods — and when it isn't done, the patient is surprised at checkout, which is where write-offs and bad reviews come from.
- **Recall decay.** Hygiene recall lists rot quietly; the practice discovers it two quarters later as a hygiene-schedule hole.

## 4. What we build

**Pillars:** Operations (5) + Sales (2) + Back Office (6) + Intake (1). **Form factors:** headless automation (verification, reactivation) + embedded surface (the chair board) + digital employee (the scheduling coordinator).

| Module | What it does | Autonomy start |
|---|---|---|
| **Unscheduled-treatment engine** | Ranks every diagnosed-unscheduled procedure by production value × clinical urgency × insurance-benefit expiry × patient responsiveness, then works the queue in the doctor's own clinical language. | R1 (drafts) → R2 |
| **Same-day fill** | On cancellation, builds a ranked ASAP list (procedure fit to the freed time and provider, distance, stated flexibility, history of accepting short notice) and reaches out in waves rather than blasting. | R2 within pre-approved slot classes |
| **Benefits pack** | Assembles tomorrow's verification set — eligibility, remaining maximum, frequency limits, waiting periods, downgrade rules — and produces a per-patient sheet plus an exception list for the humans to call. | R1 |
| **Recall watchtower** | Watches hygiene intervals and benefit-year expiry together, so "your benefits expire in November" is the hook, not "you're due." | R2 |
| **Chair board** | Tomorrow's production, holes and their value, verification exceptions, and this week's recovered production — counted, not asserted. | — |

**Integrations:** Open Dental (API) first, Dentrix / Eaglesoft via their available seams; a claims clearinghouse for eligibility (270/271) where one exists; SMS; the practice's payment link.

## 5. The ROI model (assumption-stated)

```
Unscheduled recovery = unscheduled treatment $ × contact% × acceptance%
Fill recovery        = canceled chair-hours/wk × fill% × production per chair-hour × 48
Verification time    = verifications/wk × minutes each × loaded staff rate
Recall recovery      = overdue patients × reactivation% × annual patient value
```

Verification savings are staff-time, not revenue, and the build must label them as such — an ROI panel that adds hours-saved to dollars-earned is exactly the kind of dishonesty that loses a technical owner-dentist.

## 6. The demo path (10 minutes)

1. Chair board: tomorrow's production, two holes, their dollar value, three verification exceptions.
2. The unscheduled queue — $340k of diagnosed treatment ranked, top ten with the actual procedure and the benefit-expiry hook.
3. A 7:04am cancellation → ranked ASAP list → wave one sent → seat filled by 7:26.
4. The benefits pack for tomorrow, and the three it could not verify, each with a stated reason.
5. Event log + counted automation rate + the eval score on procedure-fit matching.

## 7. Guardrails

**No clinical advice and no diagnosis** — the system moves treatment the dentist already diagnosed and never suggests, upgrades, or interprets clinical findings. **No insurance determinations** — it reports what the payer said and flags what it could not confirm; it never tells a patient what will be covered. HIPAA posture: minimum necessary, access audit log, BAA required before any live data (stated in the README, not glossed). No balance-billing or collections language.

---

## 8. The prompt

> Copy everything below into a fresh chat in this workspace.

---

**Build a pre-built vertical AI OS prototype for dental practices and small DSOs. Working name: Chair OS.**

Build it into `Pre Build Ideas/dental-practices/build/`. This is an yourco pre-build: a demoable prototype on synthetic data, not a production system, never touching real patient data. Read `CLAUDE.md`, `processes/ai-os-modules.md` and `processes/autonomy-matrix.md`, then read `Pre Build Ideas/property-management/build/core.py` and mirror its architecture and honesty rules exactly.

**The business you are modelling.** A two-doctor general practice, $2.4M annual production, four hygiene chairs, ~1,900 active patients, ~$1.05M in diagnosed-but-unscheduled treatment sitting in the ledger, a 9% short-notice cancellation rate, running Open Dental. Build a realistic fee schedule using real procedure categories (exam, prophy, SRP, crown, endo, implant, ortho), a plausible payer mix with different plan rules, and a benefit-year calendar. An office manager should recognize their own Tuesday in the seed.

**Build these four engines — the product is production per chair-hour:**

1. **Unscheduled-treatment engine.** Rank every diagnosed-unscheduled procedure by a defensible score: production value × clinical urgency class × remaining-benefit expiry × patient responsiveness history. Work the queue with drafts written in the treating doctor's clinical language, referencing the actual procedure and tooth, with a bounded ladder that terminates in a recorded outcome (scheduled / declined-with-reason / unreachable).
2. **Same-day fill.** On a cancellation, compute what will actually fit the freed time *and* the freed provider, then build a ranked ASAP list (procedure fit, distance, stated flexibility, history of accepting short notice) and contact in waves — never a blast — stopping the moment the seat is filled. Time-to-fill is a recorded metric.
3. **Benefits pack.** Assemble tomorrow's verification set: eligibility, remaining annual maximum, frequency limitations, waiting periods, downgrade/alternate-benefit rules. Produce a per-patient sheet and an exception list for humans. Anything it could not confirm is reported as unconfirmed with the reason — never inferred from a plan template.
4. **Recall watchtower.** Watch hygiene interval and benefit-year expiry together and use whichever is the honest hook.

Plus a **chair board**: tomorrow's scheduled production, the holes and their dollar value, verification exceptions, and production recovered this week — counted from the event log, never asserted.

**Two guardrails that must live in `core.py` as rules, not prompt text:** (a) the system never diagnoses, never suggests treatment, and never interprets a clinical finding — it only moves treatment a dentist already diagnosed; (b) the system never makes an insurance determination or tells a patient what will be covered — it reports what the payer returned and explicitly flags what it could not confirm. Both refusals must be demonstrable in the demo.

**Architecture.** Python stdlib only. `core.py` holds every rule: fee schedule, procedure taxonomy and chair-time model, the ranking score, plan-rule evaluation, the ladder cadences, the recall interval logic, and the autonomy matrix. `agents.py` holds the agents with a declared rung per action. `seed.py` generates the practice at any scale (`--patients 1900 --months 24`) including a full ledger of diagnosed-unscheduled treatment at varying ages, cancellation events at realistic hours, hygiene recall states, and payer responses including ones that fail to return a benefit. `data/` is a JSON store. `app/` is the surfaces on a stdlib server bound to `127.0.0.1`; add the `.claude/launch.json` entry and verify it responds.

**The two honesty rules, enforced in `core.py`:** (1) any number not computable from recorded events returns `None` with a `_missing` reason and renders as `unmeasured — <reason>`; (2) every state change appends to an immutable event log with actor and rung, and the automation rate is counted from it.

**ROI panel:** four lines — unscheduled recovery, fill recovery, verification time, recall recovery — computed from the practice's own inputs, arithmetic on screen, labelled a MODEL. Staff-time savings must be reported in hours and dollars *separately* from revenue and never summed into one headline number. Any line without a recorded input renders blank with its reason.

**Moat layer:** approval gate as the R1 floor on every patient-facing message; an eval harness scoring procedure-fit matching and benefit-rule evaluation against a labelled set you generate, reporting false-positive rate on "covered" claims separately because that error costs the practice money; audit log view; rung promotion only on a recorded streak.

**HIPAA posture:** minimum necessary, access audit log, and a build README note that live deployment requires counsel and a signed BAA — which this prototype does not have and does not need, because every record is synthetic.

**Data:** synthetic only, 555 phone ranges, invented payer names, no outbound network calls. Stub Open Dental / Dentrix / Eaglesoft, the eligibility clearinghouse, and SMS behind adapter interfaces; a missing adapter reports `cannot-simulate`, a blocker, not a pass.

**White-label:** the demo practice's brand only — no yourco name, logo, or agent names on any patient-facing surface.

**Tests:** `test_chair_os.py`, stdlib asserts, pinning: an unverifiable benefit is never reported as covered; the system refuses to produce a clinical recommendation; an uncomputable ROI line returns `None` with a reason; the event log is append-only; the fill engine never contacts a patient whose procedure cannot fit the freed time; no message sends above its declared rung.

**Deliverables:** the running build, the launch.json entry, a build `README.md` with the 10-minute demo script (chair board → unscheduled queue → 7:04am cancellation refilled → benefits pack with three honest failures → event log), and an honest "what this does not do yet." Report the test count and everything the build refuses to compute.

Do not send anything, do not deploy, do not use a real practice's or payer's name.
