#!/usr/bin/env python3
"""Crew OS — domain core (commercial cleaning / janitorial).

Rules live here: night-report triage with the security bias, the access-info
refusal, the inspection-evidence rule behind every quality claim, coverage
with per-building access, and the matrix.

The thesis: a janitorial company holds keys to everyone else's buildings at
2am. Security discipline, access discipline, and evidence discipline are the
product; the cleaning is table stakes.

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

TABLES = ("config", "contracts", "crew", "reports", "inspections", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="CREWOS_DATA_ROOT")


# ---------------------------------------------------------------- triage

SECURITY = (
    r"\b(door|entrance|dock)\b.*\b(unlocked|open|propped|ajar|forced)\b|\bunlocked\b.*\bdoor\b",
    r"\balarm\b.*\b(going off|went off|tripped|sounding)\b|\bset off the alarm\b",
    r"\b(someone|stranger|person|guy)\b.*\b(inside|in the building|wouldn'?t leave)\b",
    r"\b(broken|smashed|shattered)\b.*\b(window|glass|lock)\b|"
    r"\b(window|glass|lock)\b.*\b(broken|smashed|shattered)\b|\bbreak-?in\b",
    r"\bsafe\b.*\bopen\b|\b(cash|laptop|equipment)\b.*\bmissing\b|"
    r"\bmissing\b.*\b(cash|laptop|equipment)\b",
)
ACCESS_REQUEST = (
    r"\b(what('?s| is)|need|send|text me)\b.*\b(alarm code|door code|gate code|lockbox|key ?code|combo)\b",
    r"\b(alarm|door|gate) code\b.*\?",
)
COMPLAINT = (
    r"\b(wasn'?t|weren'?t|not)\b.*\b(done|cleaned|emptied|vacuumed|mopped)\b",
    r"\b(missed|skipped)\b.*\b(trash|restrooms?|floors?|offices?|suites?)\b|"
    r"\b(trash|restrooms?|floors?|offices?|suites?)\b.*\b(missed|skipped)\b|"
    r"\bstill dirty\b|\bcomplaint\b",
)
SUPPLY = (r"\b(need|out of|low on|order)\b.*\b(liners?|towels?|soap|chemical|supplies|paper)\b",)


def classify_report(text):
    """security | access_request | complaint | supply | human."""
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty report — a person reads it"}
    for rx in SECURITY:
        if re.search(rx, t):
            return {"label": "security",
                    "why": "security incident — a human now; the client's building is our custody"}
    for rx in ACCESS_REQUEST:
        if re.search(rx, t):
            return {"label": "access_request",
                    "why": "access information never moves through this system — a supervisor "
                           "handles it by voice, on the client's own channel"}
    for rx in COMPLAINT:
        if re.search(rx, t):
            return {"label": "complaint",
                    "why": "quality complaint — the reply cites the last inspection, or admits there is none"}
    for rx in SUPPLY:
        if re.search(rx, t):
            return {"label": "supply", "why": "supply request — draft at R1"}
    return {"label": "human", "why": "no clean signal — a person reads it"}


# ---------------------------------------------------------------- inspection evidence

INSPECTION_WINDOW_DAYS = 14


def clean_claim(contract_id, ref=None):
    """'Cleaned per spec' is assertable only with an inspection record inside
    the window. Otherwise: cannot assert — and the reply says so honestly."""
    ref = ref or now()
    recs = [i for i in store.load("inspections")
            if i.get("contract_id") == contract_id
            and (parse(i.get("at")) or ref) >= ref - timedelta(days=INSPECTION_WINDOW_DAYS)]
    if not recs:
        return {"assertable": False,
                "refused": f"cannot assert 'cleaned per spec' — no inspection record inside "
                           f"{INSPECTION_WINDOW_DAYS} days. The honest reply admits that and "
                           f"books one, rather than arguing without evidence."}
    latest = max(recs, key=lambda i: i["at"])
    return {"assertable": True, "inspection": latest["id"], "at": latest["at"],
            "score": latest.get("score"),
            "note": "the reply cites this record — a claim with evidence behind it"}


# ---------------------------------------------------------------- coverage

def coverage_board(ref=None):
    """Tonight's contracts vs assigned crew; the uncovered ones ranked, and a
    candidate without recorded access to the building is never proposed."""
    crew = store.load("crew")
    rows, uncovered = [], []
    for c in store.load("contracts"):
        if c.get("demo_tag"):
            continue
        assigned = [m for m in crew if c["id"] in (m.get("assigned") or [])
                    and not m.get("out_tonight")]
        if assigned:
            rows.append({"contract": c["name"], "crew": [m["name"] for m in assigned]})
            continue
        candidates, blocked = [], []
        for m in crew:
            if m.get("out_tonight"):
                continue
            if c["id"] not in (m.get("access") or []):
                blocked.append({"who": m["name"],
                                "why": "no recorded access to this building — a stranger with no "
                                       "key is not a fill, and access is never improvised"})
                continue
            candidates.append({"who": m["name"], "buildings": len(m.get("access") or [])})
        uncovered.append({"contract": c["name"], "contract_id": c["id"],
                          "value_month": c.get("value_month"),
                          "candidates": candidates[:5], "blocked": blocked[:5]})
    return {"covered": len(rows), "uncovered": uncovered}


def recovered_this_week(ref=None):
    """Counted, never asserted: complaint replies a human sent, security
    incidents a human closed, coverage gaps filled, inside 7 days."""
    ref = ref or now()
    replies = closed = coverage = 0
    for e in store.events():
        at = parse(e.get("at"))
        if not at or (ref - at).days > 7:
            continue
        human = str(e.get("actor", "")).startswith("human:")
        if e["kind"] == "draft_complaint_reply" and human:
            replies += 1
        elif e["kind"] == "incident_closed" and human:
            closed += 1
        elif e["kind"] == "propose_coverage" and human:
            coverage += 1
    return {"replies_sent": replies, "incidents_closed": closed, "coverage_filled": coverage,
            "note": "counted from the event log — never asserted"}


# ---------------------------------------------------------------- eval

report_eval = Eval("night-report triage",
                   costly_label="security",
                   costly_note=("A SECURITY INCIDENT IN A GROUP CHAT UNTIL MONDAY IS HOW A "
                                "JANITORIAL COMPANY LOSES A CLIENT AND MEETS ITS INSURER. "
                                "Escalating a trash complaint costs a shrug."))

EVAL_CASES = [
    {"input": "found the back door unlocked when we arrived", "label": "security"},
    {"input": "alarm was going off when the crew got to suite 400", "label": "security"},
    {"input": "there was a guy inside who wouldn't leave, we left", "label": "security"},
    {"input": "window by the loading dock is smashed", "label": "security"},
    {"input": "client says a laptop is missing from the 3rd floor", "label": "security"},
    {"input": "what's the alarm code for the medical building?", "label": "access_request"},
    {"input": "can you text me the lockbox combo for suite 200", "label": "access_request"},
    {"input": "restrooms on 3 weren't done last night per the client", "label": "complaint"},
    {"input": "trash was missed in the corner offices again", "label": "complaint"},
    {"input": "we're out of liners and low on towels at the bank", "label": "supply"},
    {"input": "", "label": "human"},
    {"input": "crew got done early, all good tonight", "label": "human"},
    {"input": "loading dock door was propped open with a brick", "label": "security"},
    {"input": "need the door code for the annex tonight", "label": "access_request"},
    {"input": "floors on 2 still dirty according to the property manager", "label": "complaint"},
    {"input": "out of soap and almost out of paper at the courthouse", "label": "supply"},
    {"input": "client's office manager says the safe was open when they arrived", "label": "security"},
]


def run_eval():
    return report_eval.run(EVAL_CASES, lambda t: classify_report(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "classify_report":    {"rung": "R3", "reason": "routing with a security bias; the queue is visible"},
    "escalate_security":  {"rung": "R2", "reason": "act now, tell the human — the building is our custody"},
    "close_security_incident": {"rung": "R0", "reason": "a human closes a security incident after follow-up with the client", "never_promote": True},
    "share_access_info":  {"rung": "R0", "reason": "codes, keys and combos never move through this system — one leaked thread is a breach", "never_promote": True},
    "assert_cleaned_without_inspection": {"rung": "R0", "reason": "a quality claim without an inspection record is an argument, not an answer", "never_promote": True},
    "draft_complaint_reply": {"rung": "R1", "reason": "outward reply — a human sends, citing the inspection or admitting none"},
    "draft_supply_order": {"rung": "R1", "reason": "money — a human orders"},
    "propose_coverage":   {"rung": "R2", "reason": "a proposal with the blockers named; assignment stays human"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Crew OS — what it computes to")
        .line("Uncovered nights caught", "revenue", "uncovered contracts × monthly value × churn share",
              ["uncovered", "avg_contract_month", "churn_share"],
              lambda g: float(g["uncovered"]) * float(g["avg_contract_month"]) * 12 * float(g["churn_share"]),
              note="uncovered is counted tonight; the churn share is your call")
        .line("Relay and dispatch time", "time_saved", "hrs/wk × 52 × rate",
              ["relay_hours_wk", "supervisor_rate"],
              lambda g: float(g["relay_hours_wk"]) * 52 * float(g["supervisor_rate"]))
        .line("Evidence-backed disputes", "scenario", "disputes/yr × avg contract shrinkage",
              ["disputes_yr", "avg_shrinkage"],
              lambda g: float(g["disputes_yr"]) * float(g["avg_shrinkage"]),
              assumption="an exposure you weigh — won arguments cannot be counted")
        .line("The access discipline", "scenario", "you decide what never-leaked-a-code is worth",
              ["access_value"], lambda g: float(g["access_value"]),
              assumption="never a saving — yours or blank"))


def roi(given):
    rec = {}
    cb = coverage_board()
    rec["uncovered"] = len(cb["uncovered"])
    values = [c.get("value_month") for c in store.load("contracts") if c.get("value_month")]
    if len(values) >= 20:
        rec["avg_contract_month"] = round(median(values), 2)
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("classify_report", "escalate_security", "draft_complaint_reply", "draft_supply_order",
          "propose_coverage")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("client:",))
