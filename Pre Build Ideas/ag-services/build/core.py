#!/usr/bin/env python3
"""Field OS — domain core (agricultural services / custom application).

Rules live here: drift-first complaint triage with regulator-grade logging,
the as-applied billing gate, the RUP dispatch gate, the chemical-question
refusal, and the matrix.

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

TABLES = ("config", "growers", "jobs", "messages", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="FIELDOS_DATA_ROOT")

COMPLAINT_PROTOCOL = ("Logged with timestamp, caller, location, and their words verbatim. A human "
                      "calls back within the hour. The system asserts nothing about cause — "
                      "acknowledging is not admitting, and denying is not investigating.")

# ---------------------------------------------------------------- triage

DRIFT_EXPOSURE = (
    r"\b(spray(ed)?|drift(ed)?|mist|cloud|plane|rig)\b.*\b(my|our|the neighbor'?s?)\b.*"
    r"\b(garden|tomatoes|trees|crop|beans|yard|pasture|pond|hives?)\b",
    r"\b(tomatoes|leaves|garden|trees|beans)\b.*\b(curl(ing)?|wilt(ing)?|dying|burn(ed|t)?)\b",
    r"\bbees?\b.*\b(dying|dead|kill)\b|\bhives?\b.*\b(dead|collapse|dying)\b",
    r"\b(kids?|children|family|we) (were|was) (outside|in the yard)\b.*\b(spray|plane|went over)\b",
    r"\b(cattle|horses?|livestock|dog|chickens)\b.*\b(sick|acting|since (you|the) spray)\b",
    r"\b(smell(ed)?|taste)\b.*\bspray\b.*\b(house|inside|windows)\b",
)
CHEMICAL_QUESTION = (
    r"\b(what|which|how much)\b.*\b(rate|chemical|product|mix)\b",
    r"\bcan (i|you) (mix|tank.?mix|combine)\b",
    r"\bwhat should (i|we) spray\b|\bwhat do you recommend for\b.*\b(aphids?|rust|weeds?|fungus|beetles?)\b",
)
WORK_REQUEST = (
    r"\b(spray|spread|apply|fertilize|top.?dress)\b.*\b(my|our|the)\b.*\b(beans?|corn|wheat|"
    r"pasture|field|acres?|quarter)\b",
    r"\bget (my|our|the)\b.*\b(sprayed|spread|covered|done)\b|\bbook (me|us) in\b",
)


def read_message(text):
    """drift_exposure | chemical_question | work_request | human. Drift reads
    first — always; the complaint file starts at the first word."""
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty message — a person reads it"}
    for rx in DRIFT_EXPOSURE:
        if re.search(rx, t):
            return {"label": "drift_exposure", "protocol": COMPLAINT_PROTOCOL,
                    "why": "possible drift/exposure complaint — the first hour decides whether "
                           "this file is defensible; a human calls, the log is regulator-grade"}
    for rx in CHEMICAL_QUESTION:
        if re.search(rx, t):
            return {"label": "chemical_question",
                    "why": "chemical/rate question — the label is the law; a licensed agronomist "
                           "answers, never software"}
    for rx in WORK_REQUEST:
        if re.search(rx, t):
            return {"label": "work_request", "why": "work request — job draft at R1"}
    return {"label": "human", "why": "no clean signal — a person reads it"}


# ---------------------------------------------------------------- the as-applied gate

AS_APPLIED_FIELDS = ("acres", "product", "rate", "applied_at", "applicator_license")


def can_bill(job):
    """A job bills only with its complete as-applied record."""
    rec = job.get("as_applied") or {}
    missing = [f for f in AS_APPLIED_FIELDS if not rec.get(f)]
    if missing:
        return False, (f"cannot bill — as-applied record missing: {', '.join(missing)}. An "
                       f"application without its record is unprovable work, and unprovable work "
                       f"is a dispute.")
    return True, (f"{rec['acres']} acres of {rec['product']} at {rec['rate']} on "
                  f"{str(rec['applied_at'])[:10]} by license {rec['applicator_license']}")


# ---------------------------------------------------------------- the RUP gate

def can_dispatch(job):
    """A restricted-use product needs a licensed applicator on the order
    BEFORE the rig leaves the yard."""
    if not job.get("rup"):
        return True, "general-use product — dispatches on the schedule"
    if job.get("applicator_license"):
        return True, f"RUP with licensed applicator {job['applicator_license']} on the order"
    return False, ("a restricted-use product cannot be dispatched without a licensed applicator "
                   "recorded on the order — the violation happens before the rig leaves the yard")


# ---------------------------------------------------------------- job board

def job_board(ref=None):
    ref = ref or now()
    rows = []
    for j in store.load("jobs"):
        if j.get("billed_at") or j.get("demo_tag"):
            continue
        age = (ref - (parse(j.get("requested_at")) or ref)).days
        okd, dispatch_why = can_dispatch(j)
        okb, bill_why = can_bill(j)
        rows.append({"job": j["id"], "grower": j.get("grower"), "desc": j.get("desc"),
                     "age_days": age, "rup": bool(j.get("rup")),
                     "dispatchable": okd, "dispatch_why": dispatch_why,
                     "billable": okb, "window_note": j.get("window_note")})
    rows.sort(key=lambda r: -r["age_days"])
    return rows


def recovered_this_week(ref=None):
    """Counted, never asserted: invoices a human sent, jobs a human dispatched,
    and complaints logged regulator-grade, inside 7 days."""
    ref = ref or now()
    invoices = dispatched = complaints = 0
    for e in store.events():
        at = parse(e.get("at"))
        if not at or (ref - at).days > 7:
            continue
        human = str(e.get("actor", "")).startswith("human:")
        if e["kind"] == "draft_invoice" and human:
            invoices += 1
        elif e["kind"] == "dispatch_job" and human:
            dispatched += 1
        elif e["kind"] == "log_complaint":
            complaints += 1
    return {"invoices_sent": invoices, "jobs_dispatched": dispatched,
            "complaints_logged": complaints,
            "note": "counted from the event log — never asserted"}


# ---------------------------------------------------------------- eval

triage_eval = Eval("complaint & message triage",
                   costly_label="drift_exposure",
                   costly_note=("A DRIFT COMPLAINT HANDLED CASUALLY IS A STATE-INVESTIGATION "
                                "EXHIBIT. Handled in the first hour — logged, acknowledged, "
                                "escalated — it is a defensible file. Over-routing costs a call."))

EVAL_CASES = [
    {"input": "your rig sprayed right up to my fence and now my tomatoes are curling", "label": "drift_exposure"},
    {"input": "bees are dying all over my hives since tuesday", "label": "drift_exposure"},
    {"input": "the kids were outside when your plane went over our place", "label": "drift_exposure"},
    {"input": "my cattle have been acting sick since you sprayed the neighbor's quarter", "label": "drift_exposure"},
    {"input": "we could smell the spray inside the house with the windows open", "label": "drift_exposure"},
    {"input": "what rate of atrazine should I run on my corn", "label": "chemical_question"},
    {"input": "can you mix the fungicide with the foliar feed in one pass", "label": "chemical_question"},
    {"input": "can you get my beans sprayed this week before the rain", "label": "work_request"},
    {"input": "book me in for fall spreading on the north quarter", "label": "work_request"},
    {"input": "", "label": "human"},
    {"input": "invoice looks good, check is in the mail", "label": "human"},
    {"input": "the mist off your rig settled over our pond yesterday", "label": "drift_exposure"},
    {"input": "our chickens have been acting sick since the spray plane came over", "label": "drift_exposure"},
    {"input": "what should I spray for aphids on the beans", "label": "chemical_question"},
    {"input": "top-dress the wheat on the home quarter when you can", "label": "work_request"},
    {"input": "leave the gate open when you finish tonight", "label": "human"},
]


def run_eval():
    return triage_eval.run(EVAL_CASES, lambda t: read_message(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_message":       {"rung": "R3", "reason": "routing only; the drift-first read is the point"},
    "log_complaint":      {"rung": "R2", "reason": "the regulator-grade log entry cannot wait for a click"},
    "recommend_chemical_or_rate": {"rung": "R0", "reason": "the label is the law — a licensed agronomist recommends", "never_promote": True},
    "assert_drift_cause": {"rung": "R0", "reason": "the system logs and escalates; causation is the investigation's job", "never_promote": True},
    "bill_without_as_applied": {"rung": "R0", "reason": "an application without its record is unprovable work", "never_promote": True},
    "dispatch_rup_unlicensed": {"rung": "R0", "reason": "the violation happens before the rig leaves the yard", "never_promote": True},
    "draft_job":          {"rung": "R1", "reason": "a job is a promise of a weather window — a human books"},
    "draft_invoice":      {"rung": "R1", "reason": "money — a human sends, past the as-applied gate"},
    "dispatch_job":       {"rung": "R1", "reason": "a rig roll — a human dispatches, past the RUP gate"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Field OS — what it computes to")
        .line("Acres billed provably", "revenue", "unbilled billable jobs × avg job value",
              ["billable_unbilled", "avg_job"],
              lambda g: float(g["billable_unbilled"]) * float(g["avg_job"]),
              note="billable-with-records is counted; the value is your book")
        .line("Office and records time", "time_saved", "hrs/wk × 52 × rate",
              ["office_hours_wk", "office_rate"],
              lambda g: float(g["office_hours_wk"]) * 52 * float(g["office_rate"]))
        .line("The complaint-file discipline", "scenario", "you decide what a defensible file is worth",
              ["complaint_value"], lambda g: float(g["complaint_value"]),
              assumption="never a saving — a state investigation is not our number to model")
        .line("Missed weather windows", "scenario", "windows missed/yr × avg acres × margin",
              ["windows_missed_yr", "avg_window_acres", "margin_acre"],
              lambda g: float(g["windows_missed_yr"]) * float(g["avg_window_acres"]) * float(g["margin_acre"]),
              assumption="an exposure you weigh"))


def roi(given):
    rec = {}
    board = job_board()
    rec["billable_unbilled"] = sum(1 for r in board if r["billable"])
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("read_message", "log_complaint", "draft_job", "draft_invoice", "dispatch_job")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("grower:", "neighbor:"))
