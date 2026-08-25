#!/usr/bin/env python3
"""Rig OS — domain core (crane & rigging).

Rules live here: critical-lift RFQ flags (Traveler pattern), the operator
certification gate per crane class, the lift-plan rule (software never
approves one), the wind gate by arithmetic, site-data quoting, and the matrix.

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

TABLES = ("config", "cranes", "operators", "rfqs", "lifts", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="RIGOS_DATA_ROOT")

# ---------------------------------------------------------------- critical-lift flags

CRITICAL_SIGNALS = (
    ("near_capacity", r"\b(7[5-9]|[89]\d|100)\s?%\b|\bnear (max|capacity|the chart)\b|\bheavy for the\b"),
    ("over_occupied", r"\b(over|above)\b.*\b(occupied|building|school|store|office|roof with people|crowd)\b",),
    ("multi_crane", r"\b(two|both|tandem|dual)\b.*\bcranes?\b|\btandem (lift|pick)\b"),
    ("personnel", r"\b(man ?basket|personnel platform|lift (the )?(guys|crew|workers))\b"),
    ("special", r"\bblind (lift|pick)\b|\bover (the )?water\b|\bnight (lift|pick)\b"),
)


def rfq_flags(text):
    t = (text or "").lower()
    flags = [kind for kind, rx in CRITICAL_SIGNALS if re.search(rx, t)]
    return {"critical": bool(flags), "flags": flags,
            "why": ("critical-lift signals: " + ", ".join(flags)) if flags
                   else "no critical signals — quotable as standard taxi work"}


# ---------------------------------------------------------------- the cert gate

def can_assign_operator(operator, crane, ref=None):
    ref = ref or now()
    certs = operator.get("certs") or {}
    need = crane.get("cert_class")
    exp = parse(certs.get(need))
    if not certs.get(need):
        return False, (f"cannot assign {operator.get('name')} to the {crane.get('desc')} — no "
                       f"recorded {need} certification. The class matters: a TSS card doesn't "
                       f"swing a lattice boom.")
    if exp and exp < ref:
        return False, (f"cannot assign {operator.get('name')} — {need} certification expired "
                       f"{str(certs[need])[:10]}")
    return True, f"{need} certification current"


# ---------------------------------------------------------------- the lift-plan rule

def can_schedule_lift(lift):
    """A critical lift needs a recorded engineered plan REFERENCE. Software
    never approves a plan — it checks that one exists and who signed it."""
    if not lift.get("critical"):
        return True, "standard lift — schedules on the calendar"
    plan = lift.get("lift_plan")
    if plan and plan.get("ref") and plan.get("signed_by"):
        return True, (f"critical lift with engineered plan {plan['ref']} signed by "
                      f"{plan['signed_by']} on file — software checked the record exists, "
                      f"nothing more")
    return False, ("a critical lift cannot be scheduled without a recorded engineered lift plan "
                   "and its signer. Software never approves a plan — the lift director signs, "
                   "and this system only checks the record exists.")


# ---------------------------------------------------------------- the wind gate

def can_dispatch_today(lift, forecast_mph=None):
    limit = lift.get("wind_limit_mph")
    if limit is None:
        return False, ("no recorded wind limit for this configuration — the chart's number gets "
                       "recorded or the crane doesn't leave; a guess is not a limit")
    if forecast_mph is None:
        return False, "no recorded forecast — dispatch waits for the number"
    if forecast_mph > limit:
        return False, (f"forecast {forecast_mph}mph exceeds the configuration's recorded "
                       f"{limit}mph limit — the arithmetic stands the job down; a human may only "
                       f"agree with it")
    return True, f"forecast {forecast_mph}mph inside the {limit}mph limit"


# ---------------------------------------------------------------- site-data quoting

SITE_FIELDS = ("radius_ft", "weight_lbs", "obstructions_noted")


def can_quote_firm(rfq):
    missing = [f for f in SITE_FIELDS if rfq.get(f) in (None, "")]
    if missing:
        return False, (f"no firm number without site data — missing: {', '.join(missing)}. "
                       f"It quotes as estimate-pending-site-visit instead; a wrong radius is a "
                       f"change-order fight or a tipped crane.")
    return True, f"site data recorded: {rfq['weight_lbs']}lbs at {rfq['radius_ft']}ft"


def recovered_this_week(ref=None):
    """Counted: lifts completed, quotes a human sent, cert lapses caught."""
    ref = ref or now()
    completed = [l for l in store.load("lifts")
                 if l.get("completed_at") and (ref - (parse(l["completed_at"]) or ref)).days <= 7]
    quotes = sum(1 for e in store.events(kind="draft_quote")
                 if str(e.get("actor", "")).startswith("human:")
                 and (ref - (parse(e.get("at")) or ref)).days <= 7)
    lapses = sum(1 for e in store.events(kind="cert_alert")
                 if (ref - (parse(e.get("at")) or ref)).days <= 7)
    return {"lifts_completed": len(completed), "quotes_sent": quotes, "cert_lapses_caught": lapses,
            "note": "counted from the lift ledger and the event log — never asserted"}


# ---------------------------------------------------------------- eval

flag_eval = Eval("critical-lift flags",
                 costly_label="critical",
                 costly_note=("A CRITICAL LIFT QUOTED AS TAXI WORK GETS PLANNED ON A PHONE CALL — "
                              "and cranes that tip were all 'routine' that morning. Over-flagging "
                              "costs an engineering review."))

EVAL_CASES = [
    {"input": "set trusses over the occupied school gym wing", "label": "critical"},
    {"input": "tandem pick with both cranes for the vessel", "label": "critical"},
    {"input": "need a man basket for the crew at the stack", "label": "critical"},
    {"input": "load's heavy for the 90-tonner, probably 85% of chart", "label": "critical"},
    {"input": "blind pick over the back of the building", "label": "critical"},
    {"input": "night lift over the water at the marina", "label": "critical"},
    {"input": "set two hvac units on a strip mall roof, sunday morning closed", "label": "standard"},
    {"input": "hang steel for a two-story frame, open site", "label": "standard"},
    {"input": "lift a hot tub over a one-story ranch house, nobody home", "label": "standard"},
    {"input": "set a generator beside the substation access road", "label": "standard"},
]


def run_eval():
    return flag_eval.run(EVAL_CASES,
                         lambda t: "critical" if rfq_flags(t)["critical"] else "standard")


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "scan_rfq":           {"rung": "R3", "reason": "flagging only; the flags force the engineering path"},
    "approve_lift_plan":  {"rung": "R0", "reason": "the lift director signs — software only checks the record exists", "never_promote": True},
    "assign_uncertified_operator": {"rung": "R0", "reason": "a TSS card doesn't swing a lattice boom", "never_promote": True},
    "dispatch_over_wind_limit": {"rung": "R0", "reason": "the arithmetic stands the job down; a human may only agree", "never_promote": True},
    "quote_critical_as_taxi": {"rung": "R0", "reason": "the flags force the engineering path — no shortcut exists", "never_promote": True},
    "quote_firm_without_site_data": {"rung": "R0", "reason": "a wrong radius is a change-order fight or a tipped crane", "never_promote": True},
    "draft_quote":        {"rung": "R1", "reason": "money — a human sends"},
    "schedule_lift":      {"rung": "R1", "reason": "a crane day is a promise — a human books, past the gates"},
    "cert_alert":         {"rung": "R2", "reason": "an internal date alert; expiry grounds silently otherwise"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Rig OS — what it computes to")
        .line("Quotes turned inside the window", "revenue", "RFQs/mo × close lift × avg job",
              ["rfqs_mo", "close_lift", "avg_job"],
              lambda g: float(g["rfqs_mo"]) * 12 * float(g["close_lift"]) * float(g["avg_job"]))
        .line("Cranes kept off silent grounding", "revenue", "lapses caught × avg crane-day",
              ["lapses_caught", "avg_crane_day"],
              lambda g: float(g["lapses_caught"]) * float(g["avg_crane_day"]))
        .line("Scheduling hours", "time_saved", "hrs/wk × 52 × rate",
              ["office_hours_wk", "office_rate"],
              lambda g: float(g["office_hours_wk"]) * 52 * float(g["office_rate"]))
        .line("The lift-plan file", "scenario", "you decide what the record discipline is worth",
              ["plan_value"], lambda g: float(g["plan_value"]),
              assumption="never a saving — a crane that didn't tip is not our number to model"))


def roi(given):
    rec = {}
    rec["lapses_caught"] = sum(1 for e in store.events(kind="cert_alert"))
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("scan_rfq", "draft_quote", "schedule_lift", "cert_alert")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("gc:",))
