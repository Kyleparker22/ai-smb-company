# Arrangement OS — build 25

Pre-built vertical AI OS for funeral homes.
Spec: [`../BUILD.md`](../BUILD.md) · shared engine: [`../../_kit/`](../../_kit/).

```bash
python3 seed.py                   # 2 locations, 60 cases, a full GPL, pre-need
python3 test_arrangement_os.py    # 31 assertions
```

Launch name **`prebuild-arrangement-os`** (port 8845, 127.0.0.1 only).

## What it is

"Hartwell & Sons Funeral Home" — 2 locations, ~380 cases/yr. Four modules: **first-call triage**,
**GPL-grounded quote desk**, **document chase**, **pre-need ledger**.

## The refusals it is organised around

**A first call reaches the on-call director immediately.** The system captures logistics — where,
who, callback number — and says nothing else. `automate_grief_support` is R0: *compassion is not a
template; every human word comes from a human.* Eval costly class = missed first call (*A FAMILY
FAILED AT THE WORST MOMENT*), recall 1.0.

**No GPL, no numbers.** Every quote is itemized from the recorded General Price List; an off-list
item refuses the whole quote; bundles always show their items. `quote_off_gpl` is R0 — the Funeral
Rule runs on the list, and so does this system.

Also: `handle_remains_decision` R0 (software never touches disposition), `pressure_sale_at_need`
R0 (no upsell language toward a grieving family, ever), permits carry date alerts ("a service date
depends on this"), the document ladder is bounded, and unfunded pre-need contracts read
*unmeasured, not assumed*. The ROI panel never frames an answered 2am call as revenue.

## 10-minute demo

Board (date-sensitive permits) → Calls (the first call: director paged, logistics only) → Quote
desk (itemized quote; the off-list refusal) → Cases & documents → ROI → Trust.

## What this does not do yet

- **No integrations.** Case management (Passare/Osiris-class), state EDRS, answering service are
  adapter seams.
- **Triage is deterministic pattern-matching** — a real deployment puts a model behind the routine
  path and leaves the first-call priority and all four R0s exactly as they are.
- **Nothing is sent.**
