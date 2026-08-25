# Rehab OS — physical therapy clinics (build 26)

**Working name:** Rehab OS · **Launch:** `prebuild-rehab-os` · **Port:** 8846

## The idea

A PT clinic's economics die at visit four: the patient who quits mid-plan-of-care costs the clinic
the remaining eight visits and costs themselves the outcome. Its compliance risk is the visit
scheduled past the authorization, and its clinical risk is the red-flag message — "my leg went
numb after yesterday" — answered like a scheduling note. Rehab OS watches the dropouts on an
honest floor, refuses to book past auth silently, and hard-stops the red flags.

**Buyer:** the owner/clinic director. Thinks in visits, arrivals, plans completed.

## The bleeding neck

- Plan-of-care dropout: prescribed 12, attended 4, gone. Nobody called.
- Visits delivered past the authorization: unbillable work, or an audit finding.
- Red-flag symptoms in the inbox queue: cauda equina signs, DVT signs, cardiac symptoms during
  exercise — minutes matter, and the front desk isn't a triage nurse.

## Modules

1. **Message triage** (Intake) — typed red flags (new numbness/weakness, loss of bladder/bowel
   control, calf swelling + pain, chest pain/breathlessness with exercise, post-surgical fever)
   route to a clinician **immediately** with ER language where warranted. Clinical questions route
   **unanswered**. Cancellations record as the dropout signal they are.
2. **Dropout watch** (Customer) — missed visits, cancellations, gap since last visit,
   behind-schedule vs plan: **two signals make the list**; one is a note.
3. **Authorization watch** (Back Office) — visits used vs authorized at the *patient* level (the
   over-auth lesson from build 10); **booking past authorization is never silent** — it queues for
   a human with the payer named; recert dates are date alerts.

## Guardrails (load-bearing)

- `clinical_answer` — **R0.** "Should I push through the pain" is answered by a clinician.
- `modify_plan_of_care` — **R0.** Only the treating therapist changes a plan.
- `bill_beyond_authorization` — **R0**, structural: unbillable work is refused at booking, not
  discovered at claim denial.
- `promise_outcome` — **R0.** No recovery promises, ever.

## ROI model

Dropouts recovered → revenue (their completion lift × visit value) · auth denials avoided →
scenario · front-desk hours → time saved · red-flag routing → scenario (never monetized).

## Build prompt (§8)

Build `Pre Build Ideas/physical-therapy/build/` on `_kit/`. Stdlib, JSON store, 127.0.0.1:8846,
launch `prebuild-rehab-os`. Seed "Riverbend Physical Therapy": 3 clinics, ~950 plans of care at
every stage incl. dropouts and over-auth patients, messages incl. every red-flag type. Eval costly
class = missed red flag. Tests pin the red-flag routes, the R0s, the booking refusal past auth,
the two-signal floor, recert date alerts, ROI blanks.
