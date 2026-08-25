#!/usr/bin/env python3
"""yourco — the nine KPIs, defined now, refusing until they mean something.

WHY THIS EXISTS. the Founder listed nine KPIs to track (2026-08-24): NRR, LTV, CAC, LTV:CAC, churn, burn
multiple, EBITDA, operating cash flow, customer retention. **Seven of the nine are undefined at
n=0** — six need customers, and burn multiple divides by net new ARR, which is zero. The wrong
response is to track two and forget the rest until someone asks. The right one is to define all nine
NOW, with the exact precondition each is waiting on, so that on the day client #1 signs the numbers
compute themselves and nobody re-derives a formula under pressure.

THE POSTURE, WHICH IS THE WHOLE POINT
- A KPI is `computed` or `refused`. There is no third state and there are no placeholders, no "TBD",
  no industry benchmark standing in for a fact about this company.
- A refusal always says **what is missing** and **when it clears** (`firstComputableWhen`). A KPI
  that refuses without naming its precondition is just an empty cell.
- **Undefined is not infinite and not zero.** Burn multiple with no new ARR is undefined; runway on
  zero burn is undefined; a churn rate off two customers is noise with a percent sign on it. Each is
  said in those words rather than rendered as a large number.
- **A number can be computed and still be wrong to lean on.** EBITDA and operating cash flow do
  compute today, and both carry caveats that are louder than the figures: fixed burn has been
  materially uncertain since 2026-08-17, and nothing in either number prices the founder's own time.
  Caveats travel with the value, not in a footnote somewhere else.

WHERE THE INPUTS COME FROM. `finance/actuals.json` (Charles, updated at each monthly close) and
`crm/data.json`. Nothing is parsed out of prose, and nothing is estimated: a missing input is null,
and null propagates into a refusal rather than into a zero.

Read-only. GET /api/kpis · CLI: python3 dashboard/kpis.py
"""
import os, sys, json, datetime

HERE = os.path.dirname(os.path.abspath(__file__))          # CODE
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
# Playground switch — data moves, code does not. See playground/_README.md.
ROOT = os.environ.get("YOURCO_DATA_ROOT") or REPO           # DATA

ACTUALS = os.path.join(ROOT, "finance", "actuals.json")
CRM = os.path.join(ROOT, "crm", "data.json")

# Small-n floors. A rate computed off a handful is noise with a percent sign on it — the same rule
# and the same number the referral-conversion read uses (dashboard/wbr.py MIN_ASKS).
MIN_COHORT = 5            # customers before any retention/churn percentage is reported
MIN_MONTHS_RETENTION = 6  # months a cohort must have been live before churn means anything
MIN_MONTHS_NRR = 12       # NRR is a year-over-year measure; anything shorter is a different metric


def _load(p):
    try:
        with open(p) as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def _months_since(iso):
    if not iso:
        return None
    try:
        d = datetime.date.fromisoformat(str(iso)[:10])
    except ValueError:
        return None
    t = datetime.date.today()
    return (t.year - d.year) * 12 + (t.month - d.month)


def _kpi(key, name, question, formula, owner, when, unit="", value=None, refusal=None,
         needs=None, caveats=None, inputs=None):
    """One KPI. `value is None` and `refusal` set is the only legal way to have no number."""
    return {
        "key": key, "name": name, "question": question, "formula": formula, "owner": owner,
        "unit": unit, "value": value,
        "state": "computed" if value is not None else "refused",
        "refusal": refusal, "needs": needs, "firstComputableWhen": when,
        "caveats": caveats or [], "inputs": inputs or [],
    }


def compute():
    a = _load(ACTUALS) or {}
    crm = _load(CRM) or {}
    cust = a.get("customers") or {}
    cash, burn, rev = a.get("cash") or {}, a.get("burn") or {}, a.get("revenue") or {}
    live = cust.get("live")
    first = cust.get("firstGoLive")
    months_live = _months_since(first)
    burn_note = burn.get("note")
    months = a.get("months") or []
    last_close = months[0] if months else None

    out = []

    # ---- 1. Net revenue retention -----------------------------------------------------------
    out.append(_kpi(
        "nrr", "Net revenue retention",
        "Does the money from customers we already have grow on its own?",
        "(starting MRR + expansion − contraction − churned MRR) ÷ starting MRR, for a cohort "
        "measured 12 months apart",
        "Charles (with Bird on expansion)",
        f"{MIN_COHORT}+ customers live for {MIN_MONTHS_NRR} full months. Earliest possible date is "
        f"{MIN_MONTHS_NRR} months after the first go-live — which has not happened, so this metric "
        f"has no earliest date yet.",
        unit="%",
        refusal=(f"{live if live is not None else 'unknown'} live customers, none for "
                 f"{MIN_MONTHS_NRR} months. NRR compares a cohort with its own past; there is no past."),
        needs="a first go-live date, then twelve months",
        inputs=["actuals.customers.live", "actuals.customers.firstGoLive", "per-customer MRR history"],
        caveats=["NRR is the metric yourco's land-and-expand thesis lives or dies on, and it is the "
                 "one that takes longest to earn the right to state. Expect to quote it in 2028."],
    ))

    # ---- 2. Customer retention rate ---------------------------------------------------------
    ok_cohort = isinstance(live, int) and live >= MIN_COHORT and (months_live or 0) >= MIN_MONTHS_RETENTION
    out.append(_kpi(
        "retention", "Customer retention rate",
        "Do customers stay?",
        "customers at end of period ÷ customers at start of period (logo, not dollar)",
        "Kortney (health) → Charles (reports)",
        f"{MIN_COHORT}+ customers live {MIN_MONTHS_RETENTION}+ months.",
        unit="%",
        refusal=(None if ok_cohort else
                 f"{live if live is not None else 'unknown'} live customers. Below {MIN_COHORT} a "
                 f"retention rate is one customer's decision wearing a percentage."),
        needs=f"{MIN_COHORT} live customers with {MIN_MONTHS_RETENTION} months behind them",
        inputs=["actuals.customers.live", "actuals.customers.churned"],
    ))

    # ---- 3. Churn -----------------------------------------------------------------------------
    out.append(_kpi(
        "churn", "Churn rate",
        "How fast do we lose what we won?",
        "customers lost in period ÷ customers at start of period",
        "Kortney → Charles",
        f"Same gate as retention: {MIN_COHORT}+ customers, {MIN_MONTHS_RETENTION}+ months.",
        unit="%",
        refusal=(None if ok_cohort else
                 f"{live if live is not None else 'unknown'} live customers, and none has yet had the "
                 f"chance to leave. Zero churn at zero customers is not a good churn rate."),
        needs="the same cohort retention needs — they are two readings of one fact",
        inputs=["actuals.customers.churned"],
        caveats=["The first churn will be a 100% or 50% churn rate. Say the raw count for the first "
                 "year and the percentage after — a rate off a cohort this small misleads in both "
                 "directions."],
    ))

    # ---- 4. CAC --------------------------------------------------------------------------------
    sm = (a.get("salesAndMarketingSpend") or {}).get("monthly")
    acquired = sum((cust.get("acquired") or {}).values()) if isinstance(cust.get("acquired"), dict) else 0
    cac_val = round(sm / acquired, 2) if (sm and acquired) else None
    out.append(_kpi(
        "cac", "Customer acquisition cost",
        "What does it cost to win one?",
        "fully-loaded sales + marketing spend in a period ÷ new customers acquired in that period",
        "Charles (cost) + Reilly/Bird (attribution)",
        "One acquisition, plus a sales-and-marketing line in the ledger.",
        unit="$", value=cac_val,
        refusal=(None if cac_val is not None else
                 ("No customers acquired yet, and no sales-and-marketing spend line exists. "
                  "expenses.md has a `marketing` category, which is not the same thing.")),
        needs="a first acquisition and an S&M split in finance/actuals.json",
        inputs=["actuals.salesAndMarketingSpend.monthly", "actuals.customers.acquired"],
        caveats=["Any CAC computed at solo-founder stage is a FLOOR, not a cost: the dominant input "
                 "is the Founder's unpaid time, which no ledger prices. Label it a floor every time it is "
                 "quoted — a flattering CAC is the easiest number in this list to fool yourself with.",
                 "The connector program will make CAC bimodal — a referred client and a cold-outbound "
                 "client cost nothing alike. Report the two separately or the blend hides both."],
    ))

    # ---- 5. LTV --------------------------------------------------------------------------------
    out.append(_kpi(
        "ltv", "Customer lifetime value",
        "What is one customer worth over the whole relationship?",
        "average revenue per account × gross margin % ÷ churn rate",
        "Charles",
        "Needs churn (gate above) AND gross margin — and gross margin needs per-client cost data "
        "from clients/*/cost.md, which is why HQ's margin metric is honest-null today.",
        unit="$",
        refusal="Refused twice over: no churn rate to divide by, and no gross margin to multiply by. "
                "LTV is the most-quoted and least-defensible number in SaaS precisely because both "
                "of its inputs are usually guessed.",
        needs="churn + gross margin, in that order",
        inputs=["kpi.churn", "goals.marginPct", "actuals.revenue.mrr"],
        caveats=["yourco absorbs model spend, so gross margin here must be net of token cost per "
                 "client — the cost ledger exists (clients/*/cost.md) and is the input that makes "
                 "this real rather than a slide."],
    ))

    # ---- 6. LTV:CAC ----------------------------------------------------------------------------
    out.append(_kpi(
        "ltvCac", "LTV to CAC ratio",
        "Do we make more from a customer than it cost to get one?",
        "LTV ÷ CAC",
        "Charles",
        "Both of its inputs first. It cannot arrive before them, and it is the last of the nine.",
        unit="x",
        refusal="Both inputs are refused, so the ratio is refused. A ratio of two estimates is not "
                "an estimate — it is two errors multiplied.",
        needs="LTV and CAC",
        inputs=["kpi.ltv", "kpi.cac"],
    ))

    # ---- 7. Burn multiple ----------------------------------------------------------------------
    net_new_arr = 0 if (rev.get("mrr") == 0) else None
    out.append(_kpi(
        "burnMultiple", "Burn multiple",
        "How many dollars are we burning per dollar of new revenue?",
        "net burn ÷ net new ARR",
        "Charles",
        "The first dollar of new ARR. Nothing else is required — this one clears the moment a deal "
        "goes live.",
        unit="x",
        refusal=("Net new ARR is $0, so the burn multiple is UNDEFINED — not infinite, and not bad. "
                 "Dividing by zero produces no information about efficiency; it only restates that "
                 "there is no revenue, which the north star already says more plainly."),
        needs="one dollar of new ARR",
        inputs=["actuals.burn.monthlyFixed", "actuals.revenue.mrr"],
        caveats=["This is the cleanest single read on whether the machine works, and it will be "
                 "brutal at first: burn ÷ a small first ARR is a large number by construction. "
                 "Expect a bad figure for two or three quarters and judge the trend, not the level."],
    ))

    # ---- 8. EBITDA ------------------------------------------------------------------------------
    mrr = rev.get("mrr")
    fixed = burn.get("monthlyFixed")
    ebitda = (round((mrr or 0) - fixed, 2) if (mrr is not None and fixed is not None) else None)
    out.append(_kpi(
        "ebitda", "EBITDA (monthly, run-rate)",
        "Does the operation make money before financing and tax?",
        "revenue − operating expenses (excluding interest, tax, depreciation, amortisation)",
        "Charles",
        "Computable now — and one of only two on this list that is.",
        unit="$", value=ebitda,
        refusal=(None if ebitda is not None else "finance/actuals.json is missing revenue or burn."),
        inputs=["actuals.revenue.mrr", "actuals.burn.monthlyFixed"],
        caveats=([f"Fixed burn is the LAST CONFIRMED figure, not a current one. {burn_note}"]
                 if burn_note else []) +
                ["Excludes API/token spend and usage-priced tools, which are real and variable.",
                 "Prices no founder compensation. A one-person company's EBITDA flatters itself by "
                 "exactly one salary, and this one flatters itself by a full-time founder's."],
    ))

    # ---- 9. Operating cash flow -----------------------------------------------------------------
    ocf = None
    ocf_note = None
    if last_close and last_close.get("cashOut") is not None:
        ocf = round((last_close.get("revenue") or 0) - last_close["cashOut"], 2)
        ocf_note = f"month {last_close.get('month')}, closed {last_close.get('closedOn')}"
    out.append(_kpi(
        "ocf", "Operating cash flow (last closed month)",
        "Did more cash come in than went out?",
        "cash received from operations − cash paid for operations, for the last CLOSED month",
        "Charles",
        "Computable now, one closed month at a time.",
        unit="$", value=ocf,
        refusal=(None if ocf is not None else "no closed month carries a cashOut figure."),
        needs=None if ocf is not None else "a monthly close",
        inputs=["actuals.months[0]"],
        caveats=([ocf_note] if ocf_note else []) +
                ["Charges that FAILED are excluded — they never left the account. That makes this "
                 "number true and optimistic at the same time: a failed charge is a bill that is "
                 "still owed.",
                 "The company holds $0 cash and the Founder funds charges personally as they arrive, so "
                 "'operating cash flow' here describes a founder's card, not a treasury."],
    ))

    return out


def build():
    rows = compute()
    a = _load(ACTUALS) or {}
    computed = [r for r in rows if r["state"] == "computed"]
    return {
        "generated": datetime.datetime.now().isoformat(timespec="seconds"),
        "kpis": rows,
        "computed": len(computed),
        "refused": len(rows) - len(computed),
        "actualsAsOf": a.get("asOf"),
        "actualsOwner": a.get("owner"),
        "headline": (f"{len(computed)} of {len(rows)} compute today. The other "
                     f"{len(rows) - len(computed)} are defined and waiting on a named precondition — "
                     f"six of them on the first customer."),
        "note": ("Definitions and refusal conditions: finance/kpi-definitions.md. Inputs: "
                 "finance/actuals.json (Charles, at each monthly close) + crm/data.json. Nothing "
                 "here is estimated, benchmarked or placeheld."),
    }


def main():
    p = build()
    print(f"\n=== KPIs — {p['headline']}")
    print(f"    actuals as of {p['actualsAsOf']} (owner: {p['actualsOwner']})\n")
    for r in p["kpis"]:
        head = f"  {r['name']}"
        if r["state"] == "computed":
            v = r["value"]
            s = (f"${v:,.2f}" if r["unit"] == "$" else f"{v}{r['unit']}")
            print(f"{head}: {s}")
        else:
            print(f"{head}: REFUSED")
            print(f"      {r['refusal']}")
            if r.get("needs"):
                print(f"      needs: {r['needs']}")
        print(f"      clears when: {r['firstComputableWhen']}")
        for c in r["caveats"]:
            print(f"      ⚠ {c}")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
