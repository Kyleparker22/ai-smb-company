# Rehab OS — build 26

Pre-built vertical AI OS for physical therapy clinics.
Spec: [`../BUILD.md`](../BUILD.md) · shared engine: [`../../_kit/`](../../_kit/).

```bash
python3 seed.py             # 3 clinics, ~950 plans of care, ~7,900 visits
python3 test_rehab_os.py    # 37 assertions
```

Launch name **`prebuild-rehab-os`** (port 8846, 127.0.0.1 only).

## What it is

"Riverbend Physical Therapy" — 3 clinics, $3.4M. Three modules: **message triage**,
**dropout watch**, **authorization watch**.

## The refusals it is organised around

**The red-flag stop.** Five typed red flags — cauda equina signs, DVT signs, cardiac symptoms
during exercise, new neuro deficits, post-op infection — each reaching a clinician immediately
with ER language: *the front desk is not a triage nurse.* Clinical questions ("should I push
through the pain") route to the treating therapist **unanswered**. Eval costly class = missed red
flag (*MEASURED IN HOURS OF PERMANENT DAMAGE*), recall 1.0.

**Booking past authorization is never silent.** Visits used vs authorized at the *patient* level
(the over-auth lesson from build 10). Over auth → refused with the stake named ("unbillable work
or an audit finding") AND queued for a human to take to the payer. No auth recorded → refused,
*never assumed unlimited*. `bill_beyond_authorization` is R0. Recert dates are date alerts.

Also: `modify_plan_of_care` R0 (only the treating therapist), `promise_outcome` R0, the dropout
watch on the two-signal floor (no-shows, cancellations, gap, behind-plan), and a cancellation
records the dropout signal it is.

## 10-minute demo

Board → Inbox (the bladder-control message → clinician + ER language; soreness → unanswered) →
Dropout watch → Authorizations (book all three demo patients: over — refused to payer queue; no
auth — refused; within — R1 draft) → ROI → Trust.

## What this does not do yet

- **No integrations.** EMR (WebPT/Prompt-class), clearinghouses, reminders are adapter seams.
- **Triage is deterministic pattern-matching** — a real deployment puts a model behind the routine
  path and leaves the red-flag stop exactly as it is.
- **No clinical content of any kind** — by design, permanently.
- **Nothing is sent.**
