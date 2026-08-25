# Plate OS — catering & events (build 28)

**Working name:** Plate OS · **Launch:** `prebuild-plate-os` · **Port:** 8848

## The idea

A caterer's failures are all coordination failures with a date attached: the menu change that
never reached the kitchen, the space double-booked for two rehearsal dinners, the final count that
grew on the invoice, and the nut-allergy note handled by whoever read it. Plate OS makes the
Banquet Event Order the single locked truth of the day, refuses the conflicts structurally, and
hard-stops the allergen conversations.

**Buyer:** the owner/director of catering. Thinks in events, per-head margin, and the horror of a
wrong plate on the day.

## The bleeding neck

- BEO drift: a change agreed by phone at T-24h that the kitchen never saw.
- Double-booking a space or crew — discovered when two parties arrive.
- "One guest has a severe nut allergy" answered casually is an ambulance at the reception.
- Final-count disputes: billed 180, guaranteed 150, no record of the 30.

## Modules

1. **Inquiry & message triage** (Intake) — allergen/dietary-medical notes route to a trained human
   **with no answer drafted**; new inquiries get availability from the calendar; change requests
   route to BEO control.
2. **BEO change control** (Operations) — outside the 72-hour lock window a change drafts normally
   (R1). **Inside the window a change is never auto-applied** — it queues for a human with the
   kitchen impact named, because the kitchen has already ordered and prepped.
3. **The calendar** (Operations) — booking a space already booked that date is **structurally
   refused**; capacity overruns refuse with the number.
4. **Final-count billing** (Back Office) — the invoice computes from the recorded guaranteed count
   plus recorded additions; a bill above that cannot be produced.

## Guardrails (load-bearing)

- `answer_allergen_question` — **R0.** Trained humans handle allergy conversations.
- `auto_apply_locked_change` — **R0**, structural via the lock window.
- `double_book_space` — **R0**, structural via the calendar check.
- `bill_above_final_count` — **R0**, structural via the billing clamp.

## ROI model

Inquiries answered fast → revenue (their close rate) · BEO-error cost avoided → scenario ·
coordination hours → time saved · allergen discipline → scenario (never a saving).

## Build prompt (§8)

Build `Pre Build Ideas/catering-events/build/` on `_kit/`. Stdlib, JSON store, 127.0.0.1:8848,
launch `prebuild-plate-os`. Seed "Juniper & Rye Catering": ~420 events across the year, 4 spaces,
BEOs with items and final counts, messages incl. allergen notes and late changes. Eval costly
class = missed allergen/dietary-medical signal. Tests pin the lock window, the double-booking
refusal, the billing clamp, the allergen R0, ROI blanks, counted automation.
