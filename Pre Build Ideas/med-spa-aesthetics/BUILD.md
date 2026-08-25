# 2 · Med Spas & Aesthetics — **Consult OS**

*Pre-build. Not built, not sold, no client. See `../_README.md` for the shared build contract.*

## 1. The idea in one paragraph

A med spa buys attention expensively — Instagram, paid social, influencer, referral — and then loses most of it in the gap between the inquiry and the treatment room. The DM arrives at 9pm and gets answered at 11am. The consult is booked and one in four doesn't show. The consult happens, the patient says "let me think about it," and nobody structures the decision. And the patient who *does* treat is on a biological clock — neurotoxin fades at three to four months — that nobody's calendar is watching. **Consult OS** runs that whole corridor: instant multi-channel response, a no-show prevention ladder, a decision-chaser after the consult, and a treatment-cadence rebooking engine. The owner sees cost-per-booked-consult, consult→treatment conversion, and rebooking compliance in one place, per source.

## 2. Who buys it

The **owner-injector or the practice manager** of a single or two-location med spa doing $800k–$4M, running Boulevard / Zenoti / Aesthetic Record / Nextech, spending real money on paid social. They feel the pain as *"my leads are expensive and my front desk can't keep up"* — and they are unusually willing to buy tools, which cuts both ways: high receptivity, crowded field, so the moat argument (operated, gated, evaluated) is what differentiates us from the twelve chatbots in their inbox.

## 3. The bleeding neck

- **Response latency on expensive leads.** Inquiries land on Instagram DM, TikTok, web form, text, and phone, at night and on weekends. The front desk is with patients all day. A lead answered in five minutes and one answered next morning are not the same lead.
- **Consult no-shows.** No deposit, no pre-visit relationship, no reminder ladder that does anything but remind.
- **The undecided consult.** High-ticket aesthetic decisions (a $4,800 laser package, a $1,200 filler plan) are considered purchases. The follow-up is usually nothing, or one text.
- **Rebooking drift.** Neurotoxin, filler, laser series, memberships — all cadence-driven, none of it watched. A patient who slips from 3.5 months to 7 months is a 50% revenue cut on that patient, silently.

## 4. What we build

**Pillars:** Intake (1) + Sales (2) + Customer/Retention (4). **Form factors:** digital employee (the concierge) + headless automation (ladders and cadence) + embedded surface (the owner's funnel board).

| Module | What it does | Autonomy start |
|---|---|---|
| **Concierge** | Answers DM / text / form / call in under a minute, 24/7. Qualifies interest area, timeline, budget band, contraindication screen (routes, never advises), books the consult, takes the deposit link. | R2 to book and answer logistics; **R1 hard floor** on anything clinical |
| **Show-up ladder** | Deposit request, confirmation, pre-visit expectation-setting, day-before and morning-of, plus an instant-rebook offer the moment a cancellation lands. | R2 |
| **Decision chaser** | After the consult: the treatment plan restated in plain language, financing options (as options, not advice), the specific objection captured by the injector, a bounded follow-up ladder ending in a recorded decision. | R1 |
| **Cadence engine** | Per-treatment reorder clocks (toxin, filler, laser series, facial memberships). Flags drift *before* the patient lapses, with the injector's own note as the hook. | R1→R2 |
| **Funnel board** | Source → inquiry → response time → booked → showed → treated → rebooked, with cost-per-stage where ad spend is connected and `unmeasured` where it is not. | — |

**Integrations:** Boulevard / Zenoti / Aesthetic Record (appointments, treatment history), Meta + TikTok lead surfaces, Twilio SMS, a payments link for deposits, and the practice's EMR read-only where one exists.

## 5. The ROI model (assumption-stated)

```
Speed-to-lead value   = after-hours inquiries × incremental book% × avg consult value × show%
No-show recovery      = consults × no-show% reduction × avg first treatment
Decision recovery     = undecided consults × incremental close% × avg plan value
Cadence recovery      = active patients × lapse% prevented × annual treatment value
```

Every line refuses to render without its input. Cost-per-booked-consult specifically must show `unmeasured — ad spend not connected` rather than guessing, because that number is the one the owner will check against their own ad account.

## 6. The demo path (10 minutes)

1. Funnel board by source, one column blank and labelled.
2. A 9:40pm Instagram DM → answered in 40 seconds → qualified → consult booked with a deposit link → confirmation.
3. A message mentioning a medication/condition → clinical stop → routed to the injector, with the transcript showing the AI declining to advise.
4. A cancellation at 8:05am → the ASAP list ranked → the slot refilled.
5. An undecided $4,800 plan → the chaser ladder and the injector's captured objection.
6. The cadence board: 61 patients drifting past their toxin window, ranked by value.

## 7. Guardrails

**No medical advice, ever** — no dosing, no unit counts, no contraindication rulings, no "you'd be a good candidate." Anything clinical is routed to a licensed injector, and the routing bias is toward over-routing. No before/after claims, no outcome promises, no fabricated testimonials or results. PHI handled under a HIPAA posture (minimum necessary, audit log, no PHI in third-party prompts without a BAA in place) — flag explicitly that a real deployment needs counsel and a BAA before any live patient data. Deposits are a link, never a card number typed by an agent.

---

## 8. The prompt

> Copy everything below into a fresh chat in this workspace.

---

**Build a pre-built vertical AI OS prototype for med spas and aesthetic clinics. Working name: Consult OS.**

Build it into `Pre Build Ideas/med-spa-aesthetics/build/`. This is an yourco pre-build: a demoable prototype on synthetic data, not a production system, not a client deployment, and never touching real patient data. Read `CLAUDE.md`, `processes/ai-os-modules.md`, and `processes/autonomy-matrix.md`, then read `Pre Build Ideas/property-management/build/core.py` and mirror its architecture and its honesty rules exactly.

**The business you are modelling.** A two-location med spa, $2.1M revenue, three injectors and one laser tech, ~180 new inquiries/month across Instagram DM, TikTok, web form, text and phone, ~$650 average first treatment, ~$3,400 average package, on Boulevard. Give it a name, an owner-injector persona, a service menu with real aesthetic treatments and price bands, memberships, and an ad-spend picture. An operator should recognize their own week in the seed data.

**The product thesis is the corridor from inquiry to repeat treatment. Build these four:**

1. **Instant concierge.** Answers every inquiry channel in under a minute, 24/7. Qualifies interest area, timeline, budget band and new-vs-existing; runs a *screening* triage that routes anything clinical to a human rather than answering it; books the consult against real availability; issues a deposit link. Response latency is a first-class recorded metric per lead.
2. **Show-up ladder.** Deposit request → confirmation → pre-visit expectation-setting → day-before → morning-of, plus a cancellation-triggered ASAP refill that ranks the waitlist by plan value, recency and stated flexibility.
3. **Decision chaser.** After a consult, the injector's plan and captured objection drive a bounded follow-up ladder that must terminate in a recorded decision (treated / declined-with-reason / expired). Financing is presented as options, never as advice.
4. **Cadence engine.** Per-treatment reorder clocks (neurotoxin 3–4 months, filler by product, laser series intervals, membership visits). It flags patients drifting toward lapse *before* they lapse, ranked by annual value, with the injector's own last note as the personalization hook.

Plus an **owner's funnel board**: source → inquiry → response time → booked → showed → treated → rebooked, with cost-per-stage where ad spend is connected and an explicit blank where it is not.

**The clinical guardrail is load-bearing and must live in `core.py`, not in a prompt string.** The system never gives medical advice: no dosing, no unit counts, no contraindication rulings, no candidacy opinions, no outcome promises, no before/after claims. A deterministic classifier routes clinical content to a licensed human, biased toward over-routing, and the eval reports its recall separately from everything else. Build the demo so this refusal is *visible* — a prospect should watch it decline to answer and understand that the refusal is the product.

**Architecture.** Python stdlib only. `core.py` holds every rule: the service menu and price bands, the qualification taxonomy, the clinical-routing classifier, the ladder cadences, treatment reorder intervals, the decision state machine, and the autonomy matrix. `agents.py` holds the agents with a declared rung per action. `seed.py` generates the practice at any scale (`--inquiries 180 --months 12`) with realistic channel mix, night/weekend arrival times, no-shows, undecided consults, and patients at every point of cadence drift. `data/` is a JSON store. `app/` is the surfaces on a stdlib server bound to `127.0.0.1`; add the `.claude/launch.json` entry and verify it responds.

**The two honesty rules, enforced in `core.py`:** (1) any number not computable from recorded events returns `None` with a `_missing` reason and renders as `unmeasured — <reason>` — never estimated, never zero-filled; (2) every state change appends to an immutable event log with actor and autonomy rung, and the automation percentage is counted from that log, never asserted.

**Moat layer:** approval gate as the R1 floor on every outward message; an eval harness over the qualification and clinical-routing classifiers with a labelled set you generate; an audit log view; rung promotion only on a recorded streak.

**HIPAA posture, stated honestly:** minimum-necessary data, an access audit log, and a written note in the build README that a real deployment requires counsel review and a signed BAA before any live patient data — and that this prototype has neither because it uses synthetic records only.

**Data:** synthetic only, 555 phone ranges, no real names, no outbound network calls. Stub Boulevard/Zenoti, Meta/TikTok lead surfaces, SMS and payments behind adapter interfaces so the seam is visible; a missing adapter reports `cannot-simulate`, which is a blocker, not a pass. Payments are a link only — never handle card data.

**White-label:** the demo practice's brand only. No yourco name, no yourco logo, no agent names on any patient-facing surface.

**Tests:** `test_consult_os.py`, stdlib asserts, pinning: an uncomputable funnel metric returns `None` with a reason; the event log is append-only; a clinical phrase always routes to a human and never receives an answer; no outward message can send above its declared rung; the cadence engine never flags a patient whose treatment history is absent.

**Deliverables:** the running build, the launch.json entry, a build `README.md` with the 10-minute demo script (funnel board → 9:40pm DM booked in 40 seconds → clinical refusal → cancellation refilled → undecided plan chased → cadence drift list), and an honest "what this does not do yet." Report the test count and every number the build refuses to compute.

Do not send anything, do not deploy, do not use a real practice's name.
