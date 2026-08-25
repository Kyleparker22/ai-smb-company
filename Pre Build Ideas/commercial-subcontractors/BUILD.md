# Change OS — commercial subcontractors (build 11)

**Working name:** Change OS · **Launch:** `prebuild-change-os` · **Port:** 8831

## The idea

A $5–30M trade subcontractor (mechanical, electrical, concrete) leaks margin in three places that
are all *already earned*: the change order performed on a verbal directive and never billed, the
retainage that sits uncollected for a year after closeout, and the preliminary-notice deadline that
quietly lapses and takes the lien right with it. Change OS watches all three from the records the
sub already keeps.

**Buyer:** the owner or CFO of the sub. They think in unbilled dollars and notice deadlines.

## The bleeding neck

- Field crews perform extra work on a superintendent's say-so; by billing day nobody remembers
  which Tuesday it was. Industry folklore says 2–5% of contract value walks away this way — we do
  NOT quote that number; we count *their* unbilled change events from *their* field notes.
- Retainage (5–10% of every invoice) outlives the job by months because nobody owns the chase.
- Notice and lien deadlines are per-state, unforgiving, and tracked in someone's head.

## Modules (8-pillar mapping)

1. **Change-event capture** (Operations) — field notes classified: base scope · change event ·
   ambiguous. The costly error is a change event read as base scope: that is money never billed.
   Eval ships with the build.
2. **CO ledger** (Back Office) — change events become draft COs. **A CO without a recorded signed
   directive or written authorization cannot be submitted — the system refuses**, because a
   handshake CO submitted in writing becomes a dispute, not a payment.
3. **Pay-app & retainage watchtower** (Back Office) — billed vs paid vs held, counted per project
   from the pay-app records. Retainage aging named per GC.
4. **Notice & lien calendar** (Company Brain) — deadlines computed from first/final furnishing
   dates under **per-state configurable rules** that name themselves a default. Every date is a
   **DATE ALERT, not legal advice**. Filing anything is R0 — an attorney files.
5. **Invitation triage** (Sales) — go/no-go on bid invitations scored from the sub's own history
   with that GC (pay speed counted from records, not reputation).

## Guardrails (load-bearing)

- `assert_entitlement` (claim/legal language to a GC) — **R0, never**. Drafts route to a human.
- `file_lien` / `file_notice` — **R0, never**. The calendar alerts; counsel files.
- `submit_co` — R1, and structurally impossible without a directive reference on file.
- All outward messages (CO submission, retainage chase) — R1 floor.
- No industry benchmark stats; the ROI panel computes only from their recorded ledger.

## ROI model (their inputs, shown arithmetic)

- Unbilled change events captured → revenue (counted from the ledger)
- Retainage outstanding beyond terms → cash timing
- Pay-app assembly hours → time saved
- Lapsed-deadline exposure → scenario (never presented as a saving)

## 10-minute demo

Board (unbilled COs, retainage aging, next deadlines) → classify a messy field note → watch the
submit refusal on the directive-less CO → the notice calendar with the rule set named as
replaceable → invitation go/no-go with pay-speed receipts → trust tab (eval, matrix, log).

## Build prompt (§8)

Build `Pre Build Ideas/commercial-subcontractors/build/` mirroring `Pre Build Ideas/property-management/build` and the
shared `_kit/` engine. Python stdlib only, JSON store, server on 127.0.0.1:8831, launch name
`prebuild-change-os`. Synthetic data: ~25 projects across TX/FL, ~18 GCs with counted pay
behaviour, ~200 field notes including genuinely ambiguous ones, COs at every state, retainage
aging, notice deadlines both comfortable and near. Honesty rules verbatim from `_kit`: unmeasured
over estimates, append-only event log, counted automation, typed ROI lines, the costly eval class
(missed change event) reported alone. Tests pin every refusal above.
