# Stone OS — monument & headstone dealers (build 51)

**Working name:** Stone OS · **Launch:** `prebuild-stone-os` · **Port:** 8871
**Synthetic operator:** "Hartwell Memorials" — 1 showroom + shop, ~90 active orders, serves 14
cemeteries.

## Why this industry (the overlooked test)
No AI vendor targets monument dealers. The work is grief-adjacent, paper-heavy, and every order
crosses a 6–12 month pipeline (contract → cemetery approval → proof → engraving → foundation →
setting) where one dropped handoff strands a family's memorial for a season. The error economics
are absolute: granite is not reworked.

## The bleeding neck
The engraving proof. A misspelled name or wrong date cut into stone is an irreversible,
five-figure, front-page failure — and proofs are today approved by phone. The quiet leaks:
cemetery-specific rules (size, base, finish, approval forms — different at all 14 cemeteries)
re-learned per order; setting scheduled before the cemetery approves or the foundation cures;
final balances uncollected because nobody wants to dun a widow.

## Modules
1. **Order pipeline** (Operations) — the 8-stage state machine with per-stage clocks; a stalled
   order names its blocker (family / cemetery / shop / weather).
2. **The proof gate** (Operations) — inscription typed once, rendered to a proof; **approval is a
   recorded human act by the family** (signature ref) — software never approves a proof, and
   engraving cannot start without the approval record (structural).
3. **Cemetery rulebook** (Company Brain) — per-cemetery recorded requirements cited on every
   order; an order to a cemetery with no recorded rules reads UNKNOWN, never assumed.
4. **Family comms** (Customer) — stage-change updates drafted grief-appropriate, R1; the balance
   reminder ladder is bounded and gentle; nothing sends itself.
5. **Setting scheduler** (Back Office) — setting only after cemetery approval + foundation cure
   days (recorded), both DATE-checked.

## Guardrails (load-bearing)
- `approve_proof` — **R0.** Only the family approves, on the record. A proof approved by software
  is a misspelled headstone waiting to happen.
- `start_engraving_without_proof_approval` — **R0**, structural: no code path.
- `declare_cemetery_compliant` — **R0**; the recorded rulebook is cited or the answer is UNKNOWN.
- `send_family_message` — R1 always; tone-checked drafts (no urgency language in grief comms).

## ROI (typed)
Remake avoidance (scenario — never a promised save) · orders/season throughput lift (operator
lift on counted pipeline) · deposit-to-balance collection counted from the ledger · office hours
returned (time_saved).

## Demo path
Pipeline board (stalled orders name blockers) → typo'd inscription proof → approval refused by
software, queued to family → cemetery rulebook citation → setting blocked pre-cure → trust tab.

## Build prompt
Shared contract, full built-out standard. Costly eval label: the proof/inscription-change message
(a family correcting a date is the one message that can never be mis-routed).
