# model-assumptions.md

> The written version of every assumption in `finance/yourco-financial-model.xlsx`, so the model is auditable
> without opening Excel. Built **2026-08-09**. Owner: Charles (finance). Locks: the Founder.
>
> **This is an assumption-stated model, not a forecast.** It is a machine for asking *"what would have to be true?"* —
> not a prediction. Every economic input lives on the workbook's **Assumptions** sheet and nowhere else; every other
> sheet is formulas. Change one yellow cell and the whole thing moves. This file mirrors that sheet row for row.
>
> Two tags are used throughout, and they mean exactly what they say:
> **SOURCED** = traceable to a locked internal document, cited. · **ASSUMED** = no evidence behind it.

---

## 0 · The reality the model is required to start from

Month 0 in the workbook is **2026-08-31**, and it is not flattering:

| Fact | Value | Source |
|---|---|---|
| Cash on hand | **$0** | `finance/runway.md` — the Founder supplied 2026-08-05 |
| MRR | **$0** | `finance/revenue.md` — pre-revenue |
| Active clients | **0** | Sample Client is at *Proposal*, not signed |
| Audits ever delivered | **0** | no audit engagement has ever run |
| Fixed monthly obligations | **~$614.22/mo**, funded personally by the Founder | `finance/expenses.md`, receipt-sourced |
| Runway | **0.0 months** | cash ÷ burn = 0 |

Month 1 of the model is **September 2026**. The workbook is not allowed to start anywhere else, and the Cash & Runway
sheet displays the month-0 row in red above the projection.

---

## 1 · Pricing — the tier ladder

**SOURCED** from `pricing/v0/os-tiers.md` (implementation + retainer bands, a split of the OS envelope Polo locked
2026-06-16) and `pricing/v0/audit.md` (audit fees — **$0 since the Founder's 2026-08-16 call**; the 06-16 lock is retained there as the return price).

| Tier | Implementation (one-time) | Retainer /mo |
|---|---|---|
| On-ramp — single employee | $1,000 – $5,000 | $1,500 – $2,500 |
| Core (~3 agents) | $2,000 – $2,500 | $3,000 – $4,000 |
| Suite (~5 agents) | $2,500 – $3,500 | $4,500 – $6,000 |
| Operation (~7 agents) | $3,500 – $4,500 | $6,500 – $8,000 |
| Command (up to 10 agents) | $4,500 – $5,000 | $8,500 – $10,000 |

> ⚠ **Read the caveat before quoting any of this.** `pricing/v0/os-tiers.md` is still headed
> *"v0 proposal — Polo's draft for the Founder to lock."* The four tier **names** are locked
> (`decisions/2026-06-22_horizontal-positioning-and-os-tiers.md`); the four tier **price points** have never been
> ratified, and they have been treated as canon across the workspace for 47 days without it. **The model uses them as
> a working assumption and says so on the face of the sheet.** The one live proposal in the business — Sample Client,
> scoped Suite→Operation — is priced at **$1,000/mo**, which is one third of the Core floor this model blends off.

| Input | Value | Tag | Note |
|---|---|---|---|
| Audit fee — Standard | **$0** | SOURCED | **the Founder 2026-08-16 — the Audit is free** (`decisions/2026-08-16_audit-is-free.md`). Return price $1,000 suspended in `pricing/v0/audit.md`. Model any audit-fee revenue line as **zero**; note it was always ~zero for converters, since the fee was 100% credited — the change removes revenue from **non-converting** audits and the upfront float. |
| Audit fee — Pro (compliance / multi-location) | **$0** | SOURCED | same — **the Founder 2026-08-16, the Audit is free**; return price $1,500 suspended |
| Share of audits sold at the Pro fee | 20% | **ASSUMED** | no audit has ever been sold; the mix is invented |
| → Blended audit fee (derived) | $1,100 | derived | Standard×(1−Pro share) + Pro×Pro share |
| Founders' free audits (cumulative, one-time) | 3 | SOURCED | `decisions/2026-07-14_founders-audit-offer.md` |

**The audit credit.** 100% of the audit fee is credited against the entire upfront when the client signs a minimum
6-month engagement (`pricing/v0/audit.md`). Modelled as a negative line against implementation revenue on every
converting client.

---

## 2 · How the "blended retainer" is built (it is not a guessed number)

The single most common failure in the old model was a blended retainer with no story behind it — Charles's
2026-08-05 review called out a $2,500 figure that was "neither the per-employee floor nor a stated OS mix." This model
derives the blend from three visible inputs instead:

**(a) Band placement** — where in each tier's range a deal actually lands.

| Input | Value | Tag |
|---|---|---|
| Band placement — early (0 = floor, 1 = top) | **0.00** (every tier at its floor) | ASSUMED |
| Band placement — mature | **0.50** (band midpoint) | ASSUMED |
| Months to glide from early to mature | **30** | ASSUMED |

**(b) Tier mix** — all **ASSUMED**. Reference point: the corrected 2026-07-06 business plan, whose only surviving copy
is `.claude/worktrees/friendly-knuth-1079a4/06_business-plan.md`.

| Tier | Early mix | Mature mix |
|---|---|---|
| On-ramp | 20% | 10% |
| Core | 60% | 45% |
| Suite | 15% | 30% |
| Operation | 5% | 12% |
| Command | 0% | 3% |

**(c) The resulting blends** (computed, not typed):

| Derived | Value |
|---|---|
| Blended retainer / client / month — **early** | **$3,100** |
| Blended retainer / client / month — **mature** | **$4,497** |
| Blended implementation / client — early | $1,950 |
| Blended implementation / client — mature | $2,835 |

These reproduce the corrected business plan's ~$3,100 (Y1) → ~$4,400 (Y3) blended retainer *as an output of stated
mix and band placement*, rather than as an asserted number. The model glides linearly between them over 30 months.

---

## 3 · The three scenario drivers — every one is n = 0

These are the cells the whole model hangs on. **None of them has any evidence behind it.**

| Driver | Conservative | **Base** | Aggressive | Why there is no data |
|---|---|---|---|---|
| Audits started, first selling month | 1.0 | **2.0** | 3.0 | Zero audits delivered in 61 days of operating |
| Audits added per month (linear ramp) | 0.15 | **0.30** | 0.50 | The entire revenue line is this cell compounded 36 times |
| Audits — ceiling per month | 6 | **11** | 16 | No sales or delivery throughput has ever been observed |
| Audit → paying client conversion | 30% | **45%** | 60% | Nobody has ever been asked to buy: 22 deals, 19 stuck at "relationship", 0 signed |
| Annual logo churn | 25% | **18%** | 12% | Nothing has ever churned, because nothing has ever signed |

Supporting timing assumptions, both **ASSUMED**:

- **Conversion lag: 1 month.** An audit sold in month *m* produces its client in month *m+1*.
- **First month an audit is actually sold: month 2 (Oct 2026).** Two warm prospects are live and Sample Client is at
  proposal, so month 2 is not heroic — but it has never happened.

Monthly churn is derived as `1 − (1 − annual churn)^(1/12)`, not as annual ÷ 12.

---

## 4 · Cost drivers

| Input | Value | Tag | Basis |
|---|---|---|---|
| COGS — absorbed model/voice/hosting per client/mo | **$300** | ASSUMED | The plan states a $200–400 range for a multi-agent OS; $300 is its midpoint. **Never measured** — yourco has never run a client OS. For scale: internal API spend ran ~$83/mo across ~20 loops (`finance/token_spend.md`). |
| Fixed subscriptions — base /mo | **$614.22** | SOURCED | `finance/expenses.md` 2026-08-05, itemised: Google $8.73 · Instantly $291 · Canva $18 · Plausible $9 · ElevenLabs $6 · Tailscale $8 · Hostinger $24.49 · Descript $35 · Granola $14 · Anthropic Max $200. Left at full even though `runway.md`'s triage plan takes it to ~$362 — deliberately conservative. |
| Tooling — additional per client /mo | $40 | ASSUMED | seats/usage that scale with clients |
| Tooling — per employee /mo | $150 | ASSUMED | software seats per head |
| Connector / referral commission — % of retainer revenue | **5%** | ASSUMED | The program pays 10–15% by connector volume plus a 1% downline override (counsel-gated), but only a share of clients will ever be referred. 5% blended is a guess. `decisions/2026-06-30_referral-program-v1.md` |
| Payroll burden on employee salaries | **18%** | ASSUMED | employer taxes + benefits + insurance. A **stated rate, not a quote.** Owner draws carry no burden. |
| Delivery haircut — unmetered cost as % of revenue | **8%** | ASSUMED | Rework, support, tools at volume, voice minutes. Without it the model computes ~93% gross margin against the plan's stated 80–85%; **this is the explicit haircut that reconciles the two**, and it is a judgement, not a measurement. With it, gross margin lands at ~82–86%. |
| CAC — cost to acquire one client | **$1,500** | **ASSUMED — NO DATA WHATSOEVER** | yourco has never acquired a client. All 25 companies in the CRM came from the Founder's warm network at $0 marketing cost, and none closed. **This is a placeholder, not an estimate.** It is charged to opex on every new client *and* used on the Unit Economics sheet, so it is not counted once and forgotten. |
| LTV horizon cap | 36 months | ASSUMED | 18%/yr churn mathematically implies a ~61-month client life. Nobody has observed a client life of any length, so LTV is capped rather than run to infinity. The uncapped figure is shown beside it, labelled. |

---

## 5 · People — hires fire on an MRR trigger, not on a date

Each role switches on in the first month where **prior-month MRR ≥ its trigger** *and* the earliest month has passed.
Once on, it stays on. **Every salary is ASSUMED — yourco has never made a hire.**

| Role | Annual base | Burden | MRR trigger | Earliest month | Clients this head carries |
|---|---|---|---|---|---|
| the Founder — founder draw | $72,000 | none (owner draw) | $15,000 | 1 | — |
| Partner (50/50) — draw | $72,000 | none (owner draw) | $30,000 | 1 | — |
| Delivery / Implementation Lead | $85,000 | 18% | $30,000 | 6 | 12 |
| Advisor (first salesperson) | $65,000 | 18% | $45,000 | 9 | — |
| Client Success / Ops | $60,000 | 18% | $60,000 | 12 | 8 |
| Platform Engineer | $120,000 | 18% | $90,000 | 18 | — |
| Finance / Admin (part-time) | $35,000 | 18% | $120,000 | 24 | — |

Plus a **capacity-driven** line that is neither a date nor a trigger:

| Input | Value | Tag |
|---|---|---|
| Additional delivery operator — annual base | $75,000 | ASSUMED |
| Clients one delivery head can carry | **12** | ASSUMED |
| Clients the two principals can carry between them | **10** | ASSUMED |

The model hires **as many additional delivery operators as capacity requires**:
`ceiling((active clients − capacity from named roles) ÷ clients per delivery head)`. This is what stops the plan
quietly serving 90 clients with three people. Reference point: Charles's 2026-08-05 capacity review put two
principals at ~11–16 white-glove clients in Year 1, consistent with the 10 used here — but **nobody has measured a
delivery operator's real load, because no engagement has ever run.**

**The founder-draw treatment matters for the partner conversation.** Both principals draw **$0** until MRR clears
their trigger, so the model does **not** charge principal labour before then. That is why the cash requirement comes
out small — see §7.

---

## 6 · How the engine works

```
audits started (ramp, from the first selling month)
  → cumulative audits; the first 3 are free (founders' offer)
  → audits billed × blended audit fee                          = audit revenue
  → clients convert one month later at the conversion rate     = new clients
  → active clients carry forward, less monthly churn           = active clients
  → active clients × blended retainer                          = retainer MRR
  → new clients × blended implementation, less the audit credit = one-time revenue
  → COGS = active clients × absorbed cost + revenue × delivery haircut
  → opex = payroll (trigger-fired) + subscriptions + connector commissions + CAC on new clients
  → EBITDA → cumulative cash, from a $0 start
```

Blended retainer and implementation glide from the early blend to the mature blend over 30 months
(`maturity factor = min(1, month ÷ 30)`).

---

## 7 · Base-case outputs (resynced 2026-08-10 from the workbook)

> These figures were re-read from `finance/yourco-financial-model.xlsx` on 2026-08-10 after that day's
> four model changes (one hire type — the Advisor at $10,000/mo fully loaded · principals' delivery
> capacity gliding to zero by month 24 · onboarding charged in dollars and hours · removed roles
> actually deleted). The previous version of this table predated all four and understated the model by
> roughly 2x. Source of truth is the workbook; `dashboard/finance_model.json` is the extracted mirror.

| Output | Conservative | **Target** | Aggressive |
|---|---|---|---|
| Active clients — end Y1 / Y2 / Y3 | 25 / 60 / 95 | **50 / 118 / 190** | 75 / 177 / 285 |
| ARR run-rate — end Y1 | $1.10M | **$2.19M** | $3.29M |
| ARR run-rate — end Y2 | $3.04M | **$5.97M** | $8.95M |
| ARR run-rate — end Y3 | $5.13M | **$10.23M** | $15.38M |
| Recognized revenue — Y1 | $489k | **$1.02M** | $1.53M |
| Recognized revenue — Y3 | $4.36M | **$8.61M** | $12.90M |
| EBITDA — Y3 | $2.08M | **$4.30M** | $6.52M |
| NOI % — Y3 | 47.1% | **49.6%** | 50.4% |
| Total people at month 36 | 8 | **13** | 18 |
| Gross margin at month 36 | ~85.6% | **~85.6%** | ~85.5% |
| **Peak cash need (max drawdown)** | $1,528 | **$1,528** | $764 |
| Breakeven month (first EBITDA-positive) | 3 | **3** | 2 |
| Cumulative cash, month 36 | $2.27M | **$4.69M** | $7.04M |

The **Conservative** case now lands close to where the *old* plan put Year 3 (~85–95 clients, ~$4.4M).
That is not corroboration — it means the Target case was raised, not that the floor was validated.
Every figure here is an assumption compounded 36 times; nothing in it has happened once.

### The cash answer, stated honestly

**The cash structure changed on 2026-08-10 (the Founder).** Two decisions replaced the old trigger-based story:

1. **the Founder injects $50,000 on day one, alone.** Partner B and Mike contribute no cash. Month-0 cash is $50,000, not $0.
2. **All three principals draw their $50k salary from month 1** — MRR trigger 0, not $25,000.

Together these mean **there is no unpaid principal time at all.** The old "the real investment is time" framing —
16 unpaid months, $96,000, ~$97,200 to profitability — describes a company that no longer exists on paper. The
Cash & Runway block that computed it now reads zero by design, and says so rather than presenting a table of zeros.

| Target case (recalculated 2026-08-10) | Value |
|---|---|
| Starting cash, month 0 | **$50,000** — the Founder's injection |
| Cash needed *beyond* the injection | **$0** |
| Lowest cumulative cash reached (the trough) | $22,104, month 3 |
| **Most of the $50,000 ever at risk** | **$27,896** |
| Breakeven month (first EBITDA-positive) | 4 |
| Unpaid principal-months | **0** — everyone is paid from month 1 |
| Total repayable to the Founder | **$53,000** = $50,000 + ~$3,000 build spend |
| **Month the Founder is repaid** (lump sum, cash ≥ loan + 3-month reserve) | **5** |
| Contingent second tranche the Founder can inject if needed | **$50,000** |
| **Total capital available** | **$100,000** |

**Updated 2026-08-10 (second pass):** equipment, partner expenses and conferences are now charged
(`Assumptions!B151–B158`) — **$3,000 per person on hire**, **$500 per principal per month**, and
**2 / 4 / 6 conference events a year at $5,000**, the last starting only after the first EBITDA-positive
month so it cannot deepen the trough. Together ~**$28,000 in Year 1**. They cost Year-1 EBITDA about
$34k in every case and, decisively, **they push the Conservative case through the injection.**

**The loan is junior, not senior.** the Founder is repaid out of cash remaining *after* member distributions — cumulative
cash in this workbook is already net of them, so the model was computing it this way before the terms said so
(the Founder, 2026-08-10). The repayment carries no priority over the 10%-of-MRR distribution.

**The first $50,000 no longer covers every case.** Before equipment, partner expenses and conferences were
charged, all three cases finished inside the injection. They no longer do:

| | Conservative | Target | Aggressive |
|---|---|---|---|
| Trough (lowest cumulative cash) | **−$11,155 (m5)** | $1,575 (m3) | $4,819 (m3) |
| Of the first $50,000, consumed | **all of it, +$11,155** | $48,425 — 97% | $45,181 — 90% |
| **Cash needed beyond the injection** | **$11,155** | $0 | $0 |
| Headroom against the full $100,000 | $38,845 | $51,575 | $54,819 |
| Breakeven month | 6 | 4 | 4 |
| *(before these costs, for comparison)* | *$11,100 · 78%* | *$22,104 · 56%* | *$24,484 · 51%* |

> **The second tranche is now load-bearing, not a cushion.** The Conservative case goes $11,155 below zero in
> month 5, so "the Founder's $50,000 covers it" is false for the downside case and the further $50,000 is what makes the
> plan solvent. Two of three cases still fit, but only barely — Target now spends **97%** of the injection and
> Aggressive **90%**, leaving $1,575 and $4,819 of headroom respectively. Read "it fits" as "it fits with almost
> nothing to spare." The margin did not narrow because the market moved; it narrowed because we started charging
> costs the model had been ignoring — the margin did not narrow because the market moved, it narrowed because we started charging costs the
> model had been ignoring. That is the right direction of travel and it should be reported as a correction, not
> as bad news.
>
> Note also what is still excluded: legal, CPA, insurance, payment processing and taxes. The real breach is
> larger than $11,155, and the first case to hit it is the one the model calls Conservative — which, per §7 above,
> is itself no longer a floor.

**What the change cost, stated plainly.** Paying three principals from month 1 removes ~$12,500/mo of runway
early. Year-1 EBITDA falls in every case — Conservative $236k → **$161k**, Target $523k → **$460k**, Aggressive
$735k → **$685k** — and breakeven slips a month or two. Year 3 is unchanged, because the salaries were already on
by then. That is the price of the decision, and it is a real one.

**Still unreconciled:** the ~$3,000 of pre-formation build spend inside the repayable balance is the Founder's estimate
(revised up from $1,700 on 2026-08-10), not a receipted figure. June cash out is $405.73 confirmed, subscriptions
run ~$614/mo since, and the Anthropic top-ups are still logged TBD in `finance/expenses.md`. **Confirm against
receipts before the loan is papered** — this is the one number in the block that a lawyer will ask for evidence of.

If a principal needs income from month 1, set their MRR trigger to 0 on the Assumptions sheet and re-read — the
model is built for exactly that edit.

### Unit economics (per client)

| Metric | Early client | Mature client |
|---|---|---|
| Blended retainer / mo | $3,100 | $4,498 |
| COGS + delivery haircut / mo | $548 | $660 |
| Gross profit / mo | $2,552 | $3,838 |
| Gross margin | 82% | 85% |
| Net upfront cash (implementation − audit credit) | $850 | $1,735 |
| Audits required to land one client | 2.2 | 2.2 |
| Client life implied by churn | ~61 months | ~61 months |
| LTV over the capped 36-month horizon | $92.7k | $139.9k |
| LTV uncapped, for reference only | $156.4k | $235.7k |
| CAC | **$1,500 — no data** | **$1,500 — no data** |
| Payback period | <1 month | 0 months |

**Read this table with the CAC line covered up.** Every other number on it derives from priced bands and stated
assumptions. CAC is a number nobody has ever observed, and it is the denominator of the LTV:CAC and payback rows.
The honest statement is: *gross margin per client is structurally very high, because the client's entire delivery
cost is model spend. The cost of putting a client on the books is unknown.*

---

## 8 · What would make this wrong

The three assumptions the whole model hangs on, in order:

1. **Audit volume.** Every dollar downstream starts as an audit, and yourco has delivered **zero** of them. Zero cold
   emails have ever been sent despite $291/mo of sending infrastructure; all 25 companies in the CRM were sourced
   personally by the Founder; there were four external interactions in 61 days. **If the ramp starts at 0 instead of 2/month,
   nothing else in this model matters.**
2. **Audit → client conversion.** 45% in the Base case is invented. Nobody has ever been asked to buy — 22 deals in
   the CRM, 19 stuck at "relationship", 0 signed, 0 closed. Dropping it to 20% takes Base Y3 ARR from $4.69M to
   **$2.08M** (verified by editing the cell).
3. **Retainer realism.** The model blends off list prices that were never ratified, while the one live proposal
   (Sample Client) is $1,000/mo — one third of the Core floor. Repricing the Core floor to $1,000 takes Base Y1 ARR
   from $623k to **$469k** and Y3 from $4.69M to **$4.22M** (verified by editing the cell).

Also unproven, in roughly descending order of how much they move the answer: **churn** (nothing has ever churned) ·
**COGS per client** (never measured) · **clients per delivery head** (no engagement has ever run) ·
**CAC** (no data of any kind) · **every salary** (no hire has ever been made).

---

## 9 · Deliberate conservatisms

- The audit credit is applied to **every** converting client, including the 3 founders' audits that were never billed.
  Costs the model ~$3,000 across 36 months; keeps the logic simple and one-directional.
- Fixed subscriptions stay at the full **$614.22/mo** even though `runway.md`'s triage plan takes them to ~$362/mo.
- An **8%-of-revenue delivery haircut** sits on top of the per-client infra cost, so gross margin lands near the
  plan's stated 80–85% instead of the ~93% the raw arithmetic gives.
- **LTV is capped at 36 months** rather than run out to the ~61-month life the churn assumption implies.
- **CAC is charged to opex** on every new client as well as being used on the Unit Economics sheet.

## 10 · Known optimism — things the model does *not* charge

- **Cash is modelled as accrual.** Revenue lands in the month it is earned; no collection lag, no deposits, no
  payment-processing fees (there is no Stripe rail yet — all five Stripe items are unchecked).
- **No legal or counsel fees.** Counsel gate #1 — the client agreement any client would sign — is *not started*
  (`processes/counsel-gates.md`). It is a real, imminent, unpriced cost.
- **No CPA / bookkeeping, no business insurance premium** (represented in §13 of the plan but unbound), **no taxes,
  no equipment, no marketing spend beyond per-client CAC.**
- **No principal labour before the draw triggers.**

Add these before this workbook is used for anything other than a conversation.

---

## 11 · What changed vs the previous model

The prior workbook (built 2026-06-13, extended by Charles 2026-08-05) is superseded. Its problems, from
`finance/model-review_charles_2026-08-05.md`, and what the rebuild does about each:

| Prior problem | Now |
|---|---|
| Annual-only, hardcoded, no driver behind the $2,500 blended retainer | Monthly 36-month engine; the blend is derived from tier bands × mix × band placement |
| $90,000 hardcoded Y1 opex with no bridge to the books | Opex built from the real $614.22 subscription line + trigger-fired payroll + commissions + CAC |
| No cash cell, no runway, no breakeven | Cash & Runway sheet: $0 start, monthly cash position, max drawdown, breakeven, payback month, and the unpaid-principal-time reading |
| Retention asserted at n=0 and *improving* annually with no mechanism | Churn is a flat scenario driver, labelled n=0, and moved by the scenario switch |
| 26 Y1 clients with no capacity logic | Capacity-driven operator hiring plus a capacity check table on the Headcount sheet |
| Model computed 92–94% GM against a plan claiming ~80% | Explicit 8% delivery haircut reconciles them at ~82–86% |
| Predated OS-tier pricing, the partner admission, the Max subscription | All present; the partner is a modelled principal with his own draw trigger |

---

## 12 · Verification

Formulas were evaluated with an independent Excel calculation engine (`formulas` 1.3.4) — LibreOffice is not
installed on this Mac, so the house recalc step was replaced with that. Result: **6,902 cells resolved, zero error
cells** (no `#REF!`, `#DIV/0!`, `#VALUE!`, `#NAME?`, `#N/A`, `#NUM!`, `#NULL!`).

A structural scan confirms **no economic literal exists anywhere outside the Assumptions sheet** — the only bare
numbers on the other seven sheets are month indices 0–36.

Three single-cell edits were made and the whole workbook re-evaluated, confirming it behaves as a planning tool and
not a static projection:

| Edit | Effect |
|---|---|
| Scenario selector 2 → 1 (Conservative) | Month-36 MRR $390k → $121k; people 12 → 6; total investment $97k → $175k |
| Base conversion 45% → 20% | Y1 ARR $623k → $277k; Y3 ARR $4.69M → $2.08M |
| Core retainer floor $3,000 → $1,000 | Y1 ARR $623k → $469k; Y3 ARR $4.69M → $4.22M |

*Not committed — the main session commits.*
