# Dispatch OS — build 1 of 10

Pre-built vertical AI OS for residential home services (HVAC · plumbing · electrical).
Spec: [`../BUILD.md`](../BUILD.md). Shared honesty engine: [`../../_kit/`](../../_kit/).

```bash
python3 seed.py                      # build the synthetic shop (2,800 jobs, 18 months)
python3 test_dispatch_os.py          # the honesty suite
```

Then open it from the repo root via the launch name **`prebuild-dispatch-os`** (port 8821,
127.0.0.1 only). Never guess a port — `.claude/skills/show-surface/`.

## What it is

A $6M residential contractor, "Ridgeline Home Services" — 22 employees, 9 trucks, four zones.
Everything is synthetic: invented names, 555 numbers, no addresses, no network calls of any kind.

Three leaks, and nothing else:

| Leak | What the build does |
|---|---|
| **The call that rang out** | 24/7 intake: emergency stop → qualify → offer only slots the board can genuinely honour → book at the published diagnostic fee |
| **The estimate nobody chased** | Every estimate is a state machine that cannot rest in `presented`; a bounded five-touch ladder in the technician's voice; every loss carries a structured reason |
| **The repair nobody re-offered** | Technician notes parsed into a deferred-work ledger with a seasonal re-offer calendar and a 120-day cooling-off |

Plus dispatch assist (proposes only, permanently) and the owner's board.

## The parts a buyer should actually poke at

**The emergency stop** (`core.emergency_signal`) is the one classifier in the build biased on
purpose. An ambiguous report ("not sure, something smells weird"), an empty report, and an
unreadable report all route to a human. A false alarm costs one phone call; a miss costs a house.
The eval reports its recall **alone**, never folded into an accuracy number: 18 labelled cases,
recall 1.0, 0 missed, 0 false alarms.

**It refuses to guess.** An unmatched symptom produces `job_class: None` and a clarifying question,
not a booked truck. A slot is offered only when the skill, the job minutes *and* the drive time all
fit — `open_slots` returns `[]` rather than something the dispatcher will have to unpick.

**It refuses to state numbers it cannot compute.** Wipe the store and every figure comes back
blank with a reason. On the seeded shop, the ROI panel opens with one line already blank
(`needs recovered_book_rate`) because that rate is the operator's to give, and the revenue
subtotal says *1 line blank, excluded* rather than quietly summing three of four.

**Missed calls are valued at the median ticket, not the mean.** The mean here is $2,555 and the
median is $771 — a handful of system replacements drag the mean somewhere no missed service call
lands, and the panel says so on its face.

**"Recovered this week" claims almost nothing.** Only wins whose event log shows an agent touch
*before* the decision are counted; the rest are labelled the shop's own work and explicitly not
claimed.

**The automation rate is counted, and the denominator is honest.** Gated actions the gate held for
a human are in the denominator (leaving them out was a bug that made the rate read 100%), and
`log_deferred_work` is excluded from "pipeline-moving" because parsing 900 notes the technician
already wrote would inflate the figure to meaninglessness.

## Autonomy

R1 is the floor for anything a homeowner could hold the shop to. Three actions **never** promote,
whatever the streak: `quote_price`, `book_after_hours`, and `propose_board` (who goes where is a
judgement about people). `route_emergency` is R3 — putting a human on the phone is the one action
that is safer automatic than gated. A clean streak alone cannot promote anything; calibration
evidence is required too.

## 10-minute demo

1. **Revenue at risk** — three leaks counted, the median-vs-mean note, the narrow recovery claim.
2. **Live calls** — answer the 9:40pm "AC not cooling": qualified, booked into a real slot at $89.
3. Answer the **gas smell** call: routed to a human, no job created, and the script tells the caller
   to leave and call 911 first. Then the **"something smells weird"** call — ambiguity routes too.
   Then **"the thing on the wall is beeping"** — it asks a question instead of booking.
4. **Estimates** — the $9,400 system quote at day 16, its drafted touches, all unsent, and the
   loss-reason table.
5. **Deferred work** — this month's campaign, safety items re-offered out of season on purpose,
   everything else held back *with the reason*, and the notes that parsed to nothing surfaced for a
   human rather than dropped.
6. **What it's worth** — one line blank; type the missing rate and watch it compute.
7. **Trust & audit** — the approval queue, the eval with emergency recall alone, the matrix with its
   three never-promote rows, the append-only log.

## What this does not do yet

- **No real integrations.** ServiceTitan / Housecall Pro / Jobber, telephony, and QuickBooks are
  named adapter seams, not connectors. Nothing here has spoken to an external service.
- **Classification is deterministic pattern-matching, not a model.** That is right for the emergency
  stop (auditable, testable, biased on purpose) and wrong for the long tail of symptom language — a
  real deployment puts a model behind `classify()` and keeps `emergency_signal()` exactly as it is.
- **Drive time is a zone matrix, not a mapping API.** The shape is right; the numbers are invented.
- **No voice.** A real intake agent is Vapi + Twilio per the locked stack; this build shows the
  decision, not the call.
- **The deferred ledger reads notes only.** Photos are in the spec and not in the build.
- **Nothing is sent.** Every outbound message in this build is a draft behind the gate, by design.
