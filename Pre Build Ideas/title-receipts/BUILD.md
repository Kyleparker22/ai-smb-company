# Receipt OS — the underwritable audit trail (build 71)

**Working name:** Receipt OS · **Launch:** `prebuild-receipt-os` · **Port:** 8894
**Synthetic operator:** "Beacon Title & Escrow" — 3 offices, ~90 closings/mo.
(Distinct from build 20 Closing OS, which refuses the wire fraud — Receipt OS turns the
refusal LOG into an asset: evidence that buys premium reductions and wins referrals.)

## The never-seen mechanism
The agency's security controls generate receipts — callback-verified wire changes,
dual-control releases, blocked attempts — and Receipt OS packages that evidence into an
**underwritable file**: the cyber/E&O renewal packet an insurer can price against, and the
one-page "our security has receipts" proof that wins realtor referrals. The moat itself
becomes a revenue line. Pattern name: evidence-backed premium reduction.

## Modules
1. **The control ledger** (Operations) — every security-relevant act recorded: wire-change
   requests (and their callback verifications, with who called whom at which recorded
   number), dual-control releases (both humans named), blocked/refused attempts, drill
   results. Append-only; a control event cannot be edited, corrections are new entries.
2. **The coverage-year file** (Back Office) — controls aggregated per policy period:
   counted verifications, counted blocks, drill pass/fail dates, the exceptions list
   (every wire that moved with ANY gap in its chain — the honest column that makes the
   rest credible). An unexercised control reads UNTESTED, never "in place" (the security-
   model lesson: a control with no drill behind it is a claim, not a control).
3. **The renewal packet** (Sales) — drafts R1 for the agency's insurance renewal: the
   counted year, the exceptions honestly listed, the drill record; NO premium promise —
   "underwriters price; we evidence" (the packet never claims a discount, it earns one).
4. **The referral proof** (Customer) — the realtor-facing one-pager: counted verifications
   and blocks, zero client data, white-label; drafted R1.
5. **Intake triage** (Intake) — costly label: the wire-change request itself (the Closing
   OS rule holds absolutely: verbatim, verified-callback path, never acted from the
   message) · insurer/audit info request · realtor proof ask · closing status · human.

## Guardrails (load-bearing)
- `act_on_emailed_wire_change` — **R0** (inherited law of the vertical).
- `claim_untested_control` — **R0**; no drill record → UNTESTED, and the packet says so.
- `omit_exception` — **R0, structural**: the exceptions query is the same store as the
  counted successes — one read path, the packet cannot render without both.
- `promise_premium_outcome` — **R0**; the packet evidences, underwriters price.
- Packets and outward drafts R1; client data never appears in any packet (scrub, tested).

## ROI (typed)
Premium reduction earned (counted at renewal, never promised) · realtor referral lift
(counted sources, operator lift) · the breach-that-didn't-happen (scenario) · audit-prep
hours (time_saved).

## Demo path
The control ledger live (a verification chain end-to-end) → the coverage-year file with the
exceptions column → UNTESTED control honesty → the renewal packet draft (no premium promise)
→ the realtor one-pager → the emailed wire-change refusal → trust tab.

## Build prompt
Shared contract, full built-out standard. Costly eval label: the wire-change request.
