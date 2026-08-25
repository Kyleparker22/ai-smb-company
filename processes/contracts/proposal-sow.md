# Proposal / SOW — DRAFT TEMPLATE

> ⚠️ **Draft. Pricing is a proposal until the Founder locks it (Polo's gate). The counsel-reviewed Engagement Agreement governs; this attaches to it as the SOW.** Fill every `[[ ]]`. Outcome + scope from `clients/<client>/01_discovery.md`; **return-side numbers from the Audit's bottleneck quantification** (Step 3 of `processes/audit-sop.md` — the dollar leak in *their* numbers); fees from `pricing/v0/*`; entity details from `finance/legal-docs/business-info.md`.
>
> **Two-sided rule (standard as of 2026-07-20):** every outgoing proposal shows **both sides of the ledger** — what it costs *and* what it returns, side by side. The cost number never travels alone. The return side is computed from the client's own audit inputs with the math shown; if an engagement somehow reaches proposal without a quantified bottleneck, go get the numbers before sending — a one-sided proposal doesn't go out. Decision: `decisions/2026-07-20_two-sided-proposals.md`.
>
> **What this is:** the missing rung between *interested* and *signed*. The Engagement Agreement is the contract; **this** is the one-page, client-facing document that packages the outcome, scope, timeline, and investment for a yes — then doubles as the signed **Statement of Work** under the agreement. Lead with the outcome, never the features. Owner: **Pickle** (packaging) + **Polo** (price) + **David** (pipeline/send). Send via DocuSign.

---

## Proposal for [[CLIENT LEGAL NAME]]
**Prepared by** YourCo LLC · the Founder · founder@yourco.example.com · [[DATE]]
**Valid through** [[DATE + 30 days]]

### The outcome you're buying
You will have **"[[EMPLOYEE NAME]]"** — a named digital employee that **[[does the job in one plain sentence, e.g. answers every inbound call and text, qualifies the lead, books the estimate, confirms it, and logs it]]** — **live in your business within 48 hours of signing.**

> You own the outcome. You never touch the tokens, the models, or the infrastructure — YourCo runs all of it.

### What [[EMPLOYEE NAME]] does
[[3–6 bullets of the specific scope, from discovery — the triggers it answers, what it produces, the tools it works inside (phone / inbox / calendar / CRM).]]

### What's included — every month, one price
- **Build & deployment** of the named employee, integrated with your [[phone / inbox / calendar / CRM]].
- **Full operation** — model/token usage, voice, telephony, hosting: all absorbed by YourCo. **You are never billed for usage.**
- **The reliability layer** — evals, watchdogs, and an **approval gate**: nothing customer-facing sends without your rules. This is the part no one else delivers.
- **Your live console** — watch it work, approve drafts, see outcomes and reliability, any time.
- **Weekly iteration** — we tune it against real usage and send you a readout of what it handled and what improved.
- **Every AI advance, free** — because YourCo runs the stack, when the underlying AI gets better (and it does, fast), we upgrade [[EMPLOYEE NAME]] underneath at no change to your price. A tool you'd buy today is outdated in a year; this gets better every year you have it.

### Where the human stays in the loop
[[Name the gates honestly — what always routes to a person, what it will never do, e.g. "never gives clinical/legal/financial advice," "never quotes a price," "every customer-facing send is yours to approve."]] We show the human steps; we don't hide them.

### Timeline
**Day 0** — you sign and grant the access [[EMPLOYEE NAME]] needs to do the job. **Within 48 hours of that "go-ready" moment** — [[EMPLOYEE NAME]] is live on its first use case (the clock starts when the agreement is signed and access is granted, so a delay on access simply pauses it — fair to both sides). **Weekly** — iteration + your readout. **When trusted** — we scope the next employee (optional).

### How we'll know it worked *(acceptance — what "done" means)*
*Added 2026-08-24 — counsel-gated, see the footer.* This is the section most proposals skip. It is also
the one that makes the rest of this document a commitment rather than a description: without it, "a
deployed AI system" is a thing you received, not a result you got.

**Go-live acceptance.** [[EMPLOYEE NAME]] is accepted when, running on live traffic for
**[[N]] consecutive business days**, it does all of the following:

| # | What must be true | Measured how | Threshold |
|---|---|---|---|
| 1 | [[e.g. inbound calls are answered]] | [[from the call log]] | [[≥95% within 2 rings]] |
| 2 | [[e.g. a qualified caller is booked without a human correcting it]] | [[booking log vs. approval log]] | [[≥N of qualified calls]] |
| 3 | [[e.g. nothing customer-facing goes out unapproved]] | [[the approval log]] | [[100% — this one is absolute]] |

YourCo demonstrates each line against the system's own records. Client then has **[[5]] business days** to
accept, or to say in writing which line is not met.

**If a line is not met.** YourCo fixes it at no additional charge and re-presents. Where go-live acceptance
is unmet **for reasons within YourCo's control**, the retainer does not begin — or, if it has begun, that
period is credited. [[Counsel: confirm the credit mechanism and the "within YourCo's control" carve-out —
access delays and third-party outages sit on the other side of that line (Agreement §4).]]

**Not just at go-live.** The same lines are reported **every month**, from the system's own logs, in the
weekly readout and the monthly report — not from anyone's recollection.

> **The rule that keeps this honest: a criterion has to be measurable from the system's own records.**
> If we cannot measure it, it does not go in this table. A number nobody can check is worse than no
> number, and an acceptance test nobody can run is worse than none — it just moves the argument to the
> end of the engagement instead of settling it at the start.

**Scope changes.** Anything that changes what is being built, when it lands, or what it costs is a
**Change Order** signed by both parties (Agreement §1.1). Ordinary tuning and iteration are what the
retainer buys and are not Change Orders.

### What we commit to keeping it running *(service levels)*
Acceptance above says what "working" means. This says what "running" means — a different promise, measured
separately.

- **Availability:** **[[99.5%]]** of each month on the layer yourco operates.
- **If something breaks:** **[[1 business hour]]** to a human on anything down or customer-facing;
  **[[4 business hours]]** on degraded; **[[1 business day]]** on questions. Business hours are
  **[[Mon–Fri, 9–6 ET]]**.
- **Outside those hours** you hold the kill switch and can stop [[EMPLOYEE NAME]] yourself — you never
  wait on us to stop something. And anything you have gated cannot go out without your approval, so the
  overnight failure is *nothing happens*, not *the wrong thing happens*.
- **If we miss, you get credited**, and if we miss repeatedly you can leave immediately without the notice
  period. Full terms, and the things we honestly cannot warrant — a model provider or phone network going
  down is not something any operator can promise you — are in the **Service Level Agreement**.

> We report these every month from the system's own logs. **If we ever fail to measure a month, we count
> it as missed** — the side holding the logs should carry that burden, not you.

### What this is worth vs. what it costs *(both sides — your numbers)*
From your audit, in your numbers — the math shown, nothing benchmarked from strangers:

| What's leaking today | What you invest |
|---|---|
| **[[$ X,XXX]] / mo** — [[the quantified bottleneck, math visible, e.g. "30 missed calls/mo × 30% would've booked × $1,000 avg job"]] | **[[$ retainer]]** / mo (+ [[$ build]] one-time) |
| **[[N hrs]] / wk** of [[owner/role]]'s time on [[the task]] — worth [[$ X]]/mo at your rates | — |

**Projected payback: [[e.g. the retainer returns ~[[N]]× the leak it closes / pays for itself at [[N]] recovered jobs per month]].**

> These are projections computed from the numbers you gave us in the audit, with every assumption stated above — not guarantees. If your inputs change, the math changes; we'll re-run it with you.

### Investment *(proposal — the Founder locks)*
| | One-time | Monthly |
|---|---|---|
| [[EMPLOYEE NAME]] | **[[$ build]]** | **[[$ retainer]]** /mo |
| [[+ per-unit option, if any]] | — | [[$ per listing/vehicle/SKU/proposal]] |

- **Term:** [[month-to-month / [[N]]-month]] · **Payment:** the build-fee deposit is **due on signing** (Stripe payment link), then the retainer **on receipt / net 0** via **Stripe** — **ACH preferred**, card accepted. *(See `processes/payments.md`.)*
- The retainer covers operating the employee **and all underlying infrastructure**. No usage/token/model/infra charges, ever.
- **Expansion** (optional): each additional employee is a fixed build fee + a retainer step-up — never a new sale from scratch.

### Signatures — this becomes the SOW
By signing, [[CLIENT]] and YourCo adopt this as the **Statement of Work** under, and subject to, the **Engagement Agreement** (and its DPA). Where they conflict, the Agreement controls; the DPA controls on data matters.

**[[CLIENT LEGAL NAME]]** — Signature: ______________________ · Name/Title: [[ ]] · Date: [[ ]]
**YourCo LLC** — Signature: ______________________ · the Founder, [[title]] · Date: [[ ]]

---
> ⚠️ **Counsel-gated (Ray):** the acceptance and service-level sections above, `sla.md`, and Agreement §§1.1, 1.2, 3.1, 10, are drafts added 2026-08-24 and have **not** been reviewed by counsel. Do not send a proposal carrying an acceptance table with a fee-credit remedy until Ray has cleared it — a remedy clause is a liability term, not sales copy.
>
> Honesty footer: figures are a proposal until the Founder locks them. Return-side figures are projections from the client's own audit inputs with assumptions shown — never guarantees, never third-party benchmarks presented as theirs. Demos shown during the sale are illustrative. The Engagement Agreement (counsel-reviewed) is the binding contract; this SOW attaches to it.
