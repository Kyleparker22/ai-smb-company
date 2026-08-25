# Haul OS — build 19

Pre-built vertical AI OS for dumpster / roll-off / waste hauling operators.
Spec: [`../BUILD.md`](../BUILD.md) · shared engine: [`../../_kit/`](../../_kit/).

```bash
python3 seed.py            # 220 containers, 700 orders, 42 charges
python3 test_haul_os.py    # 36 assertions
```

Launch name **`prebuild-haul-os`** (port 8839, 127.0.0.1 only).

## What it is

"Granite City Roll-Off" — $6M, 7 trucks. Three modules: **prohibited-waste triage**, **charge
evidence**, **container board**.

## The refusal it is organised around

**The system can never say yes to a hazardous item.** Ten typed prohibited classes — paint and
solvents, batteries, tires, chemicals, asbestos signals ("popcorn ceiling from the 70s"), propane
and fuel, freon appliances, electronics, medical sharps, mattresses. The classifier is asymmetric
on purpose: it may wrongly send drywall to a human; it may never approve paint. The answer is a
typed refusal with disposal help routed to a human. Eval costly class = hazardous approved
(*A CONTAMINATED LOAD, A REJECTED TIP, AND A FINE*), recall 1.0. Vague contents ("stuff from my
uncle's shed") are unknown — *"probably fine" is how loads get contaminated.*

**A charge without its evidence cannot be asserted.** Overweight needs the scale ticket on file;
contamination needs the photo record. Missing → *cannot assert charge*, logged, never an
approvable row. Evidenced charges draft at R1 with the evidence attached.

Plus the idle-container board (delivered, no pull ordered — every idle day a turn not made; no
delivery date → age *unknowable and says so*) and missed promised pickups, counted.

## 10-minute demo

Board → "Can I toss…?" (the paint question refused with help; drywall yes with the weight caveat)
→ Charges (assert the ticketless one — refused; the ticketed one drafts) → Containers (idle aging,
missed pickups) → ROI → Trust.

## What this does not do yet

- **No integrations.** Dispatch software, scale systems, GPS are adapter seams.
- **Triage is deterministic pattern-matching** — a real deployment puts a model behind the
  routine path and leaves the never-yes rule exactly as it is.
- **No routing/dispatch optimisation.**
- **Nothing is sent.**
