# Bay OS — build 12

Pre-built vertical AI OS for independent auto repair shops.
Spec: [`../BUILD.md`](../BUILD.md) · shared engine: [`../../_kit/`](../../_kit/).

```bash
python3 seed.py            # ~1,460 ROs, ~470 declined items
python3 test_bay_os.py     # 39 assertions
```

Launch name **`prebuild-bay-os`** (port 8832, 127.0.0.1 only).

## What it is

"Cedar Ridge Auto Care" — 8 bays, $3.2M. Four modules: **declined-work recovery**, **intake
triage**, **approval watch**, **comeback watch**.

## The refusal it is organised around

**A safety-critical finding can never leave as a text.** Worn brakes, cord-showing tires, tie-rod
play — each becomes a call task for a human with the finding verbatim. Press "Text re-offer" on one
and the system refuses with the rule: *a safety-critical finding is a phone call from a human,
never a marketing text, never softened.* The eval's costly class is a safety item called
deferrable — "THE FAILURE THAT ENDS A SHOP" — recall 1.0, zero missed.

Also load-bearing:
- `state_vehicle_safe` is **R0** — only a technician who inspected the vehicle says "safe."
- `phone_diagnosis` is **R0** — "what's wrong with it?" gets an inspection booked, never a guess.
- Price **bands** come from the shop's own closed ROs (middle half, floor of 6); a firm price is
  R1 and never promotes.
- The re-offer ladder is bounded (3 touches, 45-day cooldown) — silence is an answer.
- The comeback rate is counted (same vehicle, same system, ≤30 days) and refuses below 50 ROs.

## 10-minute demo

Board → Declined work (classify, then try to text the brake item — refusal) → Intake (the
brakes-to-the-floor call, the alternator guess refused) → Comebacks → ROI → Trust.

## What this does not do yet

- **No integrations.** DMS (Tekmetric/Shop-Ware/Mitchell), SMS, phones are adapter seams.
- **Classification is deterministic pattern-matching** — right for the safety stop (auditable,
  biased on purpose), brittle for the long tail of tech shorthand. A real deployment puts a model
  behind `classify_item()`'s routine half and keeps the safety patterns exactly as they are.
- **Nothing is sent.**
