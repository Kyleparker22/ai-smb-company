# Bay OS — auto repair (build 12)

**Working name:** Bay OS · **Launch:** `prebuild-bay-os` · **Port:** 8832

## The idea

An independent 6–10 bay shop's biggest untapped revenue is work it already found: inspection items
the customer declined at pickup and nobody ever re-offered. Its biggest liability is the opposite
mistake — describing a brake, tire or steering finding in soft "when you get a chance" language.
Bay OS recovers the first and structurally refuses the second.

**Buyer:** the shop owner / GM. Thinks in ARO, bay utilization, and comebacks.

## The bleeding neck

- Declined work: found, written up, declined, forgotten. It sits in the shop's own records.
- Safety findings communicated casually — or worse, by text — become liability when the caliper
  fails on the highway.
- Comebacks (same system, 30 days) eat bays and goodwill and are rarely counted honestly.

## Modules

1. **Declined-work recovery** (Sales) — every declined inspection item classified:
   `safety_critical` · `deferrable` · `cosmetic` · needs-review. Deferrable/cosmetic items enter a
   bounded re-offer ladder. **Safety-critical items never enter a drip campaign** — they become a
   call task for a human with the safety language intact.
2. **Intake triage** (Intake) — inbound messages classified; an undriveable/safety call is priority
   and *nothing is diagnosed over the phone*.
3. **Approval watch** (Operations) — estimates sitting "presented" aged and nudged (R1 drafts).
4. **Comeback watch** (Customer) — repeat RO, same vehicle, same system, ≤30 days: counted, never
   asserted; the rate refuses below a floor of ROs.

## Guardrails (load-bearing)

- `state_vehicle_safe` — **R0, never.** The system never tells a customer a vehicle is safe; a
  technician who has inspected it says that.
- **Safety language is never softened.** A safety-critical re-offer cannot be sent as a text drip;
  it queues as a human call with the finding verbatim. The eval's costly class is a safety item
  classified as deferrable.
- `quote_firm_price` — R1, never promotes; ranges come from the shop's own RO history, a firm
  price needs a human on an inspected car.
- No phone diagnosis: intake answers scheduling, never "it's probably the alternator".

## ROI model

- Declined work recovered → revenue (counted from the ledger)
- Approval-aging nudges → revenue (their close rate, their number)
- Phone-tag and follow-up hours → time saved
- Comeback cost made visible → scenario

## 10-minute demo

Board → classify a fresh inspection sheet (watch the brake line route to a call, not a text) →
try to text the safety item and watch it refuse → comeback counter with its floor → ROI from their
numbers → trust tab.

## Build prompt (§8)

Build `Pre Build Ideas/auto-repair/build/` on the shared `_kit/`. Stdlib only, JSON store,
127.0.0.1:8832, launch `prebuild-bay-os`. Seed "Cedar Ridge Auto Care": ~8 bays, ~4,300 ROs/18mo,
declined items at every age and class, comebacks seeded knowingly, calls including an undriveable
one. Honesty rules from `_kit` verbatim; eval costly class = safety item called deferrable; tests
pin the safety-text refusal, the R0 probe, the comeback floor, ROI blanks, counted automation.
