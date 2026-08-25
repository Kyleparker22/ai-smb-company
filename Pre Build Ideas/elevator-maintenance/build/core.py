#!/usr/bin/env python3
"""Cab OS — domain core (elevator & escalator maintenance).

Rules live here: entrapment-first triage with the never-self-evacuate script,
the test calendar (no record reads UNKNOWN), the scope engine (clause or
ambiguous, never billable off silence), red-tag discipline, and the matrix.

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

TABLES = ("config", "buildings", "units", "calls", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="CABOS_DATA_ROOT")

ENTRAPMENT_SCRIPT = ("ENTRAPMENT PROTOCOL: a mechanic is dispatched NOW and the building contact "
                     "is being called. Desk script, verbatim: stay on the line with the "
                     "passengers, tell them the car is the safest place to be, and NEVER advise "
                     "or allow self-evacuation — most elevator fatalities are people climbing "
                     "out of stalled cars, not people waiting in them.")

TEST_INTERVALS = {"cat1": 365, "cat5": 365 * 5}

# ---------------------------------------------------------------- triage

NOBODY_INSIDE = r"\b(nobody|no ?one|empty|no passengers?)\b.*\binside\b|\bnobody in\b"
ENTRAPMENT = (
    r"\b(stuck|trapped|shut) in (the |an )?elevator\b|\belevator\b.*\b(stuck|trapped|won'?t open)\b",
    r"\b(people|someone|passengers?|kids?|we'?re?)\b.*\b(inside|in the car|in there)\b",
    r"\b(inside|someone|people)\b.*\bdoors won'?t open\b",
    r"\b(stuck|trapped)\b.*\bbetween floors\b|"
    r"\bbetween floors\b.*\b(stuck|trapped|people|someone|kids?)\b|"
    r"\bdoors won'?t open\b.*\b(inside|people)\b",
)
UNIT_DOWN = (
    r"\b(elevator|escalator|lift|car)\b.*\b(down|out|dead|not (working|running)|stopped|broken|"
    r"won'?t (open|close|start|move|restart))\b",
    r"\b(down|out of service)\b.*\b(elevator|escalator)\b",
)
NOISE = (
    r"\b(grinding|squeal|clunk|bang|shudder|jerk|vibrat)\w*\b.*\b(elevator|escalator|car|ride)\b",
    r"\b(elevator|escalator|ride|car)\b.*\b(grinding|squeal|clunk|bang|shudder|jerk|rough|vibrat)\w*",
)
INSPECTION = (
    r"\b(cat ?[15]|annual|inspection|test)\b.*\b(due|schedule|book|when|coming)\b",
    r"\b(schedule|book)\b.*\b(test|inspection)\b",
)


def read_call(text):
    """entrapment | unit_down | noise | inspection | human. Entrapment first —
    a human in the box, minutes matter, the words matter."""
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty call — a person answers"}
    nobody = re.search(NOBODY_INSIDE, t)
    for rx in ENTRAPMENT:
        if re.search(rx, t) and not nobody:
            return {"label": "entrapment", "script": ENTRAPMENT_SCRIPT,
                    "why": "a human in the car — mechanic dispatched NOW, and the desk script "
                           "never allows self-evacuation (only an explicit 'nobody inside' "
                           "downgrades this read)"}
    for rx in UNIT_DOWN:
        if re.search(rx, t):
            return {"label": "unit_down", "why": "unit out of service — dispatch drafts"}
    for rx in NOISE:
        if re.search(rx, t):
            return {"label": "noise", "why": "ride-quality complaint — a mechanic visit drafts"}
    for rx in INSPECTION:
        if re.search(rx, t):
            return {"label": "inspection", "why": "test scheduling — from the unit calendar"}
    return {"label": "human", "why": "no clean signal — a person answers"}


# ---------------------------------------------------------------- the test calendar

def unit_state(u, ref=None):
    """Per-test state. A unit with no test record reads UNKNOWN, never
    compliant."""
    ref = ref or now()
    out = {"unit": u["id"], "building": u.get("building"), "tests": {}}
    for test, interval in TEST_INTERVALS.items():
        last = parse((u.get("tests") or {}).get(test))
        if not last:
            out["tests"][test] = {"state": "unknown",
                                  "why": "no test record — UNKNOWN, never compliant"}
            continue
        due = last + timedelta(days=interval)
        days = (due - ref).days
        out["tests"][test] = {"state": "overdue" if days < 0 else "due" if days <= 60 else "current",
                              "due": iso(due), "days": days}
    out["red_tagged"] = bool(u.get("red_tagged_at"))
    return out


def can_reactivate(u, mechanic_signoff=None):
    """A red-tagged unit returns to service only with the clearing mechanic's
    recorded sign-off. Software can never do it."""
    if not u.get("red_tagged_at"):
        return True, "not red-tagged"
    if mechanic_signoff:
        return True, f"cleared by recorded mechanic sign-off {mechanic_signoff}"
    return False, ("this unit is red-tagged. It returns to service with the clearing mechanic's "
                   "recorded sign-off and nothing else — somebody turning a red-tagged unit back "
                   "on is how the next entrapment becomes a fatality investigation.")


# ---------------------------------------------------------------- the scope engine

CATEGORY_PATTERNS = (
    ("lamp_cosmetic", r"\b(lamp|bulb|light|button|cosmetic|panel scratch)\b"),
    ("door_operator", r"\b(door (operator|roller|track)|doors? (slow|sticking))\b"),
    ("controller", r"\b(controller|board|drive|breaker)\b"),
    ("vandalism", r"\b(vandal|kicked|graffiti|pried)\b"),
    ("modernization", r"\b(modern|upgrade|replace the (car|cab)|new controller)\b"),
)


def categorize(text):
    t = (text or "").lower()
    for cat, rx in CATEGORY_PATTERNS:
        if re.search(rx, t):
            return cat
    return None


def scope_check(unit, work_desc):
    """in_contract (clause cited) | billable (exclusion cited) | ambiguous
    (a human decides). Never billable off silence."""
    b = store.by_id("buildings", unit.get("building_id")) or {}
    contract = b.get("contract") or {}
    cat = categorize(work_desc)
    if not cat:
        return {"verdict": "ambiguous", "category": None,
                "why": "no category matched — a human reads the ticket"}
    for cl in contract.get("includes", []):
        if cat in cl.get("covers", []):
            return {"verdict": "in_contract", "category": cat, "clause": cl["id"],
                    "clause_text": cl["text"], "why": f"covered by clause {cl['id']}"}
    for cl in contract.get("excludes", []):
        if cat in cl.get("covers", []):
            return {"verdict": "billable", "category": cat, "clause": cl["id"],
                    "clause_text": cl["text"],
                    "why": f"excluded by clause {cl['id']} — billable draft, a human bills"}
    return {"verdict": "ambiguous", "category": cat,
            "why": f"the contract neither includes nor excludes {cat!r} — a human decides; "
                   f"billable is never asserted off silence"}


def callback_rate(window_days=90):
    """Callbacks (repeat trouble call, same unit, ≤14 days) — counted, floor 30."""
    cutoff = now() - timedelta(days=window_days)
    calls = sorted((c for c in store.load("calls")
                    if c.get("label") in ("unit_down", "noise") and c.get("unit_id")
                    and (parse(c.get("at")) or now()) >= cutoff),
                   key=lambda c: c.get("at") or "")
    if len(calls) < 30:
        return unmeasured(f"only {len(calls)} trouble calls in {window_days} days — need 30",
                          field="rate", n=len(calls))
    callbacks, seen = 0, {}
    for c in calls:
        prior = seen.get(c["unit_id"])
        if prior and (parse(c["at"]) - parse(prior["at"])).days <= 14:
            callbacks += 1
        seen[c["unit_id"]] = c
    return {"rate": round(callbacks / len(calls), 3), "callbacks": callbacks, "of": len(calls),
            "note": "same unit inside 14 days — counted, not asserted"}


def recovered_this_week(ref=None):
    """Counted: entrapments resolved, tests completed, billables a human sent."""
    ref = ref or now()
    entrapments = sum(1 for e in store.events(kind="dispatch_entrapment")
                      if (ref - (parse(e.get("at")) or ref)).days <= 7)
    tested = 0
    for u in store.load("units"):
        for t, at in (u.get("tests") or {}).items():
            if at and (ref - (parse(at) or ref)).days <= 7:
                tested += 1
    billables = sum(1 for e in store.events(kind="draft_billable")
                    if str(e.get("actor", "")).startswith("human:")
                    and (ref - (parse(e.get("at")) or ref)).days <= 7)
    return {"entrapments_dispatched": entrapments, "tests_recorded": tested,
            "billables_sent": billables,
            "note": "counted from the unit records and the event log — never asserted"}


# ---------------------------------------------------------------- eval

triage_eval = Eval("call triage",
                   costly_label="entrapment",
                   costly_note=("AN ENTRAPMENT READ AS A BREAKDOWN IS A HUMAN IN A BOX WAITING "
                                "BEHIND A WORK ORDER — and the wrong words kill: self-evacuation "
                                "is the fatality mechanism. Over-routing costs a dispatch."))

EVAL_CASES = [
    {"input": "we're stuck in the elevator at the medical building", "label": "entrapment"},
    {"input": "there are people trapped between floors in the east car", "label": "entrapment"},
    {"input": "someone's inside and the doors won't open", "label": "entrapment"},
    {"input": "my kids are in there and it's stuck between 3 and 4", "label": "entrapment"},
    {"input": "the service elevator is down again at the loading dock", "label": "unit_down"},
    {"input": "escalator stopped this morning and won't restart", "label": "unit_down"},
    {"input": "the north car is out of service since the storm", "label": "unit_down"},
    {"input": "there's a grinding noise on the ride up", "label": "noise"},
    {"input": "car number two shudders between floors", "label": "noise"},
    {"input": "when is our cat 1 test due this year", "label": "inspection"},
    {"input": "need to schedule the annual inspection with the state guy", "label": "inspection"},
    {"input": "", "label": "human"},
    {"input": "invoice received, processing this week", "label": "human"},
    {"input": "the escalator makes a squeal at the top landing", "label": "noise"},
    {"input": "elevator won't open on 5, nobody inside", "label": "unit_down"},
]


def run_eval():
    return triage_eval.run(EVAL_CASES, lambda t: read_call(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_call":          {"rung": "R3", "reason": "routing only; entrapment-first is the point"},
    "dispatch_entrapment": {"rung": "R2", "reason": "a human in the box — the dispatch and the script cannot wait"},
    "advise_self_evacuation": {"rung": "R0", "reason": "the words cannot be produced — self-evacuation is the fatality mechanism", "never_promote": True},
    "reactivate_red_tagged": {"rung": "R0", "reason": "only the clearing mechanic's recorded sign-off returns a unit to service", "never_promote": True},
    "mark_test_compliant_without_record": {"rung": "R0", "reason": "no record, no green check", "never_promote": True},
    "assert_billable_off_silence": {"rung": "R0", "reason": "the clause or 'ambiguous' — never money off silence", "never_promote": True},
    "draft_dispatch":     {"rung": "R1", "reason": "a mechanic roll — a human dispatches"},
    "draft_billable":     {"rung": "R1", "reason": "money — a human bills, with the clause cited"},
    "draft_test_booking": {"rung": "R1", "reason": "outward booking — a human sends"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Cab OS — what it computes to")
        .line("Scope leakage recovered", "revenue", "billable findings × avg ticket (clauses cited)",
              ["billable_findings", "avg_ticket"],
              lambda g: float(g["billable_findings"]) * float(g["avg_ticket"]))
        .line("Test deadlines kept", "revenue", "tests due × avg test fee",
              ["tests_due", "avg_test_fee"],
              lambda g: float(g["tests_due"]) * float(g["avg_test_fee"]),
              note="due and overdue are counted from the unit records")
        .line("Dispatch hours", "time_saved", "hrs/wk × 52 × rate",
              ["office_hours_wk", "office_rate"],
              lambda g: float(g["office_hours_wk"]) * 52 * float(g["office_rate"]))
        .line("The entrapment log", "scenario", "you decide what the response record is worth",
              ["entrapment_value"], lambda g: float(g["entrapment_value"]),
              assumption="never a saving — a life-safety record is not our number to model"))


def roi(given):
    rec = {}
    due = 0
    for u in store.load("units"):
        st = unit_state(u)
        due += sum(1 for t in st["tests"].values() if t["state"] in ("due", "overdue", "unknown"))
    rec["tests_due"] = due
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("read_call", "dispatch_entrapment", "draft_dispatch", "draft_billable",
          "draft_test_booking")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("building:",))
