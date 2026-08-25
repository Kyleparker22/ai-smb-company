# Lot OS — independent used-car dealer (build 41)

**Working name:** Lot OS · **Launch:** `prebuild-lot-os` · **Port:** 8861
**Synthetic operator:** "Crossroads Auto Group" — 2 lots, ~140 units, buy-here-pay-here adjacent
but bank-financed.

## The bleeding neck
Leads die in minutes (speed-to-lead IS the business), aged units eat floorplan interest daily and
nobody computes it, and the two lawsuit machines: a condition claim beyond the recorded history
("never been in an accident") and a payment quote that wanders into unlicensed-finance territory.

## Modules
1. **Lead response ladder** (Sales) — inbound leads acknowledged with drafted copy in minutes;
   bounded follow-up; the aging lead escalates to a phone call.
2. **The condition rule** (Company Brain) — outward copy about a unit can state ONLY what the
   recorded history/inspection contains, citing it. "Clean title per the recorded report dated X"
   is expressible; "never wrecked" is not.
3. **Payment discipline** (Back Office) — payment figures draft only from recorded lender terms
   (rate, term, amount) with the disclosure line attached; no recorded terms → the copy invites
   a finance conversation instead. Reg-Z posture.
4. **The title gate** (Operations) — a deal cannot mark delivered without the recorded title
   status; the refusal names what's missing.
5. **Aged-inventory board** (Operations) — floorplan days × recorded daily cost, counted; the
   30/60/90 units named.

## Guardrails (load-bearing)
- `assert_condition_beyond_record` — **R0.** The record talks or nobody does.
- `quote_payment_without_terms` — **R0** without recorded lender terms.
- `deliver_without_title_status` — **R0.**
- Trade-in values: a band from the recorded book or refused — never a guess.

## ROI (typed)
Leads answered inside the window (counted) · floorplan interest on aged units (counted from their
recorded rate) · desk hours (time_saved) · the compliance file (scenario).

## Demo path
Board (aged units with interest counted) → lead ladder copy → ask for "never wrecked" copy
(refused, record cited instead) → payment quote without terms (refused) → trust tab.

## Build prompt
Shared contract, full built-out standard. Costly eval label: the fresh lead (speed is the
costly miss).
