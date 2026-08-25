# Carrier OS — build 7 of 10

Pre-built vertical AI OS for freight brokerages and 3PLs.
Spec: [`../BUILD.md`](../BUILD.md) · shared engine: [`../../_kit/`](../../_kit/).

```bash
python3 seed.py                      # 20 carriers, 7,300 loads, a year of lane history
python3 test_carrier_os.py           # 71 assertions, every one a refusal
```

Launch name **`prebuild-carrier-os`** (port 8827, 127.0.0.1 only).

## What it is

"Halyard Freight Group" — 22 people, ~140 loads/week, van and reefer, a carrier base including two
deliberate fraud patterns. Modules: **carrier trust file**, **fraud tripwires**, **offer triage**,
**check-call engine**, **load board**.

## The central design idea: an autonomy asymmetry

**The system may refuse a carrier on its own. It may never approve one, never release a load, never
dispatch.**

`refuse_carrier` is R3 — refusing is the safe direction, and a wrong refusal costs one phone call
while a wrong approval costs a cargo claim and a customer. `approve_carrier`, `release_load` and
`dispatch` are R1 and **permanently excluded from promotion**: a million clean approvals cannot
move them, and a test proves it. On the seeded board, the event log contains **zero** agent
approvals and **zero** agent releases. Carrier approval and load release are also two *separate*
human decisions.

`assert_fraud` is R0. The system reports which tripwires fired and on what evidence; it never says
what a carrier *is*. A refusal returns a list of evidence and says so explicitly.

## Staleness pulls toward unknown, not toward good

Every score component carries its own timestamp. A check from today is full weight; a 400-day-old
one is heavily de-rated; a component **never checked contributes nothing**. Critically, de-rating
pulls the component toward **0.5 (unknown)** rather than merely reducing its weight — re-weighting
alone can never lower a perfect score, so a carrier whose authority was last verified 300 days ago
would have scored identically to one verified this morning. That was a real bug, caught by a test
that asserted the two scores must differ.

## Eight tripwires, each scored alone

`new_authority_high_value` · `contact_mismatch` · `recent_domain_change` · `rate_implausibly_low` ·
`insurance_expires_in_transit` · `equipment_mismatch` · `cargo_below_value` · `authority_not_active`.
Three are **hard stops**. Each is a separate function, each is evaluated **independently** (fires on
its own pattern, quiet on a clean carrier), and the eval reports the **false-negative** rate alone —
a missed pattern costs a claim, a false alarm costs a phone call.

`rate_implausibly_low` never invents a benchmark to fire against: with no lane history it stays
silent. It also had a real bug — the offer rate lives on the *offer*, not the load, so the tripwire
could never fire in practice until the rate was threaded through. Found by running the demo, not by
reading the code.

## The benchmark refuses thin lanes

Computed from the brokerage's **own** booked history; under 8 loads it returns
`unmeasured — only N booked loads… need 8`. Two lanes in the seed are deliberately thin, and margin
by lane shows them blank rather than zero.

## The demo, in one screen

Load `ld_demo`: ATL-CHI, van, $60,000 of freight, customer pays $1,980, lane benchmark $1,436 from
221 booked loads.

| Carrier | Rate | Trust | Verdict |
|---|---|---|---|
| Meridian Trucking | $1,740 | 0.851 | clean — and still not approved |
| Ironwood Transport | $1,690 | 0.782 | clean — and still not approved |
| **Northpine Trucking LLC** | $940 | 0.67 | **refused**: phone and domain don't match the registered record, domain 11 days old, rate 35% below the lane median |
| **Swiftline Capacity Partners** | $1,420 | 0.38 | **hard stop**: cargo limit $25k on $60k of freight, authority 41 days old |

Northpine is the hijacked-identity pattern: an old, clean authority reached at a brand-new domain
and a phone that isn't the one on the record. Nothing about the score alone would have stopped it.

## What this does not do yet

- **No live data of any kind.** FMCSA, carrier-monitoring vendors, the TMS, load boards, ELD and SMS
  are adapter seams. **No scraping** — a real credentialed connection needs a written compliance
  assessment first.
- **Carriers, MC/DOT numbers and safety data are invented.**
- **No document verification** (COIs, W-9s, authority letters) — a real deployment reads them.
- **Fraud exposure is a scenario, never a saving.** Prevented incidents cannot be counted; the panel
  shows what the tripwires caught in recorded history and what one event costs, and lets the broker
  decide what that is worth.
- **Nothing is sent, nothing is released.**
