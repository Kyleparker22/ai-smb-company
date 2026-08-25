# Route OS — pest control (build 18)

**Working name:** Route OS · **Launch:** `prebuild-route-os` · **Port:** 8838

## The idea

A recurring-revenue pest company lives on route density and dies on quiet churn: the reservice
call that was actually a cancellation warning, the skipped stop that got billed anyway (the
dispute that ends the account), and the after-treatment message — "my dog licked the baseboard" —
that must reach Poison Control language and a human, never a bot's reassurance.

**Buyer:** the owner. Thinks in recurring accounts, route density, cancels.

## The bleeding neck

- A reservice request is the loudest churn signal a pest company gets, and it is usually handled
  as a scheduling task and forgotten.
- A skipped stop billed as completed is fraud-shaped, even when it is a sync bug.
- Chemical exposure questions answered casually are a poisoning incident plus liability.

## Modules

1. **Message triage** (Intake) — exposure signals (child/pet contact, breathing issues after
   treatment) show the **Poison Control instruction verbatim** and route to a human immediately;
   chemical-safety questions ("is it safe for my dog", "when can we re-enter") route to a
   **licensed applicator unanswered** — the label is the law; reservices schedule AND count as
   churn signals; cancellations route.
2. **Billing integrity** (Back Office) — **a service that was not completed cannot be billed as
   completed.** Skips are typed (locked gate, weather, no access) and visible.
3. **Churn watch** (Customer) — reservice + payment issue + skipped service, on the two-signal
   floor.
4. **Guarantee language** (Sales) — drafts are structurally checked: no "eliminate", no "100%",
   no "never come back" — coverage language only.

## Guardrails (load-bearing)

- `answer_chemical_safety` — **R0.** Licensed applicators answer; the label is the law.
- Exposure → `POISON_INSTRUCTION` verbatim + human. The eval's costly class is a missed exposure.
- `bill_skipped_service` — refused by construction; the billing path requires a completed record.
- `promise_elimination` — **R0**, with a structural language check on every draft.

## ROI model

Reservice-driven saves → revenue (their save rate) · skip-billing disputes avoided → scenario ·
scheduling/callback hours → time saved · route density → their number.

## 10-minute demo

Board → the dog-licked-it message (Poison Control language, human, nothing assessed) → the
re-entry question (routed unanswered) → try to bill the skipped stop (refused) → churn watch →
the elimination-language check → ROI → trust.

## Build prompt (§8)

Build `Pre Build Ideas/pest-control/build/` on `_kit/`. Stdlib, JSON store, 127.0.0.1:8838,
launch `prebuild-route-os`. Seed "Sentry Pest Solutions": ~6,800 recurring accounts, services
completed/skipped across 6 months, messages incl. exposure and safety questions. Eval costly
class = missed exposure. Tests pin the poison-control route, the unanswered safety question, the
skipped-billing refusal, the language check, the churn floor, ROI blanks.
