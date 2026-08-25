# Traveler OS — machine & job shops (build 29)

**Working name:** Traveler OS · **Launch:** `prebuild-traveler-os` · **Port:** 8849

## The idea

A CNC job shop quotes its future every day, and its three classic self-inflicted wounds are:
quoting off last month's metal price, promising a date the machines can't honor, and shipping a
cert-required part without its paper. Traveler OS (named for the job traveler that follows every
part) refuses all three structurally.

**Buyer:** the owner/GM. Thinks in spindle hours, OTD, and the aerospace customer they cannot
afford to lose.

## The bleeding neck

- Metal moves weekly; a quote off a stale price is either lost money or a lost job.
- A promise date with no capacity math is a broken promise scheduled in advance.
- An AS9100/medical part shipped without its material cert and inspection record is a customer
  gone and a liability held.

## Modules

1. **RFQ desk** (Sales) — an RFQ is scanned for **cert requirements** (AS9100, ITAR, medical,
   traceability language) — the eval's costly class is a missed cert flag. A quote requires a
   **fresh recorded material price** (≤14 days — *metal moved; reprice it*) and a recorded machine
   rate; otherwise it refuses.
2. **The cert gate** (Operations) — a cert-required job **cannot ship** without the material cert
   AND the inspection record on file: *"cannot certify"* with the missing paper named.
3. **Promise dates** (Operations) — computed from recorded machine capacity minus booked hours;
   no capacity recorded → **no promise**. OTD counted with a floor.

## Guardrails (load-bearing)

- `ship_without_certs` — **R0**, structural via the cert gate.
- `quote_stale_material` — **R0**, structural via the freshness check.
- `promise_without_capacity` — **R0.** A date without math is a broken promise scheduled early.
- `waive_inspection` — **R0.** Nobody clicks past an inspection.

## ROI model

RFQs quoted same-day → revenue (their win lift) · expedite fees avoided → scenario · quoting
hours → time saved · the cert discipline → scenario (the aerospace customer is priceless or
priced by the operator).

## Build prompt (§8)

Build `Pre Build Ideas/machine-job-shops/build/` on `_kit/`. Stdlib, JSON store, 127.0.0.1:8849,
launch `prebuild-traveler-os`. Seed "Kestrel Precision Machining": machines with capacity, ~140
jobs incl. cert-required with and without paper, materials fresh and stale, RFQs incl. cert
language. Eval costly class = missed cert flag. Tests pin the cert gate, the staleness refusal,
the no-capacity refusal, OTD floor, ROI blanks, counted automation.
