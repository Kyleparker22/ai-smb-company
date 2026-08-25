# Member OS — build 17

Pre-built vertical AI OS for gyms and fitness franchises.
Spec: [`../BUILD.md`](../BUILD.md) · shared engine: [`../../_kit/`](../../_kit/).

```bash
python3 seed.py              # 5,200 members, failed payments, messages
python3 test_member_os.py    # 33 assertions
```

Launch name **`prebuild-member-os`** (port 8837, 127.0.0.1 only).

## What it is

"Foundry Fitness" — 4 locations, $6.8M. Four modules: **cancellation integrity**, **dunning**,
**churn watchtower**, **message triage**.

## The refusal it is organised around

**A cancellation is processed, not negotiated.** The statutory clock starts at the request (R2 —
delay is the harm), computed under per-state rules that name themselves a default. A retention
offer may be drafted for a human — as a *separate* row — but processing never waits on the save
attempt. `delay_cancellation` is R0: in the auto-renewal-law era, slow-walking a cancel is
regulatory exposure, not retention.

Also load-bearing:
- **An injury report gets nothing in writing from software** — `respond_to_injury` R0, a human calls.
- **Dunning never threatens** — a fixed gentle template, a 3-touch ladder, then a person;
  `threaten_collections` R0 and threat language is structurally refused.
- **No health outcome is ever promised** — `medical_claim` R0.
- The churn list keeps the **two-signal floor** (from build 10): one signal is a note, two is a
  pattern; single-signal members counted separately. Involuntary churn is split from voluntary
  and refuses below 10 cancellations.

The eval's costly class merges the two must-act messages — injury (liability) and cancellation
(illegal continued billing). Recall 1.0, zero missed.

## 10-minute demo

Board → Inbox (the cancel: clock starts, save offer separate; the injury: nothing drafted) →
Dunning (the template, the bounds) → Churn watch (the floor) → ROI → Trust.

## What this does not do yet

- **No integrations.** Billing (ABC/Daxko/Mindbody), access control, SMS are adapter seams.
- **Triage is deterministic pattern-matching** — a real deployment puts a model behind the routine
  path and leaves the cancellation and injury stops exactly as they are.
- **Cancellation rules are simplified shapes, not law** — counsel replaces them per state.
- **Nothing is sent.**
