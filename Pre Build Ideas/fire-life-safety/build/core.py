#!/usr/bin/env python3
"""Code OS — domain core (fire & life-safety inspection).

Rules live here: impairment-first triage with fire-watch language, the device
calendar (no record reads UNKNOWN, never compliant), the certification refusal,
the deficiency quote ladder, and the matrix.

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

TABLES = ("config", "sites", "devices", "deficiencies", "messages",
          "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="CODEOS_DATA_ROOT")

FIRE_WATCH = ("IMPAIRMENT PROTOCOL: the building owner is being called NOW. Until the system is "
              "restored and verified, the impaired area needs a fire watch per your AHJ's "
              "requirements. This system never downgrades an impairment and never closes one — "
              "a human verifies the fix.")

INTERVALS = {"extinguisher": 365, "alarm_panel": 365, "sprinkler": 365, "backflow": 365,
             "emergency_light": 365, "kitchen_hood": 180}

# ---------------------------------------------------------------- triage

IMPAIRMENT = (
    r"\b(sprinkler|riser|fire pump|standpipe)\b.*\b(off|down|shut|broken|leak|drained|impair)\w*",
    r"\b(panel|alarm)\b.*\b(trouble|fault|offline|dead|beeping and (dead|blank))\b",
    r"\bfire watch\b|\bimpairment\b",
    r"\b(valve|main)\b.*\b(closed|shut off)\b",
)
DUE_ASK = (
    r"\b(inspection|test)s?\b.*\b(due|overdue|schedule|book|when)\b",
    r"\b(schedule|book)\b.*\b(inspection|test|annual)s?\b",
    r"\bwhen (is|was|are)\b.*\b(inspect|test|tag)\w*",
    r"\bannual\b.*\b(due|coming|schedule)\b",
)
QUOTE_ASK = (
    r"\b(quote|estimate|price|cost|how much)\b.*\b(repair|replace|fix|deficien|head|panel|light)\w*",
    r"\b(deficien|repair)\w*\b.*\b(quote|estimate|price|cost)\b",
)
MARSHAL = (
    r"\b(fire marshal|ahj|city inspector|deputy marshal)\b",
    r"\bmarshal\b.*\b(visit|notice|citation|failed)\b",
)


def read_message(text):
    """impairment | due_ask | quote_ask | marshal | human. Impairment first."""
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty message — a person reads it"}
    for rx in IMPAIRMENT:
        if re.search(rx, t):
            return {"label": "impairment", "protocol": FIRE_WATCH,
                    "why": "a life-safety system impairment — the owner is called NOW with "
                           "fire-watch language; software never downgrades or closes one"}
    for rx in MARSHAL:
        if re.search(rx, t):
            return {"label": "marshal",
                    "why": "AHJ contact — the owner, immediately; software never corresponds "
                           "with the fire marshal"}
    for rx in QUOTE_ASK:
        if re.search(rx, t):
            return {"label": "quote_ask", "why": "deficiency quote question — the ladder answers"}
    for rx in DUE_ASK:
        if re.search(rx, t):
            return {"label": "due_ask", "why": "inspection scheduling — drafted from the calendar"}
    return {"label": "human", "why": "no clean signal — a person reads it"}


# ---------------------------------------------------------------- the device calendar

def device_state(d, ref=None):
    """due / overdue / current / UNKNOWN. A device with no inspection record
    reads UNKNOWN — never compliant."""
    ref = ref or now()
    last = parse(d.get("last_inspected"))
    interval = INTERVALS.get(d.get("kind"), 365)
    if not last:
        return {"state": "unknown",
                "why": "no inspection record on file — this device is UNKNOWN, not compliant; "
                       "a green check without a record is the lie this system cannot tell"}
    due = last + timedelta(days=interval)
    days = (due - ref).days
    if days < 0:
        return {"state": "overdue", "days_overdue": -days, "due": iso(due)}
    if days <= 30:
        return {"state": "due", "days_left": days, "due": iso(due)}
    return {"state": "current", "days_left": days, "due": iso(due)}


def site_board(ref=None):
    ref = ref or now()
    rows = []
    devices = store.load("devices")
    for s in store.load("sites"):
        sd = [d for d in devices if d.get("site_id") == s["id"]]
        states = [device_state(d, ref) for d in sd]
        rows.append({"site": s["name"], "site_id": s["id"], "devices": len(sd),
                     "overdue": sum(1 for x in states if x["state"] == "overdue"),
                     "due": sum(1 for x in states if x["state"] == "due"),
                     "unknown": sum(1 for x in states if x["state"] == "unknown"),
                     "open_deficiencies": len([f for f in store.load("deficiencies")
                                               if f.get("site_id") == s["id"]
                                               and not f.get("repaired_at")
                                               and not f.get("declined_at")])})
    rows.sort(key=lambda r: -(r["overdue"] + r["unknown"]))
    return rows


# ---------------------------------------------------------------- deficiency ladder

DEF_MAX_TOUCHES = 3
DEF_COOLDOWN_DAYS = 10


def deficiency_plan(f, ref=None):
    ref = ref or now()
    if f.get("repaired_at") or f.get("declined_at") or f.get("demo_tag"):
        return {"action": "none", "why": "closed"}
    touches = f.get("touches") or []
    if len(touches) >= DEF_MAX_TOUCHES:
        return {"action": "none", "why": f"ladder exhausted at {DEF_MAX_TOUCHES} — silence is an answer"}
    last = parse(touches[-1]["at"]) if touches else parse(f.get("found_at"))
    if last and (ref - last).days < DEF_COOLDOWN_DAYS:
        return {"action": "none", "why": f"inside the {DEF_COOLDOWN_DAYS}-day cooldown"}
    return {"action": "draft_chase", "why": f"touch {len(touches)+1} of {DEF_MAX_TOUCHES}"}


def recovered_this_week(ref=None):
    """Counted: inspections completed, deficiencies repaired, impairments
    escalated, inside 7 days."""
    ref = ref or now()
    inspected = [d for d in store.load("devices")
                 if d.get("last_inspected")
                 and (ref - (parse(d["last_inspected"]) or ref)).days <= 7]
    repaired = [f for f in store.load("deficiencies")
                if f.get("repaired_at") and (ref - (parse(f["repaired_at"]) or ref)).days <= 7]
    impairments = sum(1 for e in store.events(kind="escalate_impairment")
                      if (ref - (parse(e.get("at")) or ref)).days <= 7)
    return {"devices_inspected": len(inspected), "deficiencies_repaired": len(repaired),
            "repaired_value": round(sum(f.get("quote", 0) for f in repaired), 2),
            "impairments_escalated": impairments,
            "note": "counted from the device and deficiency records — never asserted"}


# ---------------------------------------------------------------- eval

triage_eval = Eval("message triage",
                   costly_label="impairment",
                   costly_note=("AN IMPAIRMENT SAT ON OR SOFTENED IS A BUILDING WITHOUT ITS "
                                "SPRINKLERS AND NOBODY WATCHING. Over-routing a scheduling ask "
                                "costs a call."))

EVAL_CASES = [
    {"input": "the riser valve is shut off on floor 3 after the leak", "label": "impairment"},
    {"input": "sprinkler system is down in the east wing", "label": "impairment"},
    {"input": "panel is showing trouble and the horn circuit is dead", "label": "impairment"},
    {"input": "do we need a fire watch while the pump is being repaired", "label": "impairment"},
    {"input": "the main valve got closed during the plumbing work", "label": "impairment"},
    {"input": "fire marshal left a notice after his walk-through", "label": "marshal"},
    {"input": "when is our annual due for the extinguishers", "label": "due_ask"},
    {"input": "need to schedule the kitchen hood test", "label": "due_ask"},
    {"input": "how much to replace the three bad heads you found", "label": "quote_ask"},
    {"input": "price on fixing the emergency lights from the report", "label": "quote_ask"},
    {"input": "", "label": "human"},
    {"input": "invoice received, thanks", "label": "human"},
    {"input": "city inspector is coming tuesday, can you be here", "label": "marshal"},
    {"input": "the alarm panel is offline at the warehouse", "label": "impairment"},
    {"input": "when was the backflow last tested", "label": "due_ask"},
]


def run_eval():
    return triage_eval.run(EVAL_CASES, lambda t: read_message(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_message":        {"rung": "R3", "reason": "routing only; impairment-first is the point"},
    "escalate_impairment": {"rung": "R2", "reason": "the owner call cannot wait for a click — fire watch language verbatim"},
    "mark_compliant_without_record": {"rung": "R0", "reason": "a green check without a record is the lie this system cannot tell", "never_promote": True},
    "downgrade_impairment": {"rung": "R0", "reason": "software never decides an impairment was minor", "never_promote": True},
    "close_impairment":    {"rung": "R0", "reason": "a human verifies the fix and closes", "never_promote": True},
    "certify_inspection":  {"rung": "R0", "reason": "the licensed inspector signs; software drafts the paperwork", "never_promote": True},
    "correspond_with_ahj": {"rung": "R0", "reason": "the owner talks to the fire marshal", "never_promote": True},
    "draft_deficiency_chase": {"rung": "R1", "reason": "outward message — a human sends, the finding cited"},
    "draft_inspection_booking": {"rung": "R1", "reason": "outward booking — a human sends"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Code OS — what it computes to")
        .line("Overdue inspections recovered", "revenue", "overdue+unknown devices × avg inspection",
              ["overdue_devices", "avg_inspection"],
              lambda g: float(g["overdue_devices"]) * float(g["avg_inspection"]),
              note="overdue and unknown are counted from the device records")
        .line("Deficiency repairs chased", "revenue", "open deficiency value × your close rate",
              ["open_deficiency_value", "close_rate"],
              lambda g: float(g["open_deficiency_value"]) * float(g["close_rate"]))
        .line("Scheduling hours", "time_saved", "hrs/wk × 52 × rate",
              ["office_hours_wk", "office_rate"],
              lambda g: float(g["office_hours_wk"]) * 52 * float(g["office_rate"]))
        .line("The impairment log", "scenario", "you decide what the response record is worth",
              ["impairment_value"], lambda g: float(g["impairment_value"]),
              assumption="never a saving — a life-safety record is not our number to model"))


def roi(given):
    rec = {}
    states = [device_state(d) for d in store.load("devices")]
    rec["overdue_devices"] = sum(1 for s in states if s["state"] in ("overdue", "unknown"))
    open_d = [f for f in store.load("deficiencies")
              if not f.get("repaired_at") and not f.get("declined_at") and not f.get("demo_tag")]
    rec["open_deficiency_value"] = round(sum(f.get("quote", 0) for f in open_d), 2)
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("read_message", "escalate_impairment", "draft_deficiency_chase",
          "draft_inspection_booking")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("client:",))
