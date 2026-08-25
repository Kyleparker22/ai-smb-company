# Cash structure: the Founder's $50k as a repayable founder loan, principals paid from day 1

## Decision

the Founder injects **$50,000 into the company on day one, alone**; **all three principals draw their $50,000 salary from month 1** rather than on a $25,000-MRR trigger; and the Founder's injection plus the pre-formation build spend he has already funded (**~$3,000, estimate pending receipts**) is a **repayable founder loan of $53,000**, returned as a lump sum in the first month cumulative cash covers it plus a three-month operating reserve. The loan is **junior to member distributions** — distributions are taken first and the Founder is repaid from what remains. **the Founder has declared a further $50,000 available** if the company needs it, taking total capital available to $100,000.

This entry also logs the **same-day model recalibration** that landed with no decision file: one hire type (the Advisor at $10,000/month fully loaded, hired on client load), principals' delivery capacity gliding to zero by month 24, onboarding charged in dollars (the 30-hours-per-client figure is a **benchmark wired into no calculation**, `Assumptions!B131` — it is what the Actuals tab measures against, not a model input), and the four removed specialist roles plus the MRR-triggered first salesperson deleted outright.

## Context

Three things converged on 2026-08-10, the day before the Business Plan / Financial Model / CRM lock with Partner B.

The model was rebuilt four times that day and the business plan realigned to it (v1.2), but nothing was written to `decisions/` — the changes roughly doubled the Target case (Year-3 recognized revenue $4.4M → $8.68M) with no record of why. `finance/model-assumptions.md` still carried the pre-change table and understated the model by about 2x.

Separately, the Cash & Runway sheet was found to sum unpaid principal-months over **two** principals, never reading Mike's salary switch, though Assumptions, the payroll line, the profit allocation and the Principal Earnings tab all carried three. It also split peak cash "50/50" at a 50/35/15 company. Both were corrected the same day.

Correcting it exposed the deeper problem: the whole "peak cash need is tiny" story was an artifact of nobody being paid. The model showed a $1,528 drawdown only because all three principals worked unpaid until MRR cleared $25,000 — the real cost sat in 15 unpaid principal-months worth $62,500, in a block most readers skip. the Founder chose to stop modelling a company that runs on unpaid founders.

## Options considered

- **Keep the MRR trigger, fix only the two-vs-three bug.** Cheapest, and leaves the headline "$1,528 to get to profitable" intact — but that headline is only true because three people work for nothing, and a partner who finds that later re-prices everything before it.
- **Split the $50k 50/35/15 across the three members.** Puts real cash at risk for Partner B and Mike from day one and matches the equity split. Rejected: it changes what Partner B is being asked for at the exact moment he is deciding whether to join, and the Founder is the one with the money in already.
- **Treat the injection as permanent capital, not a loan.** Simpler to paper. Rejected — it silently converts the Founder's cash into everyone's equity.
- **Give the loan priority over distributions.** Considered and **rejected the same day**: it would let the Founder's recovery stall the other two members' first distributions, which is a bad way to start a partnership over a sum this size. the Founder takes the timing risk instead.
- **Chosen: the Founder funds it alone as a junior repayable loan, everyone is paid from month 1, with a second $50,000 declared available.**

## Why

Paying the principals from day one makes the model describe the company that will actually exist. A plan whose viability depends on its founders not being paid is not a plan, it is a subsidy with a spreadsheet around it — and it hides the true funding requirement in a block labelled "the other half of the investment."

Funding it alone keeps the ask to Partner B and Mike honest: their contribution is time, and the cash question has one answer — the Founder's, already committed. Making it a **loan** rather than capital means the Founder recovers what he put in before anyone takes profit, without converting his cash into a larger share of a company whose split is already agreed.

Making the loan **junior** rather than senior costs the Founder little and buys a lot: on these numbers he is repaid in month 5 either way, and a founder loan that can hold up his partners' first distribution is a needless source of friction in the first year of a three-member company. the Founder carries the timing risk because the Founder is the one who chose to put the money in.

The cost is real and stated: Year-1 EBITDA falls in every case, breakeven slips to month 4 (5 Conservative, 3 Aggressive), and the Founder is repaid in month 5 in the Target case.

**Amended later the same day — the $50,000 does not cover every case.** When this decision was first written, all three cases finished inside the injection and the second tranche read as a cushion. Three costs the model had never charged were then added (equipment at $3,000 per person on hire, partner expenses at $500 per principal per month, and conferences at 2/4/6 events a year — about $28,000 in Year 1). With those charged, **the Conservative case runs $3,900 below zero in month 4**, and Target consumes 83% of the injection rather than 56%. Year-1 EBITDA lands at $129k Conservative / $427k Target / $645k Aggressive.

**So the second tranche is load-bearing, not a comfort.** The honest statement is that two of three cases fit inside $50,000, the third needs about $4,000 more, and the declared further $50,000 is what makes the downside case solvent. Nothing about the business changed to cause that — we simply started charging costs the model had been ignoring, which is a correction rather than a deterioration. What remains excluded (legal, CPA, insurance, payment processing, taxes) means the real breach is larger than $3,900, and the case that hits it first is the one labelled Conservative — which, the same day, stopped being a floor.

## Reversibility

Highly reversible on the mechanics, and deliberately so: the salary trigger is one cell per principal on the Assumptions sheet (E68/E69/E70). Setting it back to $25,000 immediately re-prices the trade and brings the unpaid-time block back to life — the block was kept rather than deleted for exactly this reason.

The loan is not reversible by editing a cell: once the Founder's money is in, it is in. It is also **not papered** — a Reserved Matter under the OA, owed by nobody until the agreement is signed (counsel gate #14, currently 🔴 after the three-member restatement).

The ~$3,000 of pre-formation build spend inside the repayable balance is the Founder's estimate (revised up from $1,700 the same day), not a receipted figure — June cash out is $405.73 confirmed, subscriptions run ~$614/mo since, and the Anthropic top-ups are still logged TBD in `finance/expenses.md`. **Confirm against receipts before the loan is papered**, or the Founder is repaid a number nobody can defend.

## Trip-wire

- **Review:** 2026-11-10
- **Overturn if:** the company burns through the $50,000 without reaching breakeven — the Conservative case already breaches it by $3,900, so this is no longer hypothetical for the downside. Also overturn if the principals cannot in fact be paid from month 1 because no revenue exists to pay them from, which on current evidence (zero audits delivered, zero clients signed) is the live risk rather than a hypothetical one.
- **Check:** `signedClients >= 1`
- **Check covers:** only the precondition that any revenue exists at all. The real test — cash consumed against the $50,000 versus the modelled trough — is not instrumented, because the company has no bank feed and `finance/runway.md` is updated by hand at monthly close. A firing check means "revenue has started, now compare actuals to the trough", not "this decision is safe."
