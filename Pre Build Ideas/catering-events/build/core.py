#!/usr/bin/env python3
"""Plate OS — domain core (catering & events).

Rules live here: the BEO lock window, the calendar conflict refusal, the
final-count billing clamp, allergen-first message triage, and the matrix.

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

TABLES = ("config", "spaces", "bookings", "messages", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="PLATEOS_DATA_ROOT")

BEO_LOCK_HOURS = 72

# ---------------------------------------------------------------- triage

ALLERGEN = (
    r"\b(allerg(y|ic|ies|en)|anaphyla|epipen|celiac|gluten.?free\b.*\bmedical|"
    r"severe(ly)? allergic)\b",
    r"\b(nut|peanut|shellfish|dairy|sesame)\b.*\b(allerg|reaction|can'?t have|medical)\b",
)
CHANGE = (r"\b(change|swap|add|remove|switch|update|bump|upgrade|downgrade)\b.*"
          r"\b(menu|entree|appetizer|beo|count|guests?|vegetarian|dessert|bar|package|reception)\b|"
          r"\bfinal count\b.*\b(is|will be|now)\b",
          r"\b(vegan|vegetarian|kosher|halal)s?\b.*\b(rsvp|menu|added|joining|need)\b",)
INQUIRY = (r"\b(available|availability|quote|pricing|book|host|wedding|rehearsal|corporate|"
           r"holiday party|gala|pavilion|barn)\b.*"
           r"\b(date|january|february|march|april|may|june|july|august|september|october|"
           r"november|december|spring|summer|fall|winter|\d+ (people|guests?|persons?)|"
           r"\d+ person)\b|"
           r"\bdo you (cater|do)\b",)


def read_message(text):
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty message — a person reads it"}
    for rx in ALLERGEN:
        if re.search(rx, t):
            return {"label": "allergen",
                    "why": "allergen/dietary-medical note — a trained human handles this; the "
                           "wrong reassurance is an ambulance at the reception"}
    for rx in CHANGE:
        if re.search(rx, t):
            return {"label": "change_request",
                    "why": "an event change — routed to BEO control with the lock window checked"}
    for rx in INQUIRY:
        if re.search(rx, t):
            return {"label": "inquiry", "why": "new inquiry — availability from the calendar, draft at R1"}
    return {"label": "human", "why": "no clean signal — a person reads it"}


# ---------------------------------------------------------------- BEO change control

def change_check(event, ref=None):
    """Outside the lock window → drafts normally. Inside → never auto-applied;
    a human confirms with the kitchen impact named."""
    ref = ref or now()
    when = parse(event.get("date"))
    if not when:
        return {"locked": None, "refused": "no event date recorded — nothing can be changed safely"}
    hours = (when - ref).total_seconds() / 3600
    if hours < 0:
        return {"locked": True, "refused": "the event has already happened — changes are history, not edits"}
    if hours <= BEO_LOCK_HOURS:
        return {"locked": True, "hours_to_event": round(hours, 1),
                "refused": f"inside the {BEO_LOCK_HOURS}h lock window ({hours:.0f}h to event) — "
                           f"the kitchen has ordered and prepped; a human confirms this change "
                           f"with the kitchen impact named, it is never auto-applied"}
    return {"locked": False, "hours_to_event": round(hours, 1),
            "note": f"outside the lock window — a change drafts at R1"}


# ---------------------------------------------------------------- the calendar

def can_book(space_id, date_iso, guests=None, exclude_event=None):
    """A space already booked that date is refused. Capacity overruns refuse
    with the number."""
    space = store.by_id("spaces", space_id)
    if not space:
        return False, "no such space"
    day = (date_iso or "")[:10]
    for e in store.load("bookings"):
        if e.get("space_id") == space_id and (e.get("date") or "")[:10] == day \
                and e["id"] != exclude_event and not e.get("cancelled_at"):
            return False, (f"{space['name']} is already booked on {day} ({e.get('name','event')}) "
                           f"— two parties arriving at one door is not a scheduling style")
    if guests and space.get("capacity") and guests > space["capacity"]:
        return False, f"{guests} guests over {space['name']}'s capacity of {space['capacity']}"
    return True, "clear — booking drafts at R1"


# ---------------------------------------------------------------- final-count billing

def invoice(event):
    """The bill = guaranteed final count × per-head + recorded additions — by
    construction. No recorded final count → nothing can be billed."""
    fc = event.get("final_count")
    rate = event.get("per_head")
    if not fc:
        return unmeasured("no guaranteed final count recorded — nothing can be billed against a "
                          "verbal number", field="total")
    if not rate:
        return unmeasured("no per-head rate on the event", field="total")
    adds = [a for a in (event.get("additions") or []) if a.get("recorded_at")]
    unrecorded = [a for a in (event.get("additions") or []) if not a.get("recorded_at")]
    total = fc * rate + sum(a.get("amount", 0) for a in adds)
    out = {"total": round(total, 2), "final_count": fc, "per_head": rate,
           "additions": [{"desc": a.get("desc"), "amount": a.get("amount")} for a in adds],
           "basis": "guaranteed count × per-head + recorded additions — nothing else exists"}
    if unrecorded:
        out["excluded"] = [{"desc": a.get("desc"), "amount": a.get("amount"),
                            "why": "not recorded before the event — a remembered addition is a "
                                   "dispute, not a charge"} for a in unrecorded]
    return out


def recovered_this_week(ref=None):
    """Counted, never asserted: BEO changes a human confirmed, bookings a human
    made, and availability replies sent, inside 7 days."""
    ref = ref or now()
    changes = booked = replies = 0
    for e in store.events():
        at = parse(e.get("at"))
        if not at or (ref - at).days > 7 or not str(e.get("actor", "")).startswith("human:"):
            continue
        if e["kind"] == "draft_beo_change":
            changes += 1
        elif e["kind"] == "draft_booking":
            booked += 1
        elif e["kind"] == "draft_availability_reply":
            replies += 1
    return {"changes_confirmed": changes, "bookings_made": booked, "replies_sent": replies,
            "note": "counted from the event log — never asserted"}


# ---------------------------------------------------------------- eval

triage_eval = Eval("message triage",
                   costly_label="allergen",
                   costly_note=("AN ALLERGEN NOTE ANSWERED CASUALLY IS AN AMBULANCE AT THE "
                                "RECEPTION. Routing a menu question costs a coordinator a minute."))

EVAL_CASES = [
    {"input": "one guest has a severe nut allergy, what can she eat", "label": "allergen"},
    {"input": "my mother is celiac, is the pasta station safe medically", "label": "allergen"},
    {"input": "a groomsman is severely allergic to shellfish, he carries an epipen", "label": "allergen"},
    {"input": "can we swap the salmon entree for chicken", "label": "change_request"},
    {"input": "final count is now 165, up from 150", "label": "change_request"},
    {"input": "do you cater corporate holiday parties in december", "label": "inquiry"},
    {"input": "is the barn available june 14 for about 120 guests", "label": "inquiry"},
    {"input": "", "label": "human"},
    {"input": "the team loved everything saturday, thank you", "label": "human"},
    {"input": "two vegans just rsvp'd, does the menu need anything", "label": "change_request"},
    {"input": "my nephew has a dairy allergy, which passed apps are ok for him", "label": "allergen"},
    {"input": "looking at your pavilion for a rehearsal dinner in october", "label": "inquiry"},
    {"input": "bump the bar package to premium for the reception", "label": "change_request"},
    {"input": "what's your availability for a 200 person gala this winter", "label": "inquiry"},
]


def run_eval():
    return triage_eval.run(EVAL_CASES, lambda t: read_message(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_message":       {"rung": "R3", "reason": "routing only; the allergen stop is the point"},
    "answer_allergen_question": {"rung": "R0", "reason": "trained humans handle allergy conversations — the wrong reassurance is an ambulance", "never_promote": True},
    "auto_apply_locked_change": {"rung": "R0", "reason": "inside the lock window the kitchen has ordered and prepped — a human confirms", "never_promote": True},
    "double_book_space":  {"rung": "R0", "reason": "two parties at one door is not a scheduling style", "never_promote": True},
    "bill_above_final_count": {"rung": "R0", "reason": "a remembered addition is a dispute, not a charge", "never_promote": True},
    "draft_beo_change":   {"rung": "R1", "reason": "the BEO is the contract of the day — a human applies"},
    "draft_availability_reply": {"rung": "R1", "reason": "outward reply — a human sends"},
    "draft_booking":      {"rung": "R1", "reason": "a booking is a promise of a date — a human confirms"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Plate OS — what it computes to")
        .line("Inquiries answered inside an hour", "revenue", "inquiries/yr × close lift × avg event",
              ["inquiries_yr", "close_lift", "avg_event"],
              lambda g: float(g["inquiries_yr"]) * float(g["close_lift"]) * float(g["avg_event"]),
              note="inquiries are counted; the lift is your call")
        .line("Coordination time", "time_saved", "events × hrs × rate",
              ["events_yr", "hours_per_event", "coordinator_rate"],
              lambda g: float(g["events_yr"]) * float(g["hours_per_event"]) * float(g["coordinator_rate"]))
        .line("BEO-error cost avoided", "scenario", "errors/yr × avg make-good",
              ["beo_errors_yr", "avg_makegood"],
              lambda g: float(g["beo_errors_yr"]) * float(g["avg_makegood"]),
              assumption="an exposure you weigh — avoided errors cannot be counted")
        .line("The allergen discipline", "scenario", "you decide what the stop is worth",
              ["allergen_value"], lambda g: float(g["allergen_value"]),
              assumption="never a saving"))


def roi(given):
    rec = {"events_yr": len([e for e in store.load("bookings") if not e.get("cancelled_at")]),
           "inquiries_yr": len([m for m in store.load("messages") if m.get("label") == "inquiry"])}
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("read_message", "draft_beo_change", "draft_availability_reply", "draft_booking")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("client:",))
