# Business plan review — Melanie, 2026-08-10 (second pass)

**Scope:** `06_business-plan.md` v1.2, re-checked against `finance/yourco-financial-model.xlsx` as it stands after the Founder's cash-structure decision (`decisions/2026-08-10_cash-structure-and-model-recalibration.md`), the model rebuild, and the Excel recalculation. Read alongside `finance/model-assumptions.md`, `dashboard/finance_model.json` and `finance/expenses.md`. This supersedes nothing in my 08-10 review except where it says so. My standing duty is the prose; Section 8's figures are Charles's. I verified them anyway, because a prose judgment about numbers is worth nothing if the numbers weren't checked.

**Verdict: the cash rewrite is honest about its own cost and stale by one number — but "no case needs more than the $50,000" is a smaller claim than it sounds, because the model deleted its own floor case the same day.** Thirty-one assertions re-verified against the workbook; one hard mismatch (the principals' three-year totals, left behind when the salary sentence above them was rewritten) and one dead client count. The Capital prose is *better* than what it replaced — it leads with the 78% rather than burying it. What it does not say is that all three "cases" now share a single untested revenue-timing assumption, and that the worst of the three is the case that was the middle one this morning.

I propose six changes. the Founder approves; I have made none of them.

---

## 1 · §8 states the principals' earnings from the model as it was before lunch — URGENT

Line 201: *"In the Target case the three-year totals are the Founder $1.49M, Partner B $1.30M, Mike $1.03M."*

The workbook, `Principal Earnings` row 17, now reads:

| Target, 3-yr cash earnings | Plan says | Model says |
|---|---|---|
| the Founder | $1.49M | **$1,515,671 — $1.52M** |
| Partner B | $1.30M | **$1,316,488 — $1.32M** |
| Mike | $1.03M | **$1,050,911 — $1.05M** |

`dashboard/finance_model.json` (`principalEarnings3yr.Target`) agrees with the workbook, so HQ and the plan now serve different numbers for the same line.

How it happened is worth more than the correction. Commit `207b0d0` rewrote the first half of that sentence — *"Salary of $50k each once MRR clears $25k"* became *"Salary of $50k each **from month 1** — no MRR trigger"* — and left the second half untouched. Paying three people five months earlier necessarily raises their three-year total; the sentence that caused the change sits eleven words in front of the numbers it invalidated.

This is the highest-consequence stale figure in the document. Everything else in §8 is a company-level projection a reader discounts on instinct. This is the line a prospective member reads about himself, and it is the line his adviser will re-derive.

**Propose:** correct to $1.52M / $1.32M / $1.05M. And add the machine backstop — `runtime/consistency-check.py` already verifies HQ's mirror against the workbook (invariant added 2026-08-10) but checks *nothing* in `06_business-plan.md` §8 against `dashboard/finance_model.json`, which is why a two-surface guard let a three-surface fact drift. The comparison is buildable today: every figure in the §8 table plus this line exists in the JSON.

## 2 · "No case needs more than the $50,000" is the new "$1,528"

This morning I said the plan led with a comforting cash number and gestured at the real one. That specific problem is gone. The replacement is honest in a way I want to name before I criticise it: §8 and §11 both lead the Conservative 78%, both label the second tranche *availability, not modelled cash*, and both say the excluded costs make the hole larger. That is the house standard being met.

Three things the prose still does not say, all of which a bank or a partner's counsel will reach on their own.

**(a) The model no longer contains a downside conversion case.** The Conservative column now runs 45% audit→client conversion, 2 audits in the first selling month, and 18% annual churn. Those are, cell for cell, the *Base* case of this morning. The workbook says so on its own face — `Assumptions!H50`: *"⚠ The model no longer contains a case below 45% conversion. No prospect has ever been asked to buy — there is still no close rate."* So "all three cases" is not three tests of the cash position; it is one revenue thesis run at three slopes, with the pessimistic slope removed. §9's recalibration note makes exactly this admission about the *client targets* — *"Nothing about the business changed to justify that; the targets were raised."* The Capital prose needs the same sentence and does not have it.

**(b) There is no case in which revenue is late.** All three cases sell the first audit in month 2 and bank the first dollar in month 3 (`Assumptions!B54`; `Scenario Engines` rows 12/57/102). The company has delivered zero audits in 61 days and sent zero cold emails. Strip the revenue and the arithmetic is short: opex is **$13,264.22/month** in months 1–2 (`Cash & Runway!E27–E28` — three principal draws plus the $614.22 subscription line plus tooling), so with no revenue at all the injection runs out **during month 4**. That is the number the "$50,000 covers every case" sentence is really making a claim about, and it is a claim about timing, not about scenarios.

**(c) Neither $50,000 is money the company has.** `Assumptions!B146` — cash on hand today — is **$0**, and `finance/runway.md` reads 0.0 months. The injection is a modelled opening position at 2026-12-31, unpapered, and a Reserved Matter under an operating agreement nobody has signed (gate #14, 🔴). The second $50,000 is a declaration by one member, undrawn, in no projection, and withdrawable at will. "Total capital available: $100,000" is true as written and reads, to someone skimming, like a balance sheet.

**Propose:** keep every number. Add two sentences to §11 — one saying that the model's floor case was itself raised on 2026-08-10 and no case tests late revenue, one saying the $100,000 is committed-and-declared rather than held. The honest framing is that the cash structure is sound *against the plan*, and that the plan's first month of revenue has never happened.

## 3 · §10 has no liquidity failure mode, and today's decision created one

Eight ways the company could fail are listed. None of them is "the company runs out of money."

Until this morning that was defensible: peak drawdown was $1,528 and there was nothing to fail at. Today the company commits **$150,000/year of principal salary from month 1** against $0 in the bank, funded by an unpapered loan from one member, while §10 item 2 already concedes that the demand thesis is unproven and item 1 concedes the launch gate has no date. Those two risks now have a cash consequence they did not have this morning, and §10 does not connect them.

The decision file itself states the live version of this — *"the principals cannot in fact be paid from month 1 because no revenue exists to pay them from, which on current evidence… is the live risk rather than a hypothetical one."* That sentence belongs in the plan's own failure list, not only in the decision that created it.

**Propose:** a new §10 item — *the company pays three salaries before it earns a dollar* — carrying the month-4 exhaustion arithmetic from item 2(b), the $0-cash-today fact, and the mitigation that actually exists (the second tranche, and the salary trigger being one cell per principal, which the decision deliberately kept reversible).

## 4 · §7 describes the partnership without saying who paid for it

§8 now states plainly that the Founder funds the company alone and that Partner B and Mike contribute no cash. §7 — the section titled *People and the partnership*, the one a prospective member actually reads — does not mention it. It covers the split, the vesting, the three open governance decisions and the unrecorded contribution, and is silent on the fact that one of the three members is putting $53,000 at risk and the other two are putting in none.

This is my item 2 from this morning, and it survives its own premise being deleted. I argued then that the asymmetry was *unpaid time contributed equally against cash contributed 50/35/15*. Both halves of that are now false — there is no unpaid time, and there is no 50/35/15 cash split. The asymmetry did not soften; it went to a corner: **100% of the cash from one member, 50% of the company.** That is a defensible arrangement and probably the right one — it is exactly why the injection is a loan and not capital, and the decision file's reasoning ("their contribution is time, and the cash question has one answer") is good reasoning. §7 should carry it, so the partner learns it from us.

**Propose:** two sentences in §7 — the Founder funds the company alone, as a repayable loan junior to distributions; the partners' contribution is time and lane, and D12 is the open question about what Mike's is.

## 5 · §10's ranking is still stale, and item 3 carries a number from a dead model

My item 4 this morning was that §10's ordering — #1 the launch gate, #4 the partner admission — was set when the partnership was two people and settled. It was not addressed, and nothing has since made it less stale: gate #14 is still 🔴, D10/D11/D12 are still open, Mike's contribution is still unrecorded. I stand by it, with one revision — I now think the ordering is the *second* problem in §10 and the missing liquidity risk (item 3 above) is the first.

Separately, §10 item 3 reads: *"…24 clients by end of Year 1 requires the autonomy bet proven by roughly client five."* **24 matches no case in the model.** Year-1 actives are 25 (Conservative), 50 (Target), 75 (Aggressive). It is a survivor of the pre-realignment plan, sitting inside a paragraph about the delivery promise breaking — which is the risk the number is supposed to size.

**Propose:** replace 24 with 50 (Target) and re-rank per item 3.

## 6 · §8 credits the model with charging onboarding hours it does not charge

§8's assumptions line: *"onboarding $150 and 30 principal-hours per new client."*

The dollars are live. The hours are not. `Assumptions!H131`: *"⚠ NOT WIRED INTO ANY CALCULATION as of 2026-08-10. It was consumed by a capacity draw that was removed when the principals' 50 became a net-of-onboarding figure… changing it moves no output."* The 30 hours is a benchmark held for the Actuals tab to be compared against — a good thing to keep, and not a cost the model charges.

The decision file has the same error, one line up: *"onboarding charged in both dollars and hours."*

This matters because it is load-bearing for the item §8 itself flags as still open — Polo gap **(c)**, the Year-1 capacity sanity check. If a reader believes 30 hours per onboarding is priced into the capacity number, the claim that three principals carry 50 clients looks tested. It is not; the 50 is asserted net of onboarding (`Assumptions!H73`) and the hours are decoration.

**Propose:** state that onboarding is charged in dollars only, and that the 30 hours is a benchmark for the Actuals tab. Sweep the same correction into the decision entry.

## 7 · Where this morning's review was wrong

- **Item 1 (Capital understates investment 40x) — dead, and superseded by a better fix than mine.** I proposed leading with *$64,028 total investment = $1,528 cash + $62,500 unpaid time*. the Founder deleted the unpaid time instead of documenting it, which is the correct answer to the problem I found and not the one I recommended. My proposal would have produced an accurate description of a company nobody wanted to run.
- **Item 2 (contribution asymmetry) — the arithmetic I quoted no longer exists.** The $764 / $535 / $229 cash split and the fifteen unpaid principal-months are both gone. The finding survives in a different form (item 4 above); the numbers I used to make it should not be quoted from that review again.
- **Item 3 (the Partner B lock-in schedule missing from Year-0) — not addressed, still stands.** §9's Year-0 block still omits 8/11–8/26. That block starts tomorrow.
- **What I missed this morning:** I read §10 for ordering and did not notice it has no liquidity risk at all, or that item 3 carries a client count from a superseded model. Both were there before today's decision. Checking a ranking is not the same as checking a list for a hole.

## 8 · Verified clean

Re-checked against the recalculated workbook and correct as written — **§8's table in full**: clients 25/60/95 · 50/118/190 · 75/177/285 (model: 25.0/60.0/95.1 · 50.0/117.9/189.6 · 75.0/176.9/285.0); ARR end-Y3 $5.13M / $10.23M / $15.38M; recognized revenue Y1 $530k / $1.07M / $1.57M and Y3 $4.42M / $8.68M / $12.94M; EBITDA Y3 $2.08M / $4.30M / $6.52M; NOI 30/46/47 · 43/48/50 · 44/48/50; gross margin ~86% (85.5–85.6%); humans 3/8 · 3/13 · 5/18; cash needed beyond the injection $0 in all three; **the trough figures, each recomputed from `Scenario Engines` rather than read off a summary** — $38,900 consumed at month 4 (Conservative), $27,896 at month 3 (Target), $25,516 at month 2 (Aggressive); breakeven months 5 / 4 / 3.

**The founder-loan block**: $53,000 total repayable, month-5 lump-sum repayment, junior to distributions, second tranche $50,000 undrawn, $100,000 available, $61,100 headroom at the Conservative trough, and the ~$3,000 flagged as the Founder's estimate pending receipts — all match `Cash & Runway` rows 64–78 and `finance/expenses.md`'s new open block.

**Assumptions cited in §8**: blended retainer $3,100 → $4,498; blended audit fee $1,100; COGS $300/client/mo; 8% delivery haircut; CAC $1,500; onboarding $150; churn 18/12/8. **§7 and §9**: Advisor at $10,000/month fully loaded, 20 clients each, first Advisor at month 13 (so "no hire before client 51" holds exactly); principals' capacity 50, flat to month 12, zero at month 24; Year 2 = 3 + 6 Advisors = 9 people; Year 3 = 3 + 10 = 13; revenue per human Y3 $8,675,551 ÷ 13 = **$667k**; §9's Year-3 line ($10.2M ARR, $8.7M revenue, $4.3M EBITDA, 13 people). **§8's compensation mechanics**: commission 5% each at a $35k MRR trigger, 10%-of-MRR distribution at $50k, February true-up for the prior calendar year.

Two precision notes rather than errors: §8's table row reads *active clients achieved*, while the sentence above it says the cases are *"defined by year-end client targets the Founder set"* — for Target Year 2 the stated target is **115** (`Assumptions!D121`) and the achieved figure is 118. And §8's line that the Sep–Dec 2026 gap assumes no spend is still true; the workbook now sizes it (~$2,457, `Monthly P&L` row 4) and the plan could use the number.

---

## Hand-off to Charles — not mine to fix

Three source surfaces still describe the pre-decision model, and §8 is mirrored from them:

- `finance/model-assumptions.md` **§3** lists conversion 30/45/60 and churn 25/18/12 (model: 45/60/75 and 18/12/8) and **§5** is the entire old People table — a 50/50 partner, Delivery Lead, Client Success, Platform Engineer, $25k draw triggers, 12 clients per delivery head. §7 of the same file is correct and current, so the document contradicts itself.
- The workbook's own prose: `Cash & Runway!A3` still says *"Starting from $0 cash… Negative cumulative cash = money the principals have put in"* against `B5 = $50,000`; `Dashboard!A2` and `Monthly P&L` row 4 still say *"$0 cash"* at month 0; `Headcount Plan` I6–I8 still read *"fires on the $25k MRR trigger"* against `E68–E70 = 0`.
- `Assumptions!H68–H70` carry the same *"starting when MRR clears $25,000"* note on the three cells that now trigger at 0.

None of it changes a computed value. All of it is what a reader checking our arithmetic reads first.

---

## What I did not do

I have not edited `06_business-plan.md`, the workbook, `dashboard/finance_model.json`, or `finance/model-assumptions.md`. Item 1 is the only correction I would call urgent — it is a specific number about a specific person, wrong by one commit, in the document he is being walked through starting tomorrow. Items 2 and 3 are the judgment calls and are properly the Founder's: the Capital section is materially more honest than it was this morning, and my claim is only that it has not yet noticed the model's floor moved underneath it. Items 4–6 are prose and precision. I did not verify the ~$3,000 build spend — that reconciliation is Charles's open item and no receipt in this workspace supports the figure.
