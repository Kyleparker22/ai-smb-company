# Traveler OS — build 29

Pre-built vertical AI OS for CNC machine & job shops.
Spec: [`../BUILD.md`](../BUILD.md) · shared engine: [`../../_kit/`](../../_kit/).

```bash
python3 seed.py                # machines, ~140 jobs, RFQs, materials (2 stale)
python3 test_traveler_os.py    # 33 assertions
```

Launch name **`prebuild-traveler-os`** (port 8849, 127.0.0.1 only).

## What it is

"Kestrel Precision Machining" — 24 people, $6.5M. Three modules: **RFQ desk**, **the cert gate**,
**promise dates**.

## The refusals it is organised around

**The cert gate.** A cert-required job cannot ship without its material cert AND inspection record
— *"cannot certify"*, with the missing paper named: *a cert-required part without its paper is a
customer gone and a liability held.* `waive_inspection` is R0 — nobody clicks past an inspection.
The RFQ scanner's costly eval class is a missed cert flag (*THE PART GETS QUOTED AND BUILT LIKE A
BRACKET FOR A BARBECUE*), recall 1.0, over-flagging biased on purpose.

**No quote off a stale material price.** Prices carry a priced-at date; past 14 days the quote
refuses — *metal moved; reprice it.* Undated or unrecorded prices refuse too: *a guess with a
number on it.* No machine rate recorded → *shop cost is a fact, not a feeling.*

**No promise date without capacity math.** Dates compute from recorded machine capacity minus
booked hours — *arithmetic, not optimism* — and refuse when capacity isn't recorded: *a date
without math is a broken promise scheduled early.* OTD is counted with a floor of 20.

## 10-minute demo

Board (OTD, cert-blocked, backlog weeks) → RFQ desk (scan the medical-titanium RFQ: flags found,
quote refused on the stale Ti price; the fresh 6061 one quotes with arithmetic) → Jobs (ship both
demo brackets — one refused, one drafts) → Materials (the stale rows) → ROI → Trust.

## What this does not do yet

- **No integrations.** ERP (JobBOSS/ProShop-class), CAM estimating, metal-price feeds are adapter
  seams.
- **RFQ scanning is deterministic pattern-matching** — a real deployment puts a model behind
  estimating and leaves the cert gate exactly as it is.
- **No scheduling optimiser** — capacity math is deliberately simple arithmetic.
- **Nothing is sent.**
