# Plate OS — build 28

Pre-built vertical AI OS for catering & events companies.
Spec: [`../BUILD.md`](../BUILD.md) · shared engine: [`../../_kit/`](../../_kit/).

```bash
python3 seed.py             # ~370 bookings, 4 spaces
python3 test_plate_os.py    # 31 assertions
```

Launch name **`prebuild-plate-os`** (port 8848, 127.0.0.1 only).

## What it is

"Juniper & Rye Catering" — $5.2M, ~420 events/yr. Four modules: **inquiry & message triage**,
**BEO change control**, **the calendar**, **final-count billing**.

## The refusals it is organised around

**The 72-hour lock window.** Outside it, a BEO change drafts at R1. Inside it, a change is
**never auto-applied** — the kitchen has ordered and prepped, so it queues for a human with the
kitchen impact named. A past event cannot be changed at all: *changes are history, not edits.*

**A space is never double-booked** — *two parties at one door is not a scheduling style* — and
capacity overruns refuse with the number.

**The bill = guaranteed count × per-head + recorded additions, by construction.** The unrecorded
verbal add is excluded and named: *a remembered addition is a dispute, not a charge.* No recorded
final count → nothing can be billed against a verbal number.

**Allergen notes get no drafted answer** (the build-16 rule, carried) — a trained human calls;
*the wrong reassurance is an ambulance at the reception.* Eval costly class = missed allergen
note, recall 1.0.

## 10-minute demo

Board (the locked wedding) → Inbox (the nut-allergy note → nothing drafted; the locked-window swap
→ queued with kitchen impact; the open change → drafts) → Calendar (book The Barn on the locked
date — refused) → Final-count billing (the unrecorded add excluded) → ROI → Trust.

## What this does not do yet

- **No integrations.** Catering software (Total Party Planner/Curate-class), POS, payments are
  adapter seams.
- **Triage is deterministic pattern-matching** — a real deployment puts a model behind the routine
  path and leaves the allergen stop and the lock window exactly as they are.
- **No menu costing engine** — per-head rates arrive as recorded inputs.
- **Nothing is sent.**
