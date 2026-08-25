# Consign OS — resale & consignment shops (build 50)

**Working name:** Consign OS · **Launch:** `prebuild-consign-os` · **Port:** 8870
**Synthetic operator:** "Second Story Consignment" — 2 storefronts, apparel + furniture + goods,
online listings through the shop's **business** commerce channels.

## Where this build came from
Partner B's FB-Marketplace-assistant idea (2026-08-17), rebuilt for the version that survives the
anti-library: not an app automating everyday people's personal accounts (personal-account
automation is ToS-breaking bot behavior — the posture `rejections/2026-07-05` forbids), but an
operated OS for the **businesses** that live on resale — consignment, resale, thrift — listing
through sanctioned business channels. `CHANNELS` contains no personal account **by construction**.

## The bleeding neck
The counterfeit accusation is the reputation/legal event: "the Louis Vuitton I bought here is
fake" handled ad-hoc becomes a one-star story or worse — and the shop's own listing claiming
"authentic" is what turns it into liability. The quiet leaks: intake sitting unlisted for days,
consignor payouts computed by memory instead of the agreement, offers accepted below the
consignor's floor, recalled goods reaching the floor, and the unsold-item clock nobody runs.

## Modules
1. **Message triage** (Intake) — counterfeit/damage claim · authenticity question · buyer offer ·
   pickup scheduling · consignor payout ask.
2. **Honest listings** (Operations) — descriptions built ONLY from the recorded intake facts;
   the brand line is "tagged <brand> by the consignor" unless a third-party authentication cert
   is on the record, and then the listing cites the cert, never the software's judgment.
3. **The consignor ledger** (Back Office) — payouts DRAFT from the recorded agreement's split ×
   the recorded sale price; markdowns follow the recorded schedule; ad-hoc numbers can't be
   produced.
4. **Offer desk** (Sales) — offers below the consignor's recorded floor get a drafted counter,
   never an acceptance; no recorded floor → software doesn't negotiate at all.
5. **The clock** (Back Office) — unsold-item term and reclaim window per agreement as DATE
   ALERTS; bounded reclaim ladder; donation after the clock is a human act, and only after.

## Guardrails (load-bearing)
- `certify_authenticity` — **R0.** Software never calls an item genuine. The record speaks or
  nothing does.
- `deny_claim` — **R0.** The counterfeit/damage claim gets the record and a human.
- `settle_off_agreement` — **R0**; the recorded split/markdown schedule or a human.
- `accept_below_floor` — **R0**; the consignor's recorded floor, or the consignor decides.
- `list_prohibited_item` — **R0**; the recall/prohibited list (config-named default) is a wall.
- `donate_before_clock` — **R0**; and donation is human-only even after it.

## ROI (typed)
Listing hours returned (time_saved) · sell-through lift on aged inventory (revenue, operator
lift) · payouts owed counted from the ledger · the counterfeit file (scenario, never a number).

## Demo path
Board (unlisted backlog, aged listings, payouts owed) → the fake-bag claim (record + refusal to
certify or deny) → the $40 offer on a $55 floor (counter, never acceptance) → the recalled crib
(refused listing) → payout math from the agreement → trust tab.

## Build prompt
Shared contract, full built-out standard. Costly eval label: the counterfeit/damage claim.
