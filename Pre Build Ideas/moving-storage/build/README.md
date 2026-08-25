# Move OS — build 22

Pre-built vertical AI OS for moving & storage companies.
Spec: [`../BUILD.md`](../BUILD.md) · shared engine: [`../../_kit/`](../../_kit/).

```bash
python3 seed.py            # ~300 moves, condition records, claims
python3 test_move_os.py    # 34 assertions
```

Launch name **`prebuild-move-os`** (port 8842, 127.0.0.1 only).

## What it is

"Beacon Hill Moving & Storage" — 11 trucks, $4.8M. Four modules: **quote desk**, **the charge
clamp**, **claims desk**, **message triage**.

## The refusals it is organised around

**A binding estimate cannot be issued without a recorded survey and inventory** — *a guess is not
a binding number.* The refusal names what's missing.

**Final charges = binding estimate + signed change orders, by construction.** An unsigned change
order is excluded and named on the invoice: *"a conversation, not a charge."* There is no argument
to `final_charges()` that produces a higher number — the anti-hostage-load rule, and
`condition_delivery_on_extra_payment` is R0: *the industry's shame; this system cannot express it.*

**A claim is assessed on the load + delivery condition pair** — missing either, the system asserts
nothing *in either direction* (a pre-existing scratch honestly reads "no new damage"). The
acknowledgment clock starts at the report under a rule set that names itself a default; every date
is a DATE ALERT.

Eval costly class = missed claim report (*ONE-STAR REVIEWS AND, INTERSTATE, REGULATORY EXPOSURE*),
recall 1.0.

## 10-minute demo

Board → Inbox (the cracked-leg report: clock starts, evidence check runs) → Quotes & charges
(binding without survey — refused; with survey — R1 draft; final charges with the unsigned CO
excluded and named) → Claims (both demo assessments) → ROI → Trust.

## What this does not do yet

- **No integrations.** Moving software (SmartMoving/Supermove-class), tariffs, payments are
  adapter seams.
- **Triage is deterministic pattern-matching** — a real deployment puts a model behind the routine
  path and leaves the clamp and the survey rule exactly as they are.
- **Claim rules are simplified shapes** — counsel replaces them (federal clocks interstate).
- **Nothing is sent.**
