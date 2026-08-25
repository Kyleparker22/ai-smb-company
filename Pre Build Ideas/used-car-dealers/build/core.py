#!/usr/bin/env python3
"""Lot OS — domain core (independent used-car dealer).

Rules live here: lead-first triage (speed IS the business), the condition rule
(only the recorded history talks), payment discipline (recorded lender terms or
a finance conversation), the title delivery gate, the aged-inventory board, and
the matrix.

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

TABLES = ("config", "units", "leads", "deals", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="LOTOS_DATA_ROOT")

# ---------------------------------------------------------------- triage

LEAD = (
    r"\b(is|still) (the|this|that|it)\b.*\bavailable\b|\bavailable\b.*\b(civic|f-?150|camry|"
    r"truck|suv|car)\b",
    r"\b(interested in|asking about|saw|looking at)\b.*\b(the|your)\b.*"
    r"\b(listing|civic|f-?150|camry|altima|silverado|truck|car|suv)\b",
    r"\bcome (see|look at|test drive)\b|\btest ?drive\b",
)
PAYMENT_ASK = (
    r"\b(monthly|payments?|finance|apr|down payment|per month|a month)\b",
)
TRADE_ASK = (
    r"\b(trade|trade-?in)\b.*\b(worth|value|give me|offer)\b",
    r"\bwhat('?s| is| would) my\b.*\b(worth|value)\b",
    r"\bwhat (would|will) you (give|offer|pay)\b|\b(give|offer|pay) (me )?for my\b",
)
CONDITION_ASK = (
    r"\b(accident|wreck|clean title|carfax|history|frame|flood|rust|mechanical)\b",
)


def read_message(text):
    """lead | payment_ask | trade_ask | condition_ask | human. The lead reads
    first — speed to lead IS the business."""
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty message — a person reads it"}
    for rx in LEAD:
        if re.search(rx, t):
            return {"label": "lead",
                    "why": "a live lead — acknowledged in minutes with drafted copy; the aging "
                           "lead escalates to a phone call"}
    for rx in CONDITION_ASK:
        if re.search(rx, t):
            return {"label": "condition_ask",
                    "why": "a condition/history question — only the recorded report talks, cited "
                           "by date; 'never wrecked' is not expressible"}
    for rx in TRADE_ASK:
        if re.search(rx, t):
            return {"label": "trade_ask",
                    "why": "a trade-in value question — a band from the recorded book or refused"}
    for rx in PAYMENT_ASK:
        if re.search(rx, t):
            return {"label": "payment_ask",
                    "why": "a payment question — figures draft only from recorded lender terms "
                           "with the disclosure attached; otherwise a finance conversation"}
    return {"label": "human", "why": "no clean signal — a person reads it"}


# ---------------------------------------------------------------- the condition rule

def condition_statement(unit):
    """What outward copy may say about a unit: ONLY what the recorded history
    contains, citing the report and date. Anything beyond it is refused."""
    rep = unit.get("history_report")
    if not rep:
        return {"refused": ("no recorded history report on this unit — outward copy about its "
                            "condition cannot exist. Get the report, or the copy stays silent.")}
    return {"statement": (f"Per the recorded {rep['source']} report dated {rep['date'][:10]}: "
                          f"{rep['summary']}"),
            "note": "the record talks; nobody else does. 'Never wrecked' is not expressible."}


# ---------------------------------------------------------------- payment discipline

def payment_quote(deal):
    """Payment figures draft only from recorded lender terms; the disclosure
    line rides along. No terms → the finance conversation, never a number."""
    t = deal.get("lender_terms")
    if not t or not all(k in t for k in ("apr", "months", "amount")):
        return {"refused": ("no recorded lender terms on this deal — a payment number without "
                            "them is an unlicensed finance quote. The reply invites the finance "
                            "conversation instead.")}
    r = t["apr"] / 100 / 12
    n = t["months"]
    p = t["amount"] * (r * (1 + r) ** n) / ((1 + r) ** n - 1) if r else t["amount"] / n
    return {"monthly": round(p, 2), "terms": t,
            "disclosure": (f"Estimated payment based on {t['apr']}% APR for {t['months']} months "
                           f"on ${t['amount']:,.0f} financed, on approved credit through the "
                           f"recorded lender. Taxes and fees additional."),
            "note": "drafted from the recorded terms; the disclosure is part of the copy"}


# ---------------------------------------------------------------- the title gate

def can_deliver(deal):
    if deal.get("title_status") in ("in_hand", "lien_release_recorded"):
        return True, f"title status recorded: {deal['title_status']}"
    return False, (f"cannot mark delivered — title status is "
                   f"{deal.get('title_status') or 'unrecorded'}. A delivered car with an unsolved "
                   f"title is the complaint that brings the state in.")


# ---------------------------------------------------------------- trade band

def trade_band(model_key):
    """A band from the dealer's own recorded book — below 4 comparable records
    we refuse."""
    book = store.load("config").get("trade_book") or {}
    rows = book.get(model_key) or []
    if len(rows) < 4:
        return unmeasured(f"only {len(rows)} recorded {model_key!r} purchases in the book — need "
                          f"4 to state a band; a guess costs real money on both sides",
                          field="band", n=len(rows))
    s = sorted(rows)
    return {"band": [s[len(s) // 4], s[(3 * len(s)) // 4]], "n": len(rows),
            "basis": "middle half of our own recorded purchases — the exact number needs eyes on the car"}


# ---------------------------------------------------------------- lead ladder + aging

LEAD_MAX_TOUCHES = 3
LEAD_COOLDOWN_HOURS = 20


def lead_plan(lead, ref=None):
    ref = ref or now()
    if lead.get("sold_at") or lead.get("dead_at") or lead.get("demo_tag"):
        return {"action": "none", "why": "closed"}
    touches = lead.get("touches") or []
    if len(touches) >= LEAD_MAX_TOUCHES:
        return {"action": "call", "why": f"ladder exhausted at {LEAD_MAX_TOUCHES} — a salesperson calls"}
    if touches:
        last = parse(touches[-1]["at"])
        if last and (ref - last).total_seconds() < LEAD_COOLDOWN_HOURS * 3600:
            return {"action": "none", "why": f"inside the {LEAD_COOLDOWN_HOURS}-hour cooldown"}
    return {"action": "draft_touch", "why": f"touch {len(touches)+1} of {LEAD_MAX_TOUCHES}"}


def aged_board(ref=None):
    """Floorplan days × the dealer's recorded daily cost, per unit — counted."""
    ref = ref or now()
    cfg = store.load("config")
    daily = cfg.get("floorplan_daily_cost")
    rows = []
    for u in store.load("units"):
        if u.get("sold_at") or u.get("demo_tag"):
            continue
        acquired = parse(u.get("acquired_at"))
        if not acquired:
            rows.append({"unit": u["id"], "desc": u.get("desc"),
                         **unmeasured("no acquisition date — age unknowable", field="days")})
            continue
        days = (ref - acquired).days
        row = {"unit": u["id"], "desc": u.get("desc"), "days": days,
               "bucket": "90+" if days >= 90 else "60+" if days >= 60 else "30+" if days >= 30 else "fresh"}
        if daily:
            row["interest_accrued"] = round(days * daily, 2)
        else:
            row["interest_note"] = "no recorded floorplan cost — dollars unknowable, not invented"
        rows.append(row)
    rows.sort(key=lambda r: -(r.get("days") or 0))
    return rows


def recovered_this_week(ref=None):
    """Counted: leads answered inside the hour, units sold, deals delivered."""
    ref = ref or now()
    answered = 0
    for l in store.load("leads"):
        touches = l.get("touches") or []
        first_at = parse(touches[0]["at"]) if touches else None
        came = parse(l.get("at"))
        if first_at and came and (first_at - came).total_seconds() <= 3600 \
           and (ref - came).days <= 7:
            answered += 1
    sold = [u for u in store.load("units")
            if u.get("sold_at") and (ref - (parse(u["sold_at"]) or ref)).days <= 7]
    delivered = [d for d in store.load("deals")
                 if d.get("delivered_at") and (ref - (parse(d["delivered_at"]) or ref)).days <= 7]
    return {"leads_answered_in_hour": answered, "units_sold": len(sold),
            "deals_delivered": len(delivered),
            "note": "counted from the lead and deal records — never asserted"}


# ---------------------------------------------------------------- eval

triage_eval = Eval("message triage",
                   costly_label="lead",
                   costly_note=("A LEAD THAT SITS AN HOUR IS A LEAD BUYING SOMEWHERE ELSE — "
                                "speed to lead IS this business. Over-routing costs a read."))

EVAL_CASES = [
    {"input": "is the blue civic still available", "label": "lead"},
    {"input": "saw your listing for the f-150, interested", "label": "lead"},
    {"input": "can we come test drive the camry saturday", "label": "lead"},
    {"input": "looking at the silverado on your site", "label": "lead"},
    {"input": "what would payments be with 2k down", "label": "payment_ask"},
    {"input": "what's the apr you can get me", "label": "payment_ask"},
    {"input": "what's my 2018 accord worth on trade", "label": "trade_ask"},
    {"input": "what would you give me for my truck", "label": "trade_ask"},
    {"input": "has the altima been in an accident", "label": "condition_ask"},
    {"input": "is it a clean title? any frame damage?", "label": "condition_ask"},
    {"input": "", "label": "human"},
    {"input": "what time do you close today", "label": "human"},
    {"input": "still available? the white suv", "label": "lead"},
    {"input": "does the carfax show anything on the wrangler", "label": "condition_ask"},
    {"input": "how much a month would the tahoe run me", "label": "payment_ask"},
]


def run_eval():
    return triage_eval.run(EVAL_CASES, lambda t: read_message(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_message":       {"rung": "R3", "reason": "routing only; the lead-first read is the point"},
    "assert_condition_beyond_record": {"rung": "R0", "reason": "only the recorded report talks — 'never wrecked' is not expressible", "never_promote": True},
    "quote_payment_without_terms": {"rung": "R0", "reason": "a payment without recorded lender terms is an unlicensed finance quote", "never_promote": True},
    "deliver_without_title_status": {"rung": "R0", "reason": "a delivered car with an unsolved title brings the state in", "never_promote": True},
    "guess_trade_value":  {"rung": "R0", "reason": "a band from the recorded book or nothing", "never_promote": True},
    "draft_lead_reply":   {"rung": "R1", "reason": "outward reply — a human sends, in minutes"},
    "draft_payment_reply": {"rung": "R1", "reason": "outward money figure — a human sends, disclosure attached"},
    "draft_condition_reply": {"rung": "R1", "reason": "outward reply — the record cited, a human sends"},
    "mark_delivered":     {"rung": "R1", "reason": "a delivery is a title event — a human marks, past the gate"},
    "aging_alert":        {"rung": "R2", "reason": "an internal floorplan alert; the arithmetic is the point"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Lot OS — what it computes to")
        .line("Leads answered inside the hour", "revenue", "leads/mo × close lift × avg gross",
              ["leads_mo", "close_lift", "avg_gross"],
              lambda g: float(g["leads_mo"]) * 12 * float(g["close_lift"]) * float(g["avg_gross"]),
              assumption="the close lift from speed is your estimate — we count the speed, you price it")
        .line("Floorplan interest on aged units", "cash_timing", "counted from your recorded daily cost",
              ["aged_interest"], lambda g: float(g["aged_interest"]),
              note="counted per unit from acquisition dates and your recorded rate")
        .line("Desk hours", "time_saved", "hrs/wk × 52 × rate",
              ["desk_hours_wk", "desk_rate"],
              lambda g: float(g["desk_hours_wk"]) * 52 * float(g["desk_rate"]))
        .line("The compliance file", "scenario", "you decide what the disclosure discipline is worth",
              ["compliance_value"], lambda g: float(g["compliance_value"]),
              assumption="never a saving — the condition and payment rules are the product"))


def roi(given):
    rec = {}
    rec["aged_interest"] = round(sum(r.get("interest_accrued", 0) for r in aged_board()), 2)
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("read_message", "draft_lead_reply", "draft_payment_reply",
          "draft_condition_reply", "mark_delivered", "aging_alert")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("buyer:",))
