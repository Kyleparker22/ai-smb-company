#!/usr/bin/env python3
"""Pump OS — domain core (septic & portable sanitation).

Rules live here: backup-emergency triage, the manifest billing gate (gallons +
site + manifest or no invoice), the phone-diagnosis refusal, the land-application
permit gate, interval recall, and the matrix.

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

TABLES = ("config", "customers", "systems", "jobs", "messages", "units",
          "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="PUMPOS_DATA_ROOT")

EMERGENCY_ACK = ("A truck window is being confirmed right now and a human will call you back "
                 "within minutes. Until then: stop running water into the system. We diagnose "
                 "on site, not on the phone.")

# ---------------------------------------------------------------- triage

EMERGENCY = (
    r"\b(sewage|waste ?water|septic)\b.*\b(back(ing|ed)? up|in the (house|tub|shower|basement)|"
    r"coming up|overflow)\b",
    r"\b(toilet|drain|tub|shower)s?\b.*\b(backing up|gurgling and (overflow|coming up)|black water)\b",
    r"\bsmell\b.*\b(sewage|septic)\b.*\b(inside|in the house|basement)\b",
    r"\balarm\b.*\b(septic|pump|tank)\b|\b(septic|pump|tank)\b.*\balarm\b",
)
DIAGNOSIS_ASK = (
    r"\b(is it|could it be|do you think)\b.*\b(the )?(baffle|field|leach|pump|line|tank|filter)\b",
    r"\bwhat('?s| is) wrong with\b.*\b(system|tank|field)\b",
    r"\bwhy (is|does|would)\b.*\b(septic|tank|drain|field)\b",
)
DUE_SERVICE = (
    r"\b(pump(ed|ing)? ?(out)?|service|clean(ed|ing)?)\b.*\b(due|time|again|schedule|book)\b",
    r"\b(schedule|book|need)\b.*\b(pump ?out|pump(ed|ing)?|service)\b",
    r"\bpump (the )?(tank|it)\b",
    r"\b(it'?s|been) (about |over )?(two|three|four|\d) years?\b",
)
PORTABLE = (
    r"\b(porta|portable|rental)\b.*\b(toilets?|units?|johns?|restrooms?)\b|"
    r"\bporta.?(johns?|pott?y|potties)\b",
    r"\b(wedding|festival|event|job ?site|construction)\b.*\b(units?|toilets?|restrooms?)\b",
)


def read_message(text):
    """emergency | diagnosis_ask | due_service | portable | human."""
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty message — a person reads it"}
    for rx in EMERGENCY:
        if re.search(rx, t):
            return {"label": "emergency", "ack": EMERGENCY_ACK,
                    "why": "sewage backup / alarm — a truck window and a human now; nothing is "
                           "diagnosed by phone"}
    for rx in DIAGNOSIS_ASK:
        if re.search(rx, t):
            return {"label": "diagnosis_ask",
                    "why": "a diagnosis question — a system nobody has opened is a system nobody "
                           "diagnoses; a tech visit drafts instead"}
    for rx in PORTABLE:
        if re.search(rx, t):
            return {"label": "portable", "why": "portable-unit order — draft at R1"}
    for rx in DUE_SERVICE:
        if re.search(rx, t):
            return {"label": "due_service", "why": "due-service request — booking drafts"}
    return {"label": "human", "why": "no clean signal — a person reads it"}


# ---------------------------------------------------------------- the manifest gate

MANIFEST_FIELDS = ("gallons", "disposal_site", "manifest_ref")


def can_bill(job):
    """A pump-out bills only with gallons + disposal site + manifest reference.
    Unprovable work is a dispute, and here it is also a regulatory exhibit."""
    rec = job.get("disposal") or {}
    missing = [f for f in MANIFEST_FIELDS if not rec.get(f)]
    if missing:
        return False, (f"cannot bill — disposal record missing: {', '.join(missing)}. An "
                       f"unmanifested load is unprovable work AND a DEQ exhibit; the record "
                       f"completes or the invoice doesn't exist.")
    return True, (f"{rec['gallons']} gal to {rec['disposal_site']} under manifest "
                  f"{rec['manifest_ref']}")


def can_land_apply(job):
    """Land application needs the recorded permit reference."""
    if job.get("land_application") and not job.get("permit_ref"):
        return False, ("land application without a recorded permit reference — the spread "
                       "doesn't happen; a permit is a paper fact, not a verbal one")
    return True, "ok"


# ---------------------------------------------------------------- interval recall

RECALL_MAX_TOUCHES = 3
RECALL_COOLDOWN_DAYS = 30


def due_systems(ref=None):
    ref = ref or now()
    rows = []
    for s in store.load("systems"):
        if s.get("demo_tag"):
            continue
        last = parse(s.get("last_pumped"))
        interval = s.get("interval_years")
        if not last or not interval:
            rows.append({"system": s["id"], "customer": s.get("customer_name"),
                         **unmeasured("no pump date or interval recorded — due date unknowable",
                                      field="overdue_days")})
            continue
        due = last + timedelta(days=int(interval * 365))
        if due <= ref:
            rows.append({"system": s["id"], "customer": s.get("customer_name"),
                         "overdue_days": (ref - due).days,
                         "recalls": len(s.get("recalls") or [])})
    rows.sort(key=lambda r: -(r.get("overdue_days") or 0))
    return rows


def recall_plan(system, ref=None):
    ref = ref or now()
    recalls = system.get("recalls") or []
    if len(recalls) >= RECALL_MAX_TOUCHES:
        return {"action": "none", "why": f"ladder exhausted at {RECALL_MAX_TOUCHES} — silence is an answer"}
    if recalls:
        last = parse(recalls[-1]["at"])
        if last and (ref - last).days < RECALL_COOLDOWN_DAYS:
            return {"action": "none", "why": f"inside the {RECALL_COOLDOWN_DAYS}-day cooldown"}
    return {"action": "draft_recall", "why": f"touch {len(recalls)+1} of {RECALL_MAX_TOUCHES}"}


def recovered_this_week(ref=None):
    """Counted, never asserted: jobs billed with manifests, recalls a human
    sent, and portable orders booked, inside 7 days."""
    ref = ref or now()
    billed = [j for j in store.load("jobs")
              if j.get("billed_at") and (ref - (parse(j["billed_at"]) or ref)).days <= 7]
    recalls = orders = 0
    for e in store.events():
        at = parse(e.get("at"))
        if not at or (ref - at).days > 7 or not str(e.get("actor", "")).startswith("human:"):
            continue
        if e["kind"] == "draft_recall":
            recalls += 1
        elif e["kind"] == "draft_portable_order":
            orders += 1
    return {"jobs_billed": len(billed),
            "billed_value": round(sum(j.get("amount", 0) for j in billed), 2),
            "recalls_sent": recalls, "portable_orders": orders,
            "note": "counted from the job ledger and the event log — never asserted"}


# ---------------------------------------------------------------- eval

triage_eval = Eval("message triage",
                   costly_label="emergency",
                   costly_note=("SEWAGE IN A HOUSE HANDLED AS A BOOKING IS A FAMILY LIVING IN A "
                                "BIOHAZARD WHILE THEY WAIT. Over-routing a due-service ask costs "
                                "a call."))

EVAL_CASES = [
    {"input": "sewage is backing up into the downstairs shower", "label": "emergency"},
    {"input": "toilets are gurgling and black water is coming up the tub drain", "label": "emergency"},
    {"input": "the septic alarm has been going off since midnight", "label": "emergency"},
    {"input": "we can smell sewage inside the house near the basement", "label": "emergency"},
    {"input": "is it the baffle or the leach field, what do you think", "label": "diagnosis_ask"},
    {"input": "what's wrong with my system, it's slow after rain", "label": "diagnosis_ask"},
    {"input": "it's been about three years, probably time to pump again", "label": "due_service"},
    {"input": "need to schedule a pump out before we sell the house", "label": "due_service"},
    {"input": "need four porta johns for a wedding in june", "label": "portable"},
    {"input": "job site needs two units and weekly service", "label": "portable"},
    {"input": "", "label": "human"},
    {"input": "invoice looks right, check is out today", "label": "human"},
    {"input": "why does the drain field smell after heavy rain", "label": "diagnosis_ask"},
    {"input": "the pump alarm light is on in the yard", "label": "emergency"},
    {"input": "can you pump the tank thursday when you're out this way", "label": "due_service"},
]


def run_eval():
    return triage_eval.run(EVAL_CASES, lambda t: read_message(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_message":      {"rung": "R3", "reason": "routing only; the emergency read is the point"},
    "route_emergency":   {"rung": "R2", "reason": "act now, tell the human — the truck window cannot wait"},
    "diagnose_by_phone": {"rung": "R0", "reason": "a system nobody has opened is a system nobody diagnoses", "never_promote": True},
    "bill_without_manifest": {"rung": "R0", "reason": "an unmanifested load is unprovable work and a DEQ exhibit", "never_promote": True},
    "schedule_land_application_unpermitted": {"rung": "R0", "reason": "a permit is a paper fact, not a verbal one", "never_promote": True},
    "draft_invoice":     {"rung": "R1", "reason": "money — a human sends, past the manifest gate"},
    "draft_recall":      {"rung": "R1", "reason": "outward reminder — a human sends"},
    "draft_visit_booking": {"rung": "R1", "reason": "outward booking — a human sends"},
    "draft_portable_order": {"rung": "R1", "reason": "outward order confirm — a human sends"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Pump OS — what it computes to")
        .line("Recalled pump-outs", "revenue", "overdue systems × avg ticket",
              ["overdue_systems", "avg_ticket"],
              lambda g: float(g["overdue_systems"]) * float(g["avg_ticket"]),
              note="overdue is counted from each system's own recorded interval")
        .line("Portable event capture", "revenue", "orders × avg order (yours)",
              ["portable_orders_mo", "avg_order"],
              lambda g: float(g["portable_orders_mo"]) * 12 * float(g["avg_order"]))
        .line("Office hours", "time_saved", "hrs/wk × 52 × rate",
              ["office_hours_wk", "office_rate"],
              lambda g: float(g["office_hours_wk"]) * 52 * float(g["office_rate"]))
        .line("The manifest file", "scenario", "you decide what a clean DEQ audit is worth",
              ["audit_value"], lambda g: float(g["audit_value"]),
              assumption="never a saving — a clean audit is not our number to model"))


def roi(given):
    rec = {}
    rec["overdue_systems"] = len([r for r in due_systems() if r.get("overdue_days") is not None])
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("read_message", "route_emergency", "draft_invoice", "draft_recall",
          "draft_visit_booking", "draft_portable_order")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("customer:",))
