# Bella — Stage 2: Build

## Build approach
Bella is a **productize-the-process build**: the diagnostic motion (Stage-1 discovery) and the artifacts (`processes/audit-sop.md`, `clients/_yourco-template/audit-report/`) already exist. Building Bella means (1) give the Audit a named owner with a repeatable end-to-end runbook, (2) make the 4-axis scoring and the dollar-quantification method concrete and reproducible, (3) hold her to an Audit-specific eval set (`03_eval.md`), and (4) wire the converted-engagement handoff to Janice/Kimi. This doc is Bella's operating runbook; it references and extends `processes/audit-sop.md` without editing the shared SOP.

> **Note for orchestrator (SOP deltas to fold into `processes/audit-sop.md` if approved):** the shared SOP names Kimi as the Audit's runner; per the roster + `_README.md`, **Bella runs the Audit and owns the SOP**, Kimi receives the converted engagement. The runbook below is the authoritative operating detail; the SOP's ownership line should be reconciled to "Bella runs it; Polo prices it; the Founder approves the report."

---

## The end-to-end Audit runbook

```
Online Revenue Leak Snapshot (free teaser)  →  Step 0
Pre-call intake (async, ~10 min)            →  Step 1  — review + 15-min public scan
Diagnostic call 1 (60–90 min)               →  Step 2  — run the question guide
yourco analysis (offline)                   →  Step 3  — 4-axis scoring
                                                Step 4  — dollar-quantify the #1
                                                Step 5  — map to OS pillars / agents
Findings call 2 (45–60 min)                 →  Step 6  — present the Audit Report
Report delivered + offer                    →  Step 7  — proposal (fee credits the build)
Converted engagement                        →  Step 8  — handoff to Janice → Kimi
```

---

## Step 0 — Online Revenue Leak Snapshot (lead-gen front door)
The free, vertical-specific mini-diagnostic (`agents/webb/pages/yourco-site-v2/_parked/snapshot.html` + `snapshot-config.js`). ~6 vertical questions, findings gated behind name + email + business, instant yourco-branded report (likely leaks, dollar leak from their own inputs with math shown, ROI, a few cited stat-facts). On completion → CRM (source "online snapshot", owner Bella) + Slacked/emailed to the Founder (`runtime/snapshot_intake.py`). Ships **without per-report approval** (templated). It's the teaser that earns the discovery call; then the Audit runbook below takes over. Sadie sources + cites each stat; Bella curates them into the config and keeps the per-vertical copy sharp.

## Step 1 — Intake review + public-data scan
1. Read the submitted intake (`audit-intake.html`): business + vertical, size/revenue band, tools, where time goes, what breaks, #1 frustration.
2. 15-min public scan: website (services, response promises, booking flow), reviews (recurring complaints = ops signals), hours, channels they answer on.
3. Pre-fill a working **candidate-bottleneck list** (3–6 hypotheses) to test on the call — *hypotheses, not conclusions.* Never score off the scan alone; the owner's numbers come from the call.

## Step 2 — Diagnostic call 1 — the question guide
Run in order. Listen for **where money leaks, where time goes, and what only-the-owner can do.** (Canonical in `audit-sop.md` §Step 2; reproduced here as Bella's working script.)

**A. The money map**
1. Walk me through how a customer goes from "never heard of you" to "paid you." Where do they come from?
2. Roughly how many inquiries/leads a month? How many turn into customers?
3. What's an average job/customer worth to you?
4. Where in that journey do you *lose* people — and do you know why?

**B. The time map**
5. What do you (the owner) spend the most time on that isn't the actual work / isn't growth?
6. What happens to a call/message that comes in while you're on a job or after hours?
7. What's the task you most dread or keep putting off?
8. If you cloned yourself, what would the clone do first?

**C. The breakage map**
9. What falls through the cracks when you're busy? (follow-ups, quotes, scheduling, invoicing?)
10. What's something a customer complained about that was really an *ops* problem, not a quality one?
11. What's the bottleneck that, if it vanished, would let you take on more work *today*?

**D. The readiness check**
12. What tools/software do you already pay for? (CRM, scheduling, email, phone, etc.)
13. Who else touches these processes — just you, or a team?
14. If we fixed the #1 thing in 48 hours, what would "it's working" look like to you?

**E. The control map** (added 2026-08-24 — always ask; mapped to rungs in `processes/audit-sop.md` §Step 4b)
15. When we build this, what should it be able to just *do* — and what should always come to you first?
16. Is there anything it should **never** touch, no matter how well it works? *(money, pricing, firing a customer, anything legal or medical — let them name their own.)*
17. Today, who's the last set of eyes before something goes to a customer? What do they actually catch?
18. Would you rather it move fast and you catch the occasional mistake, or check with you first and move slower? *(ask again for internal vs. customer-facing — the answer usually flips.)*
19. If it got something wrong in front of a customer, what does that cost you — a shrug, an apology, or the account?
20. When something does go wrong, who do you want to hear it from, and how fast?
21. What would you need to *see* before you'd let it handle [their answer to 15] without asking you? **Write this one down verbatim — it becomes the promotion criterion.**
22. Six months from now, what should you have stopped doing entirely?

**Never say "autonomy," "guardrail," or "governance" on this call.** Block E is diagnosis in the owner's
language; turning it into a pitch for the reliability layer makes them defensive about answering honestly.

**Bella's call craft (Block):** name the contract up front ("today is diagnosis, not a pitch"); reflect numbers back to confirm them ("so ~30 calls a month, ~$1,000 a job — did I hear that right?"); capture the owner's *own* dollar figures verbatim — those become the quantification inputs, so they're undeniable.

## Step 3 — 4-axis bottleneck scoring (offline)
Score each candidate bottleneck on four axes (1–5), then compute heat and rank.
**Heat = (Money × Frequency × Owner-drain × Fixability) ÷ 625 → expressed as a 0–100% bar** (625 = 5⁴ max; normalizes so the report's heat bar reads as a percentage).

| Axis | 1 (low) | 3 (mid) | 5 (high) | How Bella scores it |
|---|---|---|---|---|
| **Money at stake** | pennies | meaningful but not core | a big chunk of revenue leaks here | from the call's own-number math (leads × loss rate × job value) — the bigger the at-risk dollars, the higher |
| **Frequency** | rare / seasonal | weekly | daily / every lead | how often the leak fires; a daily leak compounds, a rare one doesn't |
| **Owner-drain** | a helper could do it | shared with team | only the owner does it / it eats their day | the more it's stuck on the owner's plate, the higher — owner time is the scarcest input |
| **Fixability (yourco)** | needs deep human judgment / messy | partially automatable | clean, repeatable, automatable now | how cleanly an operated agent can take it; high = a confident 48-hour win |

**Scoring discipline:**
- Score **independently per axis** before ranking — don't let a gut "this is the one" back-fill the scores.
- A bottleneck only ranks #1 if it's high on **Money AND Fixability** — a huge leak yourco can't cleanly fix is not the first build (it goes on the roadmap as a phase-2/human note).
- On uncertain inputs, **round the conservative direction** (down on money, down on frequency) — protects the no-inflation gate.

### The scoring sheet (template — copy per prospect)
```
PROSPECT: __________   VERTICAL: __________   DATE: __________

| # | Bottleneck (one line)            | Money | Freq | Drain | Fix | Heat % | Rank |
|---|----------------------------------|:-----:|:----:|:-----:|:---:|:------:|:----:|
| 1 |                                  |       |      |       |     |        |      |
| 2 |                                  |       |      |       |     |        |      |
| 3 |                                  |       |      |       |     |        |      |
| 4 |                                  |       |      |       |     |        |      |

#1 BOTTLENECK: ______________________________________________
WHY #1 (Money + Fixability both high): ______________________
HONEST-NO-SELL CHECK: is the #1 something yourco can meaningfully fix?  ☐ yes  ☐ no → if no, say so, recommend nothing.
```

## Step 4 — Dollar-quantify the #1 bottleneck
Build the leak figure **only from the client's own inputs**, and **show the math** in the report so they can check it.

**Method:** `(volume) × (loss/miss rate) × (conversion if captured) × (value per unit)` → monthly $ leaking.

> **Illustrative example (NOT a real client — labeled):** a landscaper says ~30 after-hours calls/mo go to voicemail; he figures ~30% would've booked; an average job ≈ $1,000.
> `30 missed calls/mo × 30% would book × $1,000 avg job = $9,000/mo leaking` (≈ $108k/yr).
> That number — in *his* inputs, math shown — is the whole pitch.

**Rules:** every variable is a number the owner gave on the call (or a clearly-labeled conservative assumption with the owner's sign-off on the findings call); no benchmark or "industry average" substitutes for their number unless explicitly labeled as a range; round down when unsure. If a key input is missing, present a **range** and label it, never a fabricated point estimate.

## Step 5 — Map bottlenecks → OS pillars / recommended agents
Translate the top 1–3 bottlenecks into the **8 OS pillars** (`processes/ai-os-modules.md`) and named yourco employee shapes (`clients/_yourco-template/employee-patterns-tier2.md`). Always recommend **one** first build (highest heat, cleanest win — the 48-hour go-live), then a phased roadmap for the rest. Frame as an **OS being assembled** (pillars + sequence), not a single agent shopped off a menu — the single employee is the on-ramp — sell it as the first module of the system you just mapped, never as the cheaper option.

| Bottleneck pattern | OS pillar | Recommended employee (on-ramp) |
|---|---|---|
| Missed calls / after-hours / slow response | 1 Intake / Front Desk | Front-desk / intake agent (Vapi voice or text) |
| Slow quotes/estimates / proposal admin | 2 Sales / Revenue | Estimate/proposal agent |
| Lead follow-up falling through | 2 Sales / Revenue | Nurture/follow-up agent |
| Marketing/content not happening | 3 Marketing / Demand | Content/social agent |
| Support/reviews unmanaged | 4 Customer / Retention | Support-triage / review agent |
| Manual scheduling / no-shows / dispatch | 5 Operations / Delivery | Scheduling + recall agent |
| Back-office (invoicing/AR/data entry) | 6 Back Office / Finance | AR/invoice-chaser agent |
| "We lose the institutional knowledge" | 7 Company Brain | Knowledge-capture agent |
| Onboarding/training/coaching gaps | 8 People / Training | AI sales coach / SOP agent |
| "I can't see what's happening" | (cross-cut) | Reporting/ops dashboard on the moat layer |

## Step 6 — Findings call 2 + the report
Present the **Audit Report** (`clients/_yourco-template/audit-report/`): diagnosed bottlenecks ranked (heat bar only — the 4-axis scores stay internal per `processes/audit-sop.md` §Report clarity; the exec summary names the one-word **primary focus**: money · time · quality · risk) → the dollar cost of #1 (math shown) → the **signal inventory** → the prioritized agent/OS roadmap → the proposed first build. Confirm the owner agrees the #1 is their real constraint (the diagnosis-accuracy check). End with the offer: *"Here's the one we'd build first — live in 48 hours."* (**The audit was free, so there is no fee to come off the build.** Never quote a price yourco is not charging — `decisions/2026-08-16_audit-is-free.md`.)

### Audit Report assembly
The template is **config-driven** (`audit-report/index.html`): Bella fills the `AUDIT` object — everything else renders from it. No build step. Open in a browser → Print → Save as PDF for the client copy.

```js
const AUDIT = {
  client:   "YourCo Landscaping",            // prospect name
  vertical: "Landscaping / hardscaping",
  date:     "2026-06-25",
  headline: "Your biggest leak is after-hours calls going to voicemail.",
  bigNum:   "$9,000 / mo",                 // the #1 dollar leak — from THEIR inputs
  bigLabel: "revenue leaking from missed inbound calls",
  primaryFocus: "money",                   // one word: money · time · quality · risk (SOP §Report clarity)
  bottlenecks: [                            // top 1–3, ranked; heat % drives the bar.
    //  The Step-3 4-axis scores (money/freq/drain/fix) are INTERNAL — they set the
    //  ranking and heat offline but never enter this client-facing config.
    { name: "Missed/after-hours calls",  heat:80 },
    { name: "Quotes go out slow",        heat:51 },
    { name: "No lead follow-up",         heat:36 },
  ],
  math: "30 missed calls/mo × 30% would book × $1,000 avg job = $9,000/mo (≈$108k/yr). " +
        "All figures from your own numbers on our call.",
  signalsIntro: "None of this needed new data — your business already records it all.",
  signals: [                                // the signal inventory (SOP §Step 5): 4–6 rows,
    //  ONLY sources that surfaced in THIS diagnosis, each mapped to a roadmap phase
    { source:"Phone log & voicemail", tells:"which calls you lose, when, and what they were worth", use:"First build" },
    { source:"Quotes sent + won/lost", tells:"how quote speed changes your close rate", use:"Phase 2" },
    { source:"Invoices & job history", tells:"your real avg job value + repeat gaps", use:"the math above" },
  ],
  roadmap: [                                // phased — one first build, then the rest
    { phase:"First build (live in 48h)", item:"Front-desk intake agent — answers/qualifies/books every inbound, 24/7", pillar:"1 Intake" },
    { phase:"Phase 2", item:"Quote/estimate drafting agent", pillar:"2 Sales" },
    { phase:"Phase 3", item:"Lead follow-up / nurture agent", pillar:"2 Sales" },
  ],
  firstBuild: {
    what:  "An operated front-desk agent that catches every call/message you miss and books the job.",
    offer: "Live in 48 hours. The audit is free — there's no fee, and no commitment required to get it.",
  },
  // NO price field — the fee/proposal is handled per pricing/v0/audit.md (Polo). Never a number here beyond the client's own ROI math.
};
```

**Honest-no-sell path:** if the #1 bottleneck is something AI can't meaningfully fix, the report says so plainly and recommends nothing — Bella does not assemble a build proposal. That's a successful audit, not a failed one.

## Step 7 — The offer / proposal
**The audit is free** (the Founder 2026-08-16 — `decisions/2026-08-16_audit-is-free.md`). There is no fee and therefore no credit; say the value, never quote a price yourco is not charging. Bella states the credit mechanic; **the fee itself is Polo's** (`pricing/v0/audit.md`) and never appears on the website or in the report as a number.

## Step 8 — Handoff to Janice → Kimi
A converted Audit's findings **are** the discovery doc. Bella packages: the scored bottleneck table, the #1 dollar figure + math, the recommended first build + roadmap, the prospect's tools/team/readiness notes, and the owner's "it's working looks like ___" definition. Routed **Bella → Janice** (onboard/provision tenant + mailboxes) **→ Kimi** (build → 48h go-live → iterate). Bella's job ends at a clean handoff; she does not build.

---

## Autonomy
Bella operates under yourco's **Autonomy-by-default standard** (`processes/autonomy-matrix.md`; standard set `decisions/2026-06-25_autonomy-by-default-standard.md`, extending the build-side `decisions/2026-06-12_autonomy-ladder.md`). Every action sits on a rung (R0 Observe · R1 Draft/propose · R2 Auto+notify+reversible · R3 Fully autonomous); the trajectory is full autonomy, earned per-action on Kolby's eval-vs-reality evidence, never switched on day one. **Client-facing + irreversible actions start gated (R1).** For a converted Audit that becomes an engagement, the per-client matrix (`clients/<client>/autonomy-matrix.md`, template `clients/_yourco-template/autonomy-matrix.md`) governs the *running employee*; this section governs **Bella's own Audit actions**.

### Action → rung
| Action | Rung | Control |
|---|---|---|
| Intake review · public-data scan · candidate-bottleneck pre-fill | **R3** (internal) | inherently safe (read/observe); reversible working notes in git |
| 4-axis scoring · heat ranking · diagnosis analysis | **R3** (internal) | reversible; eval #1 (scoring consistency) is the gate, not a human |
| Dollar-quantification of the #1 (math from client inputs) | **R3** (internal) | eval #2/#3 (quantification sanity + no-fabrication) catch errors before the report surfaces |
| Map bottlenecks → OS pillars / recommended first build | **R3** (internal) | honest-no-sell + Money×Fixability rank rule (eval #4) |
| Draft the Audit Report; surface it in `#yourco-bella` for review | **R3** (internal draft) | reversible; the draft is internal until the send gate below |
| **The Audit Report to the prospect (send)** | **R1 (gated)** | **the Founder approves before send.** No fabricated numbers; never quotes unlocked pricing. Hard floor. |
| Online Revenue Leak Snapshot report (templated teaser) | R2 (auto+notify) | the **one carve-out** — templated, ships without per-report approval; `[verify]` stat slots block it until Sadie sources them |

### Hard floor / gated (does not climb on evidence by default)
- **Sending the Audit Report / any client-facing email → R1, the Founder-approved.** This is the trust-defining moment (a wrong or inflated diagnosis costs more than a missed sale); it migrates off the Founder → the eval gate + the prospect relationship only as Kolby's record earns it, and even then a capped climb (see eval #2/#3 hard gates). Never starts at R2/R3 — the hard rule in the standard.
- **Quoting a fee / committing pricing → never Bella's** (Polo owns it; off the rung ladder entirely).
- **No fabricated number, name, testimonial, or unsourced stat at any rung** — the no-fabrication gate is absolute regardless of autonomy level.

## Connectors used
- **CRM (David)** — read the intake-sourced lead; write the converted engagement + findings.
- **Gmail (`contact@yourco.example.com`, draft-only)** — schedule calls; send the report **only post-the Founder-approval**.
- **Google Calendar** — book diagnostic call 1 + findings call 2.
- **Slack (`#yourco-bella` / `#all-yourco`)** — surface the drafted report for the Founder's approval.
- **`runtime/snapshot_intake.py`** — staged handler for the online snapshot (CRM write + Slack/email to the Founder), activates at website deploy.

## Closed-loop wiring
- **Scheduled task:** review new intakes on arrival (event-driven) + a weekly sweep of un-booked audit leads.
- **Artifact output:** each Audit produces a dated scored sheet + Report draft the converted engagement reads as its discovery doc; each snapshot produces a CRM lead.
- **Feedback capture:** on the findings call, log whether the owner agreed the #1 was their real constraint (diagnosis-accuracy signal) and whether the audit converted.
- **Feed-forward:** Bella (with Kolby) writes patterns to `learnings/` — e.g. "in trades, missed-call leak is the #1 in N of M audits → lead with that hypothesis" or "owners under-report job value by ~X → confirm twice." Next audit reads these as Step 0 and adjusts the candidate-bottleneck pre-fill.

## Build status
- [x] Audit SOP exists (`processes/audit-sop.md`)
- [x] Audit Report template exists (`clients/_yourco-template/audit-report/`)
- [x] Online snapshot staged (`snapshot.html` + `snapshot-config.js` + `runtime/snapshot_intake.py`)
- [x] Engagement docs authored (this folder)
- [x] 4-axis scoring + dollar-quantification method made concrete (this doc)
- [x] Handoff seam to Janice/Kimi defined
- [ ] `contact@yourco.example.com` provisioned (manual — the Founder, not blocking)
- [ ] Snapshot stats sourced + cited by Sadie (retire `[verify]` slots)
- [ ] First real Audit run (the Founder runs #1 personally) confirmed against the eval set
- [ ] Website launch (offer page + intake live) — same launch-gate as everything external
