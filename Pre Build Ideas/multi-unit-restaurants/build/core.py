#!/usr/bin/env python3
"""Unit OS — domain core (multi-unit restaurant group).

Rules live here: complaint/review triage with the illness and allergen hard
stops, food-cost variance computed only where counts exist, the per-unit
scorecard, and the autonomy matrix.

The thesis: the group's margin hides in per-unit variance nobody computes,
and its existential risk is a dangerous message answered casually in writing.
Count the first, hard-stop the second.

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

TABLES = ("config", "units", "periods", "messages", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="UNITOS_DATA_ROOT")


# ---------------------------------------------------------------- triage

# The dangerous classes. Bias: a cold-burrito complaint escalated costs a
# manager a read; an illness claim answered by software is an admission in a
# lawsuit, and an allergen question answered wrong is an ambulance.
ILLNESS = (
    r"\b(food poisoning|got (so |really )?sick|sick after (eating|dinner|lunch)|"
    r"vomit(ing|ed)?|throwing up|stomach (bug|cramps)|e\.? ?coli|salmonella|norovirus)\b",
)
ALLERGEN_INCIDENT = (
    r"\ballergic reaction\b|\bepipen\b|\banaphyla|\bhives?\b.*\bafter\b|"
    r"\b(said|told).*\b(gluten.?free|nut.?free|dairy.?free)\b.*\b(wasn'?t|was not|reaction)\b",
)
ALLERGEN_QUESTION = (
    r"\b(is|are|does|do)\b.*\b(gluten|nut|peanut|dairy|shellfish|shrimp|prawn|soy|sesame|egg)s?\b",
    r"\ballerg(y|ies|en)\b.*\?|\bcontain\b.*\b(gluten|nuts?|dairy)\b",
    r"\bsame (oil|fryer|grill)\b|\bcross.?contaminat",
)
HEALTH_DEPT = (
    r"\bhealth (department|inspector|dept)\b|\binspection\b.*\b(scheduled|notice|failed)\b",
)
COMPLAINT = (
    r"\b(cold|wrong|missing|slow|rude|dirty|long wait|order was|never (came|arrived)|"
    r"disappointed|terrible|refund)\b",
)


def read_message(text):
    """illness | allergen_incident | allergen_question | health_dept |
    complaint | human. The first four get NO drafted reply — that is the rule."""
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty message — a person reads it"}
    for rx in ILLNESS:
        if re.search(rx, t):
            return {"label": "illness",
                    "why": "possible foodborne-illness claim — a human calls with the insurer's "
                           "language; software drafts nothing, admits nothing"}
    for rx in ALLERGEN_INCIDENT:
        if re.search(rx, t):
            return {"label": "allergen_incident",
                    "why": "allergen reaction claim — a human, now; nothing in writing from software"}
    for rx in HEALTH_DEPT:
        if re.search(rx, t):
            return {"label": "health_dept", "why": "health-department contact — the owner, immediately"}
    for rx in ALLERGEN_QUESTION:
        if re.search(rx, t):
            return {"label": "allergen_question",
                    "why": "allergen safety question — answered by trained staff only, never by software"}
    for rx in COMPLAINT:
        if re.search(rx, t):
            return {"label": "complaint", "why": "service complaint — a response drafts at R1"}
    return {"label": "human", "why": "no clean signal — a person reads it"}


# ---------------------------------------------------------------- variance

VARIANCE_FLAG_PP = 1.5  # percentage points of sales


def variance(period):
    """Actual vs theoretical food cost for one unit-period. No counts → no
    number; last month is not this month."""
    if not period.get("counts_taken"):
        return unmeasured("no inventory counts taken this period — variance cannot be computed, "
                          "and last month's number is not this month's", field="variance_pp")
    sales = period.get("sales") or 0
    if sales <= 0:
        return unmeasured("no sales recorded for the period", field="variance_pp")
    if period.get("actual_cost") is None or period.get("theoretical_cost") is None:
        return unmeasured("cost inputs incomplete", field="variance_pp")
    actual_pct = period["actual_cost"] / sales
    theo_pct = period["theoretical_cost"] / sales
    pp = round((actual_pct - theo_pct) * 100, 2)
    return {"variance_pp": pp, "actual_pct": round(actual_pct, 4),
            "theoretical_pct": round(theo_pct, 4),
            "flagged": pp > VARIANCE_FLAG_PP,
            "dollars": round(period["actual_cost"] - period["theoretical_cost"], 2)}


def variance_board():
    """Latest period per unit, computed or refused per unit."""
    periods = store.load("periods")
    latest = {}
    for p in sorted(periods, key=lambda x: x.get("period") or ""):
        latest[p["unit_id"]] = p
    rows = []
    for u in store.load("units"):
        p = latest.get(u["id"])
        if not p:
            rows.append({"unit": u["name"], "unit_id": u["id"],
                         **unmeasured("no inventory periods recorded", field="variance_pp")})
            continue
        v = variance(p)
        rows.append({"unit": u["name"], "unit_id": u["id"], "period": p.get("period"), **v})
    rows.sort(key=lambda r: -(r.get("variance_pp") if r.get("variance_pp") is not None else -99))
    return rows


# ---------------------------------------------------------------- scorecard

def scorecard():
    """Per-unit counted facts. Every cell computes or refuses."""
    msgs = store.load("messages")
    rows = []
    for u in store.load("units"):
        um = [m for m in msgs if m.get("unit_id") == u["id"]]
        complaints_30 = [m for m in um if m.get("label") == "complaint"
                         and (parse(m.get("at")) or now()) >= now() - timedelta(days=30)]
        unanswered = [m for m in um if m.get("label") == "complaint" and not m.get("responded_at")]
        latest_v = next((r for r in variance_board() if r["unit_id"] == u["id"]), {})
        rows.append({"unit": u["name"], "unit_id": u["id"],
                     "variance_pp": latest_v.get("variance_pp"),
                     "variance_missing": latest_v.get("_missing"),
                     "complaints_30d": len(complaints_30),
                     "response_backlog": len(unanswered)})
    return rows


def variance_brief(unit_id):
    """For a flagged unit: the counted facts and the QUESTIONS they raise.
    Variance names a gap, never a thief — attributing cause is R0; this brief
    arms the area manager's walk, it does not conclude."""
    row = next((r for r in variance_board() if r["unit_id"] == unit_id), None)
    if not row:
        return {"error": "no such unit"}
    if row.get("_missing"):
        return {"unit": row["unit"], "brief": None,
                "why": row["_missing"],
                "note": "no counts, no brief — a brief on fiction would just be confident fiction"}
    if not row.get("flagged"):
        return {"unit": row["unit"], "brief": None,
                "why": f"variance {row['variance_pp']}pp is inside the {VARIANCE_FLAG_PP}pp flag line"}
    return {"unit": row["unit"], "variance_pp": row["variance_pp"], "dollars": row["dollars"],
            "brief": [
                "Was the waste log kept this period, and does it explain any of the gap?",
                "Any menu-price or portion-spec change mid-period the theoretical didn't pick up?",
                "Were invoices priced against the counts (a vendor price jump moves actual, not theoretical)?",
                "Transfer sheets between units — recorded both directions?",
                "Who closed on the highest-variance nights? (a scheduling fact, not an accusation)",
            ],
            "rule": "variance names a gap, never a thief — the walk concludes, software does not"}


def recovered_this_week(ref=None):
    """Counted from the log: complaint replies a human sent, dangerous messages
    escalated to a human, and variance briefs opened, inside 7 days."""
    ref = ref or now()
    replies = escalations = briefs = 0
    for e in store.events():
        at = parse(e.get("at"))
        if not at or (ref - at).days > 7:
            continue
        if e["kind"] == "draft_complaint_reply" and str(e.get("actor", "")).startswith("human:"):
            replies += 1
        elif e["kind"] == "escalate_dangerous":
            escalations += 1
        elif e["kind"] == "variance_brief_opened":
            briefs += 1
    return {"replies_sent": replies, "dangerous_escalated": escalations,
            "briefs_opened": briefs,
            "note": "counted from the event log — never asserted"}


# ---------------------------------------------------------------- eval

triage_eval = Eval("message triage",
                   costly_label="dangerous",
                   costly_note=("AN ILLNESS OR ALLERGEN SIGNAL ANSWERED BY SOFTWARE IS AN "
                                "ADMISSION IN A FUTURE LAWSUIT. Escalating a cold burrito costs "
                                "a manager thirty seconds."))

# For eval scoring, the four hard-stop classes collapse to "dangerous".
DANGEROUS = ("illness", "allergen_incident", "allergen_question", "health_dept")

EVAL_CASES = [
    {"input": "I got food poisoning from your carnitas last night", "label": "dangerous"},
    {"input": "my daughter had an allergic reaction, we used her epipen", "label": "dangerous"},
    {"input": "your server said the mole was gluten free and it wasn't, she had a reaction", "label": "dangerous"},
    {"input": "is the mole gluten free? my son has celiac", "label": "dangerous"},
    {"input": "do the tortillas contain nuts", "label": "dangerous"},
    {"input": "health inspector left a notice at the counter today", "label": "dangerous"},
    {"input": "my burrito was cold and the wait was 40 minutes", "label": "complaint"},
    {"input": "order was wrong again, missing the guac we paid for", "label": "complaint"},
    {"input": "service was slow but the food was great honestly", "label": "complaint"},
    {"input": "", "label": "human"},
    {"input": "do you cater weddings?", "label": "human"},
    {"input": "whole table was throwing up after the party platter", "label": "dangerous"},
    {"input": "are the churros fried in the same oil as the shrimp", "label": "dangerous"},
    {"input": "inspection notice taped to the door at the elm street store", "label": "dangerous"},
    {"input": "waited an hour and the order never came", "label": "complaint"},
    {"input": "the patio was dirty and our server was rude about it", "label": "complaint"},
]


def _eval_label(text):
    lbl = read_message(text)["label"]
    return "dangerous" if lbl in DANGEROUS else lbl


def run_eval():
    return triage_eval.run(EVAL_CASES, _eval_label)


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_message":       {"rung": "R3", "reason": "routing only; the hard stops are the point"},
    "escalate_dangerous": {"rung": "R2", "reason": "act now, tell the human — a dangerous message must not queue"},
    "draft_complaint_reply": {"rung": "R1", "reason": "outward reply — a human sends"},
    "draft_review_reply": {"rung": "R1", "reason": "public words — a human sends"},
    "respond_to_illness_claim": {"rung": "R0", "reason": "software drafts nothing on an illness claim — no accidental admissions", "never_promote": True},
    "answer_allergen_question": {"rung": "R0", "reason": "allergen safety is answered by trained staff, never software", "never_promote": True},
    "respond_to_health_department": {"rung": "R0", "reason": "the owner talks to the health department", "never_promote": True},
    "estimate_variance":  {"rung": "R0", "reason": "variance without counts is fiction — no counts, no number", "never_promote": True},
    "attribute_variance_cause": {"rung": "R0", "reason": "variance names a gap, never a thief — the walk concludes, software does not", "never_promote": True},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Unit OS — what it computes to")
        .line("Variance points recovered", "revenue", "flagged variance $ × your recovery share",
              ["flagged_variance_dollars", "recovery_share"],
              lambda g: float(g["flagged_variance_dollars"]) * float(g["recovery_share"]),
              note="the dollars are counted from your own periods; the share is your call")
        .line("Response drafting time", "time_saved", "msgs/wk × min × 52 × rate/60",
              ["messages_wk", "min_per_reply", "manager_rate"],
              lambda g: float(g["messages_wk"]) * float(g["min_per_reply"]) * 52 * float(g["manager_rate"]) / 60)
        .line("Illness-claim exposure", "scenario", "you decide what a clean paper trail is worth",
              ["claim_exposure"], lambda g: float(g["claim_exposure"]),
              assumption="never presented as a saving — prevented lawsuits cannot be counted"))


def roi(given):
    rec = {}
    flagged = [r for r in variance_board() if r.get("flagged")]
    rec["flagged_variance_dollars"] = round(sum(r.get("dollars", 0) for r in flagged), 2)
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("read_message", "escalate_dangerous", "draft_complaint_reply", "draft_review_reply")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("guest:",))
