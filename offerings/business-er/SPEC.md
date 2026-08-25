# Business ER — Build Spec

**Working name:** Business ER (frontier #12)
**Author:** the Founder
**Stack:** Vapi + Twilio intake line (locked voice stack, `decisions/2026-06-08_Reed-production-stack.md`) + web/email intake fallback · triage agent (Claude API, structured intake protocol) · golden-template rapid-overlay for stabilization builds · the standard moat layer (eval · approval · audit log) · CRM (every case is a pipeline row from minute one)
**Status:** Spec — see `offerings/_frontier-roadmap.md` row #12. Build trigger: **post-launch AND delivery proven (first 3–5 white-glove engagements complete).**
**Pillar / form factor:** Intake (pillar 1) turned on yourco itself; form factor 1 (the triage agent answers) in front of a human-led stabilization engagement.

---

## 1. Concept

A **911 line for operational emergencies.** The office manager quit with no notice and she was the only one who knew billing. The scheduling system died Friday and forty jobs are unassigned Monday. The one estimator is in the hospital and bids are due. SMB owners in this state don't want a discovery call in two weeks — they want someone to pick up *now*. Business ER is a 24/7 intake line where a triage agent answers immediately, runs a structured assessment, and — for true operational emergencies — yourco starts **same-day stabilization, first 72 hours free**. Stabilize first, talk business after: the free window exists to stop the bleeding, not to sell. When the situation is stable, and only then, the natural conversation happens — usually "the reason this was an emergency is that this function had no continuity," which is the Understudy (#7) pitch written by the client's own week.

The strategic bet: **crisis is the one moment an SMB owner will adopt AI overnight.** Every objection (time to evaluate, change resistance, "we'll get to it") evaporates when the alternative is the business stopping. The Land stage of the flywheel has no stronger converter — but only if the ER actually answers, which is why this offering's centerpiece is not the pitch, it's the **capacity honesty** in §3: an ER that can't staff its calls fails publicly on its first real one, and the roadmap trigger exists precisely to prevent that.

## 2. Why it's never been done

Emergency response exists for IT ("managed service provider, 4-hour SLA") and for nothing else in the SMB operational stack — because a services firm's emergency capacity is idle payroll. Humans waiting by a phone for crises that arrive unpredictably is a cost structure only enterprise retainers can carry, so nobody offers SMBs an operational ER, and consultants who *could* parachute in sell two-week discovery instead — arriving after the owner has already improvised or given up. The AI-native unlock is threefold: (1) **the intake layer costs nothing while idle** — a triage agent answers at 2 a.m. for pennies, so 24/7 availability stops being a payroll problem; (2) **stabilization is fast because the scaffolding is prebuilt** — the golden template + module library means "get a working intake/dispatch/billing stopgap running" is an overlay task measured in hours, not a from-scratch build; (3) **the free window is affordable because the marginal cost of the stopgap is mostly tokens**, which yourco absorbs by design (token economics, CLAUDE.md). What remains scarce is founder attention — the one input that doesn't scale — and no incumbent has an honest answer for that either; ours is the capacity gate below, stated in public rather than discovered by a caller.

## 3. Build shape — capacity honesty is the centerpiece

### 3.1 Staffing math (what one founder + the OS can actually absorb)

An ER case consumes the scarcest resource in the company: **the Founder-hours in an unplannable burst.** The design assumes, conservatively: a true emergency consumes the founder's discretionary capacity for its first 24–48h; concurrent true emergencies cannot be served white-glove by one person. Therefore, hard limits, encoded in the intake system, not in good intentions:

- **Concurrent-case cap: 1 active emergency case at a time** (v1; revisit only with delivery capacity beyond the Founder). The cap is a config value the triage agent reads — when at capacity, the line says so honestly: it still triages, still delivers the immediate-guidance layer (checklist-grade stabilization steps the agent can safely give), and offers the first available slot — it never silently takes a case it can't serve.
- **Intake is always-on; commitment is capacity-gated.** The 24/7 promise is "you will reach a competent triage immediately," never "we take every case."
- **Existing clients preempt:** an ER case never degrades a paying engagement's service; if it would, the case waits or is declined. This is stated in the ER terms.
- The cap and its current state live in one runtime config; the dashboard shows it; the triage agent may not override it (guardrail, not judgment).

### 3.2 Triage tiers (the agent's first job is telling these apart)

| Tier | What it is | Response |
|---|---|---|
| **T1 — true operational emergency** | A core function is stopped or stops within days: key person gone, system down, deadline that halts the business | Same-day human callback; 72h-free stabilization if accepted and within capacity |
| **T2 — urgent but schedulable** | Real pain, no cliff: "drowning in intake," chronic backlog, looming-but-weeks-out risk | Honest reframe on the call ("urgent, not an emergency — here's the fast normal path"), audit CTA, CRM warm lead |
| **T3 — sales call in disguise** | Curiosity, price-shopping, "what would AI cost," vendors, tire-kickers | Courteous route to the standard funnel (site, demos, audit). Never enters the ER queue; never gets the free window |

The tier test the agent applies: *what stops, and when?* No named stopping function with a date = not T1. Misclassifying T3 as T1 is the failure mode that kills the offering (free consulting for shoppers, capacity burned) — the triage protocol is eval'd on exactly this discrimination (Kolby: seeded T3-dressed-as-T1 test calls in the weekly pass).

### 3.3 The 72h-free scope boundary (stabilization only — no free builds)

The free window buys **stabilization**: triage, a stopgap that keeps the function moving (temporary intake line, manual-process bridge doc, an approval-gated draft agent on the golden template), and a written stabilization report (what broke, what's holding, what's fragile). It explicitly does **not** buy: a production module, integrations beyond the minimum stopgap, anything the client keeps running past the window without converting, or ongoing operation. At hour ~48 the client gets the honest fork, in writing: (a) convert to a paid engagement — the stopgap hardens into a real module; (b) hand back — we document the stopgap and wind it down cleanly at 72h, report is theirs to keep. Free work has a wall clock and a scope fence, both stated at intake, because "free 72 hours" without a fence is a free build with extra steps.

### 3.4 Conversion path (after stability, never during)

**No selling inside the crisis.** During the window the only conversation is the emergency. The pitch happens at the stability checkpoint, and it writes itself: the stabilization report's "what's fragile" section *is* the audit's bottleneck map for this client, one week early — the natural continuations are the Understudy (#7, if the emergency was a key person) or the first OS module (if it was a process/system). A client converted this way starts with yourco having already proven delivery under the worst conditions — the strongest possible Land→Outcome handoff. A client who hands back leaves with a clean report and a good story; both outcomes feed referral.

**Data sources:** the intake call/form itself · whatever scoped read access the client grants for stabilization (minimal, revocable, standard consent pack) · golden-template module library. **Effort band:** M for the machinery (triage protocol + eval ~2–3 days, Vapi wiring ~1–2 days, capacity-gate config + terms doc ~1–2 days); each real case is an unplannable S–M burst of founder time — which is the whole point of the trigger.

## 4. Moat fit

- **The moat under time pressure:** a stopgap agent stood up in hours still runs R1 approval-gated on the standard reliability layer — "fast" never means "ungoverned." That an emergency deployment ships with an eval gate and audit log is precisely what no-code emergency improvisation cannot claim, and it's what makes same-day AI deployment *safe to offer at all*.
- **Trust at maximum stakes:** an owner who watched yourco stabilize their worst week extends more standing trust than any demo can produce. ER cases mint the executive trust the whole model runs on.
- **Feeds the proof surfaces:** every case produces ledger rows under adverse conditions — the Trust Ledger (#1) and Interviewable Employee (#2) get their best material ("tell me about a time…" now has real answers).
- **Model-upgrade dividend:** better models triage better and stabilize faster inside the same guardrails — response quality appreciates at constant price.
- **Flywheel:** Land stage (roadmap coverage map) — crisis converts at crisis motivation; the stabilization report hands off directly to Expand offerings (#7, #15).

## 5. Gates / compliance

- **launch-gate (`processes/launch-gate.md`; scope row #12):** the public line, its number, and any marketing of it are branded external surfaces — nothing published until the gate clears. The trigger already sits post-launch, so this is automatically satisfied at activation.
- **Gate #1 scope-rider (engagement legal suite, `processes/counsel-gates.md`):** the ER short-form terms join the existing review batch — 72h-free scope + liability language (stabilization is best-effort, not an SLA or a guarantee against loss), rapid-consent data-access pack, the existing-clients-preempt clause, and clean wind-down terms. **No new gate** — rides the same counsel package.
- **Gate #4 (FTSA/TCPA)** applies only if the ER ever sends outbound SMS (status updates); voice-inbound + email is the v1 posture and stays exempt.
- Recording posture: FL two-party consent — the Vapi line uses explicit disclosure/consent at call start or no recording, matching the recording rider already logged on gate #1 (2026-08-06 entry).
- **Credibility gate:** no fabricated response-time or save-the-day stats anywhere external; until real cases exist, marketing describes the mechanism, not outcomes. The capacity cap is disclosed behavior, not fine print.
- White-label boundary: stopgap agents deployed into a client's business carry the client's brand per house rule; the ER line itself is yourco-branded (it's yourco's own front door).

## 6. Pricing frame *(assumption-stated; Polo locks)*

First 72h: **free, scope-fenced per §3.3** — priced as CAC, logged per case (tokens + founder hours) so Charles's close shows the channel's true cost. On conversion: stabilization hardening is a standard module setup at the normal bands; ongoing = the standard OS retainer ladder — **no crisis surcharge and no crisis discount** (surge-pricing a drowning owner poisons the trust the offering exists to mint; discounting teaches the market to manufacture emergencies). If a non-converting client asks to keep the stopgap running, that's a normal module engagement at normal rates, quoted after the window — never negotiated during it. All framing illustrative until first-cases evidence.

## 7. Activation trigger (build)

**Post-launch AND first 3–5 white-glove engagements complete** — exactly as roadmap row #12, and the reasoning is the offering's own §3: an ER staffed by a founder who hasn't yet proven ordinary-conditions delivery fails on its first call, and it fails in public. Pre-trigger work permitted: triage protocol + tier eval, terms doc for the gate-#1 batch, capacity-gate config — all buildable without a line, a client, or a dollar. The phone number comes last.

## 8. What we will NOT do

- **No case intake beyond capacity — ever.** The cap is enforced by config, disclosed by the agent, and never overridden by enthusiasm. An honest "we're at capacity, here's what you can do right now" beats a botched rescue every time.
- **No selling during the crisis.** No pitch, no upsell, no "while we're in here" scope creep until the stability checkpoint. The 72h window contains zero sales conversation.
- **No free builds.** Stabilization only; the scope fence and wall clock are stated at intake and honored at hour 72, including a clean wind-down for non-converters.
- **No SLA theater.** No guaranteed response times, no "we'll save your business" claims, no uptime promises for stopgaps — best-effort stabilization, stated as such in the terms.
- **No autonomous stopgaps.** Emergency deployments start at R1 like everything else; crisis is never a reason to skip the approval gate, the eval, or the audit log. High-stakes actions (payments, pricing, HR, legal/medical substance) stay R1 per the standard matrix.
- **No manufactured urgency in marketing.** We don't advertise with fear ("your business could stop tomorrow"); the channel is for owners already in the water, not for scaring dry ones in.
- **No poaching from the free window.** A T2/T3 caller rerouted to the normal funnel is not quietly given ER treatment to win the deal — tier discipline is what keeps the line answerable.
- **No case details in marketing without written client consent** — war stories are the client's to authorize, anonymized-pattern learnings only otherwise (the Immune System #8 rule, applied to ER exhaust).
