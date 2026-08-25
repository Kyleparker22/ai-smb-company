# Haul OS — dumpster & waste hauling (build 19)

**Working name:** Haul OS · **Launch:** `prebuild-haul-os` · **Port:** 8839

## The idea

A roll-off operator's day is a stream of "can I throw X in the dumpster?" texts, disputed
overage/contamination charges, and containers sitting full at job sites earning nothing. The
answer engine must be allowed to say *yes* to drywall and must be **incapable** of saying yes to
asbestos; the charge engine must be incapable of asserting a fee it cannot evidence; and the idle
containers must be on a board.

**Buyer:** the owner/dispatcher. Thinks in pulls per truck per day and container turns.

## The bleeding neck

- One bot-approved hazardous item = a contaminated load, a rejected tip, EPA exposure, and a fine
  that eats a month.
- "You say it was overweight — show me the ticket." Charges without evidence become credit memos.
- Containers delivered and forgotten: every idle day is a turn not made.

## Modules

1. **Prohibited-waste triage** (Intake) — item questions classified: allowed (with the weight
   caveat), **hazardous (typed, never approved — routed with disposal-option help)**, unknown
   (human). The costly eval class is a hazardous item approved.
2. **Charge evidence** (Back Office) — an overweight charge requires the scale ticket on file; a
   contamination charge requires the photo record. Missing → **"cannot assert charge."**
3. **Container board** (Operations) — idle containers aging (delivered, no pickup order), missed
   promised pickups counted.

## Guardrails (load-bearing)

- `approve_hazardous_item` — **R0.** The system can say no and can route to a human with
  disposal options; it can never say yes.
- `assert_charge_without_ticket` — **R0**, structural: the charge path demands the evidence id.
- Weight/overage advice carries the scale note, never a promise ("under X tons" is a caveat, not
  a quote).

## ROI model

Idle container-days turned → revenue (their pull value) · charge recovery with evidence → revenue
(counted) · phone/text hours → time saved · contaminated-load exposure → scenario.

## 10-minute demo

Board → ask "can I toss the old paint cans" (typed refusal + disposal help) vs "drywall from the
garage" (yes, with the weight note) → assert the ticketless overage (refused) vs the ticketed one
(drafts) → idle containers aging → ROI → trust.

## Build prompt (§8)

Build `Pre Build Ideas/dumpster-waste/build/` on `_kit/`. Stdlib, JSON store, 127.0.0.1:8839,
launch `prebuild-haul-os`. Seed "Granite City Roll-Off": ~220 containers, ~700 orders with
promised dates, charges with and without tickets, item questions incl. every hazardous type.
Eval costly class = hazardous approved. Tests pin the never-yes rule, the evidence refusal, idle
aging, missed pickups, ROI blanks, counted automation.
