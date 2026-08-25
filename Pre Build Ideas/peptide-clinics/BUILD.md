# Protocol OS — cash-pay peptide & longevity clinics (build 74)

**Working name:** Protocol OS · **Launch:** `prebuild-protocol-os` · **Port:** 8897

## The idea

The generic clinic pitch is *you miss calls*. True, and not where the money is. In a cash-pay
program business **revenue is retention**: a patient on a protocol either continues or quietly
stops, and the clinic usually finds out a month later by noticing the refill never happened.

So this build is organised around the **cycle**, not the funnel — who is due, who is lapsing, who
went quiet after a dose change — with an inbox that never mistakes a symptom for admin.

**Buyer:** clinic owner / medical director. Thinks in active patients, cycles, and continuation.

## The bleeding neck

- **Quiet churn.** Nobody is watching each patient's own interval, so a lapse is discovered late.
- **The quiet stop after a change** — a dose changes, the patient goes silent, nobody calls.
- **The inbox mixes a receipt request with a swelling face**, and the second cannot wait.
- Labs get resulted and sit unreviewed.

## Modules

1. **Inbox triage** (Intake) — six typed urgent signals stop everything. Clinical questions route
   **unanswered**. Admin is handled.
2. **The cycle** (Customer) — due / overdue / lapsing computed from each patient's **own** interval
   and **own** last fill, never an assumed cadence.
3. **Quiet after a change** (Customer) — dose changed, nothing heard since. Carries **no message
   draft on purpose**: it is a prompt for a person to call.
4. **Labs waiting** (Operations) — resulted and unreviewed, the quietest liability in the building.

## Guardrails (load-bearing)

- `clinical_advice` · `adjust_dose` · `interpret_labs` — **R0, all unpromotable.**
- `contact_excluded` — **R0.** A patient who stopped for a medical reason, had an adverse event,
  opted out, transferred or died is **outside every sweep by construction** — the query never loads
  them, so it is not a filter that can be forgotten.
- Every patient-facing message is **R1** and contains no dose or clinical content.
- Eval costly class: **a reaction filed as a refill request.**

## ROI model

Lapsing patients continued → revenue · quiet-after-change calls that land → revenue (the clinician's
work, not the software's) · inbox and refill-chasing hours → time saved · urgent routing → **scenario**
(patient-safety routing is never monetized by us).

## 10-minute demo

Board (lapsing / overdue / continuation rate — the retention frame, not the funnel) → Inbox: the
swelling-face message (clinician now, verbatim instruction), then the dose question (routed
unanswered) → The cycle: draft a nudge, then try one on a discontinued patient and watch it refuse →
Quiet after a change (no draft — a person calls) → Trust: try to change a dose → ROI.

## Build prompt (§8)

Build `Pre Build Ideas/peptide-clinics/build/` on `_kit`. Stdlib, JSON store, 127.0.0.1:8897, launch
`prebuild-protocol-os`. Seed "Ardenwood Longevity": ~260 patients across active / lapsed / the five
never-contact statuses, protocols with real intervals and last fills, some with a recent dose change
and silence after it, 34 messages spanning urgent / clinical / admin, lab panels resulted and
unreviewed. Eval costly class = an urgent message filed as admin. Tests pin every typed urgent
signal, the structural exclusion at query level, all four R0s, drafts carrying no clinical content,
the cycle computing off each patient's own interval, and every ROI blank.
