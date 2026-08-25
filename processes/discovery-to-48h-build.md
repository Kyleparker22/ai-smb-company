# Discovery → 48h Build Playbook (any vertical, any employee type)

**Purpose:** make "live in 48 hours from a signed agreement" real for **any** digital employee, in **any** vertical. The moment a client signs, this is the rails from discovery → working employee in their business. The delivery loop is invariant; only two things vary by engagement — the **discovery questions** (the use case) and the **stack** (the employee type). Both are branch points below. A fully worked example (landscaping voice intake) is in the Appendix.

**Owner:** **Kimi** (Delivery Agent — `agents/kimi/`). Until the first engagements harden Kimi in production, **the Founder holds this as builder-operator**.

**Maps to the delivery loop:** discovery → build → eval/gates/watchdogs → 48h go-live → weekly iteration → expansion (`02_delivery_loop.md`). Every engagement starts from `clients/_yourco-template/`; client logic is overlay only. Employee shapes catalog: `clients/_yourco-template/employee-patterns.md` (26 shapes).

---

## Lineage — who Kimi mirrors
Kimi's delivery discipline mirrors **Eric Ries (*The Lean Startup*) / build-measure-learn**, applied to implementation:
- **Ship a working slice fast, then iterate** — the 48-hour go-live is a minimum *viable* employee on the first use case, not a six-month build; learning starts when it meets reality.
- **Build-measure-learn** — evals + watchdogs + the client's real usage are the "measure," weekly iteration is the "learn."
- **Validated learning over vanity** — autonomy is earned in stages against real performance, never assumed.

---

## Hour 0 — Handoff from Janice (onboarding → delivery)
Janice (`processes/onboarding.md`) has already: created `clients/<client>/` from the template, sent the pre-call intake, booked the discovery call, provisioned the employee identity (the Founder-approved), and recorded pricing in `cost.md`. Kimi takes over at the discovery call. For a **multi-employee engagement**, Janice opens one folder; Kimi runs the loop **once per employee, sequenced** (see "Multiple employees" below).

## Hour 0–4 — Discovery call (30–45 min) — **branch point #1: the use case**
**Goal:** capture everything needed to build, so build starts same-day. These questions are **vertical- and type-agnostic** — they work for a voice receptionist, an email-intake employee, a scheduler, a proposal drafter, or an internal Q&A employee:

1. **The job** — *"What's the most repetitive thing your team does that feels like it shouldn't require a human?"* Let them name the pain; then nail the first job precisely.
2. **The trigger** — what kicks the job off? (an inbound call, an email/web-form, a calendar time, a CRM event, a Slack message, a document arriving.)
3. **The inputs** — what information + access the employee needs to do the job.
4. **The decision logic** — the rules, fields, or criteria the employee applies (qualification questions, routing rules, what "good" looks like).
5. **The output / action** — what it produces or does: book, draft, reply, log, route, summarize, escalate, update a record.
6. **The gated actions** — which outputs are **human-approved before they go out** vs. fully autonomous (the approval-gate line, per engagement).
7. **The systems** — the client tools it must read/write (CRM/field software, calendar, phone, email, docs, knowledge base).
8. **Brand voice + identity** — how it should sound, the name it operates as, the tone.
9. **Success metric** — the client's *Desired Outcome*: how we'll both know it's working (calls answered, leads qualified, hours saved, response time, % drafted).
10. **Approvals + compliance** — who signs off on go-live; any regulatory constraints (privacy, TCPA/CAN-SPAM for outbound, industry rules).

Output: a filled `clients/<client>/01_discovery.md` per employee.

## Hour 0–4 — **Branch point #2: select the stack (by employee type)**
Pick the stack from the shape, not the vertical. (Voice locks to Vapi per `decisions/2026-06-08_Reed-production-stack.md`; text/data engagements use the connector that fits.)

| Employee type | Trigger / channel | Core stack | Eval focus |
|---|---|---|---|
| **Voice / phone** (reception, intake, qualify, book) | inbound/outbound call + SMS | **Vapi + Twilio + Google Calendar + ElevenLabs** + CRM log | scripted test calls; downstream actions fire |
| **Text intake / inbox** (email/web-form triage, qualify, reply-draft) | email / form | email connector (Gmail/IMAP) + CRM + Calendar | sample-email runs; correct routing + draft quality |
| **Scheduling / coordination** | calendar event / request | Google Calendar + reminders + comms (SMS/email) | booking accuracy; conflict/double-book guards |
| **Drafting / content** (proposals, follow-ups, posts) | request / CRM stage | LLM + client templates/docs + brand voice | brand-voice pass; factual grounding (no fabricated stats) |
| **Internal Q&A / knowledge** | question (Slack/chat/email) | RAG over the client's docs/KB + access controls | answer accuracy; citation; "I don't know" honesty |
| **Data / ops** (CRM hygiene, reporting, reconciliation) | schedule / data event | client systems + connectors + a report artifact | correctness vs. source; idempotency |
| **Outbound / follow-up** | schedule / list | email/SMS + CRM + **compliance gate** | CAN-SPAM/TCPA; suppression honored; deliverability |

Record the chosen stack + the approval-gate line in `01_discovery.md`.

## Hour 4–24 — Build (overlay on `yourco-template`)
1. **Provision the employee** from the template; overlay the client's logic from discovery (the system prompt / rules / fields).
2. **Wire the chosen stack's connectors** (per the table) — every read/write the job needs.
3. **Configure the approval gates** — the gated actions from discovery stay human-approved (drafts not sent, nothing destructive/external without sign-off). This is the moat made literal per engagement.
4. **Apply brand voice + identity** to every client-facing surface.
5. **Cost tracking** started in `clients/<client>/cost.md` (YourCo absorbs token/usage/infra spend).
6. Fill `clients/<client>/02_build.md` as you go.

## Hour 24–36 — Eval / gates / watchdogs (`03_eval.md`, Kolby's rubric)
- **Representative test interactions** for the type: scripted calls (voice), sample emails/forms (text), sample queries (Q&A), sample records (data) — covering **happy path + edge cases** (missing info, out-of-scope, urgent, ambiguous, after-hours).
- **Verify every downstream action fires** (the booking + the confirmation + the log; or the draft + the routing + the update).
- **Credibility gate:** 0 fabricated capabilities — everything shown works.
- **Watchdogs:** failure alert, **fallback to a human**, and the type's specific guards (double-book guard for scheduling; suppression check for outbound; "I don't know" for Q&A).
- **Quality/accuracy review** against the success metric.
- Eval set written to `clients/<client>/03_eval.md`.

## Hour 36–48 — Go-live (`go-live.md`)
- Point the live trigger at the employee (route the number / connect the inbox / enable the schedule).
- **Soft launch:** monitor the first real interactions closely; Atlas watches health + cost.
- Send the client a go-live note (what's live, how to reach a human, what to expect).
- Confirm the **48-hours-from-signed** promise; log the timestamp.

## After go-live — weekly iteration + expansion
- **Weekly:** eval review, watchdog signals, tune the logic/voice, readout to the client (Kortney owns customer health).
- **Expansion** (loop stage 6): once the first employee is trusted, propose the next — a marginal build fee + retainer step-up (Polo's per-vertical pricing).

## Multiple employees in one engagement
**Sequence, don't parallelize.** Run the full loop for employee #1 to go-live first, *then* #2. Rationale: it protects the 48h promise and the eval quality, and the first employee earns the trust that de-risks the second. In discovery, scope **both**, then pick the build order by *clearest scope × highest impact*. Each employee gets its own `01_discovery` section, eval gates, and go-live timestamp; both share the one `clients/<client>/` folder + `cost.md`.

## Hard gates (must clear before any employee goes live)
1. ✅ Discovery captured (job + trigger + logic + systems + success metric).
2. ✅ Stack selected + connectors wired.
3. ✅ Test interactions pass — all downstream actions fire.
4. ✅ Brand voice approved by the client.
5. ✅ Client sign-off on go-live.
6. ✅ Watchdogs + human-fallback wired.
7. ✅ Approval gates configured (gated actions stay human-approved).
8. ✅ Cost tracking live in `cost.md`.

## Autonomy ladder — toward building without the Founder
Decisions: `decisions/2026-06-12_autonomy-ladder.md` → extended into the standard `decisions/2026-06-25_autonomy-by-default-standard.md`. The goal is a **fully autonomous build — no the Founder bottleneck.** "No human" means **no *the Founder***; the **client** still authorizes access to their own systems and owns go-live in their own business. Gates don't get deleted — they **migrate off the Founder** onto the eval gate (Kolby) + the client's own approval, *as eval evidence earns it.*

> **Every action in this build is rung-governed per the Autonomy Matrix** (`processes/autonomy-matrix.md`; per-engagement instance `clients/_yourco-template/autonomy-matrix.md`, filled at discovery). The split is the matrix made literal: **the build itself is autonomous** (internal edits/drafting/eval = R3); the **client-facing go-live + sends to the client's customers are the gated rung** (start R1, climb to R2/R3 only on Kolby's eval-vs-reality evidence). What the Founder and the client "approve" below is therefore **rung-dependent, not fixed** — each capability sits at its current rung and advances on evidence; unproven/irreversible/high-stakes actions start gated by design.

**Always autonomous (no the Founder, every phase):** discovery synthesis · scaffolding from the template · writing prompts/logic/config · wiring connectors · running internal evals + iterating · drafting the go-live note + client brief.

**The gated moment — *who* holds it depends on the phase:**
| Phase | Build | Go-live + client-facing sends | Kolby's job |
|---|---|---|---|
| **0 — now** | autonomous | **the Founder approves** | run the eval gate |
| **1 — first engagements** | autonomous | **the Founder approves** (to build the track record) | log eval-vs-reality per engagement |
| **2 — spot-check** | autonomous | exceptions + a sample to the Founder; routine proceeds on eval-pass + client sign-off | confirm evals predict reality |
| **3 — the Founder out** | autonomous | **eval gate + watchdogs + the client's own go-live approval** | the gate *is* the control |

**Advance a phase only on data** (Kolby measures; the Founder locks the threshold): e.g. N consecutive engagements where eval-pass predicted real-world success with **zero post-go-live incidents**. Any incident holds/resets the phase. **The enabler is eval rigor** — the more predictive Kolby's gates, the sooner the Founder is removable. Removing the Founder before the track record exists is the one move that risks the moat.

**Never removable (it's the *client's* involvement, not the Founder's):** the client granting tenant/number/data access; the client being sender-of-record for messages to their own customers (CAN-SPAM/TCPA); the client's Phase-3 go-live approval.

> Current operating phase: **0 → 1** (pre-first-client). the Founder holds go-live until the first engagements build Kolby's eval-vs-reality record.

---

## Appendix — worked example: landscaping voice-intake employee
The original v0 case, kept as a concrete reference for a **voice/phone** build:
- **Discovery specifics:** call/text volume + busiest hours; qualification = zip/service area, service type (lawn vs hardscape vs design), scope/size, budget range, urgency; which calendar + availability rules; their field software (Jobber/Aspire/ServiceTitan); confirmation-SMS wording; new Twilio number vs forward-on-no-answer.
- **Build:** Vapi assistant ("<Client> intake employee") greet → qualify → close; Twilio number/forwarding; Google Calendar estimate event (address/phone/scope/budget attached) + confirmation SMS + CRM log; ElevenLabs voice to match brand.
- **Eval:** 5–10 scripted calls (happy path + no-budget + out-of-area + urgent + voicemail); verify calendar event + SMS + CRM log fire each time.
- **Expansion:** review harvester, scheduler, estimate drafter — marginal per the landscaping pricing.

> After each new *type* runs the first time, extract the repeatable parts back into `yourco-template` (Kemba) so the next engagement of that shape is faster.
