#!/usr/bin/env python3
"""Deal OS — domain core (real estate investors).

Rules live here: the underwriting engine (mortgage math, amortization, payoff,
NOI, cash-on-cash, cap rate, DSCR, IRR at exit horizons), the comp floor, the
bands-never-points rule, the investor-criteria deal screen, the advice line,
data freshness, and the matrix.

THE LOAD-BEARING IDEA: every incumbent tool in this category flatters the
deal — point predictions on hidden assumptions. This engine refuses to state a
number it cannot trace to an input, refuses point estimates on long horizons
(bands only), refuses rent/occupancy estimates below the recorded comp floor,
and refuses to be an investment advisor. THIS IS A MODEL, on its face, always.

Stdlib only. Honesty rules come from `_kit`.
"""
import re, sys
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent))

from _kit.moat import Eval, Gate, Matrix, Roi                       # noqa: E402
from _kit.store import (Store, automation_rate, iso, median, now,   # noqa: E402
                        parse, unmeasured)

TABLES = ("config", "markets", "listings", "comps", "criteria", "analyses",
          "messages", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="DEALOS_DATA_ROOT")

NOT_ADVICE = ("Not investment advice. This is arithmetic on stated assumptions — "
              "the decision, and the risk, are yours.")

STRATEGIES = ("ltr", "mtr", "str")

# ---------------------------------------------------------------- assumptions
#
# Every default is VISIBLE, named, and overridable per-underwrite. A default
# the investor never saw is a hidden assumption — the incumbent disease.

DEFAULT_ASSUMPTIONS = {
    "_source": ("DEFAULT underwriting assumptions — every one shown on the result and "
                "overridable. Replace with the investor's own before real use."),
    "down_pct": 0.25, "closing_cost_pct": 0.03, "rate_spread": 0.0,
    "vacancy_ltr": 0.06, "vacancy_mtr": 0.15,
    "maintenance_pct": 0.08, "capex_pct": 0.05, "mgmt_pct_ltr": 0.09,
    "mgmt_pct_str": 0.20, "str_opex_extra_pct": 0.12,   # cleaning/supplies/utilities
    "selling_cost_pct": 0.07,
    "appreciation_offsets": {"bear": -0.02, "bull": 0.02},  # vs the market's recorded base
    "rent_growth": 0.02,
}
COMP_FLOOR = {"count": 5, "recency_days": 180,
              "_source": "DEFAULT comp floor — below it an estimate is refused, never invented."}
STALE_DAYS = 30
LONG_HORIZON_YEARS = 3          # beyond this, points are refused; bands only


def assumptions(overrides=None):
    base = dict(DEFAULT_ASSUMPTIONS)
    base.update(store.load("config").get("assumptions") or {})
    for k, v in (overrides or {}).items():
        if k in base and isinstance(v, (int, float)) and not isinstance(v, bool):
            base[k] = v
    return base


# ---------------------------------------------------------------- mortgage math

def monthly_payment(principal, annual_rate, years=30):
    r = annual_rate / 12
    n = years * 12
    if r == 0:
        return principal / n
    return principal * r * (1 + r) ** n / ((1 + r) ** n - 1)


def amortization(principal, annual_rate, years=30, extra_monthly=0.0):
    """Full schedule. Returns yearly balances, total interest, payoff month —
    the 'when is it actually paid off' answer, including the extra-payment
    scenario."""
    r = annual_rate / 12
    pay = monthly_payment(principal, annual_rate, years) + extra_monthly
    bal, month, interest_total = principal, 0, 0.0
    yearly = []
    while bal > 0.005 and month < years * 12 + 600:
        month += 1
        interest = bal * r
        principal_part = min(pay - interest, bal)
        if principal_part <= 0:
            return {"error": "payment does not cover interest — this loan never pays off"}
        bal -= principal_part
        interest_total += interest
        if month % 12 == 0 or bal <= 0.005:
            yearly.append({"year": (month + 11) // 12, "balance": round(max(bal, 0), 2)})
    return {"payment": round(pay, 2), "payoff_month": month,
            "payoff_years": round(month / 12, 1),
            "total_interest": round(interest_total, 2), "yearly_balances": yearly}


# ---------------------------------------------------------------- comps + freshness

def market_rate(market):
    """The recorded mortgage rate for the market env, with freshness on its
    face. Stale is FLAGGED, never silently used."""
    m = store.by_id("markets", market["id"]) if isinstance(market, dict) else store.by_id("markets", market)
    rates = (m or {}).get("rates") or {}
    if not rates.get("rate_30yr"):
        return unmeasured("no recorded rate for this market — we don't guess the cost of money",
                          field="rate")
    age = (now() - (parse(rates.get("as_of")) or now())).days
    return {"rate": rates["rate_30yr"], "as_of": rates.get("as_of"), "age_days": age,
            "stale": age > STALE_DAYS,
            "note": (f"rate is {age} days old — STALE, past the {STALE_DAYS}-day threshold; "
                     f"every number it touches is flagged" if age > STALE_DAYS else
                     f"as of {str(rates.get('as_of'))[:10]}")}


def comp_estimate(listing, strategy):
    """Rent (LTR/MTR) or ADR+occupancy (STR) from recorded comps ONLY, behind
    the recorded floor. Below the floor: refused — we don't invent occupancy."""
    floor = store.load("config").get("comp_floor") or COMP_FLOOR
    ref = now()
    rows = [c for c in store.load("comps")
            if c.get("market_id") == listing.get("market_id")
            and c.get("strategy") == strategy
            and c.get("bedrooms") == listing.get("bedrooms")
            and (ref - (parse(c.get("as_of")) or ref)).days <= floor["recency_days"]]
    if len(rows) < floor["count"]:
        return {"refused": (f"{len(rows)} recent {strategy.upper()} comp(s) for "
                            f"{listing.get('bedrooms')}BR in this market — the floor is "
                            f"{floor['count']} within {floor['recency_days']} days. Below it an "
                            f"estimate is an invention, and inventions lose money."),
                "n": len(rows), "floor": floor["count"]}
    if strategy == "str":
        return {"adr": round(median([c["adr"] for c in rows]), 2),
                "occupancy": round(median([c["occupancy"] for c in rows]), 3),
                "n": len(rows), "basis": f"median of {len(rows)} recorded comps"}
    return {"rent": round(median([c["rent"] for c in rows]), 2),
            "n": len(rows), "basis": f"median of {len(rows)} recorded comps"}


# ---------------------------------------------------------------- underwriting

def _gross_income(listing, strategy, comp):
    if strategy == "str":
        return comp["adr"] * 365 * comp["occupancy"]
    return comp["rent"] * 12


def underwrite(listing, strategy, overrides=None, extra_monthly=0.0):
    """One listing × one strategy. Every number traces to an input; the whole
    result is labeled a model. Refusals happen here, not downstream."""
    if strategy not in STRATEGIES:
        return {"refused": f"unknown strategy {strategy!r}"}
    a = assumptions(overrides)
    comp = comp_estimate(listing, strategy)
    if "refused" in comp:
        return {"refused": comp["refused"], "strategy": strategy,
                "unmeasured": True, "comps": comp}
    market = store.by_id("markets", listing["market_id"]) or {}
    rate = market_rate(market)
    if rate.get("_missing"):
        return {"refused": rate["_missing"], "strategy": strategy}

    price = listing["price"]
    down = price * a["down_pct"]
    loan = price - down
    closing = price * a["closing_cost_pct"]
    cash_in = down + closing
    eff_rate = rate["rate"] + a["rate_spread"]
    am = amortization(loan, eff_rate, 30, extra_monthly)
    if "error" in am:
        return {"refused": am["error"], "strategy": strategy}

    gross = _gross_income(listing, strategy, comp)
    vacancy = {"ltr": a["vacancy_ltr"], "mtr": a["vacancy_mtr"], "str": 0.0}[strategy]
    egi = gross * (1 - vacancy)
    mgmt_pct = a["mgmt_pct_str"] if strategy == "str" else a["mgmt_pct_ltr"]
    opex = (listing.get("taxes", 0) + listing.get("insurance", 0)
            + listing.get("hoa", 0) * 12
            + egi * (a["maintenance_pct"] + a["capex_pct"] + mgmt_pct)
            + (egi * a["str_opex_extra_pct"] if strategy == "str" else 0))
    noi = egi - opex
    debt_service = am["payment"] * 12
    cashflow = noi - debt_service
    result = {
        "strategy": strategy, "listing_id": listing["id"],
        "label": "THIS IS A MODEL — arithmetic on the stated inputs, nothing more",
        "not_advice": NOT_ADVICE,
        "inputs": {"price": price, "rate": eff_rate, "rate_as_of": rate.get("as_of"),
                   "rate_stale": rate.get("stale", False), "comps": comp,
                   "assumptions": {k: v for k, v in a.items() if k != "_source"},
                   "assumptions_source": a["_source"]},
        "cash_in": round(cash_in, 2),
        "gross_income": round(gross, 2), "effective_income": round(egi, 2),
        "opex": round(opex, 2), "noi": round(noi, 2),
        "payment_monthly": am["payment"], "debt_service": round(debt_service, 2),
        "cashflow_year1": round(cashflow, 2), "cashflow_monthly": round(cashflow / 12, 2),
        "cap_rate": round(noi / price, 4),
        "cash_on_cash": round(cashflow / cash_in, 4),
        "dscr": round(noi / debt_service, 2) if debt_service else None,
        "payoff": {"years": am["payoff_years"], "month": am["payoff_month"],
                   "total_interest": am["total_interest"],
                   "yearly_balances": am["yearly_balances"][:31]},
        "stale_flag": rate.get("stale", False),
    }
    return result


# ---------------------------------------------------------------- bands, never points

def appreciation_base(market):
    """Base appreciation = the market's own recorded trailing history — never a
    national vibe. No history → unmeasured."""
    hist = (market.get("appreciation_history") or [])
    if len(hist) < 5:
        return unmeasured(f"only {len(hist)} recorded years of price history; need 5 — "
                          "an appreciation guess with no history is astrology", field="cagr")
    first, last = hist[0]["index"], hist[-1]["index"]
    years = len(hist) - 1
    return {"cagr": round((last / first) ** (1 / years) - 1, 4), "years": years,
            "basis": f"trailing {years}y CAGR of this market's recorded index"}


def exit_bands(listing, strategy, hold_years, overrides=None):
    """Equity + IRR at an exit horizon, as BEAR/BASE/BULL bands. A point
    estimate past LONG_HORIZON_YEARS is refused by construction — this
    function is the only path to a long-horizon number and it returns three."""
    uw = underwrite(listing, strategy, overrides)
    if "refused" in uw:
        return uw
    market = store.by_id("markets", listing["market_id"]) or {}
    base = appreciation_base(market)
    if base.get("_missing"):
        return {"refused": base["_missing"], "strategy": strategy}
    a = assumptions(overrides)
    bands = {}
    for name, offset in [("bear", a["appreciation_offsets"]["bear"]), ("base", 0.0),
                         ("bull", a["appreciation_offsets"]["bull"])]:
        g = base["cagr"] + offset
        value = listing["price"] * (1 + g) ** hold_years
        bal = next((y["balance"] for y in uw["payoff"]["yearly_balances"]
                    if y["year"] == hold_years), 0.0)
        proceeds = value * (1 - a["selling_cost_pct"]) - bal
        flows = [-uw["cash_in"]]
        cf = uw["cashflow_year1"]
        for yr in range(1, hold_years + 1):
            flows.append(cf * (1 + a["rent_growth"]) ** (yr - 1))
        flows[-1] += proceeds
        bands[name] = {"growth": round(g, 4), "exit_value": round(value, 2),
                       "loan_balance": round(bal, 2), "net_proceeds": round(proceeds, 2),
                       "equity_multiple": round((sum(flows[1:]) ) / uw["cash_in"] + 0, 2)
                       if uw["cash_in"] else None,
                       "irr": _irr(flows)}
    return {"strategy": strategy, "hold_years": hold_years, "bands": bands,
            "appreciation_basis": base["basis"],
            "label": "THIS IS A MODEL — three bands because a single number "
                     f"{hold_years} years out would be fiction",
            "not_advice": NOT_ADVICE}


def _irr(flows, lo=-0.99, hi=1.5):
    def npv(r):
        return sum(f / (1 + r) ** i for i, f in enumerate(flows))
    if npv(lo) * npv(hi) > 0:
        return None
    for _ in range(80):
        mid = (lo + hi) / 2
        if npv(lo) * npv(mid) <= 0:
            hi = mid
        else:
            lo = mid
    return round((lo + hi) / 2, 4)


def point_estimate(listing, strategy, hold_years, overrides=None):
    """The refusal path: a single long-horizon number does not exist here."""
    if hold_years > LONG_HORIZON_YEARS:
        store.log_event("refused", listing["id"], "agent:underwriter", "R0",
                        {"action": "project_point_estimate_long_horizon",
                         "why": f"{hold_years} years out, a point estimate is fiction — "
                                f"bands only past year {LONG_HORIZON_YEARS}"})
        return {"refused": f"a single number {hold_years} years out is fiction — here are "
                           f"bands instead", "use": "exit_bands"}
    return exit_bands(listing, strategy, hold_years, overrides)


def sensitivity(listing, strategy, overrides=None):
    """Rate ±2% × rent ±10% → DSCR / CoC grid. The stress test incumbents hide."""
    grid = []
    for dr in (-0.02, -0.01, 0.0, 0.01, 0.02):
        row = []
        for rent_mult in (0.9, 1.0, 1.1):
            uw = underwrite(listing, strategy,
                            {**(overrides or {}), "rate_spread": dr})
            if "refused" in uw:
                return uw
            scale = rent_mult
            noi = uw["effective_income"] * scale - uw["opex"] * (
                1 + (scale - 1) * 0.4)   # variable share of opex moves with income
            cf = noi - uw["debt_service"]
            row.append({"rate_delta": dr, "rent_mult": rent_mult,
                        "dscr": round(noi / uw["debt_service"], 2),
                        "coc": round(cf / uw["cash_in"], 4)})
        grid.append(row)
    return {"grid": grid, "label": "THIS IS A MODEL — the stress test on its face",
            "note": "rate ±2 points × rent ±10%. If the deal only works in the "
                    "bottom-right corner, the deal doesn't work."}


# ---------------------------------------------------------------- the deal screen

def deal_screen(investor_id=None, strategy=None, limit=25):
    """Ranked ONLY by the investor's recorded criteria. No criteria → no
    ranking — we rank by your bar, not ours."""
    crit = None
    for c in store.load("criteria"):
        if investor_id is None or c.get("investor_id") == investor_id:
            crit = c
            break
    if not crit:
        store.log_event("refused", investor_id or "unknown", "agent:screener", None,
                        {"action": "rank_without_recorded_criteria",
                         "why": "no recorded investor criteria — we rank by your bar, not ours"})
        return {"refused": "no recorded criteria for this investor — record min DSCR, min "
                           "cash-on-cash, max price and allowed strategies first. We rank by "
                           "your bar, not ours."}
    rows, skipped = [], {"over_price": 0, "unmeasured": 0, "below_bar": 0}
    for l in store.load("listings"):
        if l.get("demo_tag") or l.get("status") != "active":
            continue
        if l["price"] > crit["max_price"]:
            skipped["over_price"] += 1
            continue
        best = None
        for s in (crit.get("strategies") or list(STRATEGIES)):
            if strategy and s != strategy:
                continue
            uw = underwrite(l, s)
            if "refused" in uw:
                continue
            if uw["dscr"] >= crit["min_dscr"] and uw["cash_on_cash"] >= crit["min_coc"]:
                if best is None or uw["cash_on_cash"] > best["cash_on_cash"]:
                    best = uw
        if best is None:
            skipped["below_bar"] += 1
            continue
        rows.append({"listing": {k: l.get(k) for k in ("id", "address", "market_id", "price",
                                                       "bedrooms", "bathrooms", "sqft")},
                     "strategy": best["strategy"], "cash_on_cash": best["cash_on_cash"],
                     "dscr": best["dscr"], "cashflow_monthly": best["cashflow_monthly"],
                     "cap_rate": best["cap_rate"],
                     "why": (f"clears YOUR bar: DSCR {best['dscr']} ≥ {crit['min_dscr']}, "
                             f"CoC {best['cash_on_cash']:.1%} ≥ {crit['min_coc']:.0%}, "
                             f"price ${l['price']:,} ≤ ${crit['max_price']:,} "
                             f"as {best['strategy'].upper()}")})
    rows.sort(key=lambda r: -r["cash_on_cash"])
    return {"criteria": crit, "rows": rows[:limit], "considered": len(store.load("listings")),
            "skipped": skipped, "not_advice": NOT_ADVICE,
            "note": "ranked by the investor's own recorded bar — the why-trace on every row"}


# ---------------------------------------------------------------- the advice line

GUARANTEE_WORDS = ("guaranteed", "can't lose", "cannot lose", "sure thing", "risk-free",
                   "no risk", "certain to appreciate", "will definitely")


def advice_ok(text):
    t = (text or "").lower()
    hits = [w for w in GUARANTEE_WORDS if w in t]
    if hits:
        return False, f"guarantee language cannot ship: {', '.join(hits)}"
    return True, "ok"


# ---------------------------------------------------------------- triage

ADVICE_ASK = (
    r"\bshould (i|we) (buy|purchase|offer|go for|pull the trigger)\b",
    r"\b(is|would) (this|it|that) (a )?(good|smart|safe) (deal|investment|buy)\b",
    r"\bwould you (buy|invest|do (it|this deal))\b",
    r"\b(good|bad) idea to buy\b",
)
RUN_NUMBERS = (
    r"\b(run|crunch) the numbers\b",
    # "underwrite" is an act with only one meaning here — standalone is enough
    # ("can you underwrite the fourplex at asking" — found by the eval)
    r"\b(underwrite|pencil out|analysis on)\b",
    # "what would the fernwood duplex rent for" — the subject need not be a
    # pronoun (found by the eval)
    r"\bwhat (would|could|does)\b.*\b(rent|cash ?flow|make)\b.*\b(for|at|per)?\b",
    r"\bwhat('s| is) the (roi|cash ?flow|cap rate|dscr|return)\b",
)
SCENARIO_ASK = (
    r"\bwhat (if|happens? (if|when))\b.*\b(rates?|interest|rent|vacancy|market|drops?|rises?|falls?)\b",
    r"\b(rates? (go|went|drop|jump)|if the market (drops|crashes|cools))\b",
    r"\bpay (it )?off (early|faster|sooner)\b",
    r"\bextra (payment|principal)\b",
)
CRITERIA_UPDATE = (
    r"\b(my|our|change|update|set) (criteria|buy box|minimum|bar)\b",
    r"\bonly (show|send)( me)?\b.*\b(dscr|cash ?flow|under|below)\b",
)
STATUS_ASK = (
    r"\b(any(thing)? new|what('s| is) new|new (deals|listings|matches))\b",
    r"\b(status|update) on\b.*\b(screen|search|pipeline)\b",
)


def read_message(text):
    """advice_ask | run_numbers | scenario_ask | criteria_update | status | human.
    The advice ask reads FIRST — mishandling it turns a calculator into an
    unlicensed investment advisor."""
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty message — a person reads it"}
    for rx in ADVICE_ASK:
        if re.search(rx, t):
            return {"label": "advice_ask",
                    "why": "a verdict ask — the reply is arithmetic, bands, and the "
                           "not-advice line; never a recommendation"}
    for rx in SCENARIO_ASK:
        if re.search(rx, t):
            return {"label": "scenario_ask",
                    "why": "a what-if — answered by the sensitivity grid or bands, "
                           "never a single confident number"}
    for rx in RUN_NUMBERS:
        if re.search(rx, t):
            return {"label": "run_numbers", "why": "an underwrite request — the engine's job"}
    for rx in CRITERIA_UPDATE:
        if re.search(rx, t):
            return {"label": "criteria_update",
                    "why": "the investor moving their own bar — recorded, then the screen "
                           "re-runs against it"}
    for rx in STATUS_ASK:
        if re.search(rx, t):
            return {"label": "status", "why": "answered from the screen's own record"}
    return {"label": "human", "why": "no clean signal — a person reads it"}


# ---------------------------------------------------------------- eval

triage_eval = Eval("message triage",
                   costly_label="advice_ask",
                   costly_note=("A VERDICT FROM SOFTWARE IS UNLICENSED INVESTMENT ADVICE WITH "
                                "SIX FIGURES ATTACHED. Over-routing a numbers ask costs a read."))

EVAL_CASES = [
    {"input": "should I buy the duplex on Fernwood", "label": "advice_ask"},
    {"input": "is this a good deal or am I crazy", "label": "advice_ask"},
    {"input": "would you buy it at 285", "label": "advice_ask"},
    {"input": "good idea to buy in Harbor Point right now?", "label": "advice_ask"},
    {"input": "run the numbers on 412 Birchwood as a short term rental", "label": "run_numbers"},
    {"input": "what would the fernwood duplex rent for", "label": "run_numbers"},
    {"input": "what's the cap rate on that cedar falls listing", "label": "run_numbers"},
    {"input": "can you underwrite the fourplex at asking", "label": "run_numbers"},
    {"input": "what happens if rates drop a point next year", "label": "scenario_ask"},
    {"input": "what if I make extra principal payments, when is it paid off", "label": "scenario_ask"},
    {"input": "if the market cools 10% where does that leave me", "label": "scenario_ask"},
    {"input": "update my criteria, only show me DSCR over 1.3", "label": "criteria_update"},
    {"input": "anything new hit the screen this week", "label": "status"},
    {"input": "", "label": "human"},
    {"input": "what time are you around to talk tomorrow", "label": "human"},
    {"input": "thanks for the breakdown yesterday", "label": "human"},
]


def run_eval():
    return triage_eval.run(EVAL_CASES, lambda t: read_message(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_message":        {"rung": "R3", "reason": "routing only; the advice ask reads first"},
    "recommend_purchase":  {"rung": "R0", "reason": "a verdict from software is unlicensed investment advice — the reply is arithmetic, bands, and the not-advice line", "never_promote": True},
    "guarantee_return":    {"rung": "R0", "reason": "guarantee language cannot ship — no return is guaranteed and no honest tool says otherwise", "never_promote": True},
    "project_point_estimate_long_horizon": {"rung": "R0", "reason": "a single number years out is fiction — bands only past the near horizon", "never_promote": True},
    "estimate_below_comp_floor": {"rung": "R0", "reason": "below the recorded comp floor an estimate is an invention — refused with the floor named", "never_promote": True},
    "run_underwrite":      {"rung": "R2", "reason": "arithmetic on recorded inputs with the provenance attached — the label does the disclosing"},
    "screen_deals":        {"rung": "R2", "reason": "ranking by the investor's own recorded bar"},
    "record_criteria":     {"rung": "R1", "reason": "the investor's bar is theirs — recorded from their words, confirmed by a human"},
    "draft_deal_alert":    {"rung": "R1", "reason": "outward copy about a six-figure decision — a human sends"},
    "draft_reply":         {"rung": "R1", "reason": "outward reply — advice-checked structurally, a human sends"},
    "flag_rate_move":      {"rung": "R2", "reason": "a stale or moved rate flags every number it touched — always the safe direction"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi (for the operator)

def roi_model():
    return (Roi("Deal OS — what it computes to for the investor-operator")
        .line("Underwriting hours returned", "time_saved",
              "deals screened/mo × min per manual underwrite × 12 × rate",
              ["deals_month", "min_per_underwrite", "rate"],
              lambda g: float(g["deals_month"]) * float(g["min_per_underwrite"]) / 60 * 12
              * float(g["rate"]),
              note="deals screened is counted from this system's own log")
        .line("Screen-to-offer funnel", "revenue",
              "offers made × your close rate × your per-deal economics",
              ["offers_yr", "close_rate", "per_deal_value"],
              lambda g: float(g["offers_yr"]) * float(g["close_rate"]) * float(g["per_deal_value"]),
              assumption="your funnel, your economics — recorded, not assumed")
        .line("The bad buy avoided", "scenario",
              "you decide what the deal you didn't do is worth",
              ["bad_buy_value"], lambda g: float(g["bad_buy_value"]),
              assumption="never a saving we claim — the six-figure mistake that didn't "
                         "happen is not our number"))


def roi(given):
    rec = {}
    ana = [x for x in store.load("analyses")]
    if ana:
        rec["deals_month"] = len([x for x in ana
                                  if (now() - (parse(x.get("at")) or now())).days <= 30])
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


def screened_this_week(ref=None):
    """Counted: underwrites run, deals clearing the bar, alerts a human sent."""
    ref = ref or now()
    ana = [x for x in store.load("analyses")
           if (ref - (parse(x.get("at")) or ref)).days <= 7]
    sent = sum(1 for e in store.events(kind="draft_deal_alert")
               if str(e.get("actor", "")).startswith("human:")
               and (ref - (parse(e.get("at")) or ref)).days <= 7)
    return {"underwrites": len(ana),
            "cleared_bar": sum(1 for x in ana if x.get("cleared_bar")),
            "alerts_sent": sent,
            "note": "counted from the analysis log — human sends count; agent drafts don't"}


MOVING = ("read_message", "run_underwrite", "screen_deals", "record_criteria",
          "draft_deal_alert", "draft_reply", "flag_rate_move")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("investor:",))
