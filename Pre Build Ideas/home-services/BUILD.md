# 1 · Home Services (HVAC · Plumbing · Electrical) — **Dispatch OS**

*Pre-build. Not built, not sold, no client. See `../_README.md` for the shared build contract.*

## 1. The idea in one paragraph

A residential trades contractor's revenue leaks in three places that are all *already-earned demand*: the call that rang while the CSR was on another call, the estimate that was presented and never followed up, and the repair the technician recommended and wrote in a job note that nobody ever re-offered. **Dispatch OS** is an operated AI OS that closes all three — a 24/7 intake that answers every call and books into real capacity, an unsold-estimate recovery engine that will not let a quote die without a recorded decision, and a deferred-work ledger that turns technician recommendations into a seasonal re-offer campaign. The owner gets one screen: *revenue at risk today, and what was recovered this week.*

## 2. Who buys it

The **owner** of a $2M–$15M residential HVAC/plumbing/electrical company, 8–60 employees, running ServiceTitan / Housecall Pro / Jobber. They already know their close rate and their average ticket, which makes the ROI conversation arithmetic instead of a pitch. They are the single most reachable SMB type through a warm network, and they buy on revenue, not on efficiency.

## 3. The bleeding neck

- **Missed and abandoned calls.** Peak season means simultaneous inbound; nights and weekends go to voicemail or an answering service that takes a message and books nothing. Every unanswered call in this trade is a competitor's job, same day.
- **Unsold estimates.** A tech presents a $9,000 system replacement, the homeowner says "let me talk to my spouse," and the follow-up is one voicemail three days later — if that. The pipeline of presented-but-undecided estimates in a typical shop is large and untended.
- **Deferred work never re-offered.** The tech notes "capacitor weak, recommend replace; customer declined" — that note is worth real money next August and dies in the job record.
- **Dispatch is a person's memory.** Which tech, which skill, which part on the truck, which drive time — the board is optimized by whoever is loudest.

## 4. What we build

**Pillars** (per `processes/ai-os-modules.md`): Intake (1) + Sales/Revenue (2) + Operations (5). **Form factors:** digital employee (the intake agent) + headless automation (recovery engines) + embedded surface (the owner's board).

| Module | What it does | Autonomy start |
|---|---|---|
| **Front desk** | Answers every call/text/form 24/7. Qualifies (trade, symptom, urgency, address in service area, homeowner vs renter), quotes the diagnostic fee, offers *real* open slots from the schedule, books, confirms. Emergency path routes to a human immediately. | R2 for booking into pre-approved slot classes; R1 for anything priced or after-hours-premium |
| **Estimate recovery** | Every presented estimate enters a state machine with a mandatory terminal state (won / lost-with-reason / expired). Sequenced, personalized follow-up by text + email + call task, referencing the actual scope and the tech who quoted it. | R1 (drafts, owner/CSR sends) climbing to R2 on evidence |
| **Deferred-work ledger** | Parses technician notes + photos into structured recommendations with an equipment/season trigger. Re-offers at the right month. | R1 |
| **Capacity-aware dispatch assist** | Proposes the board: skill match, drive time, part availability, membership priority. Proposes only — the dispatcher moves it. | R1, permanently proposing |
| **Owner's board** | Revenue at risk today (unanswered calls, aging estimates, unbooked emergencies), recovered this week, and the counted automation rate. | — |

**Integrations:** ServiceTitan / Housecall Pro / Jobber (jobs, estimates, customers), Twilio + a voice layer (Vapi per the locked stack) for calls and SMS, QuickBooks for invoicing truth, Google Business Profile for review requests.

## 5. The ROI model (assumption-stated)

Inputs the owner supplies, arithmetic shown on screen, labelled a MODEL:

```
Missed-call recovery   = missed calls/wk × booked% × avg ticket × 52
Estimate recovery      = open estimates × incremental close% × avg estimate value
Deferred work          = logged recommendations × re-offer accept% × avg job
```

The build **must** refuse to display any of the three when its input is not recorded — showing `unmeasured — no call log connected` instead of a number is the whole point, and it is the thing a no-code competitor's ROI calculator will never do.

## 6. The demo path (10 minutes)

1. Owner's board: three amounts at risk, one of them showing `unmeasured` with the reason.
2. Play an inbound after-hours call → qualified → booked into a real slot → confirmation text. Then a gas-smell call → immediate human handoff.
3. Open an aging $9,400 estimate → the follow-up ladder, the drafted text in the tech's voice, the approval gate.
4. August view of the deferred ledger: 40 weak capacitors from last summer, re-offer campaign staged.
5. The event log: every action, its actor, its rung, and the counted automation percentage.

## 7. Guardrails

No pricing beyond the published diagnostic/trip fee without human approval. No safety advice — gas, CO, water intrusion, electrical burning smell route to a human on the first signal, and the classifier is biased to over-route. No booking outside real capacity. Recordings and transcripts are consent-stated per state.

---

## 8. The prompt

> Copy everything below into a fresh chat in this workspace.

---

**Build a pre-built vertical AI OS prototype for residential home-services contractors (HVAC, plumbing, electrical). Working name: Dispatch OS.**

Build it into `Pre Build Ideas/home-services/build/`. This is an yourco pre-build: a demoable prototype with synthetic data, not a production system and not a client deployment. Read `CLAUDE.md`, `processes/ai-os-modules.md`, and `processes/autonomy-matrix.md` first, and mirror the architecture of `Pre Build Ideas/property-management/build/` — read `Pre Build Ideas/property-management/build/core.py` before you write anything, and follow its structure and its honesty rules exactly.

**The business you are modelling.** A $6M residential HVAC + plumbing contractor, 22 employees, 9 trucks, ~2,800 jobs/year, ~$540 average repair ticket, ~$9,200 average system replacement, seasonal peaks in July and January. Give it a name, an owner persona, a service area, a membership plan, and a real-feeling price book. The operator who sees this should recognize their own business in the seed data.

**Solve the three revenue leaks — that is the entire product thesis:**

1. **Every inbound gets answered and booked.** An intake agent that handles call/SMS/web-form 24/7: qualifies trade, symptom, urgency, service-area, homeowner-vs-renter and existing-customer status; states the published diagnostic fee; offers only slots that genuinely exist in the schedule given skill and drive time; books; confirms. Emergency signals (gas odour, CO, active water, burning electrical smell) bypass everything and route to a human immediately — bias the classifier toward over-routing and make that bias visible in the code.
2. **No estimate dies undecided.** Every presented estimate is a state machine that cannot rest in "presented" — it must reach won, lost-with-a-recorded-reason, or expired. Build the sequenced recovery: personalized text/email drafts that reference the actual scope and the technician who quoted it, escalating to a call task, with a hard stop on the ladder. Drafts route through an approval gate.
3. **Deferred work becomes a ledger.** Parse technician job notes and photos into structured recommendations (component, condition, urgency, quoted amount, decline reason, equipment age) with a seasonal re-offer trigger. Show the August campaign built from last summer's declines.

Plus **capacity-aware dispatch assist** (proposes the board — skill match, drive time, parts, membership priority — and only ever proposes), and an **owner's board** showing revenue at risk today, recovered this week, and the counted automation rate.

**Architecture.** Python stdlib only. `core.py` holds every *rule* — the price book, the urgency taxonomy, capacity and drive-time math, the estimate state machine, the recovery cadence, the seasonal trigger calendar, and the autonomy matrix. Nothing rule-shaped goes in the agents or the UI. `agents.py` holds the agents, each declaring its autonomy rung per action. `seed.py` generates the synthetic business at any scale (`--jobs 2800 --months 18`) including call logs with realistic abandon patterns, presented estimates at every age, and technician notes in messy human prose. `data/` is a JSON store. `app/` is the surfaces, served by a stdlib HTTP server bound to `127.0.0.1`, and you add its entry to `.claude/launch.json` and verify it responds before telling me it works.

**The two honesty rules are non-negotiable and must be enforced in `core.py`, not by convention:**
1. A number that cannot be computed from recorded events is returned as `None` with a `_missing` reason and rendered as `unmeasured — <reason>`. Never estimated, never zero-filled. The ROI panel must be able to show three blanks.
2. Every state change is appended to an immutable event log with its actor (`agent:<name>` or `human:<id>`) and its autonomy rung. The automation percentage is *counted* from that log and never asserted.

**Moat layer, required.** Approval gate as the R1 floor on every outward action (send, book, price, dispatch); an eval harness that scores the intake classifier against a labelled set you generate, including the emergency-routing recall which must be reported separately; an audit log view; and a rung-promotion rule that requires a recorded streak, not a vibe.

**ROI panel.** Computes from owner-supplied inputs only, shows the arithmetic on screen, is labelled a MODEL with its assumptions listed, and refuses any line whose input is not recorded. No industry benchmark statistics unless you can source them to the last 12–18 months, and no fabricated metrics or testimonials anywhere.

**White-label.** The client-facing surfaces carry the demo company's brand only. No yourco name, no yourco logo, no agent names on anything a client would see.

**Data.** Synthetic only. No real PII, no real phone numbers (use 555 ranges), no outbound network calls of any kind — stub every integration behind an adapter interface (ServiceTitan / Housecall Pro / Jobber, Twilio/voice, QuickBooks) so the seam is visible and a real connector could drop in later. A missing adapter reports `cannot-simulate`, which is a blocker, not a pass.

**Tests.** `test_dispatch_os.py`, stdlib `assert`s, pinning the honesty rules specifically: an uncomputable ROI line returns `None` with a reason, the event log is append-only, the automation rate is counted from the log, an emergency phrase always routes to a human, and no outward action can execute above its declared rung.

**Deliverables:** the running build, the launch.json entry, a `README.md` in the build folder with a 10-minute demo script (owner's board → after-hours booking → emergency handoff → aging estimate recovery → deferred-work August campaign → event log), and an honest "what this does not do yet" section. Tell me the test count and what it refused to compute.

Do not send anything anywhere, do not deploy, and do not put a real company's name on it.
