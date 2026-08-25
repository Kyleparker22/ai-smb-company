#!/usr/bin/env python3
"""Ride OS — domain core (non-emergency medical transport).

Rules live here: condition-change-first triage (never assessed), the trip-log
billing gate, the never-bump rule for dialysis/chemo trips, the driver
credential gate, and the matrix.

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

TABLES = ("config", "drivers", "trips", "messages", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="RIDEOS_DATA_ROOT")

NEVER_BUMP = ("dialysis", "chemo", "radiation")

# ---------------------------------------------------------------- triage

CONDITION = (
    r"\b(seems?|looks?|acting)\b.*\b(confused|off|weak|dizzy|pale|worse|out of it)\b",
    r"\b(fell|fall(en)?|(can|could)n'?t (stand|walk|get up)|unresponsive|slurring)\b",
    r"\b(chest pain|trouble breathing|bleeding)\b",
)
SCHEDULE = (
    r"\b(reschedule|change|move|cancel)\b.*\b(pickup|trip|ride|appointment)\b",
    r"\b(pick ?up|ride)\b.*\b(earlier|later|tomorrow|different time)\b",
)
BILLING = (
    r"\b(bill|invoice|claim|denied|payment)\b",
)
COMPLAINT = (
    r"\b(late|no.?show|rude|missed (the|my|her|his)|didn'?t show|waited)\b",
)


def read_message(text):
    """condition_change | schedule | billing | complaint | human. The condition
    change reads first — and is NEVER assessed."""
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty message — a person reads it"}
    for rx in CONDITION:
        if re.search(rx, t):
            return {"label": "condition_change",
                    "why": "a patient-condition observation — passed verbatim to a human and the "
                           "facility; software assesses nothing, reassures nothing, and never "
                           "says 'probably fine'"}
    for rx in COMPLAINT:
        if re.search(rx, t):
            return {"label": "complaint", "why": "service complaint — a human calls with the trip log"}
    for rx in SCHEDULE:
        if re.search(rx, t):
            return {"label": "schedule", "why": "scheduling — drafts at R1, never-bump rules checked"}
    for rx in BILLING:
        if re.search(rx, t):
            return {"label": "billing", "why": "billing — the trip-log gate decides"}
    return {"label": "human", "why": "no clean signal — a person reads it"}


# ---------------------------------------------------------------- the trip-log gate

LOG_FIELDS = ("pickup_odo", "dropoff_odo", "pickup_at", "dropoff_at", "signature_ref")


def can_bill(trip):
    log = trip.get("trip_log") or {}
    missing = [f for f in LOG_FIELDS if not log.get(f)]
    if missing:
        return False, (f"cannot bill — trip log missing: {', '.join(missing)}. An undocumented "
                       f"trip is free work with a Medicaid audit attached.")
    return True, (f"log complete: {log['pickup_odo']}→{log['dropoff_odo']} odo, "
                  f"{str(log['pickup_at'])[11:16]}–{str(log['dropoff_at'])[11:16]}, "
                  f"signature {log['signature_ref']}")


# ---------------------------------------------------------------- the never-bump rule

def can_bump(trip):
    if (trip.get("purpose") or "").lower() in NEVER_BUMP:
        return False, (f"a {trip['purpose']} trip is never bumped by scheduling software — a "
                       f"missed {trip['purpose']} pickup is medical harm, not a late ride. A "
                       f"conflict escalates to a human instead.")
    return True, "bumpable within the day's schedule"


# ---------------------------------------------------------------- the credential gate

REQUIRED_CREDS = ("license", "background", "cpr", "securement")


def can_assign(driver, ref=None):
    ref = ref or now()
    creds = driver.get("credentials") or {}
    missing, expired = [], []
    for c in REQUIRED_CREDS:
        exp = parse(creds.get(c))
        if not creds.get(c):
            missing.append(c)
        elif exp and exp < ref:
            expired.append(c)
    if missing or expired:
        parts = []
        if missing:
            parts.append(f"missing: {', '.join(missing)}")
        if expired:
            parts.append(f"expired: {', '.join(expired)}")
        return False, (f"cannot assign {driver.get('name', driver.get('id'))} — "
                       f"{'; '.join(parts)}. Securement training is what keeps a wheelchair "
                       f"where it belongs at 45mph.")
    return True, "credential set current"


def tomorrow_board(ref=None):
    ref = ref or now()
    rows = []
    for t in store.load("trips"):
        if t.get("completed_at") or t.get("demo_tag"):
            continue
        when = parse(t.get("scheduled_at"))
        if when and 0 <= (when - ref).total_seconds() <= 48 * 3600:
            rows.append({"trip": t["id"], "patient": t.get("patient_ref"),
                         "purpose": t.get("purpose"),
                         "never_bump": (t.get("purpose") or "").lower() in NEVER_BUMP,
                         "when": t.get("scheduled_at")})
    rows.sort(key=lambda r: r["when"] or "")
    return rows


def unbillable_board():
    rows = []
    for t in store.load("trips"):
        if not t.get("completed_at") or t.get("billed_at") or t.get("demo_tag"):
            continue
        okb, why = can_bill(t)
        if not okb:
            rows.append({"trip": t["id"], "patient": t.get("patient_ref"),
                         "amount": t.get("amount", 0), "why": why})
    return {"rows": rows, "value": round(sum(r["amount"] for r in rows), 2),
            "note": "completed work that cannot bill — counted from the logs"}


def recovered_this_week(ref=None):
    """Counted: trips billed with complete logs, condition changes escalated,
    trips completed."""
    ref = ref or now()
    billed = [t for t in store.load("trips")
              if t.get("billed_at") and (ref - (parse(t["billed_at"]) or ref)).days <= 7]
    escalated = sum(1 for e in store.events(kind="escalate_condition")
                    if (ref - (parse(e.get("at")) or ref)).days <= 7)
    completed = [t for t in store.load("trips")
                 if t.get("completed_at") and (ref - (parse(t["completed_at"]) or ref)).days <= 7]
    return {"trips_billed": len(billed),
            "billed_value": round(sum(t.get("amount", 0) for t in billed), 2),
            "condition_escalations": escalated, "trips_completed": len(completed),
            "note": "counted from the trip ledger and the event log — never asserted"}


# ---------------------------------------------------------------- eval

triage_eval = Eval("message triage",
                   costly_label="condition_change",
                   costly_note=("A CONDITION OBSERVATION ANSWERED WITH 'PROBABLY FINE' IS "
                                "SOFTWARE PRACTICING MEDICINE ON SOMEONE'S GRANDMOTHER. "
                                "Over-routing costs a call."))

EVAL_CASES = [
    {"input": "grandma seems confused today, more than usual", "label": "condition_change"},
    {"input": "mr osei couldn't stand up from the chair this morning", "label": "condition_change"},
    {"input": "she's slurring her words a little on the ride", "label": "condition_change"},
    {"input": "patient looks really pale and out of it", "label": "condition_change"},
    {"input": "driver says she fell getting into the van", "label": "condition_change"},
    {"input": "need to reschedule tuesday's pickup to the afternoon", "label": "schedule"},
    {"input": "can the ride come earlier on thursday", "label": "schedule"},
    {"input": "cancel friday's trip, appointment moved", "label": "schedule"},
    {"input": "the claim for last week's trips was denied", "label": "billing"},
    {"input": "invoice question on the march trips", "label": "billing"},
    {"input": "the van was 40 minutes late and she missed the appointment", "label": "complaint"},
    {"input": "driver didn't show for the 8am pickup", "label": "complaint"},
    {"input": "", "label": "human"},
    {"input": "what's the office number for the billing department", "label": "human"},
]


def run_eval():
    return triage_eval.run(EVAL_CASES, lambda t: read_message(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_message":        {"rung": "R3", "reason": "routing only; the condition read comes first"},
    "escalate_condition":  {"rung": "R2", "reason": "verbatim to a human and the facility — it cannot wait"},
    "assess_patient_condition": {"rung": "R0", "reason": "software never assesses, reassures, or says 'probably fine'", "never_promote": True},
    "bill_without_trip_log": {"rung": "R0", "reason": "an undocumented trip is free work with a Medicaid audit attached", "never_promote": True},
    "bump_protected_trip": {"rung": "R0", "reason": "a missed dialysis pickup is medical harm, not a late ride", "never_promote": True},
    "assign_uncredentialed_driver": {"rung": "R0", "reason": "securement training keeps the wheelchair where it belongs at 45mph", "never_promote": True},
    "draft_schedule_reply": {"rung": "R1", "reason": "outward reply — a human sends"},
    "draft_invoice":       {"rung": "R1", "reason": "money — a human bills, past the log gate"},
    "assign_driver":       {"rung": "R1", "reason": "an assignment is a promise — a human assigns, past the gate"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Ride OS — what it computes to")
        .line("Unbillable trips recovered", "revenue", "incomplete-log trips × avg trip (counted)",
              ["unbillable_value"], lambda g: float(g["unbillable_value"]),
              note="counted — completed work whose logs can still be completed")
        .line("Dispatch hours", "time_saved", "hrs/wk × 52 × rate",
              ["dispatch_hours_wk", "dispatch_rate"],
              lambda g: float(g["dispatch_hours_wk"]) * 52 * float(g["dispatch_rate"]))
        .line("The never-bump record", "scenario", "you decide what dialysis reliability is worth",
              ["reliability_value"], lambda g: float(g["reliability_value"]),
              assumption="never a saving — the rule is the product")
        .line("The securement file", "scenario", "credential discipline, priced by you",
              ["securement_value"], lambda g: float(g["securement_value"]),
              assumption="an exposure you weigh"))


def roi(given):
    rec = {}
    rec["unbillable_value"] = unbillable_board()["value"]
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("read_message", "escalate_condition", "draft_schedule_reply", "draft_invoice",
          "assign_driver")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("family:", "facility:"))
