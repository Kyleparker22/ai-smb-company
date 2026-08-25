# Route OS — build 18

Pre-built vertical AI OS for pest control companies.
Spec: [`../BUILD.md`](../BUILD.md) · shared engine: [`../../_kit/`](../../_kit/).

```bash
python3 seed.py             # 6,800 accounts, ~3,000 services
python3 test_route_os.py    # 32 assertions
```

Launch name **`prebuild-route-os`** (port 8838, 127.0.0.1 only).

## What it is

"Sentry Pest Solutions" — $4.5M, 14 routes. Four modules: **message triage**, **billing
integrity**, **churn watch**, **guarantee-language check**.

## The refusals it is organised around

**The exposure stop.** "My dog licked the baseboard" gets the Poison Control instruction verbatim
— *call 1-800-222-1222 now; trouble breathing, call 911* — and a human immediately. Software
assesses nothing. The eval's costly class is a missed exposure (*A POISONING INCIDENT ANSWERED BY
A CHATBOT*), recall 1.0.

**The label is the law.** A chemical-safety question — "is it safe for the kids to go back in?" —
is routed to a licensed applicator *unanswered*. `answer_chemical_safety` is R0.

**A skipped stop can never be billed as completed.** The billing path requires a completed record;
a skip (typed: locked gate, weather, no access) is refused with the reason — *the dispute that
ends the account*. Completed-with-a-record bills at R2 and logs.

**No elimination promise, ever.** Every outward draft passes a structural language check —
"eliminate", "100%", "gone for good" are refused; coverage language only.

Plus the two-signal churn floor (a reservice is scheduled AND counted as the churn signal it is),
and a reservice rate that refuses below 50 completed services.

## 10-minute demo

Board → Inbox (dog-licked-it → Poison Control language; re-entry question → unanswered; roaches →
reservice + churn signal) → Billing integrity (bill the skipped stop — refused; bill the completed
one — R2) → Churn watch → Language check (try the ad copy) → ROI → Trust.

## What this does not do yet

- **No integrations.** PestPac/FieldRoutes, SMS, payments are adapter seams.
- **Triage is deterministic pattern-matching** — a real deployment puts a model behind the routine
  path and leaves the exposure stop and label rule exactly as they are.
- **No route optimisation** — density is reported, not solved.
- **Nothing is sent.**
