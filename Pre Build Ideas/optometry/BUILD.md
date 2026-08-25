# Exam OS — optometry practices (build 27)

**Working name:** Exam OS · **Launch:** `prebuild-exam-os` · **Port:** 8847

## The idea

An optometry practice compounds on the annual exam: patients lapse, the optical capture rate
quietly decides the P&L, and the inbox occasionally contains a retinal detachment describing
itself in plain English. Exam OS runs the recall engine, counts capture honestly, and hard-stops
the emergencies and the prescription shortcuts.

**Buyer:** the owner-OD / practice manager. Thinks in exams, capture rate, recall.

## The bleeding neck

- Lapsed patients: the annual exam that quietly became a 26-month gap.
- "Flashes and a dark curtain since last night" sitting in a message queue is permanent vision
  loss on a timeline of hours.
- Contact reorders against expired prescriptions: a compliance problem dressed as convenience.

## Modules

1. **Message triage** (Intake) — typed ocular emergencies (flashes/floaters with curtain or
   shadow, sudden vision loss, chemical splash — with the irrigate-now instruction — trauma,
   painful red eye with contact lens wear) route **immediately** with the right instruction.
   Clinical questions route unanswered.
2. **Recall engine** (Customer) — lapsed patients on a bounded ladder (the dental/vet pattern).
3. **Capture board** (Sales) — exams → optical purchase, counted with a floor; walkouts counted.
4. **Rx discipline** (Company Brain) — a reorder against an expired Rx is refused (*an exam renews
   a prescription, not a message*); `modify_rx` is R0; and per the FTC Eyeglass Rule posture the
   system never *withholds* an Rx either — the release drafts on request.

## Guardrails (load-bearing)

- `clinical_answer` — **R0.**
- `modify_rx` / `refill_expired_rx` — **R0**, structural.
- `withhold_rx` — **R0.** The patient's prescription is the patient's.
- The eval's costly class is a missed ocular emergency.

## ROI model

Reactivated lapsed patients → revenue (their show rate × exam+capture value) · capture lift →
revenue (their number) · recall hours → time saved · emergency routing → scenario.

## Build prompt (§8)

Build `Pre Build Ideas/optometry/build/` on `_kit/`. Stdlib, JSON store, 127.0.0.1:8847, launch
`prebuild-exam-os`. Seed "Clearwater Eye Care": ~8,200 patients with exam dates and Rx expiries,
optical purchase records, messages incl. every emergency type. Eval costly class = missed ocular
emergency. Tests pin the emergency routes with their instructions, the expired-Rx refusal, the
never-withhold rule, ladder bounds, the capture floor, ROI blanks.
