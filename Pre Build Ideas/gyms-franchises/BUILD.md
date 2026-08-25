# Member OS — gyms & fitness franchises (build 17)

**Working name:** Member OS · **Launch:** `prebuild-member-os` · **Port:** 8837

## The idea

A multi-location gym loses members three ways: cards that fail and never retry (involuntary churn
— the biggest, dumbest leak), members who quietly stop coming and are gone before anyone noticed,
and cancellation handling that drags — which in the auto-renewal-law era is not a retention
strategy, it is a regulatory complaint. Member OS recovers the first, watches the second with an
honest floor, and makes the third impossible to slow-walk.

**Buyer:** the owner/operator. Thinks in members, churn, and draft-day revenue.

## The bleeding neck

- Involuntary churn: a failed card is a service problem, not a sales problem — and it is usually
  nobody's job.
- At-risk members: a list that flags everyone is a list nobody works (the two-signal floor,
  learned in build 10, applies here verbatim).
- Cancellations: "save flows" that delay processing are now FTC/state-law exposure. Speed is
  compliance.

## Modules

1. **Cancellation integrity** (Customer) — a cancellation request is flagged for processing
   **immediately**, with the statutory window computed under per-state rules that name themselves
   a default. A retention offer may be *drafted for a human* — but **processing never waits on the
   save attempt**. `delay_cancellation` is R0.
2. **Dunning** (Back Office) — failed payments on a bounded 3-touch ladder that never threatens
   (`threaten_collections` R0); involuntary churn counted separately from voluntary.
3. **Churn watchtower** (Customer) — visit-drop, failed payment, no future booking, freeze
   request: **one signal is a note; two is a pattern.** Single-signal members counted separately.
4. **Message triage** (Intake) — injury reports and cancellations are the costly classes: human
   immediately, nothing drafted on an injury. `medical_claim` ("this will fix your back") is R0.

## Guardrails (load-bearing)

- `delay_cancellation` — **R0.** Processed, not negotiated.
- `respond_to_injury` — **R0** for drafts; a human calls. Nothing in writing from software.
- `medical_claim` / `threaten_collections` — **R0.**
- Cancellation windows per state, configurable, "replace before go-live."
- The churn list has a two-signal floor.

## ROI model

Failed payments recovered → revenue (counted) · churn saves → revenue (their save rate) · manual
billing chase hours → time saved · regulatory exposure on slow cancels → scenario.

## 10-minute demo

Board → triage the cancellation (processing clock starts, retention draft queues separately) and
the injury message (nothing drafted) → dunning ladder bounded → churn list at the floor → ROI →
trust.

## Build prompt (§8)

Build `Pre Build Ideas/gyms-franchises/build/` on `_kit/`. Stdlib, JSON store, 127.0.0.1:8837,
launch `prebuild-member-os`. Seed "Foundry Fitness": 4 locations, ~5,200 members across CA/TX with
visit histories, failed payments at every ladder stage, freeze requests, messages incl. injury and
cancellation. Eval costly class = missed injury/cancellation. Tests pin the R0s, the
processing-never-waits rule, ladder bounds, the two-signal floor, per-state windows, ROI blanks.
