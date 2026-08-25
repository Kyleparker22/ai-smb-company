#!/usr/bin/env python3
"""Rehab OS — domain core (physical therapy clinics).

Rules live here: red-flag triage, the dropout watch on the two-signal floor,
patient-level authorization arithmetic with the booking refusal, recert date
alerts, and the matrix.

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

TABLES = ("config", "patients", "visits", "messages", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="REHABOS_DATA_ROOT")

ER_INSTRUCTION = ("If this is happening now — chest pain, trouble breathing, new loss of bladder "
                  "or bowel control — call 911 or go to the emergency room. A clinician is being "
                  "reached as well.")

# ---------------------------------------------------------------- triage

RED_FLAGS = (
    ("cauda_equina", r"\b(can'?t|cannot|lost|losing)\b.*\b(bladder|bowels?)\b|"
                     r"\bnumb\b.*\b(groin|saddle|between)\b"),
    ("dvt", r"\bcalf\b.*\b(swollen|swelling|hot|red|pain)\b|\b(swollen|hot) calf\b"),
    ("cardiac", r"\b(chest (pain|tightness|pressure)|short(ness)? of breath|can'?t breathe)\b.*"
                r"\b(during|after|with|when|since|stairs|walking)\b|"
                r"\bchest (pain|pressure)\b"),
    ("neuro", r"\b(new|sudden|spreading)\b.*\b(numbness|weakness|tingling)\b|"
              r"\b(leg|arm|foot|hand) (went|is going) numb\b|\bfoot (drop|dragging)\b|"
              r"\bpins and needles\b|\b(both )?legs? (feel|are|going) weak\b|\bbelow the waist\b"),
    ("infection", r"\bfever\b.*\b(surgery|incision|post-?op)\b|\bincision\b.*\b(red|hot|oozing|open)\b"),
)
CLINICAL = (
    r"\b(should i|can i|is it ok to)\b.*\b(push through|keep (going|doing)|continue|ice|heat)\b",
    r"\b(pain|sore|hurts?)\b.*\b(normal|worse|expected)\b|"
    r"\b(normal|worse|expected)\b.*\b(pain|sore|hurts?)\b|\bhow much pain\b",
    r"\b(exercise|rep|band|weight)\b.*\b(right|correctly|too (much|hard))\b",
    r"\b(medication|ibuprofen|pain ?killer)\b",
    r"\bhow many (reps|sets|times)\b",
)
CANCEL = (r"\b(cancel|can'?t (make|come)|reschedule|miss(ing)? (my|the))\b.*"
          r"\b(appointment|session|visit|today|tomorrow|monday|tuesday|wednesday|thursday|friday|"
          r"saturday|sunday|next week)\b",)
SCHEDULE = (r"\b(book|schedule|next (visit|appointment)|what time|confirm)\b",
            r"\b(push|move) (my|the) (slot|time|appointment)\b|\brunning late\b",)


def read_message(text):
    """red_flag | clinical | cancellation | scheduling | human."""
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty message — a person reads it"}
    for kind, rx in RED_FLAGS:
        if re.search(rx, t):
            return {"label": "red_flag", "kind": kind,
                    "why": f"typed red flag: {kind} — a clinician immediately; the front desk is "
                           f"not a triage nurse", "instruction": ER_INSTRUCTION}
    for rx in CLINICAL:
        if re.search(rx, t):
            return {"label": "clinical",
                    "why": "clinical question — routed to the treating therapist unanswered"}
    for rx in CANCEL:
        if re.search(rx, t):
            return {"label": "cancellation",
                    "why": "cancellation — rebooking drafts AND the dropout signal records"}
    for rx in SCHEDULE:
        if re.search(rx, t):
            return {"label": "scheduling", "why": "scheduling — draft at R1"}
    return {"label": "human", "why": "no clean signal — a person reads it"}


# ---------------------------------------------------------------- dropout watch

RISK_SIGNAL_FLOOR = 2


def dropout_signals(patient, ref=None):
    ref = ref or now()
    sigs = []
    visits = [v for v in store.load("visits") if v.get("patient_id") == patient["id"]]
    attended = [v for v in visits if v.get("attended_at")]
    missed = [v for v in visits if v.get("no_show")]
    cancels = [v for v in visits if v.get("cancelled_at")]
    if len(missed) >= 2:
        sigs.append({"signal": "no_shows", "detail": f"{len(missed)} no-shows"})
    if len(cancels) >= 2:
        sigs.append({"signal": "cancellations", "detail": f"{len(cancels)} cancellations"})
    if attended:
        last = max(parse(v["attended_at"]) for v in attended)
        gap = (ref - last).days
        if gap > 10:
            sigs.append({"signal": "gap", "detail": f"{gap} days since last visit"})
    prescribed = patient.get("visits_prescribed")
    started = parse(patient.get("poc_started"))
    if prescribed and started:
        weeks_in = max(1, (ref - started).days / 7)
        expected = min(prescribed, weeks_in * (patient.get("visits_per_week") or 2))
        if len(attended) < expected * 0.6:
            sigs.append({"signal": "behind_plan",
                         "detail": f"{len(attended)} attended vs ~{expected:.0f} expected by now"})
    return sigs


def dropout_board():
    at_risk, single = [], 0
    for p in store.load("patients"):
        if p.get("status") != "active" or p.get("demo_tag"):
            continue
        sigs = dropout_signals(p)
        if len(sigs) >= RISK_SIGNAL_FLOOR:
            at_risk.append({"patient": p["id"], "name": p.get("name"), "count": len(sigs),
                            "signals": sigs})
        elif len(sigs) == 1:
            single += 1
    at_risk.sort(key=lambda r: -r["count"])
    return {"n": len(at_risk), "rows": at_risk[:40], "single_signal": single,
            "floor": RISK_SIGNAL_FLOOR,
            "note": "one signal is a note; two is a pattern — the visit-4 dropout is the leak"}


# ---------------------------------------------------------------- authorization

def auth_state(patient, ref=None):
    """Used vs authorized, at the PATIENT level. No auth recorded → unmeasured,
    never assumed unlimited. Recert dates are date alerts."""
    ref = ref or now()
    auth = patient.get("authorized_visits")
    used = len([v for v in store.load("visits")
                if v.get("patient_id") == patient["id"] and v.get("attended_at")])
    out = {"used": used}
    if auth is None:
        out.update(unmeasured("no authorization recorded — remaining visits unknowable, never "
                              "assumed unlimited", field="remaining"))
    else:
        out["authorized"] = auth
        out["remaining"] = auth - used
        out["over"] = used >= auth
    recert = parse(patient.get("recert_due"))
    if recert:
        out["recert_due"] = patient["recert_due"]
        out["recert_days_left"] = (recert - ref).days
        out["recert_label"] = "DATE ALERT — the plan of care needs recertification"
    return out


def can_book_billable(patient):
    """THE refusal: booking past authorization is never silent."""
    s = auth_state(patient)
    if s.get("_missing"):
        return False, ("no authorization recorded — a billable visit cannot be booked against an "
                       "unknown authorization; a human verifies with the payer first")
    if s.get("over") or s.get("remaining", 1) <= 0:
        return False, (f"{s['used']} visits used against {s.get('authorized')} authorized — "
                       f"booking past authorization is unbillable work or an audit finding; a "
                       f"human takes it to the payer")
    return True, f"{s['remaining']} authorized visit(s) remaining"


def recovered_this_week(ref=None):
    """Counted, never asserted: dropout outreaches a human sent, visits booked
    within auth, and payer escalations resolved, inside 7 days."""
    ref = ref or now()
    outreach = booked = 0
    for e in store.events():
        at = parse(e.get("at"))
        if not at or (ref - at).days > 7 or not str(e.get("actor", "")).startswith("human:"):
            continue
        if e["kind"] == "draft_dropout_outreach":
            outreach += 1
        elif e["kind"] == "book_within_auth":
            booked += 1
    reauth = [p for p in store.load("patients")
              if p.get("reauthorized_at") and (ref - (parse(p["reauthorized_at"]) or ref)).days <= 7]
    return {"outreach_sent": outreach, "visits_booked": booked,
            "reauthorizations": len(reauth),
            "note": "counted from the event log and the charts — never asserted"}


# ---------------------------------------------------------------- eval

triage_eval = Eval("message triage",
                   costly_label="red_flag",
                   costly_note=("A RED FLAG IN THE SCHEDULING QUEUE — CAUDA EQUINA, DVT, CARDIAC "
                                "— IS MEASURED IN HOURS OF PERMANENT DAMAGE. Over-routing a "
                                "soreness question costs a clinician a minute."))

EVAL_CASES = [
    {"input": "I can't control my bladder since this morning and my back is worse", "label": "red_flag"},
    {"input": "my calf is swollen and hot since yesterday's session", "label": "red_flag"},
    {"input": "had chest tightness during the exercises last night", "label": "red_flag"},
    {"input": "my foot went numb and I'm dragging it a little", "label": "red_flag"},
    {"input": "fever since my surgery and the incision looks red", "label": "red_flag"},
    {"input": "should I push through the pain on the band exercises", "label": "clinical"},
    {"input": "is it normal to be this sore two days after", "label": "clinical"},
    {"input": "can't make my appointment tomorrow, need to reschedule", "label": "cancellation"},
    {"input": "what time is my session thursday", "label": "scheduling"},
    {"input": "", "label": "human"},
    {"input": "both legs feel weak and pins and needles below the waist", "label": "red_flag"},
    {"input": "short of breath going up stairs since the last visit", "label": "red_flag"},
    {"input": "how many reps of the bridges should I do at home", "label": "clinical"},
    {"input": "running late, can we push my slot 30 minutes", "label": "scheduling"},
    {"input": "gotta cancel friday, work thing came up", "label": "cancellation"},
]


def run_eval():
    return triage_eval.run(EVAL_CASES, lambda t: read_message(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_message":     {"rung": "R3", "reason": "routing only; the red-flag stop is the point"},
    "route_red_flag":   {"rung": "R2", "reason": "a clinician is reached now — hours matter"},
    "clinical_answer":  {"rung": "R0", "reason": "clinical questions are answered by the treating therapist", "never_promote": True},
    "modify_plan_of_care": {"rung": "R0", "reason": "only the treating therapist changes a plan of care", "never_promote": True},
    "bill_beyond_authorization": {"rung": "R0", "reason": "unbillable work is refused at booking, not discovered at denial", "never_promote": True},
    "promise_outcome":  {"rung": "R0", "reason": "no recovery promise, ever", "never_promote": True},
    "draft_rebooking":  {"rung": "R1", "reason": "outward message — a human sends"},
    "draft_dropout_outreach": {"rung": "R1", "reason": "outward message — a human sends"},
    "book_within_auth": {"rung": "R1", "reason": "a booking is a promise of clinic time — a human confirms"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Rehab OS — what it computes to")
        .line("Dropouts brought back", "revenue", "at-risk × recovery rate × remaining visit value",
              ["at_risk", "recovery_rate", "avg_remaining_value"],
              lambda g: float(g["at_risk"]) * float(g["recovery_rate"]) * float(g["avg_remaining_value"]),
              note="at-risk is counted on the two-signal floor; the rate is yours")
        .line("Front-desk and chase time", "time_saved", "hrs/wk × 52 × rate",
              ["desk_hours_wk", "staff_rate"],
              lambda g: float(g["desk_hours_wk"]) * 52 * float(g["staff_rate"]))
        .line("Auth denials avoided", "scenario", "denials/yr × avg written-off visits",
              ["denials_yr", "avg_writeoff"],
              lambda g: float(g["denials_yr"]) * float(g["avg_writeoff"]),
              assumption="an exposure you weigh — avoided denials cannot be counted")
        .line("Red-flag routing", "scenario", "you decide what the stop is worth",
              ["redflag_value"], lambda g: float(g["redflag_value"]),
              assumption="never monetized by us — yours or blank"))


def roi(given):
    rec = {"at_risk": dropout_board()["n"]}
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("read_message", "route_red_flag", "draft_rebooking", "draft_dropout_outreach",
          "book_within_auth")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("patient:",))
