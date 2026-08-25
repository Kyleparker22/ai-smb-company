#!/usr/bin/env python3
"""Ratio OS — domain core (child care centers).

Rules live here: the release check against the recorded authorized list, the
ratio arithmetic from recorded attendance, message triage with the
pickup/incident bias, the waitlist funnel, and the matrix.

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

TABLES = ("config", "centers", "rooms", "children", "attendance", "clockins",
          "messages", "waitlist", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="RATIOOS_DATA_ROOT")

RELEASE_RULE = ("a child is released only to a person on the recorded authorized list, verified "
                "per the written policy (photo ID + parent phone verification). Software never "
                "authorizes a release and never adds a name on a caller's say-so.")

# ---------------------------------------------------------------- the pickup rule

def release_check(child_id, person_name):
    """THE refusal. On the list → proceed to human ID check. Not on the list →
    refused; a verification task opens; software confirms nothing."""
    child = store.by_id("children", child_id)
    if not child:
        return {"error": "no such child"}
    authorized = [p.lower() for p in (child.get("authorized_pickups") or [])]
    if (person_name or "").lower().strip() in authorized:
        return {"listed": True,
                "note": "on the recorded list — staff still checks photo ID per policy; this "
                        "check is a record lookup, not an authorization"}
    return {"listed": False,
            "refused": f"{person_name!r} is not on {child.get('name','this child')}'s recorded "
                       f"authorized list — {RELEASE_RULE}"}


# ---------------------------------------------------------------- ratios

DEFAULT_RATIO_RULES = {
    "_source": ("DEFAULT rule set, simplified — replace with the state's licensing ratios before "
                "go-live. Ratios are licensure; a wrong default here is a violation."),
    "TX": {"infant": 4, "toddler": 9, "preschool": 11, "school_age": 26},
}


def ratio_rules():
    return store.load("config").get("ratio_rules") or DEFAULT_RATIO_RULES


def room_ratio(room, ref=None):
    """Children present vs staff present vs the rule. Computed from records or
    refused — a room with no attendance records is never assumed compliant."""
    rules = ratio_rules()
    state_rules = rules.get(room.get("state_code") or "")
    if not state_rules:
        return unmeasured(f"no ratio rules for state {room.get('state_code')!r}", field="status")
    required = state_rules.get(room.get("age_group"))
    if not required:
        return unmeasured(f"no ratio rule for age group {room.get('age_group')!r}", field="status")
    present = [a for a in store.load("attendance")
               if a.get("room_id") == room["id"] and a.get("checked_in") and not a.get("checked_out")]
    staff = [c for c in store.load("clockins")
             if c.get("room_id") == room["id"] and not c.get("clocked_out")]
    if not present and not room.get("attendance_recorded"):
        return unmeasured("no attendance records for this room — the ratio is unmeasured, "
                          "never assumed compliant", field="status")
    if not staff:
        return {"status": "over", "children": len(present), "staff": 0, "required_ratio": required,
                "why": f"{len(present)} children with no staff clocked in — over by definition"}
    ratio = len(present) / len(staff)
    return {"status": "over" if ratio > required else "inside",
            "children": len(present), "staff": len(staff),
            "ratio": round(ratio, 1), "required_ratio": required}


def ratio_board():
    rows = []
    for r in store.load("rooms"):
        v = room_ratio(r)
        rows.append({"room": r["name"], "center": r.get("center"),
                     "age_group": r.get("age_group"), **v})
    order = {"over": 0}
    rows.sort(key=lambda x: order.get(x.get("status"), 1))
    return {"rows": rows, "rules_source": ratio_rules()["_source"],
            "over": sum(1 for x in rows if x.get("status") == "over"),
            "unmeasured": sum(1 for x in rows if x.get("_missing"))}


# ---------------------------------------------------------------- triage

PICKUP_CHANGE = (r"\b(uncle|aunt|grand(ma|pa|mother|father)|brother|sister|neighbor|friend|"
                 r"co-?worker|dad|mom)\b.*\b(pick(ing)? (up|her|him|them)|get(ting)? (her|him|them))\b",
                 r"\bsomeone (else|different)\b.*\bpick", r"\bpick ?up\b.*\b(change|different|new)\b")
INCIDENT = (r"\b(bit|bitten|fell|hurt|injur|bump|bruise|blood|allergic|reaction|choking|"
            r"hit (his|her) head)\b",)
ILLNESS = (r"\b(fever|rash|pink ?eye|vomit|diarrhea|lice|hand foot|covid|flu)\b.*"
           r"\b(come|attend|return|stay home|drop off)\b|\bwhen can (she|he|they) (come back|return)\b",)
ENROLL = (r"\b(enroll|waitlist|openings?|spots?|tour|availability|infant room)\b",)


def read_message(text):
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty message — a person reads it"}
    for rx in PICKUP_CHANGE:
        if re.search(rx, t):
            return {"label": "pickup_change",
                    "why": "pickup change — NEVER auto-approved; a human verification task opens "
                           "(ID + parent phone verification per the written policy)"}
    for rx in INCIDENT:
        if re.search(rx, t):
            return {"label": "incident",
                    "why": "incident/injury — a human calls; software drafts nothing"}
    for rx in ILLNESS:
        if re.search(rx, t):
            return {"label": "illness_question",
                    "why": "illness exclusion question — the policy text is surfaced by a human, "
                           "never paraphrased into advice by software"}
    for rx in ENROLL:
        if re.search(rx, t):
            return {"label": "enrollment", "why": "enrollment inquiry — tour draft at R1"}
    return {"label": "human", "why": "no clean signal — a person reads it"}


# ---------------------------------------------------------------- waitlist

def funnel(window_days=90):
    cutoff = now() - timedelta(days=window_days)
    rows = [w for w in store.load("waitlist") if (parse(w.get("at")) or now()) >= cutoff]
    if len(rows) < 10:
        return unmeasured(f"only {len(rows)} inquiries in {window_days} days — need 10",
                          field="funnel", n=len(rows))
    toured = [w for w in rows if w.get("toured_at")]
    offered = [w for w in rows if w.get("offered_at")]
    enrolled = [w for w in rows if w.get("enrolled_at")]
    return {"inquiries": len(rows), "toured": len(toured), "offered": len(offered),
            "enrolled": len(enrolled),
            "note": "counted from the waitlist records — every stage a recorded fact"}


def recovered_this_week(ref=None):
    """Counted, never asserted: verifications a human completed, tours booked,
    and enrollments recorded, inside 7 days."""
    ref = ref or now()
    verifications = sum(1 for e in store.events(kind="open_verification")
                        if (ref - (parse(e.get("at")) or ref)).days <= 7)
    tours = sum(1 for e in store.events(kind="draft_tour_offer")
                if str(e.get("actor", "")).startswith("human:")
                and (ref - (parse(e.get("at")) or ref)).days <= 7)
    enrolled = [w for w in store.load("waitlist")
                if w.get("enrolled_at") and (ref - (parse(w["enrolled_at"]) or ref)).days <= 7]
    return {"verifications_opened": verifications, "tour_offers_sent": tours,
            "enrollments": len(enrolled),
            "note": "counted from the event log and the waitlist — never asserted"}


# ---------------------------------------------------------------- eval

triage_eval = Eval("message triage",
                   costly_label="critical",
                   costly_note=("A PICKUP CHANGE TREATED AS ROUTINE, OR AN INCIDENT ANSWERED BY "
                                "SOFTWARE, IS THE NIGHTMARE SCENARIO OF THIS INDUSTRY. Routing an "
                                "enrollment ask costs nothing."))

CRITICAL = ("pickup_change", "incident")

EVAL_CASES = [
    {"input": "my brother will pick her up today instead of me", "label": "critical"},
    {"input": "grandma is getting him this afternoon, she drives a blue civic", "label": "critical"},
    {"input": "someone different will pick up the twins friday", "label": "critical"},
    {"input": "another kid bit Emma at drop-in yesterday, she has a bruise", "label": "critical"},
    {"input": "he fell off the slide and hit his head this morning?", "label": "critical"},
    {"input": "she had a fever last night, when can she come back", "label": "illness_question"},
    {"input": "do you have any infant room openings for the fall", "label": "enrollment"},
    {"input": "can we schedule a tour next week", "label": "enrollment"},
    {"input": "", "label": "human"},
    {"input": "she left her jacket in the cubby I think", "label": "human"},
    {"input": "my coworker Dana will be getting him today, dark green suv", "label": "critical"},
    {"input": "there was blood on his sock after outside time", "label": "critical"},
    {"input": "pink eye is going around her class, can she attend tomorrow", "label": "illness_question"},
    {"input": "any spots opening in the twos room this spring", "label": "enrollment"},
    {"input": "is there a tour slot on thursday", "label": "enrollment"},
]


def _eval_label(text):
    lbl = read_message(text)["label"]
    return "critical" if lbl in CRITICAL else lbl


def run_eval():
    return triage_eval.run(EVAL_CASES, _eval_label)


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_message":       {"rung": "R3", "reason": "routing only; the pickup and incident stops are the point"},
    "open_verification":  {"rung": "R2", "reason": "opening the human verification task must not wait for a click"},
    "confirm_unlisted_pickup": {"rung": "R0", "reason": RELEASE_RULE, "never_promote": True},
    "add_authorized_pickup": {"rung": "R0", "reason": "names are added by the enrolled parent through the written process, never by a caller's say-so", "never_promote": True},
    "respond_to_incident": {"rung": "R0", "reason": "an injury gets a human call — nothing in writing from software", "never_promote": True},
    "answer_medical_exclusion": {"rung": "R0", "reason": "illness rules are policy text a human surfaces, never advice software gives", "never_promote": True},
    "estimate_ratio":     {"rung": "R0", "reason": "a ratio without attendance records is fiction — licensure runs on records", "never_promote": True},
    "draft_tour_offer":   {"rung": "R1", "reason": "outward message — a human sends"},
    "draft_waitlist_followup": {"rung": "R1", "reason": "outward message — a human sends"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Ratio OS — what it computes to")
        .line("Seats filled from the waitlist", "revenue", "open seats × fill lift × annual tuition",
              ["open_seats", "fill_lift", "annual_tuition"],
              lambda g: float(g["open_seats"]) * float(g["fill_lift"]) * float(g["annual_tuition"]),
              note="open seats are counted; the lift is your call")
        .line("Front-desk time", "time_saved", "hrs/wk × 52 × rate",
              ["desk_hours_wk", "staff_rate"],
              lambda g: float(g["desk_hours_wk"]) * 52 * float(g["staff_rate"]))
        .line("Ratio-violation exposure", "scenario", "you decide what a citation costs",
              ["violation_cost"], lambda g: float(g["violation_cost"]),
              assumption="an exposure you weigh — never a saving")
        .line("The pickup discipline", "scenario", "you decide what the release rule is worth",
              ["pickup_value"], lambda g: float(g["pickup_value"]),
              assumption="never a saving — this is the one that cannot be priced"))


def roi(given):
    rec = {}
    rooms = store.load("rooms")
    licensed = sum(r.get("capacity", 0) for r in rooms)
    enrolled = len([c for c in store.load("children") if c.get("status") == "active"])
    if licensed:
        rec["open_seats"] = max(0, licensed - enrolled)
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("read_message", "open_verification", "draft_tour_offer", "draft_waitlist_followup")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("parent:",))
