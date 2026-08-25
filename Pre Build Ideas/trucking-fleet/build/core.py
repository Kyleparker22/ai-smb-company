#!/usr/bin/env python3
"""Hours OS — domain core (small trucking fleet).

Rules live here: the HOS dispatch gate (clock arithmetic by construction), log
discipline (software never edits or certifies a log; falsification requests
refused verbatim), detention evidence pairs, the accident protocol, the
maintenance calendar with the OOS gate, and the matrix.

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

TABLES = ("config", "drivers", "trucks", "loads", "messages", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="HOURSOS_DATA_ROOT")

HOS_BUFFER_H = 1.0

# ---------------------------------------------------------------- the dispatch gate

def can_dispatch(driver, load):
    """The load's run hours + buffer must fit the driver's RECORDED remaining
    clock. No recorded clock reads UNKNOWN and cannot be dispatched. The
    arithmetic is shown either way."""
    clock = driver.get("hos_remaining_h")
    if clock is None:
        return False, ("no recorded HOS clock for this driver — UNKNOWN cannot be dispatched; "
                       "the ELD syncs or the load waits. A guess here is the nuclear-verdict "
                       "scenario.")
    need = (load.get("run_hours") or 0) + HOS_BUFFER_H
    if clock < need:
        return False, (f"cannot dispatch — the run needs {load.get('run_hours')}h + "
                       f"{HOS_BUFFER_H}h buffer = {need}h, and the recorded clock shows "
                       f"{clock}h. The arithmetic decides; nobody talks anyone into it.")
    return True, (f"clock {clock}h covers {load.get('run_hours')}h + {HOS_BUFFER_H}h buffer — "
                  f"dispatchable")


def can_assign_truck(truck):
    if truck.get("oos_at"):
        return False, (f"truck {truck.get('unit', truck.get('id'))} is out of service "
                       f"({str(truck['oos_at'])[:10]}) — an OOS truck doesn't get assigned, "
                       f"it gets fixed")
    return True, "in service"


# ---------------------------------------------------------------- log discipline

def log_request(driver_id, requester, request_text):
    """Any request to edit/fix/certify a driver's log is refused and preserved
    verbatim — the falsification line, held shut."""
    ev = store.log_event("refused", driver_id, "agent:dispatch", "R0",
                        {"action": "edit_or_certify_log",
                         "requester": requester, "verbatim": request_text,
                         "why": "software never edits or certifies a log — and this request is "
                                "now part of the record"})
    return {"refused": ("a driver's log is the driver's sworn record. Annotations draft FOR the "
                        "driver to accept; nothing is ever edited for them — and this request is "
                        "now part of the record."), "event": ev["id"]}


# ---------------------------------------------------------------- detention

def detention_invoice(load):
    """Detention bills only from recorded arrival/departure stamps — the
    evidence pair. Free time and rate come from the recorded lane terms."""
    arr, dep = parse(load.get("arrived_at")), parse(load.get("departed_at"))
    if not arr or not dep:
        missing = [n for n, v in (("arrival stamp", arr), ("departure stamp", dep)) if not v]
        return {"refused": (f"cannot bill detention — missing: {', '.join(missing)}. 'We waited "
                            f"forever' is a feeling; stamps are an invoice.")}
    free_h = load.get("free_time_h")
    rate = load.get("detention_rate")
    if free_h is None or rate is None:
        return {"refused": "no recorded free-time/rate terms for this lane — the broker "
                           "conversation happens before the invoice, not inside it"}
    waited = (dep - arr).total_seconds() / 3600
    billable = max(0, waited - free_h)
    return {"waited_h": round(waited, 2), "free_h": free_h,
            "billable_h": round(billable, 2), "rate": rate,
            "total": round(billable * rate, 2),
            "basis": f"({round(waited, 1)}h at door − {free_h}h free) × ${rate}/h — from the stamps"}


# ---------------------------------------------------------------- accident protocol

PRESERVATION_BRIEF = {
    "checklist": ["ELD data for the tractor — export and hold, today",
                  "dash-cam footage — pull before overwrite",
                  "driver's phone records preserved, not reviewed",
                  "no statements to anyone's insurer before counsel",
                  "drug/alcohol testing per policy clock"],
    "rules": ["nothing outward is drafted by software after an accident",
              "no fault language in any internal note"],
    "note": "a preservation head start — counsel and the safety director drive from here"}

ACCIDENT = (
    r"\b(accident|crash|collision|hit (a|someone|another)|jack.?knif|rolled|rollover)\w*",
    r"\b(someone|somebody) (hit|rear.?ended) (me|us|the truck)\b",
)
DISPATCH_ASK = (
    r"\b(can|could) \w+ (take|run|cover|grab)\b.*\b(load|run|haul)\b",
    r"\b(dispatch|assign|send)\b.*\b(load|run)\b",
)
LOG_ASK = (
    r"\b(fix|edit|adjust|clean up|correct)\b.*\b(log|logs|eld|hours)\b",
    r"\b(log|logs|eld)\b.*\b(fix|edit|adjust|problem)\b",
)
DETENTION_MSG = (
    r"\b(detention|sat|waiting|waited)\b.*\b(dock|shipper|receiver|hours)\b",
    r"\bbeen (at|here)\b.*\b(dock|shipper)\b.*\bhours\b",
)
HOURS_ASK = (
    r"\b(how many|what('?s| are)) (hours|my hours)\b|\bhours (left|remaining)\b",
    r"\bclock\b.*\b(left|remaining|reset)\b",
)


def read_message(text):
    """accident | dispatch_ask | log_ask | detention | hours_ask | human.
    Accident first."""
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty message — a person reads it"}
    for rx in ACCIDENT:
        if re.search(rx, t):
            return {"label": "accident", "brief": PRESERVATION_BRIEF,
                    "why": "an accident — a human now; the preservation brief goes to the safety "
                           "director and software drafts nothing outward"}
    for rx in LOG_ASK:
        if re.search(rx, t):
            return {"label": "log_ask",
                    "why": "a log-edit request — the falsification line; refused and preserved "
                           "verbatim"}
    for rx in DETENTION_MSG:
        if re.search(rx, t):
            return {"label": "detention",
                    "why": "detention — bills from the recorded stamp pair or not at all"}
    for rx in DISPATCH_ASK:
        if re.search(rx, t):
            return {"label": "dispatch_ask", "why": "a dispatch ask — the clock arithmetic decides"}
    for rx in HOURS_ASK:
        if re.search(rx, t):
            return {"label": "hours_ask", "why": "an hours question — answered from the recorded ELD"}
    return {"label": "human", "why": "no clean signal — a person reads it"}


def maintenance_board(ref=None):
    ref = ref or now()
    rows = []
    for t in store.load("trucks"):
        if t.get("demo_tag"):
            continue
        odo, due = t.get("odometer"), t.get("service_due_odometer")
        if odo is None or due is None:
            rows.append({"truck": t.get("unit", t["id"]),
                         **unmeasured("no recorded odometer/interval — due state unknowable",
                                      field="miles_to_service")})
            continue
        rows.append({"truck": t.get("unit", t["id"]), "miles_to_service": due - odo,
                     "overdue": due - odo < 0, "oos": bool(t.get("oos_at"))})
    rows.sort(key=lambda r: (r.get("miles_to_service") is None, r.get("miles_to_service") or 0))
    return rows


def recovered_this_week(ref=None):
    """Counted: loads dispatched through the gate, detention billed from
    stamps, log-edit requests refused."""
    ref = ref or now()
    dispatched = sum(1 for e in store.events(kind="dispatch_load")
                     if str(e.get("actor", "")).startswith("human:")
                     and (ref - (parse(e.get("at")) or ref)).days <= 7)
    detention = 0.0
    for l in store.load("loads"):
        if l.get("detention_billed_at") and (ref - (parse(l["detention_billed_at"]) or ref)).days <= 7:
            inv = detention_invoice(l)
            detention += inv.get("total", 0) if "total" in inv else 0
    log_refusals = sum(1 for e in store.events(kind="refused")
                       if (e.get("detail") or {}).get("action") == "edit_or_certify_log"
                       and (ref - (parse(e.get("at")) or ref)).days <= 7)
    return {"loads_dispatched": dispatched, "detention_billed": round(detention, 2),
            "log_requests_refused": log_refusals,
            "note": "counted from the event log and the load ledger — never asserted"}


# ---------------------------------------------------------------- eval

triage_eval = Eval("message triage",
                   costly_label="log_ask",
                   costly_note=("A 'FIX HIS LOG' REQUEST GRANTED ONCE IS FALSIFICATION WITH THE "
                                "FLEET'S NAME ON IT — and one MISSED means it was granted by "
                                "accident. Over-routing costs a read."))

EVAL_CASES = [
    {"input": "can you fix his log from tuesday, he forgot to flag the break", "label": "log_ask"},
    {"input": "clean up the eld hours before the audit next week", "label": "log_ask"},
    {"input": "there's a log problem on truck 12, adjust it", "label": "log_ask"},
    {"input": "we had an accident on i-40, everyone is ok", "label": "accident"},
    {"input": "somebody rear-ended us at the light in the yard truck", "label": "accident"},
    {"input": "trailer jack-knifed on the ramp, no injuries", "label": "accident"},
    {"input": "can marcus take the memphis load tonight", "label": "dispatch_ask"},
    {"input": "dispatch the reefer run to whoever's closest", "label": "dispatch_ask"},
    {"input": "been at the dock four hours, shipper says another two", "label": "detention"},
    {"input": "sat at the receiver all morning waiting on a door", "label": "detention"},
    {"input": "how many hours does dana have left today", "label": "hours_ask"},
    {"input": "what's my clock looking like after the reset", "label": "hours_ask"},
    {"input": "", "label": "human"},
    {"input": "fuel card isn't working at the pilot", "label": "human"},
]


def run_eval():
    return triage_eval.run(EVAL_CASES, lambda t: read_message(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_message":       {"rung": "R3", "reason": "routing only; accident and log reads come first"},
    "dispatch_beyond_hours": {"rung": "R0", "reason": "the clock arithmetic decides — nobody talks anyone into it", "never_promote": True},
    "edit_or_certify_log": {"rung": "R0", "reason": "the falsification line — requests are refused and preserved verbatim", "never_promote": True},
    "assign_oos_truck":   {"rung": "R0", "reason": "an OOS truck gets fixed, not assigned", "never_promote": True},
    "draft_outward_after_accident": {"rung": "R0", "reason": "nothing outward from software after an accident — counsel drives", "never_promote": True},
    "dispatch_load":      {"rung": "R1", "reason": "a dispatch is a commitment — a human sends, past the clock gate"},
    "draft_detention_invoice": {"rung": "R1", "reason": "money — a human bills, from the stamps"},
    "brief_safety_director": {"rung": "R2", "reason": "the preservation brief cannot wait"},
    "maintenance_alert":  {"rung": "R2", "reason": "an internal alert; the interval is the point"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Hours OS — what it computes to")
        .line("Detention recovered with stamps", "revenue", "billable detention (counted)",
              ["detention_open"], lambda g: float(g["detention_open"]),
              note="computed from recorded stamp pairs and lane terms")
        .line("Dispatch hours", "time_saved", "hrs/wk × 52 × rate",
              ["dispatch_hours_wk", "dispatch_rate"],
              lambda g: float(g["dispatch_hours_wk"]) * 52 * float(g["dispatch_rate"]))
        .line("Violations avoided at the gate", "scenario", "your history × your exposure",
              ["violations_yr", "exposure_per"],
              lambda g: float(g["violations_yr"]) * float(g["exposure_per"]),
              assumption="prevented violations cannot be counted — this is your history priced by you")
        .line("The clean-log file", "scenario", "you decide what the refusal record is worth",
              ["log_value"], lambda g: float(g["log_value"]),
              assumption="never a saving — the refusals are the product"))


def roi(given):
    rec = {}
    total = 0.0
    for l in store.load("loads"):
        if l.get("detention_billed_at") or l.get("demo_tag"):
            continue
        inv = detention_invoice(l)
        if "total" in inv:
            total += inv["total"]
    rec["detention_open"] = round(total, 2)
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("read_message", "dispatch_load", "draft_detention_invoice",
          "brief_safety_director", "maintenance_alert")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("driver:", "broker:"))
