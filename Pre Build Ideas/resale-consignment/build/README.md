# Consign OS — build (resale & consignment shops)

Run: `python3 seed.py && python3 server.py` → http://127.0.0.1:8870 (launch name
`prebuild-consign-os`). Suite: `python3 test_consign_os.py` (87 assertions). Synthetic
"Second Story Consignment" — 2 storefronts, 400+ items, 60 consignors.

## Where this build came from

Partner B's FB-Marketplace-assistant idea (2026-08-17), rebuilt as the version that survives the
anti-library: not automation of everyday people's **personal** accounts (ToS-breaking bot behavior,
the posture `rejections/2026-07-05` forbids), but an operated OS for the businesses that live on
resale. `CHANNELS = (shop_floor, web_store, marketplace_business)` — **no personal-account channel
exists for any code path to use**, and the trust tab says so.

## The load-bearing refusals

- **Software never calls an item genuine — or fake.** The brand line is "Tagged <brand> by the
  consignor — not authenticated" unless a third-party cert is on the record, and then the listing
  cites the cert ("the certificate, not our judgment, is the statement"). `certify_authenticity`
  is **R0, never-promote**; even the counterfeit *accusation* gets a second logged refusal —
  ruling it fake is also a verdict. `listing_ok` structurally blocks authenticity language in any
  outbound copy without a recorded cert.
- **The payout is the recorded agreement's arithmetic.** Sale price × the consignor's recorded
  split (per-consignor overrides named, never silent); a missing input refuses with the field
  named. Markdowns run the recorded schedule (`markdown_on_schedule` is R2 — the agreement
  already decided that number); anything off-schedule has no path (`settle_off_agreement` R0).
- **The offer floor clamp.** An offer below the consignor's recorded floor gets a drafted counter
  at the floor — acceptance below it is the consignor's call, never software's
  (`accept_below_floor` R0). No recorded floor → software doesn't negotiate someone else's
  property at all.
- **The wall.** Recall/prohibited matches (config-named default list) never reach a channel
  (`list_prohibited_item` R0); an item with no recorded condition notes can't list either — the
  unrecorded condition is how the damage dispute starts. Descriptions are built ONLY from the
  intake record; a missing field renders "not recorded", never a guess.
- **The clock.** Term → reclaim window → donation, per the recorded agreement, all DATE ALERTS.
  Donating what the consignor can still reclaim is refused as conversion (`donate_before_clock`
  R0); donation is human-only even after the clock. The reclaim ladder is bounded (3 touches,
  7-day cooldown, "silence is an answer").

## What runs at which rung

R3 read · R2 log claim, markdown-on-schedule, propose pickup slots · R1 every outward draft
(listing, publish, offer reply, auth reply, payout, reclaim notice) · R0 the six above. The
counterfeit/damage claim is the costly eval label (16 cases, recall reported alone).

## What this does not do yet

- **No channel integrations.** Web store and marketplace business APIs are adapter seams; the
  demo drafts and a human publishes.
- **No payments.** The pay run is drafted math; money moves outside the demo.
- **No image handling.** Photo requirements are a recorded flag, not a pipeline.
- **The recall list is a named default**, not a live CPSC feed — that wiring is a go-live task.
- **Nothing is sent.**
