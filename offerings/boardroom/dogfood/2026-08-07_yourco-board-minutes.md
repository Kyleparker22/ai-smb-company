# yourco — Board Minutes, Meeting #1 (dogfood)

**Date:** 2026-08-07 · **Convened by:** Brett (Boardroom loop, dogfood run on yourco's own data)
**Owner present:** the Founder (all decisions remain his)
**Seats:** CFO lens · Skeptical-customer lens · Operator lens · **Dissent seat** (mandated)
**Charter note:** First convening — no prior resolutions to carry forward. This is the Boardroom spec (`offerings/boardroom/SPEC.md`) run against yourco itself, per the dogfood-before-client rule. Lenses are generic roles only; no simulated real people.

---

## Agenda

1. Cash position and burn (the solvency item)
2. The warm engagement (Sample Client — unsigned at proposal since June)
3. Build-vs-sell allocation (18 frontier specs vs the Year-0 milestone block)
4. The partner admission (50/50, lanes undefined)
5. Counsel (still unengaged, 33 days after the tracker named it the headline gap)
6. Dissent · Questions for the owner · Resolutions

---

## What the numbers said (every figure source-stamped)

| Figure | Value | Source |
|---|---|---|
| Cash on hand | **$0** (the Founder-supplied 2026-08-05) | `finance/runway.md` |
| Runway | **0.0 months** — cash-insolvent vs obligations; operating only as the Founder personally funds charges | `finance/runway.md` |
| MRR | $0 (pre-revenue, no signed engagements) | `finance/runway.md` |
| Fixed monthly burn | **~$614.22/mo** (restated +$200 on 2026-08-03 — the Claude Max sub was off-book) | `finance/expenses.md` §Recurring |
| Triage already written, unexecuted | cuts to **~$362/mo** floor (~$271 deeper) — recoverable: Instantly duplicates $194 + Descript $35 + Granola $14 + Plausible $9 | `finance/runway.md` §Burn triage (2026-08-05) |
| Hostinger VPS | **$24.49 UNPAID, 2 failed attempts (Jul 9 + Jul 20)** — suspension = whole-OS-dark | `finance/expenses.md` |
| Claude API org credit | **$0 since ~Jul 30 → runtime DARK**; no loop artifacts after Jul 28 | `finance/expenses.md` 2026-07-30 row |
| Warm engagement | Sample Client: proposal sent June 2026 ($0 kickoff, $1,000/mo), **still unsigned**; 2026-08-06 meeting pivoted lead use case to Design Studio; **the Founder committed a v1 walkthrough for the week of 2026-08-10** | `clients/sample-client/_README.md`, CRM activity |
| Frontier specs authored pre-revenue | ~18–20 offering specs in `offerings/` (incl. this one) | `offerings/` directory |
| Counsel engaged | **None** — "Counsel firm / contact: none engaged yet"; gate #14 counsel-ready, gate #11 is a one-pager, undone | `processes/counsel-gates.md` |
| Not integrated / missing | June Anthropic top-up amount, HighLevel backfill, several tool tiers TBD; API metering stale since Jul 22 | `finance/expenses.md` notes |

---

## Positions by lens

### CFO lens (cash, margin, concentration)

The company's real balance sheet is the Founder's personal one — at $0 cash, every recurring charge is an undocumented founder loan. Three observations:

1. **The gap is execution, not analysis.** The triage table has existed since 2026-08-05 with named cancellations worth ~$252–343/mo. Two days later, none is booked as cancelled. The company keeps producing correct financial analysis and not acting on it — the burn restatement itself (Max sub off-book, figures understated ~48% for a month) shows the ledger finds the truth late and the owner acts later.
2. **The burn is buying idle capacity.** $291/mo of Instantly for a sending machine that is OtherVenture-gated from sending; $58/mo of Descript/Granola/Plausible for paused workstreams; and the single largest line ($200 Claude Max) is the only one demonstrably in daily use. Meanwhile the runtime — the thing the company's pitch is about — is dark for want of an API top-up, and its host is 29 days unpaid.
3. **Priority order at $0:** pay Hostinger today (suspension risk is existential to the OS); execute the triage this week; treat the API top-up as a deliberate decision (fund it with auto-reload on a funded card, or accept a dark runtime until revenue — the current state, silently half-dead, is the worst of both).

### Skeptical-customer lens (why would I churn / what's degrading)

Sitting in Client Owner's chair, or any prospect's:

1. **The vendor selling "we own reliability so you don't" has let its own OS go dark twice** (credit exhaustion Jun 16–18, again Jul 30–present) and its own host go unpaid for a month. No client can see this today — but the pitch is only as honest as the practice, and the practice is currently the counterexample.
2. **From the buyer's side of the Sample Client table:** I asked for something in June; two months later I have a better, bigger idea and still nothing running. The 2026-08-06 pivot reads to the seller as renewed energy; to a buyer it can read as scope inflation in place of delivery. The one thing that rebuilds the trust curve is the committed v1 walkthrough the week of 2026-08-10 landing *on time and live*. That deadline is now the most trust-critical date the company has.
3. **What's degrading:** the staged site's stats carry a 12–18-month freshness rule; every quarter of gate limbo ages the launch assets toward their own expiry.

### Operator lens (bottlenecks, capacity, key-person)

1. **Key-person exposure is total.** With the runtime dark, "27 agents" is operationally one human with a chat window. Every loop, watchdog, and eval pass has been off for a week-plus; the OS's self-observation — the substrate these very products depend on — is decaying while unfunded.
2. **The bottleneck is not build capacity; it is the decision loop.** Observed cycle times: triage decided → not executed (2+ days); counsel named headline gap → not engaged (33 days); launch-gate → definition fields still blank (months). Build tasks close in days; owner-decision tasks don't close. Adding more build throughput to this system makes the imbalance worse.
3. **Capacity call for the coming week:** exactly one deliverable matters — the Sample Client Design Studio v1 walkthrough (committed, week of 2026-08-10). Everything else, including further frontier specs, should yield to it.

---

## Drafted consensus (read by the dissent seat before its objection)

Execute the burn triage this week; pay Hostinger immediately; make the Sample Client walkthrough the sole build priority; engage counsel once across gates #14/#11/#2/#12; do not sign the OA until lanes are defined.

## The dissent, verbatim

> I object to the consensus — not because any line is wrong, but because **every line of it has already been resolved before, in writing, by this company, and not done.** "Execute the triage" is `finance/runway.md` dated two days ago. "Engage counsel" has been the headline gap in `processes/counsel-gates.md` since July 5 — flagged weekly, 33 days, zero movement. "Force the warm engagement to an answer" is Year-0 milestone #1 in the business plan and failure-mode #2 in its own §10. This board is not producing new information; it is laundering old, ignored resolutions into a fresh artifact — and the artifact-production is the problem. The workspace record shows a system that reliably completes anything achievable inside the editor (18 frontier specs, a restructure, a video pipeline, these minutes) and reliably stalls on the three actions that require an outside human who can say no: **asking Client Owner to sign, paying a lawyer, and cancelling subscriptions.** Business-plan §10 predicted this exactly: *"Failure here will not look like a decision; it will look like one more productive quarter."* This dogfood build wave — three more polished internal artifacts in a week the company has $0 — is that sentence, happening. My objection to adopting the consensus as written: it lets the owner file these minutes as evidence of governance while the pattern continues. I move a **stop-build rule**: no new internal offering, spec, loop, or demo artifact until (1) the triage cancellations are confirmed by receipt and (2) Client Owner has been asked, by a named date, for a signature or a no. If both are done inside 14 days, the rule expires unused and cost nothing. If the rule feels unacceptable, that reaction is the diagnosis.

*(Hindsight scorer note: this objection is falsifiable — check at meeting #2 whether triage receipts exist and whether the signature-or-no ask was made. Score it material or noise then.)*

## Questions for the owner

1. What date do you ask Client Owner for the signature (or the honest no) — and is the 08-10-week walkthrough the setup for that ask?
2. Triage: which of the named cancellations do you decline to make, and why? (A kept sub is fine — an unexecuted decision is not.)
3. Is the runtime worth funding pre-revenue? Yes → top up with auto-reload on a funded card this week. No → power it down deliberately and stop paying its supporting costs. The unchosen middle is the only wrong answer.
4. Counsel is one engagement covering four gates, and gate #14 is a signature you actively want to make. What has to be true for that call to happen this month?
5. Does the dissent's stop-build rule get adopted, amended, or rejected — in writing?

## Resolutions (recommendations — the board advises, the Founder decides)

| # | Resolution | Owner | Status |
|---|---|---|---|
| R1 | Pay Hostinger $24.49 within 48h (whole-OS-dark risk) | the Founder | NEW |
| R2 | Execute the 2026-08-05 triage: cancel duplicate Instantly subs, Descript, Granola→free, pause Plausible; book in `expenses.md` | the Founder (Charles books) | NEW |
| R3 | Deliver the Sample Client v1 walkthrough on the committed week (2026-08-10); it takes priority over all internal build | the Founder | NEW |
| R4 | Within 14 days of the walkthrough: ask Client Owner directly for signature or a no; log either as the first warm-close data point | the Founder | NEW |
| R5 | Engage one counsel across gates #14 / #11 / #2 / #12 this month; fill the engagement fields in `counsel-gates.md` | the Founder (Ray tracks) | NEW |
| R6 | Decide the runtime's funding state deliberately (top-up + auto-reload on a funded card, or planned power-down) | the Founder | NEW |
| R7 | Rule on the dissent's stop-build motion in writing (adopt / amend / reject) | the Founder | NEW |

*Next meeting: 2026-09-01 (monthly). Each resolution above gets a status line — the board remembers.*

---

*This board is not a fiduciary board and holds no governance authority. These minutes are analysis and questions for the owner's judgment; all decisions remain the owner's. Nothing here is investment, tax, or legal advice — items so flagged are questions for licensed professionals.*
