#!/usr/bin/env python3
"""Hook OS — domain core (towing & recovery).

Rules live here: rotation-first call triage, the rate-card clamp (no invoice
can exceed the filed card by construction), storage arithmetic from recorded
timestamps, the damage-evidence pair, the abandoned-vehicle lien calendar as
DATE ALERTS, and the matrix.

Stdlib only. Honesty rules come from `_kit`.
"""
import math, re, sys
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent))

from _kit.moat import Eval, Gate, Matrix, Roi                       # noqa: E402
from _kit.store import (Store, automation_rate, iso, median, now,   # noqa: E402
                        parse, unmeasured)

TABLES = ("config", "calls", "tows", "impounds", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="HOOKOS_DATA_ROOT")

# ---------------------------------------------------------------- the rate card

DEFAULT_RATE_CARD = {
    "_source": ("DEFAULT rate card, simplified — replace with the company's FILED card per "
                "jurisdiction before go-live. Rates are capped by law in many states; the clamp "
                "below is the point."),
    "hookup": 125, "per_mile": 6, "storage_per_day": 45, "winch_hour": 185,
    "gate_fee_after_hours": 60,
}


def rate_card():
    return store.load("config").get("rate_card") or DEFAULT_RATE_CARD


def tow_invoice(tow):
    """Every invoice computes from the recorded card BY CONSTRUCTION — there is
    no argument to this function that can produce a number above it."""
    card = rate_card()
    lines = [{"item": "hookup", "amount": card["hookup"]}]
    miles = tow.get("miles")
    if miles is None:
        return unmeasured("no recorded mileage — the tow cannot be priced", field="total")
    lines.append({"item": f"mileage ({miles} mi)", "amount": round(miles * card["per_mile"], 2)})
    if tow.get("winch_hours"):
        lines.append({"item": f"winching ({tow['winch_hours']}h)",
                      "amount": round(tow["winch_hours"] * card["winch_hour"], 2)})
    if tow.get("after_hours_release"):
        lines.append({"item": "after-hours gate fee", "amount": card["gate_fee_after_hours"]})
    return {"lines": lines, "total": round(sum(l["amount"] for l in lines), 2),
            "basis": "computed from the filed rate card — no other number exists",
            "card_source": card["_source"]}


def storage_bill(imp, ref=None):
    """Storage = days from recorded impound stamp to recorded release stamp (or
    today). The meter starts and stops at the records."""
    ref = ref or now()
    start = parse(imp.get("impounded_at"))
    if not start:
        return unmeasured("no recorded impound timestamp — storage cannot be billed", field="days")
    end = parse(imp.get("released_at")) or ref
    days = max(1, math.ceil((end - start).total_seconds() / 86400))
    card = rate_card()
    return {"days": days, "per_day": card["storage_per_day"],
            "total": round(days * card["storage_per_day"], 2),
            "ends_at": "the recorded release" if imp.get("released_at") else "today (still held)"}


# ---------------------------------------------------------------- damage evidence

def damage_response(tow):
    """A 'your driver damaged it' dispute is answered by the hookup photo set
    or by 'cannot assert either way' — never by the dispatcher's confidence."""
    photos = tow.get("hookup_photos") or 0
    if photos < 2:
        return {"assertable": False,
                "refused": (f"cannot assert anything about pre-existing damage — only {photos} "
                            f"hookup photo(s) on file. Without the photo set the answer is a "
                            f"human conversation, not a denial.")}
    return {"assertable": True, "photos": photos,
            "note": "the photo set does the arguing — a human sends it with the reply"}


# ---------------------------------------------------------------- lien calendar

DEFAULT_LIEN_RULES = {
    "_source": ("DEFAULT rule set, simplified — replace with counsel-reviewed rules per state "
                "before go-live. Every date below is a DATE ALERT, not legal advice."),
    "TX": {"steps": [{"key": "owner_notice", "label": "owner/lienholder notice", "days_after_impound": 10},
                     {"key": "auction_eligible", "label": "earliest auction eligibility", "days_after_impound": 45}]},
    "GA": {"steps": [{"key": "owner_notice", "label": "owner/lienholder notice", "days_after_impound": 7},
                     {"key": "auction_eligible", "label": "earliest auction eligibility", "days_after_impound": 30}]},
}


def lien_rules():
    return store.load("config").get("lien_rules") or DEFAULT_LIEN_RULES


def lien_calendar(imp, ref=None):
    ref = ref or now()
    rules = lien_rules()
    state_rules = rules.get(imp.get("state_code") or "")
    if not state_rules:
        return unmeasured(f"no lien rule set for state {imp.get('state_code')!r}", field="steps")
    start = parse(imp.get("impounded_at"))
    if not start:
        return unmeasured("no recorded impound timestamp", field="steps")
    done = set(imp.get("steps_done") or [])
    steps = []
    for s in state_rules["steps"]:
        if s["key"] in done:
            continue
        due = start + timedelta(days=s["days_after_impound"])
        steps.append({"step": s["label"], "due": iso(due), "days_left": (due - ref).days,
                      "label": "DATE ALERT — not legal advice"})
    return {"steps": steps, "rules_source": rules["_source"]}


# ---------------------------------------------------------------- triage

ROTATION = (
    r"\brotation\b",
    r"\b(dispatch(ed)? (from|by)|pd|police|state patrol|sheriff|trooper)\b.*"
    r"\b(tow|wreck|accident|scene|call)\b",
    r"\b(this is|calling from) (dispatch|the county|city pd)\b",
)
BREAKDOWN = (
    r"\b(broke down|won'?t start|dead battery|flat tire|blew a tire|out of gas|stuck|"
    r"in a ditch|stranded)\b",
)
PRICE = (
    r"\b(how much|price|cost|rate|charge)\b.*\b(tow|mile|hook|storage|release|get (my|the))\b",
    r"\b(tow|storage)\b.*\b(how much|price|cost|rate)\b",
)
RELEASE = (
    r"\b(get|pick ?up|release|come get)\b.*\b(my|the) (car|truck|vehicle)\b",
    r"\bimpound(ed)?\b.*\b(my|the)\b|\bwhere('?s| is) my (car|truck)\b",
)


def read_call(text):
    """rotation | breakdown | price_question | release_request | human.
    Rotation reads first — that clock is measured in minutes."""
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty call — a person answers"}
    for rx in ROTATION:
        if re.search(rx, t):
            return {"label": "rotation",
                    "why": "police-rotation dispatch — the clock started at this call; recorded "
                           "at R2 and a truck rolls"}
    for rx in BREAKDOWN:
        if re.search(rx, t):
            return {"label": "breakdown", "why": "breakdown call — dispatch drafts with ETA"}
    for rx in PRICE:
        if re.search(rx, t):
            return {"label": "price_question",
                    "why": "price question — answered FROM the filed card, never around it"}
    for rx in RELEASE:
        if re.search(rx, t):
            return {"label": "release_request",
                    "why": "vehicle release — ID + payment recorded at the window; the storage "
                           "meter stops at the recorded release"}
    return {"label": "human", "why": "no clean signal — a person answers"}


def recovered_this_week(ref=None):
    """Counted: rotation calls answered, releases processed, storage billed."""
    ref = ref or now()
    rotations = sum(1 for e in store.events(kind="record_rotation_call")
                    if (ref - (parse(e.get("at")) or ref)).days <= 7)
    released = [i for i in store.load("impounds")
                if i.get("released_at") and (ref - (parse(i["released_at"]) or ref)).days <= 7]
    storage_total = 0.0
    for i in released:
        sb = storage_bill(i)
        if "total" in sb and sb.get("total"):
            storage_total += sb["total"]
    return {"rotation_calls": rotations, "vehicles_released": len(released),
            "storage_billed": round(storage_total, 2),
            "note": "counted from the event log and the impound records — never asserted"}


# ---------------------------------------------------------------- eval

triage_eval = Eval("call triage",
                   costly_label="rotation",
                   costly_note=("A MISSED ROTATION CALL IS A MISSED SLOT AND A DEMOTION ON THE "
                                "LIST — the clock is measured in minutes. Over-routing costs a "
                                "shrug."))

EVAL_CASES = [
    {"input": "this is county dispatch, rotation tow at mile marker 12", "label": "rotation"},
    {"input": "police on scene need a wrecker for a two-car accident", "label": "rotation"},
    {"input": "sheriff's office calling, we have a tow at the courthouse lot", "label": "rotation"},
    {"input": "car broke down on the shoulder of route 9", "label": "breakdown"},
    {"input": "I'm stuck in a ditch off the county road", "label": "breakdown"},
    {"input": "flat tire and the spare is flat too, stranded at the mall", "label": "breakdown"},
    {"input": "how much is a tow across town", "label": "price_question"},
    {"input": "what's your storage rate per day", "label": "price_question"},
    {"input": "you impounded my car last night, where is it", "label": "release_request"},
    {"input": "I need to come get my truck from your lot", "label": "release_request"},
    {"input": "", "label": "human"},
    {"input": "do you buy junk cars", "label": "human"},
    {"input": "trooper requesting rotation at the split", "label": "rotation"},
    {"input": "dead battery in the parking garage on level 3", "label": "breakdown"},
    {"input": "how much to release my vehicle", "label": "price_question"},
]


def run_eval():
    return triage_eval.run(EVAL_CASES, lambda t: read_call(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_call":            {"rung": "R3", "reason": "routing only; rotation-first is the point"},
    "record_rotation_call": {"rung": "R2", "reason": "the rotation clock starts at the record — delay is the demotion"},
    "charge_above_rate_card": {"rung": "R0", "reason": "no number above the filed card exists in this system", "never_promote": True},
    "assert_no_damage_without_photos": {"rung": "R0", "reason": "the photo pair argues, not the dispatcher", "never_promote": True},
    "file_lien":            {"rung": "R0", "reason": "the calendar alerts; counsel files", "never_promote": True},
    "sell_vehicle":         {"rung": "R0", "reason": "an auction is a human decision after the legal steps", "never_promote": True},
    "backdate_release":     {"rung": "R0", "reason": "the record is the record — the meter runs on stamps", "never_promote": True},
    "draft_dispatch":       {"rung": "R1", "reason": "a truck roll — a human dispatches"},
    "draft_invoice":        {"rung": "R1", "reason": "money — a human sends, computed from the card"},
    "process_release":      {"rung": "R1", "reason": "a release needs recorded ID + payment; a human hands over keys"},
    "lien_date_alert":      {"rung": "R2", "reason": "an internal date alert; the date is the point"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Hook OS — what it computes to")
        .line("Storage billed to the day", "revenue", "held vehicles × per-day (counted)",
              ["held_storage_value"], lambda g: float(g["held_storage_value"]),
              note="computed from recorded impound stamps and the filed card")
        .line("Rotation slots kept", "revenue", "rotation calls/mo × avg rotation ticket",
              ["rotation_calls_mo", "avg_rotation_ticket"],
              lambda g: float(g["rotation_calls_mo"]) * 12 * float(g["avg_rotation_ticket"]))
        .line("Dispatch/office hours", "time_saved", "hrs/wk × 52 × rate",
              ["office_hours_wk", "office_rate"],
              lambda g: float(g["office_hours_wk"]) * 52 * float(g["office_rate"]))
        .line("The rate-card defense file", "scenario", "you decide what a clean complaint record is worth",
              ["defense_value"], lambda g: float(g["defense_value"]),
              assumption="never a saving — the clamp is the product"))


def roi(given):
    rec = {}
    held = 0.0
    for i in store.load("impounds"):
        if i.get("released_at") or i.get("demo_tag"):
            continue
        sb = storage_bill(i)
        if sb.get("total"):
            held += sb["total"]
    rec["held_storage_value"] = round(held, 2)
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("read_call", "record_rotation_call", "draft_dispatch", "draft_invoice",
          "process_release", "lien_date_alert")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("caller:",))
