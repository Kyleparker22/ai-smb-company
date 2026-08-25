# Visit OS — veterinary practices (build 13)

**Working name:** Visit OS · **Launch:** `prebuild-visit-os` · **Port:** 8833

## The idea

A 2–4 doctor small-animal practice runs full but leaks in three places: patients quietly lapse off
their preventive schedule (the practice's compounding revenue base), same-day cancellations leave
exam rooms dark while a waitlist exists, and the phone/inbox mixes "can I book a nail trim" with
"my dog ate a bar of baker's chocolate" — and the second one cannot wait in a queue.

**Buyer:** practice owner / practice manager. Thinks in active patients, ADT, and doctor-hours.

## The bleeding neck

- Lapsed patients: overdue vaccines, heartworm/flea preventives, annuals — found by nobody because
  reminders die after one postcard.
- Cancellations at 8am leave 2pm dark with a waitlist ten deep.
- Message triage: an emergency read an hour late is a dead patient and a lawsuit.

## Modules

1. **Message triage** (Intake) — typed emergency signals (toxin ingestion, GDV signs, blocked cat,
   breathing, collapse, seizure, hit-by-car) route to a human **immediately** with the ER
   instruction shown. Clinical questions route to a DVM **unanswered**. Quality-of-life and
   euthanasia conversations are **never** handled by software.
2. **Reactivation** (Customer) — lapsed patients on a bounded reminder ladder. **A deceased or
   transferred patient is never contacted** — this is the vertical's unforgivable failure and it is
   designed out structurally, not filtered late.
3. **Slot backfill** (Operations) — cancellation → ranked waitlist candidates (species, doctor,
   visit-length fit), booking drafts at R1.
4. **The counted board** — lapse counts by what's due, backfill rate, triage eval, all counted.

## Guardrails (load-bearing)

- `clinical_answer` — **R0.** Dosing, meds, "is this normal" → a DVM answers.
- `qol_conversation` — **R0.** Euthanasia and quality-of-life talk is a human conversation, always.
- `contact_deceased` — **R0**, and the sweep cannot reach non-active patients by construction.
- Emergency instruction verbatim on every crisis route: *"If this is an emergency, go to the
  nearest emergency animal hospital now — do not wait for a reply."*
- Safety routing is never monetized in the ROI panel.

## ROI model

Reactivated lapsed patients → revenue (their show rate, their avg visit) · backfilled slots →
revenue (counted cancellations) · reminder/phone hours → time saved · after-hours coverage →
scenario.

## 10-minute demo

Board → inbox: the chocolate message (ER instruction, human, nothing assessed), the dosing question
(routed unanswered), the QoL message (human, gently) → reactivation list with the deceased-patient
proof → cancel a slot and watch the waitlist rank → ROI → trust.

## Build prompt (§8)

Build `Pre Build Ideas/veterinary/build/` on `_kit/`. Stdlib, JSON store, 127.0.0.1:8833, launch
`prebuild-visit-os`. Seed "Brookhollow Veterinary Clinic": 3 DVMs, ~2,400 patients (dogs/cats, a
few exotics), statuses including deceased/transferred, due dates across the calendar, a waitlist,
messages including every crisis type. Eval costly class = missed emergency. Tests pin the crisis
routes, the R0s, the deceased-patient exclusion, ladder bounds, ROI blanks, counted automation.
