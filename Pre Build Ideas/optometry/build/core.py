#!/usr/bin/env python3
"""Exam OS — domain core (optometry).

Rules live here: ocular-emergency triage with per-type instructions, the
recall ladder, the counted capture rate, the Rx discipline (never refilled
expired, never modified, never withheld), and the matrix.

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

TABLES = ("config", "patients", "exams", "purchases", "messages", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="EXAMOS_DATA_ROOT")

CHEMICAL_INSTRUCTION = ("Rinse the eye with clean water or saline continuously for at least 15 "
                        "minutes RIGHT NOW, then go to the emergency room. Do not wait for a "
                        "reply here. The doctor is being told as well.")
URGENT_INSTRUCTION = ("This needs to be seen today — a doctor is being told right now and the "
                      "practice will call you within minutes. If vision is going dark, go to the "
                      "emergency room.")

# ---------------------------------------------------------------- triage

EMERGENCIES = (
    ("chemical", r"\b(splash(ed)?|got|sprayed)\b.*\b(bleach|chemical|cleaner|acid|lye|cement)\b.*\beye|"
                 r"\b(bleach|chemical|cleaner|acid)\b.*\b(in|into) (my|his|her|the) eye\b"),
    ("retinal", r"\b(flash(es|ing)?|floaters?)\b.*\b(curtain|shadow|veil|dark)\b|"
                r"\b(curtain|shadow|veil)\b.*\b(vision|eye|see)\b|\bflashes and floaters\b"),
    ("vision_loss", r"\b(sudden(ly)?|woke up)\b.*\b(can'?t see|lost vision|vision (gone|loss)|blind)\b|"
                    r"\bvision went (dark|black|gray)\b"),
    ("trauma", r"\b(hit|poked|scratched|metal|grinding|nail|branch)\b.*\beye\b.*"
               r"\b(pain|bleeding|stuck|embedded|can'?t open|blurr\w*|vision|see)\b|"
               r"\bsomething (stuck|embedded) in\b.*\beye\b"),
    ("keratitis", r"\b(contact( lens)?e?s?)\b.*\b(pain(ful)?|red|light hurts|light sensitivity)\b|"
                  r"\b(pain(ful)?|red) eye\b.*\b(contacts?|lens)\b"),
)
CLINICAL = (
    r"\b(is it (normal|ok)|should i)\b.*\b(blurry|dry|itchy|red|drops|rub)\b",
    r"\b(pink ?eye|stye|dry eye|allerg)\b.*\b(drops|treat|what should)\b",
    r"\bwhat (drops|medicine)\b",
    r"\bsupposed to (feel|look|be)\b",
)
REORDER = (r"\b(reorder|refill|more|order)\b.*\b(contacts?|lenses)\b|\bcontacts?\b.*\b(running low|out of)\b",
           r"\b(almost )?out of\b.*\b(dailies|monthlies|contacts?)\b|\banother box\b|\bmore dailies\b",)
BOOKING = (r"\b(book|schedule|appointment|exam|come in)\b",)
RX_REQUEST = (r"\b(copy of|send|need|release)\b.*\b(prescription|rx)\b",
              r"\b(my|the) (script|pd)\b",)


def read_message(text):
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty message — a person reads it"}
    for kind, rx in EMERGENCIES:
        if re.search(rx, t):
            instruction = CHEMICAL_INSTRUCTION if kind == "chemical" else URGENT_INSTRUCTION
            return {"label": "emergency", "kind": kind, "instruction": instruction,
                    "why": f"typed ocular emergency: {kind} — hours matter; nothing is assessed"}
    for rx in RX_REQUEST:
        if re.search(rx, t):
            return {"label": "rx_request",
                    "why": "prescription release — drafted on request; the patient's Rx is the patient's"}
    for rx in REORDER:
        if re.search(rx, t):
            return {"label": "reorder", "why": "contact reorder — checked against the recorded Rx expiry"}
    for rx in CLINICAL:
        if re.search(rx, t):
            return {"label": "clinical", "why": "clinical question — the doctor answers, never software"}
    for rx in BOOKING:
        if re.search(rx, t):
            return {"label": "booking", "why": "booking — draft at R1"}
    return {"label": "human", "why": "no clean signal — a person reads it"}


# ---------------------------------------------------------------- Rx discipline

def reorder_check(patient, ref=None):
    """A reorder runs against the RECORDED Rx expiry. Expired → refused: an
    exam renews a prescription, not a message. No expiry recorded → refused."""
    ref = ref or now()
    exp = parse(patient.get("cl_rx_expires"))
    if not exp:
        return {"ok": False,
                "refused": "no contact-lens Rx expiry on record — nothing is refilled against an "
                           "unknown prescription; an exam settles it"}
    if exp < ref:
        return {"ok": False,
                "refused": f"the contact-lens Rx expired {(ref - exp).days} days ago — an exam "
                           f"renews a prescription, not a message; an exam draft queues instead"}
    return {"ok": True, "expires": patient["cl_rx_expires"],
            "note": "Rx current — the reorder drafts at R1"}


# ---------------------------------------------------------------- recall

RECALL_COOLDOWN_DAYS = 30
MAX_RECALLS = 3


def lapsed(ref=None):
    ref = ref or now()
    rows = []
    for p in store.load("patients"):
        if p.get("status") != "active":
            continue
        last = parse(p.get("last_exam"))
        if not last:
            continue
        overdue = (ref - last).days - 365
        if overdue > 0:
            rows.append({"patient": p["id"], "name": p.get("name"),
                         "overdue_days": overdue, "recalls": len(p.get("recalls") or [])})
    return sorted(rows, key=lambda r: -r["overdue_days"])


def recall_plan(patient, ref=None):
    ref = ref or now()
    recalls = patient.get("recalls") or []
    if len(recalls) >= MAX_RECALLS:
        return {"action": "none", "why": f"ladder exhausted at {MAX_RECALLS} — silence is an answer"}
    if recalls:
        last = parse(recalls[-1]["at"])
        if last and (ref - last).days < RECALL_COOLDOWN_DAYS:
            return {"action": "none", "why": f"inside the {RECALL_COOLDOWN_DAYS}-day cooldown"}
    return {"action": "draft_recall", "why": f"touch {len(recalls)+1} of {MAX_RECALLS}"}


# ---------------------------------------------------------------- capture

CAPTURE_FLOOR = 40


def capture_rate(window_days=90):
    """Exams that became an optical purchase, counted. Refuses below the floor."""
    cutoff = now() - timedelta(days=window_days)
    exams = [e for e in store.load("exams") if (parse(e.get("at")) or now()) >= cutoff]
    if len(exams) < CAPTURE_FLOOR:
        return unmeasured(f"only {len(exams)} exams in {window_days} days — need {CAPTURE_FLOOR}",
                          field="rate", n=len(exams))
    purchases = {p.get("exam_id") for p in store.load("purchases")}
    captured = [e for e in exams if e["id"] in purchases]
    return {"rate": round(len(captured) / len(exams), 3), "captured": len(captured),
            "of": len(exams), "note": "exam → optical purchase, counted — the walkouts are the leak"}


def recovered_this_week(ref=None):
    """Counted, never asserted: recalls a human sent, reorders released,
    Rx releases sent, and exams booked, inside 7 days."""
    ref = ref or now()
    recalls = reorders = releases = bookings = 0
    for e in store.events():
        at = parse(e.get("at"))
        if not at or (ref - at).days > 7 or not str(e.get("actor", "")).startswith("human:"):
            continue
        if e["kind"] == "draft_recall":
            recalls += 1
        elif e["kind"] == "draft_reorder":
            reorders += 1
        elif e["kind"] == "draft_rx_release":
            releases += 1
        elif e["kind"] == "draft_booking":
            bookings += 1
    return {"recalls_sent": recalls, "reorders_released": reorders,
            "rx_releases": releases, "exams_booked": bookings,
            "note": "counted from the event log — never asserted"}


# ---------------------------------------------------------------- eval

triage_eval = Eval("message triage",
                   costly_label="emergency",
                   costly_note=("A RETINAL DETACHMENT IN A MESSAGE QUEUE IS PERMANENT VISION LOSS "
                                "ON A TIMELINE OF HOURS. Over-routing a dry-eye question costs a "
                                "doctor a minute."))

EVAL_CASES = [
    {"input": "flashes and floaters since last night and now a dark curtain on the side", "label": "emergency"},
    {"input": "splashed bleach cleaner in my eye at work", "label": "emergency"},
    {"input": "woke up and can't see out of my left eye", "label": "emergency"},
    {"input": "something stuck in my eye from grinding, pain and tearing", "label": "emergency"},
    {"input": "painful red eye and I sleep in my contacts", "label": "emergency"},
    {"input": "is it normal for my eyes to be this dry with the new drops", "label": "clinical"},
    {"input": "need to reorder contacts, running low", "label": "reorder"},
    {"input": "can you send a copy of my prescription", "label": "rx_request"},
    {"input": "book an exam for me and my daughter", "label": "booking"},
    {"input": "", "label": "human"},
    {"input": "got hit in the eye with a racquetball, vision is blurry", "label": "emergency"},
    {"input": "my contact ripped and now the eye is red and really painful", "label": "emergency"},
    {"input": "are the new lenses supposed to feel this scratchy", "label": "clinical"},
    {"input": "almost out of my dailies, need another box", "label": "reorder"},
    {"input": "need my pd and the script for ordering glasses online", "label": "rx_request"},
]


def run_eval():
    return triage_eval.run(EVAL_CASES, lambda t: read_message(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_message":     {"rung": "R3", "reason": "routing only; the emergency stop is the point"},
    "route_emergency":  {"rung": "R2", "reason": "hours matter — the doctor is told now"},
    "clinical_answer":  {"rung": "R0", "reason": "the doctor answers clinical questions, never software", "never_promote": True},
    "refill_expired_rx": {"rung": "R0", "reason": "an exam renews a prescription, not a message", "never_promote": True},
    "modify_rx":        {"rung": "R0", "reason": "software never touches a prescription's content", "never_promote": True},
    "withhold_rx":      {"rung": "R0", "reason": "the patient's prescription is the patient's — release drafts on request", "never_promote": True},
    "draft_rx_release": {"rung": "R1", "reason": "outward document — a human sends, promptly"},
    "draft_recall":     {"rung": "R1", "reason": "outward message — a human sends"},
    "draft_reorder":    {"rung": "R1", "reason": "outward order against a current Rx — a human confirms"},
    "draft_booking":    {"rung": "R1", "reason": "outward message — a human sends"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Exam OS — what it computes to")
        .line("Lapsed patients reactivated", "revenue", "lapsed × show rate × exam+capture value",
              ["lapsed_count", "show_rate", "visit_value"],
              lambda g: float(g["lapsed_count"]) * float(g["show_rate"]) * float(g["visit_value"]),
              note="lapsed is counted; the show rate and value are yours")
        .line("Capture-rate lift", "revenue", "exams/yr × lift points × avg optical sale",
              ["exams_yr", "capture_lift", "avg_optical"],
              lambda g: float(g["exams_yr"]) * float(g["capture_lift"]) * float(g["avg_optical"]))
        .line("Recall and reorder time", "time_saved", "hrs/wk × 52 × rate",
              ["desk_hours_wk", "staff_rate"],
              lambda g: float(g["desk_hours_wk"]) * 52 * float(g["staff_rate"]))
        .line("Emergency routing", "scenario", "you decide what the stop is worth",
              ["emergency_value"], lambda g: float(g["emergency_value"]),
              assumption="never monetized by us — yours or blank"))


def roi(given):
    rec = {"lapsed_count": len(lapsed())}
    cr = capture_rate()
    if "_missing" not in cr:
        rec["exams_yr"] = cr["of"] * 4
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("read_message", "route_emergency", "draft_recall", "draft_reorder",
          "draft_booking", "draft_rx_release")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("patient:",))
