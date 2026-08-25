# Unit OS — build 16

Pre-built vertical AI OS for multi-unit restaurant groups.
Spec: [`../BUILD.md`](../BUILD.md) · shared engine: [`../../_kit/`](../../_kit/).

```bash
python3 seed.py            # 6 units, 72 inventory periods, 63 messages
python3 test_unit_os.py    # 29 assertions
```

Launch name **`prebuild-unit-os`** (port 8836, 127.0.0.1 only).

## What it is

"Verano Taqueria Group" — 6 units, $11M. Three modules: **message & review triage**,
**variance watchtower**, **unit scorecard**.

## The refusals it is organised around

**Four message classes get no drafted reply at all**: an illness claim, an allergen incident, an
allergen *question*, and health-department contact. Each escalates to a human at R2 with the R0
refusal logged — *"software drafts nothing, admits nothing."* The eval's costly class is a
dangerous message read as routine: *AN ADMISSION IN A FUTURE LAWSUIT.* Recall 1.0, zero missed.
The allergen question is deliberately its own class — the wrong "yes it's gluten-free" from a bot
is an ambulance, so trained staff answer, never software.

**Variance is never estimated.** Theoretical-vs-actual food cost computes only where inventory
counts exist; the unit that skipped counts reads *unmeasured — last month's number is not this
month's.* `estimate_variance` is R0.

## 10-minute demo

Board → Inbox (the carnitas message: escalated, nothing drafted; the mole question: refused; the
cold burrito: R1 draft) → Variance (Westgate unmeasured, University flagged with dollars) →
Scorecard → ROI → Trust.

## What this does not do yet

- **No integrations.** POS (Toast/Square), inventory (MarketMan/Craftable), review platforms are
  adapter seams.
- **Triage is deterministic pattern-matching** — a real deployment puts a model behind the
  complaint path and leaves the four hard stops exactly as they are.
- **No recipe costing engine** — theoretical cost arrives as a recorded input.
- **Nothing is sent.**
