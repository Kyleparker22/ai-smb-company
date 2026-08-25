# Pool OS — pool service & maintenance (build 31)

**Working name:** Pool OS · **Launch:** `prebuild-pool-os` · **Port:** 8851
**Synthetic operator:** "Bluewater Pool Care" — ~450 residential/commercial pools, 8 routes, ~$3M.

## The bleeding neck
A pool route company's liability is a reading nobody recorded, and its revenue leak is a stop
nobody proved. A "chemical burn" or drowning claim lands on whatever the tech wrote down that day;
a skipped stop billed as serviced ends the account; equipment work (filters, heaters, salt cells)
gets diagnosed on a doorstep and never quoted.

## Modules
1. **Message triage** (Intake) — injury/drowning-adjacent report · chemical question from a
   homeowner · green-pool complaint · schedule/skip. Injury reads FIRST.
2. **Service-proof billing gate** (Back Office) — a stop bills only with its recorded reading set
   (FC, pH, TA at minimum) + arrival stamp. No readings, no bill: "unprovable service is a
   dispute."
3. **Readings ledger** (Operations) — per-pool reading history vs the pool's own recorded target
   ranges; out-of-range flags, NEVER a "safe to swim" verdict.
4. **Green-pool recovery** (Customer) — complaint → drafted recovery-plan visit (R1) with honest
   copy (multi-visit, no single-visit promise).
5. **Equipment quote chase** (Sales) — tech-noted equipment issues become drafted quotes; bounded
   follow-up ladder.

## Guardrails (load-bearing)
- `declare_safe_to_swim` — **R0, never.** Software reports readings vs recorded ranges; a human
  (CPO) judges. The words "safe to swim" never leave software.
- `answer_chemical_dosing` — **R0.** The label is the law (pest/ag pattern); a certified tech answers.
- `respond_to_injury_report` — **R0.** Verbatim log + human now; drowning-adjacent language never
  gets an automated reply.
- `bill_unproven_stop` — **R0.** The reading set is the proof of service.

## ROI (typed)
Unbilled proven stops (counted) · equipment quotes captured (counted × close rate, theirs) ·
route-office hours (time_saved) · liability file discipline (scenario, never a saving).

## Demo path
Board → injury message (refusal + verbatim log) → bill a stop with no readings (refused, fields
named) → green-pool recovery draft → trust tab.

## Build prompt
Build per the shared contract in `_README.md` §"The shared build contract" at the full built-out
standard (drafted R1 copy, bounded ladders, recovered-this-week counted, ~16 eval cases, suite
pinning every refusal). Costly eval label: the injury/drowning-adjacent report.
