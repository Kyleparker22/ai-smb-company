# The YourCo Delivery Loop

Standard engagement flow. Every client engagement follows this loop. No exceptions without a logged decision in `decisions/`.

---

## 0. Engagement folder (when one gets created)
Every prospect lives in the **CRM** as a row — cold and warm leads, no folder. A **client folder** (`clients/<client>/`, cloned from `clients/_yourco-template/`) gets created at **first real call (a discovery conversation happened) or proposal sent — whichever comes first** (the Founder 2026-08-07, `decisions/2026-08-07_folder-at-first-call.md`; previously proposal-sent-or-signed). A CRM row can't hold call notes, a discovery spec, or a demo; the folder can — and the first call is when those artifacts start existing.

- **Formally:** whoever takes the first call scaffolds the folder same-day (`scaffold-engagement` skill); Janice fills + hardens it at signing (credentials, access).
- Still **no folder for cold/warm leads with no call** — those stay CRM rows. The trigger is a real conversation, not a reply.
- The cloned template ships with everything scaffolded: discovery / build / eval / go-live docs, cost tracking, the `demo-kit/`, and the **"How the OS works this client" agent-map stub in `_README.md`** — agents help end-to-end on every engagement from day one (pattern: sample-realty / sample-client / prospect-a).

---

## 0.5 The Audit (the mandatory front door — every engagement)
**Every prospect starts with the Audit** (decision: `2026-06-16_audit-first-os-as-product.md`). A fixed-scope ~1-week **free** diagnostic that learns how the business really runs and dollar-quantifies its bottlenecks (free while yourco is getting started — the Founder 2026-08-16, `decisions/2026-08-16_audit-is-free.md`). Nothing is collected until implementation; the old mechanic credited the fee in full anyway, so a converting client's economics are unchanged — what is given up is revenue from non-converting audits, the upfront float, and the qualification a price provides. It productizes Stage 1 (discovery), qualifies hard, and **produces the exact inputs the scaffolder needs to build a custom AI OS.** SOP: `processes/audit-sop.md` · report: `clients/_yourco-template/audit-report/` · offer page + intake: `agents/webb/pages/yourco-site-v2/audit.html` + `audit-intake.html` · pricing: `pricing/v0/audit.md` (Polo). The Audit's findings *are* the discovery doc → `runtime/scaffold_engagement.py` scaffolds the engagement → **Kimi builds the custom AI OS** (the product). **Hot warm-intros** (e.g. Sample Client, the pre-rule exception) can *fast-track* the Audit, but still run it — it's how Kimi gets what he needs.

> **The product is the custom AI OS, not a single employee.** Steer every engagement toward a **multi-agent system fit to the business** (highest ACV + retention; `pricing/v0/tier2-production.md` → AI-OS bundle). A single AI employee is the entry rung, offered last — but a client who starts there is a good outcome, and the expansion path is scoped from day one, not improvised later (`decisions/2026-08-10_lead-high-land-anywhere.md`).

## 1. Discovery
**Goal:** identify one first use case that can go live in 48 hours and produces a measurable business outcome.

Discovery is NOT requirements gathering. It is scope-killing. The deliverable is one (1) use case, with:
- a named outcome the executive sponsor can repeat back in one sentence
- the system(s) the digital employee will touch
- the success criteria the eval harness will measure against — **and these are the same lines that
  become the SOW's acceptance table** (`processes/contracts/proposal-sow.md`, added 2026-08-24). Write
  them once, here, in a form that is **measurable from the system's own records**. If a criterion cannot
  be measured that way it does not go in the contract, so it should not survive discovery either.
- the approval pattern (full autonomy / human-in-loop / human-must-approve)
- the digital employee's name and email address (in the client's tenant)

Output artifact: `clients/<client>/01_discovery.md`

Watch for: clients trying to add a second use case before the first is live. Push back. Log it as "expansion candidate" and move on.

---

## 2. Build
**Goal:** deliver a working agent from `yourco-template` in hours, not weeks.

Build starts from the golden template. Everything client-specific is overlay on top — never a fork. If a build requires forking the template, that is a sign YourCo doesn't yet have the right abstraction. Capture the gap in `decisions/` for a future template upgrade.

Output artifact: working agent in client tenant + `clients/<client>/02_build.md` describing the deviation overlay.

Watch for: build time exceeding 1 day. If it does, the use case wasn't tight enough at discovery — go back, don't push forward.

---

## 3. Eval / gates / watchdogs
**Goal:** prove the agent does its job and keep it honest.

This is the moat layer. Three pieces:
- **Eval harness** — automated tests of the agent's outputs against success criteria. Must pass before go-live.
- **Approval gates** — where human-in-loop is required, the gate is explicit and logged for audit.
- **Watchdogs** — runtime guards on drift, cost, error patterns, and out-of-scope behavior. Active from go-live onward.

Atlas monitors all three across active engagements.

> **Governed by the Autonomy Matrix.** The loop's gates (eval / approval / go-live) are not fixed checkpoints — each capability runs at its **current rung** and climbs on Kolby's eval-vs-reality evidence. The human approval gate is the **R1 floor** that migrates off as evidence earns each action up (R2 auto+notify+reversible → R3 fully autonomous); unproven/irreversible/high-stakes actions start gated, by design. Standard: `processes/autonomy-matrix.md`; per-client instance filled at discovery: `clients/_yourco-template/autonomy-matrix.md`.

Output artifact: `clients/<client>/03_eval.md` with the passing eval set, gate configuration, and watchdog config.

Watch for: any temptation to ship before eval gates pass. If it fails the eval, it fails the engagement.

---

## 4. 48h go-live
**Goal:** named digital employee, own email in the client tenant, live on the first use case, within ~48 hours of engagement kickoff.

Go-live means real work happening for real, not a demo. The executive sponsor receives a one-pager from the digital employee on day 1 — written by the digital employee, signed with the digital employee's name.

**Acceptance is a step, not an assumption** (added 2026-08-24). Where the SOW carries an acceptance
table, go-live is not finished when the employee runs — it is finished when each line is **demonstrated
against the system's own logs** and the client has accepted, or said in writing what is unmet. The client
has the review window stated in the SOW. Until then the retainer clock is subject to the SOW's credit
term, so this is a billing event as much as a delivery one — Charles needs to know the date.

Output artifact: client-tenant digital employee operating + go-live note in `clients/<client>/04_go_live.md`, **including the acceptance demonstration and the client's acceptance (or their written exceptions)**.

Watch for: clients wanting a demo before go-live. The demo IS the go-live. There is no separate demo phase.

---

## 5. Weekly iteration
**Goal:** improve the digital employee on a cadence the client can feel.

Every week, for every active engagement:
- watchdog signal review
- failed-eval review
- new edge cases captured and added to the eval set
- eval harness updated
- one-pager exec readout (written by the digital employee, signed by the Founder)

Output artifact: weekly readout in `clients/<client>/weekly/YYYY-MM-DD.md`.

**Day-30 referral ask (standing, added 2026-07-21):** the readout nearest day 30 of a live engagement includes the ask — *"who are two other owners who should see this?"* Route answers to the referral program — **one rate card**: a referring client earns the same escalator as any connector, taken off their own bill first (`decisions/2026-08-13_one-referral-rate-card.md`); their bookkeeper/agent/banker is a connector recruit. A thrilled client at day 30 is the program's best source (`processes/partnerships/referral-program.md`).

Watch for: weeks with no captured edge cases. Either the eval set is too narrow, or someone is not watching closely enough.

---

## 6. Account expansion
**Goal:** turn one digital employee into N.

Same client, new use case. Same `yourco-template`, new overlay. Each new digital employee is its own engagement with its own name, email, eval set, and watchdog config.

Expansion conversations anchor on outcomes already delivered — not on capability slides.

Output artifact: new `clients/<client>/<digital_employee_name>/` engagement folder.

Watch for: expansion driven by "they want more features" rather than "they have another outcome we can own." If it's the former, scope it as a v2 of the existing employee instead.
