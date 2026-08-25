# Delta OS — the change order that writes itself (build 63)

**Working name:** Delta OS · **Launch:** `prebuild-delta-os` · **Port:** 8883
**Synthetic operator:** "Keystone Interior Systems" — drywall/framing sub, 6 active jobs.
(Distinct from build 11 Change OS, which tracks change orders already known — Delta OS
DETECTS the change the day the built work departs from the drawing.)

## The never-seen mechanism
Daily site photos are compared against the plan set; the day the built work departs from the
drawings, the change order AND the contract's notice letter draft themselves — inside the
notice window, not at closeout when memory and leverage are gone. Unbilled change orders are
3–5% of a sub's revenue.

## The honest seam (demo)
No live vision model in the demo. The field app records **structured photo observations**
(photo ref + what the wall/ceiling/opening measured or contained), and the diff engine
compares OBSERVATIONS vs RECORDED PLAN LINES deterministically. The vision model is a
real-deployment seam, named in the README; the demo proves the mechanism downstream of it.

## Modules
1. **Plan register** (Company Brain) — per job: plan lines (location, spec, quantity, rev);
   an observation citing a location with no plan line reads UNPLANNED, never assumed.
2. **The diff engine** (Operations) — daily observations vs plan lines; a departure creates a
   DELTA with photo refs + plan rev cited; deltas classify (added scope / changed spec /
   rework) — classification is drafted, a human confirms (a wrong delta invoiced is worse
   than a missed one).
3. **The self-writing paper** (Back Office) — a confirmed delta drafts the change order
   (quantities × the recorded rate schedule) AND the notice letter citing the contract's
   recorded notice clause + days remaining (DATE ALERT). Both R1. A contract with no
   recorded notice clause: the letter refuses and says why.
4. **The closeout ledger** (Operations) — every delta: detected → confirmed → noticed →
   priced → signed/rejected; unsigned deltas aged; the counted "detected same-day vs found
   at closeout" stat is the product's own proof.
5. **Intake triage** (Intake) — GC directive ("go ahead and add the soffit" — the verbal
   go-ahead recorded verbatim, quoted back, never a signed CO) · schedule ask · backcharge
   dispute (costly label: a backcharge accusation needs the evidence pulled) · human.

## Guardrails (load-bearing)
- `invoice_unconfirmed_delta` — **R0, structural**: no path from detected → priced without
  the human confirmation.
- `treat_verbal_as_signed` — **R0**; the verbal directive is recorded and quoted back —
  "a note, not a signed change order" (the Proof OS lesson).
- `notice_without_recorded_clause` — refused with the gap named.
- `price_off_rate_schedule` — refused; the recorded schedule or a human.

## ROI (typed)
Change orders captured (counted deltas × recorded rates, operator confirm rate) · notice
deadlines kept (counted DATE ALERTS) · closeout write-offs (scenario) · PM hours (time_saved).

## Demo path
Plan register → today's observations → a delta detected (photo + plan rev cited) → confirm →
CO + notice letter drafted with the clause cited → verbal go-ahead quoted back → unconfirmed
delta refuses to price → trust tab.

## Build prompt
Shared contract, full built-out standard. Costly eval label: the backcharge accusation.
