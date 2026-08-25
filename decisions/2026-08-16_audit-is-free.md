# 2026-08-16 — The Audit is free (no charge), until further notice

> the Founder: *"we will be doing the Audits for free. No $ charge. This may change once we are up and running for a while and can do that, but while just getting started it will be no charge."* the Founder's call, overriding the Polo-locked price of 2026-06-16.

## The call
**The Audit is $0 to every prospect.** Not discounted, not waived case-by-case, not "free for the first three" — free, universally, while yourco is getting started. Supersedes the `$1,000 Standard / $1,500 Pro` lock in `pricing/v0/audit.md` and retires the founders'-offer carve-out (first 3 warm-network audits at $0), which is now the general rule rather than an exception.

## What this actually costs — the non-obvious part
**For a prospect who proceeds, nothing changes.** The old mechanic credited the audit fee **100%** against the implementation, so a converting client always paid the same total. What yourco gives up is therefore narrower than "$1,000 per audit":

| | Old | New |
|---|---|---|
| Client who **proceeds** | $1,000 audit, credited in full → net identical | $0 audit → **net identical** |
| Client who **does not proceed** | yourco keeps $1,000 | yourco keeps $0 |
| Cash timing | $1,000 collected upfront, then credited | nothing collected until implementation |

So the real losses are **(a) revenue from non-converting audits**, **(b) upfront cash float**, and **(c) the qualification filter** — a price is the cheapest way to separate a buyer from a browser, and removing it means Bella's calendar fills with people who would never have paid. **(c) is the one to watch**, not (a).

## What the model says, recalculated (2026-08-16, Excel full recalc)

Not estimated — the fee cells were set to $0, the workbook was recalculated in Excel, and the result
diffed against the pre-edit baseline from git (1,748 cells moved). Two very different answers:

| | Before ($1,000/$1,500) | After ($0) | |
|---|---|---|---|
| Principal earnings, 3-yr total | $833,226 | $825,727 | **−$7,499 (−0.9%)** |
| Breakeven month | 5 | 6 | +1 month |
| **Peak cash need (max drawdown)** | **$3,900** | **$11,155** | **≈3× worse** |
| Lowest cumulative cash (the trough) | $8,604 | **$1,575** | −$7,029 |
| Of the $50k injection, consumed at the trough | $41,396 | **$48,425** | 83% → **97%** |

**Read it as: cheap on the P&L, expensive on cash.** The 0.9% earnings impact confirms the thesis above —
the fee was never really revenue, because it was always credited back. But the *timing* change is severe:
the trough now leaves **$1,575 of headroom against a $50,000 injection**, where it previously left $8,604.

**This is not a reason to reverse the decision; it is a reason to know the number.** Two consequences:
1. **The float, not the fee, is the real cost.** Anything that pulls cash earlier — a deposit at signing,
   a shorter implementation, faster collection — matters more now than the audit price ever did.
2. **Conservative was already breaching** the injection by $3,900 as of 2026-08-10 (`git log`). Base now
   sits at 3% headroom. Re-run the scenarios before treating $50k as sufficient.

## Why it's still right for now
- yourco has **zero completed audits and zero case studies**. A paid diagnostic asks a stranger to pay for a claim nobody has yet proven. Free removes the only objection that cannot be answered with evidence.
- It matches the strategy of record: warm intros first (`2026-08-05` GTM sequencing) and `2026-08-16_leak-first-wedge` — the leak number *is* the pitch, and it lands harder when getting it costs nothing.
- It is consistent with the give-first pattern that is the only thing yourco has evidence for (`learnings/strategy/2026-07-28_built-artifact-converts-not-ask`).

## Guardrails (so free does not become worthless)
1. **Free ≠ unscoped.** Same SOP, same report, same fixed one-week scope (`processes/audit-sop.md`). A free audit that becomes an open-ended consulting relationship is the failure mode.
2. **Say the value, not just the price.** Copy states what the Audit *is worth* and that it is free while getting started — never "free" alone, which prices the work at zero in the buyer's head permanently.
3. **The credit language retires.** "Your audit fee is credited toward implementation" is now meaningless and must come off every surface — it implies a fee.
4. **Capacity is the new filter.** With no price filtering demand, Bella's throughput is the constraint. If audits outrun capacity, the answer is a waitlist or a qualification step — **not** a quiet return to charging.

## Trip-wire
**Revisit when yourco has 3+ completed engagements with measured outcomes** — the same threshold as `2026-08-16_leak-first-wedge`. At that point there is evidence to sell against and the price can return. Until then, any surface quoting an audit price is out of date.

**Locks:** audit pricing · founders'-offer carve-out (retired into the general rule)
