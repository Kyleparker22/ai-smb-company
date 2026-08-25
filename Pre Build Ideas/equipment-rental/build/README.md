# Yard OS — build 15

Pre-built vertical AI OS for equipment rental houses.
Spec: [`../BUILD.md`](../BUILD.md) · shared engine: [`../../_kit/`](../../_kit/).

```bash
python3 seed.py            # ~645 units, ~900 rentals, 1,400 condition records
python3 test_yard_os.py    # 35 assertions
```

Launch name **`prebuild-yard-os`** (port 8835, 127.0.0.1 only).

## What it is

"Blue Heron Equipment Rental" — $9M, 8 classes. Four modules: **off-rent integrity**,
**call triage**, **damage evidence**, **the yard board**.

## The refusal it is organised around

**Billing stops at the recorded off-rent call — by construction.** `billable_days()` has no
argument that can produce a day after the call; asking the invoice to bill "through next week"
clamps to the call and names the clamp: *"the days past it do not exist."* Recording the call is
R2 because delaying the record is the harm; `backdate_off_rent` is R0 — the record is the record.

**A damage charge requires the evidence pair.** Checkout AND check-in condition records, or the
system says *cannot assert damage* with the missing record named. Pre-existing damage is never
charged. The evidenced claim drafts at R1 with the photos counted on the row.

Also: the **standing-limit waiver** — goodwill credits under $100 execute at R2 and log; the same
action above the limit demotes to the approval gate, with the limit named. Utilization refuses any
class whose fleet denominator is missing. The eval's costly class is a missed off-rent call
(*"AN OVERBILLED INVOICE, A DISPUTE, AND A CUSTOMER SHOPPING YOUR COMPETITOR"*), recall 1.0.

## 10-minute demo

Board (pickup queue = the yard leak, utilization with a refused class) → Calls (handle the 4:50pm
off-rent; the clock stops at the call's own timestamp) → Billing integrity (bill through +7d —
clamped) → Damage evidence (both demo cases) → the waiver limit → ROI → Trust.

## What this does not do yet

- **No integrations.** Rental management (Point of Rental/Texada), telematics, and payments are
  adapter seams.
- **Call triage is deterministic pattern-matching** — a real deployment puts a model behind it and
  keeps the billing clamp and evidence rule exactly as they are.
- **No dispatch optimisation, no telematics-based hours.**
- **Nothing is sent.**
