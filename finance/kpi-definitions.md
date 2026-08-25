# The nine KPIs — defined now, refusing until they mean something

**Owner: Charles · Written 2026-08-25 · Machine copy: `dashboard/kpis.py` · Inputs: `finance/actuals.json`**

the Founder listed nine KPIs to track. **Seven of the nine are undefined at n=0** — six of them need
customers, and burn multiple divides by net new ARR, which is zero.

The wrong response is to track the two that work and come back to the rest later. The right one is
to define all nine **now, with the exact precondition each is waiting on**, so that the day client #1
signs, the numbers compute themselves and nobody re-derives a formula under pressure — or worse,
reaches for an industry benchmark and quietly presents it as a fact about yourco.

This page owns the **reasoning**: why this formula, why that floor, and what each number will lie
about if you let it. `dashboard/kpis.py` owns the **arithmetic**. The nine keys are checked against
each other by `runtime/consistency-check.py`, so this page cannot drift from what HQ shows.

---

## The rules that apply to all nine

1. **A KPI is `computed` or `refused`.** There is no third state — no "TBD", no placeholder, no
   benchmark standing in.
2. **Every refusal names what is missing and when it clears.** A refusal without a precondition is
   an empty cell wearing a sentence.
3. **Undefined is not infinite and it is not zero.** Burn multiple with no new ARR is undefined.
   Zero churn at zero customers is not a good churn rate. Each is said in those words.
4. **Small-n percentages are refused.** Below **5 customers** no retention or churn *rate* is
   reported — a percentage off a handful is noise with a percent sign on it. (Same floor and same
   reasoning as the referral-conversion read in `dashboard/wbr.py`.)
5. **A number can compute and still be wrong to lean on.** Caveats travel *with* the value, in the
   same payload, not in a footnote on another page.

---

## What computes today — and what is wrong with both of them

| KPI | Value | The caveat that matters more than the value |
|---|---|---|
| **EBITDA** (monthly run-rate) | revenue − opex | Fixed burn is the **last confirmed** figure, not a current one — five renewals in the Aug 8–10 window produced no receipt and no failure notice, and the figure was deliberately not restated on silence. It also **prices no founder compensation**: a one-person company's EBITDA flatters itself by exactly one salary. |
| **Operating cash flow** (last closed month) | cash in − cash out | **Failed charges are excluded** — they never left the account, which makes the number true and optimistic at once, because a failed charge is a bill still owed. And with $0 cash and the Founder funding charges personally, "operating cash flow" describes a founder's card, not a treasury. |

Two of nine. That is the honest state of financial measurement at yourco, and it is a better place to
start than nine confident numbers built on three assumptions each.

---

## What is waiting, and on what

| KPI | What it answers | Clears when | The thing it will lie about |
|---|---|---|---|
| **Net revenue retention** | Does money from customers we already have grow on its own? | 5+ customers live **12 full months**. Earliest date = 12 months after the first go-live, which has not happened — so it has no earliest date yet. | Nothing, once it exists. This is the metric the land-and-expand thesis lives or dies on, and it is the last one you earn the right to state. Expect to quote it in 2028. |
| **Customer retention rate** | Do customers stay? | 5+ customers, 6+ months. | Below the floor it reports one customer's decision as a percentage. |
| **Churn rate** | How fast do we lose what we won? | Same gate — churn and retention are two readings of one fact. | The **first** churn will read as 100% or 50%. Report the raw count for the first year and the percentage after. |
| **Customer acquisition cost** | What does it cost to win one? | One acquisition, plus a real sales-and-marketing line. (`expenses.md` has a `marketing` category; that is not the same thing.) | **It will be a floor, not a cost** — the dominant input is the Founder's unpaid time, which no ledger prices. Say "floor" every time it is quoted. It will also be **bimodal**: a connector-referred client and a cold-outbound client cost nothing alike, and the blend hides both. |
| **Customer lifetime value** | What is one customer worth across the relationship? | Churn **and** gross margin. Margin needs per-client cost from `clients/*/cost.md`, which is exactly why HQ's margin metric is honest-null today. | The most-quoted and least-defensible number in SaaS, because both inputs are usually guessed. yourco absorbs model spend, so margin here must be **net of token cost per client** or the number is a slide, not a fact. |
| **LTV to CAC ratio** | Do we make more than it cost? | Both inputs first — it is the last of the nine. | A ratio of two estimates is not an estimate. It is two errors multiplied. |
| **Burn multiple** | Dollars burned per dollar of new revenue? | **The first dollar of new ARR** — nothing else. This one clears the moment a deal goes live. | It will be brutal at first by construction: burn ÷ a small first ARR is a large number. **Judge the trend, not the level**, for the first two or three quarters. |

**Six of the seven clear on client #1.** That is not a coincidence and it is not a complaint — it is
the same finding the north star reports (`dashboard/northstar.py`), arriving through the finance
door instead of the agent door.

---

## Who owns each number

Finance KPIs are **Charles's** to report. Two have a second owner because the input is not financial:

- **CAC** — Charles owns the cost; **Reilly and Bird** own the attribution, and CAC without
  attribution is a total divided by a guess.
- **Retention / churn** — **Kortney** owns health (the leading half); Charles reports the lagging half.
- **NRR** — **Bird** owns expansion, which is the half of NRR that makes it exceed 100%.

---

## How this stays true

- **At each monthly close**, Charles updates `finance/actuals.json` — the machine-readable copy of
  the figures `runway.md` has already confirmed. `runtime/consistency-check.py` fails if a figure in
  `actuals.json` no longer appears in `runway.md`, so the machine copy cannot quietly drift from the
  narrative one.
- **When client #1 signs**, set `customers.firstGoLive` in `actuals.json`. That single field starts
  the clock on four of the seven refusals.
- **Adding or removing a KPI** means editing `dashboard/kpis.py` *and* this page in the same commit —
  the key sets are compared by the consistency watchdog.

## What this deliberately does not do

It does not set targets. A target for a metric that has never been measured is a wish, and yourco
already has a place where wishes are recorded as such (`dashboard/goals.json`, the Founder's). Targets for
these nine get set after the first three months of real readings, not before.
