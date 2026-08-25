#!/usr/bin/env python3
"""Fuel OS — domain core (propane delivery).

Rules live here: gas-smell-first triage with the evacuate script, the leak-check
gate (an out-of-gas ticket cannot close without the recorded test), the runout
board (usage history or UNKNOWN), the contract price clamp, the requalification
gate, and the matrix.

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

TABLES = ("config", "customers", "tanks", "tickets", "calls", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="FUELOS_DATA_ROOT")

EVACUATE_SCRIPT = ("GAS SMELL PROTOCOL, verbatim: leave the building NOW, leave the door open "
                   "behind you, do not touch light switches, phones, or anything electrical on "
                   "the way out. Call us back from outside or a neighbor's. A truck and a "
                   "technician are being dispatched — nothing about this is troubleshot by phone.")

# ---------------------------------------------------------------- triage

GAS_SMELL = (
    r"\b(smell|smells|smelling|odor)\b.*\b(gas|propane|rotten egg|sulfur)\b",
    r"\b(gas|propane)\b.*\b(smell|odor|leak(ing)?)\b",
    r"\b(rotten egg|sulfur)\b|\bhissing\b.*\b(tank|line|regulator)\b",
)
OUT_OF_GAS = (
    r"\b(out of (gas|propane)|tank('?s| is) empty|ran out|no heat and the tank|gauge (reads|shows|says) (zero|empty|0))\b",
    r"\b(furnace|heat|stove)\b.*\b(out|quit|died)\b.*\b(tank|propane|gas)\b",
)
DELIVERY = (
    r"\b(need|schedule|order)\b.*\b(fill|delivery|propane|gas)\b",
    r"\b(top (off|up)|fill (the|my) tank)\b",
    r"\bgauge (reads|shows|says|is at)\b.*\b([1-9]\d?)\s?(%|percent)\b",
)
PRICE = (
    r"\b(price|cost|rate|per gallon)\b",
    r"\bwhat('?s| is| are) (the|your|my)\b.*\b(price|rate|contract)\b",
)


def read_call(text):
    """gas_smell | out_of_gas | delivery | price | human. Gas smell first —
    the script is the product."""
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty call — a person answers"}
    for rx in GAS_SMELL:
        if re.search(rx, t):
            return {"label": "gas_smell", "script": EVACUATE_SCRIPT,
                    "why": "a gas smell — the evacuate script verbatim, a truck now; nothing is "
                           "troubleshot by phone"}
    for rx in OUT_OF_GAS:
        if re.search(rx, t):
            return {"label": "out_of_gas",
                    "why": "an out-of-gas event — a SAFETY event, not a missed delivery: the "
                           "ticket cannot close without the recorded leak check"}
    for rx in DELIVERY:
        if re.search(rx, t):
            return {"label": "delivery", "why": "delivery request — drafts on the route"}
    for rx in PRICE:
        if re.search(rx, t):
            return {"label": "price",
                    "why": "price question — contract customers hear their recorded contract "
                           "price; the market price cannot reach them"}
    return {"label": "human", "why": "no clean signal — a person answers"}


# ---------------------------------------------------------------- the leak-check gate

def can_close_outage(ticket):
    """An out-of-gas ticket closes only with a recorded leak-check result.
    THE refusal — it's regulation, and it's how houses don't explode."""
    if ticket.get("kind") != "out_of_gas":
        return True, "not an outage ticket"
    lc = ticket.get("leak_check")
    if lc and lc.get("result") and lc.get("tech"):
        return True, f"leak check recorded: {lc['result']} by {lc['tech']}"
    return False, ("an out-of-gas delivery cannot close without a recorded leak-check result — "
                   "the system was open to air, and relighting without the test is how houses "
                   "explode. The ticket stays open until the tech's result is recorded.")


# ---------------------------------------------------------------- the contract clamp

def price_for(customer):
    """A contract customer's price IS the recorded contract price — the market
    price cannot reach them by construction."""
    cfg = store.load("config")
    if customer.get("contract_price"):
        return {"per_gallon": customer["contract_price"],
                "basis": f"the recorded contract price (through {str(customer.get('contract_through', ''))[:10]})",
                "clamped": True,
                "note": "the market price cannot reach a contract customer — by construction"}
    market = cfg.get("market_price")
    if market is None:
        return unmeasured("no recorded market price — a quote without one is a guess", field="per_gallon")
    return {"per_gallon": market, "basis": "today's recorded market price", "clamped": False}


# ---------------------------------------------------------------- requalification

def can_fill_tank(tank, ref=None):
    """A tank past its recorded requalification date can't be filled; a tank
    with no date reads UNKNOWN and can't be filled either."""
    ref = ref or now()
    requal = parse(tank.get("requal_due"))
    if not requal:
        return False, ("no requalification date recorded for this tank — UNKNOWN is not "
                       "fillable; the date gets recorded or the tank gets requalified")
    if requal < ref:
        return False, (f"tank requalification expired {str(tank['requal_due'])[:10]} — an "
                       f"out-of-date vessel doesn't get filled, it gets requalified")
    return True, f"requal current through {str(tank['requal_due'])[:10]}"


# ---------------------------------------------------------------- the runout board

def runout_board(ref=None):
    """Days-to-empty from recorded usage history + current reading. No history
    reads UNKNOWN, never 'fine'."""
    ref = ref or now()
    rows = []
    for t in store.load("tanks"):
        if t.get("demo_tag"):
            continue
        usage = t.get("gallons_per_day")
        reading = t.get("last_reading_pct")
        size = t.get("size_gal")
        if usage is None or reading is None or not size:
            rows.append({"tank": t["id"], "customer": t.get("customer_name"),
                         **unmeasured("no usage history or reading — days-to-empty UNKNOWN, "
                                      "never assumed fine", field="days_to_empty")})
            continue
        gallons_left = size * (reading / 100) * 0.8  # usable capacity
        days = gallons_left / usage if usage else None
        rows.append({"tank": t["id"], "customer": t.get("customer_name"),
                     "days_to_empty": round(days, 1), "reading_pct": reading,
                     "risk": "critical" if days < 7 else "watch" if days < 14 else "ok"})
    rows.sort(key=lambda r: (r.get("days_to_empty") is None, r.get("days_to_empty") or 0))
    return rows


def recovered_this_week(ref=None):
    """Counted: outages closed WITH leak checks, deliveries made, runouts
    predicted and filled first."""
    ref = ref or now()
    closed = [t for t in store.load("tickets")
              if t.get("kind") == "out_of_gas" and t.get("closed_at")
              and (ref - (parse(t["closed_at"]) or ref)).days <= 7]
    deliveries = sum(1 for e in store.events(kind="draft_delivery")
                     if str(e.get("actor", "")).startswith("human:")
                     and (ref - (parse(e.get("at")) or ref)).days <= 7)
    return {"outages_closed_with_checks": len(closed), "deliveries_made": deliveries,
            "note": "counted from the tickets and the event log — never asserted"}


# ---------------------------------------------------------------- eval

triage_eval = Eval("call triage",
                   costly_label="gas_smell",
                   costly_note=("A GAS SMELL TRIAGED AS A DELIVERY REQUEST IS A FAMILY IN A HOUSE "
                                "THAT MIGHT EXPLODE. The evacuate script IS the product. "
                                "Over-routing costs a truck roll."))

EVAL_CASES = [
    {"input": "we smell gas in the basement by the water heater", "label": "gas_smell"},
    {"input": "strong rotten egg odor in the kitchen since this morning", "label": "gas_smell"},
    {"input": "there's a hissing sound at the tank regulator", "label": "gas_smell"},
    {"input": "propane smell outside near the line to the house", "label": "gas_smell"},
    {"input": "we're out of gas and the furnace quit last night", "label": "out_of_gas"},
    {"input": "the gauge reads zero and there's no heat", "label": "out_of_gas"},
    {"input": "tank's empty, we ran out sometime yesterday", "label": "out_of_gas"},
    {"input": "need a fill before the cold snap this weekend", "label": "delivery"},
    {"input": "gauge is at 20 percent, schedule us please", "label": "delivery"},
    {"input": "what's your price per gallon right now", "label": "price"},
    {"input": "what's my contract rate this season", "label": "price"},
    {"input": "", "label": "human"},
    {"input": "the driver was great, thanks", "label": "human"},
    {"input": "can you top off the tank when you're in the area", "label": "delivery"},
    {"input": "smelling propane in the crawl space", "label": "gas_smell"},
]


def run_eval():
    return triage_eval.run(EVAL_CASES, lambda t: read_call(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_call":           {"rung": "R3", "reason": "routing only; gas-smell-first is the point"},
    "dispatch_gas_smell":  {"rung": "R2", "reason": "the evacuate script and the truck cannot wait"},
    "troubleshoot_gas_smell": {"rung": "R0", "reason": "nothing about a gas smell is troubleshot by phone", "never_promote": True},
    "close_outage_without_leak_check": {"rung": "R0", "reason": "relighting without the test is how houses explode", "never_promote": True},
    "bill_contract_off_contract": {"rung": "R0", "reason": "the market price cannot reach a contract customer", "never_promote": True},
    "fill_unqualified_tank": {"rung": "R0", "reason": "an out-of-date vessel gets requalified, not filled", "never_promote": True},
    "draft_delivery":      {"rung": "R1", "reason": "a truck stop — a human routes it"},
    "draft_price_reply":   {"rung": "R1", "reason": "outward money figure — a human sends, from the recorded price"},
    "runout_alert":        {"rung": "R2", "reason": "an internal alert; the arithmetic is the point"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Fuel OS — what it computes to")
        .line("Runouts predicted and filled first", "revenue", "runouts avoided × emergency cost delta",
              ["runouts_avoided", "emergency_delta"],
              lambda g: float(g["runouts_avoided"]) * float(g["emergency_delta"]),
              assumption="avoided runouts are your history vs this season — argue with it")
        .line("Will-call converted to keep-full", "revenue", "conversions × avg annual gallons × margin",
              ["conversions", "annual_gallons", "margin_gal"],
              lambda g: float(g["conversions"]) * float(g["annual_gallons"]) * float(g["margin_gal"]))
        .line("Dispatch hours", "time_saved", "hrs/wk × 52 × rate",
              ["office_hours_wk", "office_rate"],
              lambda g: float(g["office_hours_wk"]) * 52 * float(g["office_rate"]))
        .line("The leak-check file", "scenario", "you decide what the recorded tests are worth",
              ["leakcheck_value"], lambda g: float(g["leakcheck_value"]),
              assumption="never a saving — a house that didn't explode is not our number to model"))


def roi(given):
    rec = {}
    board = runout_board()
    rec["critical_tanks"] = len([r for r in board if r.get("risk") == "critical"])
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("read_call", "dispatch_gas_smell", "draft_delivery", "draft_price_reply",
          "runout_alert")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("customer:",))
