#!/usr/bin/env python3
"""Rebid OS — domain core (the graveyard re-bid desk for machine shops).

Rules live here: the graveyard record (every lost quote, with its loss reason
and the hours it would consume), counted idle capacity (booked vs available,
never estimated — an unmaintained week stands the desk down), the marginal
floor per machine class (recorded cost arithmetic that prints on every
re-bid), the bounded re-bid protocol, deadline answers from counted hours,
and the matrix.

Stdlib only. Honesty rules come from `_kit`.
"""
import re, sys
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent))

from _kit.moat import Eval, Gate, Matrix, Roi                       # noqa: E402
from _kit.store import (Store, automation_rate, iso, is_missing,    # noqa: E402
                        now, parse, unmeasured)

TABLES = ("config", "machines", "weeks", "bookings", "graveyard", "messages",
          "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="REBIDOS_DATA_ROOT")

REBID_COOLDOWN_DAYS = 90  # one re-bid per quote per quarter


# ---------------------------------------------------------------- weeks

def week_of(dt=None):
    d = (dt or now()).date()
    return (d - timedelta(days=d.weekday())).isoformat()


def this_week(ref=None):
    return week_of(ref)


def next_week(ref=None):
    return week_of((ref or now()) + timedelta(days=7))


# ---------------------------------------------------------------- counted idle capacity

def counted_idle(machine_class, wk):
    """available shift hours (recorded) − booked hours (recorded jobs) =
    counted idle. A week whose schedule wasn't maintained is UNMEASURED and
    the desk stands down — we don't sell hours we can't count."""
    row = next((w for w in store.load("weeks")
                if w.get("machine_class") == machine_class and w.get("week_of") == wk), None)
    if not row:
        return unmeasured(f"no schedule row for {machine_class} week of {wk} — capacity is "
                          f"unmeasured and the desk stands down; we don't sell hours we "
                          f"can't count", field="idle_hours")
    if not row.get("maintained"):
        return unmeasured(f"the {machine_class} schedule for week of {wk} was not maintained — "
                          f"capacity is unmeasured and the desk stands down; we don't sell "
                          f"hours we can't count", field="idle_hours")
    avail = row.get("available_shift_hours")
    if avail is None:
        return unmeasured(f"no recorded shift hours for {machine_class} week of {wk}",
                          field="idle_hours")
    booked = round(sum(b.get("hours") or 0 for b in store.load("bookings")
                       if b.get("machine_class") == machine_class and b.get("week_of") == wk), 2)
    idle = round(avail - booked, 2)
    return {"idle_hours": idle, "available": avail, "booked": booked,
            "machine_class": machine_class, "week_of": wk,
            "basis": f"{avail:g}h available shifts − {booked:g}h booked = {idle:g}h counted idle"}


def reserved_hours(machine_class, wk):
    """Hours already spoken for by PENDING re-bid drafts. Two re-bids can't
    sell the same counted idle hour."""
    held = 0.0
    for a in store.load("approvals"):
        if a.get("state") == "pending" and a.get("action") == "draft_rebid":
            d = a.get("detail") or {}
            if d.get("machine_class") == machine_class and d.get("week_of") == wk:
                held += d.get("hours") or 0
    return round(held, 2)


def capacity_board(ref=None):
    cfg = store.load("config")
    classes = sorted((cfg.get("variable_cost_hr") or {}).keys())
    machines = store.load("machines")
    rows = []
    for mc in classes:
        n = sum(1 for m in machines if m.get("machine_class") == mc)
        for wk in (this_week(ref), next_week(ref)):
            idle = counted_idle(mc, wk)
            row = {"machine_class": mc, "week_of": wk, "machines": n}
            if is_missing(idle):
                row["idle"] = idle
            else:
                row.update(idle)
                row["held_hours"] = reserved_hours(mc, wk)
            rows.append(row)
    return {"rows": rows,
            "note": "counted from the recorded schedule — booked jobs vs available shifts, "
                    "never estimated; a drafted re-bid holds its hours until a human decides"}


# ---------------------------------------------------------------- the marginal floor

def floor_math(q):
    """Per machine class: recorded variable cost/hr × hours + material +
    the recorded minimum-margin line = the floor. The arithmetic prints on
    every re-bid; a bid below the floor has NO PATH."""
    cfg = store.load("config")
    if q.get("hours") in (None, ""):
        return {"refused": (f"UNREBIDDABLE — no recorded machine-hours on {q.get('part', '?')!r}: "
                            f"no hours, no marginal math. Record the hours and it becomes a "
                            f"standing order like the rest.")}
    rate = (cfg.get("variable_cost_hr") or {}).get(q.get("machine_class"))
    if rate is None:
        return {"refused": (f"no recorded variable cost/hr for machine class "
                            f"{q.get('machine_class')!r} — the floor computes from recorded "
                            f"cost, never a guess")}
    if q.get("material_cost") in (None, ""):
        return {"refused": (f"no recorded material cost on {q.get('part', '?')!r} — the floor "
                            f"computes from recorded cost, never a guess")}
    min_margin = cfg.get("min_margin")
    if min_margin is None:
        return {"refused": "no recorded minimum margin — the floor is recorded cost plus the "
                           "margin line you set, and you haven't set it"}
    labor = round(float(q["hours"]) * rate, 2)
    material = round(float(q["material_cost"]), 2)
    margin_line = round((labor + material) * min_margin, 2)
    floor_price = round(labor + material + margin_line, 2)
    return {"labor": labor, "material": material, "margin_line": margin_line,
            "floor_price": floor_price,
            "arithmetic": (f"{q['hours']:g}h × ${rate:g}/hr = ${labor:,.2f} labor + "
                           f"${material:,.2f} material + {min_margin:.0%} margin line "
                           f"${margin_line:,.2f} = ${floor_price:,.2f} floor"),
            "note": "the recorded arithmetic — this prints on every re-bid"}


def defensible_price(q):
    """The floor's cost base at the recorded TARGET margin — the price the
    shop can defend out loud. Never below the floor, by construction."""
    f = floor_math(q)
    if "refused" in f:
        return f
    tm = store.load("config").get("target_margin")
    if tm is None:
        return {"refused": "no recorded target margin — a defensible price is the floor's cost "
                           "base at the margin you set, and you haven't set it"}
    price = round((f["labor"] + f["material"]) * (1 + tm), 2)
    if price < f["floor_price"]:
        price = f["floor_price"]
    return {"price": price, "target_margin": tm, "floor": f}


# ---------------------------------------------------------------- the graveyard

def quote_status(q, ref=None):
    ref = ref or now()
    if q.get("loss_reason") == "capability":
        return "retired — capability (the machine didn't change)"
    if q.get("hours") in (None, ""):
        return "UNREBIDDABLE — no recorded hours"
    if any(h.get("response") == "silence" for h in (q.get("rebid_history") or [])):
        return "retired — silence answered"
    last = parse(q.get("last_rebid_at"))
    if last and (ref - last).days < REBID_COOLDOWN_DAYS:
        return f"cooldown — re-bid {(ref - last).days}d ago (quarter rule)"
    return "standing order — watching counted idle"


def graveyard_board(ref=None):
    rows = store.load("graveyard")
    reasons = {}
    watching = unrebiddable = retired = 0
    for q in rows:
        reasons[q.get("loss_reason") or "?"] = reasons.get(q.get("loss_reason") or "?", 0) + 1
        s = quote_status(q, ref)
        if s.startswith("standing order"):
            watching += 1
        elif s.startswith("UNREBIDDABLE"):
            unrebiddable += 1
        elif s.startswith("retired"):
            retired += 1
    return {"count": len(rows), "by_reason": reasons, "watching": watching,
            "unrebiddable": unrebiddable, "retired": retired,
            "died_at_value": round(sum(q.get("died_at_price") or 0 for q in rows), 2),
            "note": "every lost quote is a standing order against counted idle — except the "
                    "ones that honestly aren't, and each of those names why"}


# ---------------------------------------------------------------- the standing order

def rebid_check(q, ref=None):
    """Should this graveyard quote re-bid itself right now? Returns either
    {"go": True, ...} with the week, price and floor, or {"go": False,
    "kind": ..., "why": ...}. The bounds are the product: capability never
    re-bids, silence is an answer, one re-bid per quarter, and nothing sells
    an hour that wasn't counted or is already held by a pending draft."""
    ref = ref or now()
    if q.get("loss_reason") == "capability":
        return {"go": False, "kind": "capability",
                "why": "lost on capability — the machine didn't change, so the bid doesn't "
                       "either; this quote never re-bids"}
    f = floor_math(q)
    if "refused" in f:
        return {"go": False, "kind": "unrebiddable", "why": f["refused"]}
    if any(h.get("response") == "silence" for h in (q.get("rebid_history") or [])):
        return {"go": False, "kind": "silence",
                "why": "a prior re-bid drew silence — silence is an answer; this door was "
                       "knocked once and stays shut"}
    last = parse(q.get("last_rebid_at"))
    if last and (ref - last).days < REBID_COOLDOWN_DAYS:
        return {"go": False, "kind": "cooldown",
                "why": f"re-bid {(ref - last).days} days ago — one re-bid per quote per "
                       f"quarter ({REBID_COOLDOWN_DAYS}-day cooldown)"}
    d = defensible_price(q)
    if "refused" in d:
        return {"go": False, "kind": "unrebiddable", "why": d["refused"]}
    died = q.get("died_at_price")
    if died and d["price"] > died:
        return {"go": False, "kind": "not_defensible",
                "why": (f"the defensible price ${d['price']:,.2f} sits above the "
                        f"${died:,.2f} this quote died at — re-bidding higher than the price "
                        f"that already lost is not a story we can tell")}
    mc, hours = q["machine_class"], float(q["hours"])
    measured, tried = [], []
    for wk in (this_week(ref), next_week(ref)):
        idle = counted_idle(mc, wk)
        if is_missing(idle):
            continue
        measured.append(idle)
    if not measured:
        return {"go": False, "kind": "stand_down",
                "why": counted_idle(mc, this_week(ref))["_missing"]}
    for idle in measured:
        held = reserved_hours(mc, idle["week_of"])
        free = round(idle["idle_hours"] - held, 2)
        tried.append(f"{free:g}h free of {idle['idle_hours']:g}h counted wk {idle['week_of']}"
                     + (f" ({held:g}h held by pending drafts)" if held else ""))
        if free >= hours:
            return {"go": True, "week_of": idle["week_of"], "idle": idle,
                    "held_hours": held, "free_hours": free, "price": d["price"],
                    "target_margin": d["target_margin"], "floor": d["floor"]}
    return {"go": False, "kind": "no_idle",
            "why": (f"needs {hours:g}h and the counted idle can't hold it — "
                    + "; ".join(tried) + ". The standing order keeps watching.")}


# ---------------------------------------------------------------- intake triage

DEADLINE = (
    r"\bneed \d+\b.*\bby (mon|tues|wednes|thurs|fri|satur|sun)day\b",
    r"\bneed \d+\b.*\b(this|next) week\b",
    r"\bcan you (turn|do|make|run|hit|deliver)\b.*\b(by|before)\b",
    r"\b\d+ (pcs|pieces|parts|units)\b.*\b(by|before) \w+day\b",
    r"\brush\b.*\b(quote|order|job|parts)\b",
)
REBID_REPLY = (
    r"\b(re-?bid|requote)\b",
    r"\b(new|revised|updated) (price|quote|bid|number)\b",
)
QUOTE_STATUS = (
    r"\b(status|update|word) (of|on) (the|my|our) (quote|rfq|bid)\b",
    r"\bdid you (get|receive) (my|our|the) rfq\b",
    r"\bwhere (is|are) (the|my|our) quote",
)
SPEC_CHANGE = (
    r"\brev(ision)? [a-z]\b",
    r"\b(changed|updated|new) (the )?(drawing|material|tolerance|spec|print|model)\b",
    r"\btolerances? (changed|tightened|loosened)\b",
)


def read_message(text):
    """deadline_rfq | rebid_reply | quote_status | spec_change | human.
    The deadline RFQ reads first — it is answered from COUNTED capacity,
    never optimism, and missing it is the order lost."""
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty message — a person reads it"}
    for rx in DEADLINE:
        if re.search(rx, t):
            return {"label": "deadline_rfq",
                    "why": "a deadline RFQ — the yes/no computes from counted idle hours; "
                           "an optimistic yes is a broken promise scheduled early"}
    for rx in REBID_REPLY:
        if re.search(rx, t):
            return {"label": "rebid_reply",
                    "why": "a reply to a re-bid — a live buyer on a resurrected quote goes "
                           "to a human fast"}
    for rx in QUOTE_STATUS:
        if re.search(rx, t):
            return {"label": "quote_status", "why": "quote status — answered from the record"}
    for rx in SPEC_CHANGE:
        if re.search(rx, t):
            return {"label": "spec_change",
                    "why": "a spec change voids the recorded hours — the estimator "
                           "re-records before any number moves"}
    return {"label": "human", "why": "no clean signal — a person reads it"}


# ---------------------------------------------------------------- counted week

def this_week_counted(ref=None):
    """Counted, never asserted: re-bids a human sent, deadline answers a human
    committed, and losses recorded into the graveyard, inside 7 days."""
    ref = ref or now()
    rebids = answers = losses = 0
    for e in store.events():
        at = parse(e.get("at"))
        if not at or (ref - at).days > 7:
            continue
        actor = str(e.get("actor", ""))
        if e["kind"] == "draft_rebid" and actor.startswith("human:"):
            rebids += 1
        elif e["kind"] == "answer_deadline_rfq" and actor.startswith("human:"):
            answers += 1
        elif e["kind"] == "record_loss":
            losses += 1
    return {"rebids_sent": rebids, "deadline_answers_sent": answers,
            "losses_recorded": losses,
            "note": "counted from the event log — never asserted"}


# ---------------------------------------------------------------- eval

triage_eval = Eval("intake triage",
                   costly_label="deadline_rfq",
                   costly_note=("THE DEADLINE RFQ MISSED IS THE ORDER LOST — AND ANSWERED WITH "
                                "OPTIMISM IT IS WORSE: A PROMISE THE SCHEDULE CANNOT KEEP. "
                                "Answers cite counted idle hours only. Over-routing costs a read."))

EVAL_CASES = [
    {"input": "need 200 of the clamp plates by friday, can you?", "label": "deadline_rfq"},
    {"input": "can you turn 50 shafts by thursday", "label": "deadline_rfq"},
    {"input": "rush order — 80 parts, is it possible this week", "label": "deadline_rfq"},
    {"input": "need 500 spacers by monday morning", "label": "deadline_rfq"},
    {"input": "120 pcs by wednesday — doable?", "label": "deadline_rfq"},
    {"input": "got your requote on the manifold blocks, let's talk", "label": "rebid_reply"},
    {"input": "saw the new price on the brackets — send the PO terms", "label": "rebid_reply"},
    {"input": "any word on the quote for the housings?", "label": "quote_status"},
    {"input": "did you get my rfq from last tuesday", "label": "quote_status"},
    {"input": "we changed the material to 17-4 on the pump housing", "label": "spec_change"},
    {"input": "rev c drawing attached, tolerances tightened on the bore", "label": "spec_change"},
    {"input": "", "label": "human"},
    {"input": "what are your shop hours over the holiday", "label": "human"},
    {"input": "thanks for the tour last week", "label": "human"},
    {"input": "invoice 4471 shows the wrong PO number", "label": "human"},
]


def run_eval():
    return triage_eval.run(EVAL_CASES, lambda t: read_message(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_message":        {"rung": "R3", "reason": "routing only; the deadline RFQ reads first"},
    "record_loss":         {"rung": "R2", "reason": "internal record — a lost quote unrecorded is a standing order that never exists"},
    "record_booking":      {"rung": "R2", "reason": "internal schedule bookkeeping — the counted board is only as good as its records"},
    "bid_below_marginal_floor": {"rung": "R0", "reason": "below the recorded floor there is NO PATH — structural: the floor's arithmetic prints on every re-bid, and no click reaches under it", "never_promote": True},
    "sell_uncounted_capacity": {"rung": "R0", "reason": "a week whose schedule wasn't maintained has unmeasured capacity — the desk stands down; we don't sell hours we can't count", "never_promote": True},
    "rebid_capability_loss": {"rung": "R0", "reason": "the machine didn't change, so the bid doesn't either — a capability loss never re-bids", "never_promote": True},
    "promise_capacity_optimism": {"rung": "R0", "reason": "deadline answers cite counted idle hours or nothing — optimism is a broken promise scheduled early", "never_promote": True},
    "draft_rebid":         {"rung": "R1", "reason": "outward + money — a human sends, with the floor's arithmetic attached"},
    "answer_deadline_rfq": {"rung": "R1", "reason": "an outward promise — a human sends; the yes/no computes from counted idle hours"},
    "draft_rebid_reply":   {"rung": "R1", "reason": "outward reply — a live buyer on a resurrected quote, a human closes"},
    "draft_status_reply":  {"rung": "R1", "reason": "outward reply — answered from the quote record"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Rebid OS — what it computes to")
        .line("Graveyard revenue recovered", "revenue",
              "re-bids won/yr × avg re-bid price × recorded target margin",
              ["rebids_won_yr", "avg_rebid_price", "target_margin"],
              lambda g: float(g["rebids_won_yr"]) * float(g["avg_rebid_price"])
                        * float(g["target_margin"]),
              note="the margin is recorded; wins are counted as they land — until then the "
                   "win count is your number, not ours")
        .line("Idle hours absorbed", "revenue",
              "idle hours sold/yr × (avg price/hr − recorded variable cost/hr)",
              ["idle_hours_sold_yr", "avg_price_hr", "avg_variable_cost_hr"],
              lambda g: float(g["idle_hours_sold_yr"])
                        * (float(g["avg_price_hr"]) - float(g["avg_variable_cost_hr"])),
              note="contribution above the marginal floor — the whole point of selling "
                   "counted idle")
        .line("Quoting and chase hours", "time_saved", "re-bid hrs/wk × 52 × estimator rate",
              ["rebid_hours_wk", "estimator_rate"],
              lambda g: float(g["rebid_hours_wk"]) * 52 * float(g["estimator_rate"]))
        .line("The defensible-price story", "scenario",
              "you decide what never racing to the bottom is worth",
              ["price_integrity_value"], lambda g: float(g["price_integrity_value"]),
              assumption="never a saving — a price war that didn't start is not our number"))


def roi(given):
    cfg = store.load("config")
    rec = {}
    if cfg.get("target_margin") is not None:
        rec["target_margin"] = cfg["target_margin"]
    rates = list((cfg.get("variable_cost_hr") or {}).values())
    if rates:
        rec["avg_variable_cost_hr"] = round(sum(rates) / len(rates), 2)
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("read_message", "draft_rebid", "answer_deadline_rfq", "draft_rebid_reply",
          "draft_status_reply", "record_loss")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("buyer:", "customer:"))
