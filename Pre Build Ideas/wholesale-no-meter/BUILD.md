# Counter OS — the "No" meter (build 70)

**Working name:** Counter OS · **Launch:** `prebuild-counter-os` · **Port:** 8893
**Synthetic operator:** "Tri-State Supply Co." — electrical/plumbing distributor, 2 branches.
(Distinct from build 8 Quote Desk OS, which speeds the quotes you CAN answer — Counter OS
counts the sales you couldn't.)

## The never-seen mechanism
The simplest instrument in the catalog: capture and price every "we don't carry that" and
"we're out" said at the counter or on the phone. The refusal ledger becomes the purchasing
department — stocking decisions and vendor negotiations run from COUNTED lost sales instead
of gut. A distributor's biggest leak is invisible precisely because it's a sentence, not a
transaction.

## Modules
1. **The No ledger** (Operations) — every no captured in seconds (item asked for, kind:
   not-carried / out-of-stock / wrong-size, who asked, walked-or-waited); priced from the
   recorded catalog/comparable margin — a no with no comparable reads UNPRICED, counted but
   not dollared ("a counted mystery beats an invented dollar").
2. **The stocking case** (Back Office) — when an item's counted no's cross the recorded
   threshold (count × window), a stocking case drafts R1: the no history verbatim, the margin
   math, the recorded vendor/lead-time options; below the threshold NO case drafts — one
   loud contractor asking twice is an anecdote, not demand (the threshold's arithmetic
   prints on the case).
3. **The out-of-stock autopsy** (Company Brain) — OOS no's for items we DO carry trace to
   the recorded reorder point vs the pace that beat it; the case proposes the new point with
   the math shown; a walked customer on an OOS is the counted cost of that reorder point.
4. **Vendor negotiation packet** (Sales) — per vendor: the counted no's their line produced
   (fill failures, lead-time losses) — the evidence file the rep never expects a small
   distributor to have. Drafted R1.
5. **Intake triage** (Intake) — costly label: the contractor-down emergency ("my crew is
   standing around, do you have X RIGHT NOW" — answered from counted stock, never optimism)
   · a no report (the capture path itself) · price/quote ask · will-call status · human.

## Guardrails (load-bearing)
- `price_no_without_comparable` — **R0**; counted, never dollared without the recorded basis.
- `stocking_case_below_threshold` — **R0, structural**: anecdotes don't draft cases.
- `stock_answer_optimism` — **R0**; "do you have it" answers cite counted stock only.
- `invent_vendor_stats` — **R0**; the packet is the counted ledger verbatim.
- Cases and outward drafts R1.

## ROI (typed)
Captured-demand revenue (counted no's converted after stocking, the ledger's own before/after)
· OOS walk cost (counted × recorded margin) · vendor concessions (scenario) · counter
seconds (time_saved — capture must cost less than the no itself).

## Demo path
The No board (this week's counted no's, priced + unpriced) → a threshold-crossing item drafts
its stocking case with the math → the below-threshold refusal → an OOS autopsy proposing a
reorder point → the vendor packet → the contractor-down answer from counted stock → trust tab.

## Build prompt
Shared contract, full built-out standard. Costly eval label: the contractor-down emergency.
