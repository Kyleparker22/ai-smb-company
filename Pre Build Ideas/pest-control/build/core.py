#!/usr/bin/env python3
"""Route OS — domain core (pest control).

Rules live here: message triage with the exposure stop and the
label-is-the-law refusal, billing that requires a completed service record,
the reservice churn signal on the two-signal floor, the guarantee-language
check, and the matrix.

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

TABLES = ("config", "accounts", "services", "messages", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="ROUTEOS_DATA_ROOT")

POISON_INSTRUCTION = ("If someone or a pet may have been exposed, call Poison Control now at "
                      "1-800-222-1222. If anyone has trouble breathing, call 911. A licensed "
                      "applicator will call you right away.")

# ---------------------------------------------------------------- triage

EXPOSURE = (
    r"\b(licked|ate|touched|got into|chewed|swallowed|mouthed?)\b.*\b(bait|trap|spray|granules?|"
    r"powder|treatment|chemical|baseboard)\b",
    r"\b(kid|child|toddler|baby|dog|cat|puppy|kitten|pet)\b.*\b(bait|station|granules?|sprayed area)\b",
    r"\b(dizzy|nauseous|headache|trouble breathing|rash)\b.*\b(after|since)\b.*\b(treatment|spray)",
)
SAFETY_QUESTION = (
    r"\b(is it safe|when can (we|i|the kids?|my dog))\b.*\b(re-?enter|go back|inside|touch|play)\b",
    r"\bsafe (for|around)\b.*\b(dog|cat|pet|kids?|children|pregnan|garden|vegetable)\b",
    r"\bwhat('?s| is) in (the )?(spray|bait|treatment)\b|\bhow long\b.*\b(dry|air out|ventilate)\b",
)
RESERVICE = (
    r"\b(still see(ing)?|back again|didn'?t work|came back|more) \b.*\b(ants?|roaches|mice|rats?|"
    r"spiders?|wasps?|termites?|bugs?)\b",
    r"\bstill (have|getting)\b.*\b(ants?|roaches|mice|bugs?)\b|\bre-?service\b|\bretreat(ment)?\b",
)
CANCEL = (r"\bcancel\b|\bstop (the )?service\b|\bdon'?t come (back|anymore)\b",)
SCHEDULE = (r"\b(reschedule|skip this (month|quarter)|gate code|move (my|the) (service|appointment)|"
            r"what day\b|when (are you|is my))",)


def read_message(text):
    """exposure | safety_question | reservice | cancellation | scheduling | human."""
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty message — a person reads it"}
    for rx in EXPOSURE:
        if re.search(rx, t):
            return {"label": "exposure", "instruction": POISON_INSTRUCTION,
                    "why": "possible chemical exposure — Poison Control language shown, a human "
                           "and a licensed applicator immediately; software assesses nothing"}
    for rx in RESERVICE:
        if re.search(rx, t):
            return {"label": "reservice",
                    "why": "reservice request — scheduled AND counted as the churn signal it is"}
    for rx in SAFETY_QUESTION:
        if re.search(rx, t):
            return {"label": "safety_question",
                    "why": "chemical-safety question — the label is the law; a licensed "
                           "applicator answers, never software"}
    for rx in CANCEL:
        if re.search(rx, t):
            return {"label": "cancellation", "why": "cancellation — routed to a human now"}
    for rx in SCHEDULE:
        if re.search(rx, t):
            return {"label": "scheduling", "why": "scheduling request — draft at R1"}
    return {"label": "human", "why": "no clean signal — a person reads it"}


# ---------------------------------------------------------------- billing integrity

def can_bill(service):
    """THE structural rule: only a completed service with a completion record
    can be billed. A skip is a skip."""
    if service.get("status") == "completed" and service.get("completed_at"):
        return True, "completed with a record"
    return False, (f"service is {service.get('status','unknown')!r} with no completion record — "
                   f"a skipped stop billed as completed is the dispute that ends the account")


def skip_board():
    rows = [s for s in store.load("services") if s.get("status") == "skipped"]
    by_reason = {}
    for s in rows:
        by_reason.setdefault(s.get("skip_reason") or "untyped", 0)
        by_reason[s.get("skip_reason") or "untyped"] += 1
    return {"count": len(rows), "by_reason": by_reason,
            "rows": sorted(rows, key=lambda s: s.get("scheduled_at") or "")[-30:]}


# ---------------------------------------------------------------- reservice + churn

RESERVICE_WINDOW_DAYS = 30
RISK_SIGNAL_FLOOR = 2


def reservice_rate(window_days=180):
    cutoff = now() - timedelta(days=window_days)
    done = [s for s in store.load("services")
            if s.get("status") == "completed" and (parse(s.get("completed_at")) or now()) >= cutoff]
    if len(done) < 50:
        return unmeasured(f"only {len(done)} completed services in {window_days} days — need 50",
                          field="rate", n=len(done))
    res = [s for s in done if s.get("kind") == "reservice"]
    return {"rate": round(len(res) / len(done), 3), "reservices": len(res), "of": len(done)}


def churn_signals(account):
    sigs = []
    svcs = [s for s in store.load("services") if s.get("account_id") == account["id"]]
    recent_res = [s for s in svcs if s.get("kind") == "reservice"
                  and (parse(s.get("scheduled_at")) or now()) >= now() - timedelta(days=60)]
    if recent_res:
        sigs.append({"signal": "reservice", "detail": f"{len(recent_res)} reservice(s) in 60 days"})
    if account.get("payment_issue"):
        sigs.append({"signal": "payment_issue", "detail": "open payment issue"})
    skips = [s for s in svcs if s.get("status") == "skipped"
             and (parse(s.get("scheduled_at")) or now()) >= now() - timedelta(days=90)]
    if skips:
        sigs.append({"signal": "skipped_service", "detail": f"{len(skips)} skipped stop(s) in 90 days"})
    if account.get("complaint_open"):
        sigs.append({"signal": "open_complaint", "detail": "unresolved complaint"})
    return sigs


def churn_board():
    at_risk, single = [], 0
    for a in store.load("accounts"):
        if a.get("status") != "active":
            continue
        sigs = churn_signals(a)
        if len(sigs) >= RISK_SIGNAL_FLOOR:
            at_risk.append({"account": a["id"], "name": a.get("name"), "count": len(sigs),
                            "signals": sigs})
        elif len(sigs) == 1:
            single += 1
    at_risk.sort(key=lambda r: -r["count"])
    return {"n": len(at_risk), "rows": at_risk[:40], "single_signal": single,
            "floor": RISK_SIGNAL_FLOOR,
            "note": "one signal is a note; two is a pattern"}


# ---------------------------------------------------------------- guarantee language

FORBIDDEN_GUARANTEE = ("eliminate", "eradicate", "100%", "never come back", "gone for good",
                       "guaranteed gone", "permanently")
COVERAGE_LANGUAGE = "covered under your service plan — we retreat at no charge"


def guarantee_ok(text):
    t = (text or "").lower()
    hits = [w for w in FORBIDDEN_GUARANTEE if w in t]
    if hits:
        return False, (f"no elimination promises — forbidden language: {', '.join(hits)}. "
                       f"Coverage language only: '{COVERAGE_LANGUAGE}'")
    return True, "ok"


def recovered_this_week(ref=None):
    """Counted, never asserted: reservices a human booked, save visits a human
    sent, and completed services billed, inside 7 days."""
    ref = ref or now()
    reservices = saves = billed = 0
    for e in store.events():
        at = parse(e.get("at"))
        if not at or (ref - at).days > 7:
            continue
        human = str(e.get("actor", "")).startswith("human:")
        if e["kind"] == "draft_reservice_booking" and human:
            reservices += 1
        elif e["kind"] == "draft_save_visit" and human:
            saves += 1
        elif e["kind"] == "bill_completed_service":
            billed += 1
    return {"reservices_booked": reservices, "save_visits_sent": saves,
            "services_billed": billed,
            "note": "counted from the event log — never asserted"}


# ---------------------------------------------------------------- eval

triage_eval = Eval("message triage",
                   costly_label="exposure",
                   costly_note=("A MISSED EXPOSURE SIGNAL IS A POISONING INCIDENT ANSWERED BY A "
                                "CHATBOT. Over-routing a scheduling text costs a shrug."))

EVAL_CASES = [
    {"input": "my dog licked the baseboard where they sprayed", "label": "exposure"},
    {"input": "toddler got into the bait station in the garage", "label": "exposure"},
    {"input": "feeling dizzy and headache since the treatment yesterday", "label": "exposure"},
    {"input": "is it safe for the kids to go back inside now", "label": "safety_question"},
    {"input": "what's in the spray you used near the vegetable garden", "label": "safety_question"},
    {"input": "still seeing ants in the kitchen after last week", "label": "reservice"},
    {"input": "the roaches came back, need a retreat", "label": "reservice"},
    {"input": "please cancel the service, we're moving", "label": "cancellation"},
    {"input": "can we reschedule to thursday, gate code is 4482", "label": "scheduling"},
    {"input": "", "label": "human"},
    {"input": "thanks for the great service today", "label": "human"},
    {"input": "the cat was mouthing one of the granules by the door", "label": "exposure"},
    {"input": "how long before we can air out the bedroom", "label": "safety_question"},
    {"input": "seeing more spiders than before you came", "label": "reservice"},
    {"input": "don't come back next month, we're switching companies", "label": "cancellation"},
    {"input": "when are you coming this month? side gate is unlocked", "label": "scheduling"},
]


def run_eval():
    return triage_eval.run(EVAL_CASES, lambda t: read_message(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_message":        {"rung": "R3", "reason": "routing only; the exposure stop is the point"},
    "route_exposure":      {"rung": "R2", "reason": "act now, tell the human — the instruction cannot wait for a click"},
    "answer_chemical_safety": {"rung": "R0", "reason": "the label is the law — a licensed applicator answers", "never_promote": True},
    "bill_skipped_service": {"rung": "R0", "reason": "a skipped stop billed as completed is the dispute that ends the account", "never_promote": True},
    "promise_elimination": {"rung": "R0", "reason": "no elimination promise, ever — coverage language only", "never_promote": True},
    "draft_reservice_booking": {"rung": "R1", "reason": "outward scheduling — a human sends; the churn signal records either way"},
    "draft_scheduling_reply": {"rung": "R1", "reason": "outward reply — a human sends"},
    "bill_completed_service": {"rung": "R2", "reason": "billing a completed, recorded service is mechanical and reversible"},
    "draft_save_visit":    {"rung": "R1", "reason": "outward save visit on a two-signal account — a human sends, coverage language only"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Route OS — what it computes to")
        .line("Reservice-flagged accounts saved", "revenue", "at-risk × save rate × annual value",
              ["at_risk", "save_rate", "annual_value"],
              lambda g: float(g["at_risk"]) * float(g["save_rate"]) * float(g["annual_value"]),
              note="at-risk is counted on the two-signal floor; the save rate is yours")
        .line("Callback and scheduling time", "time_saved", "hrs/wk × 52 × rate",
              ["office_hours_wk", "office_rate"],
              lambda g: float(g["office_hours_wk"]) * 52 * float(g["office_rate"]))
        .line("Skip-billing disputes avoided", "scenario", "skips billed wrong last year × avg account value",
              ["skip_disputes_yr", "annual_value"],
              lambda g: float(g["skip_disputes_yr"]) * float(g["annual_value"]),
              assumption="an exposure you weigh — avoided disputes cannot be counted")
        .line("Exposure routing", "scenario", "you decide what the clean stop is worth",
              ["exposure_value"], lambda g: float(g["exposure_value"]),
              assumption="safety routing is never monetized by us — yours or blank"))


def roi(given):
    rec = {"at_risk": churn_board()["n"]}
    values = [a.get("annual_value") for a in store.load("accounts") if a.get("annual_value")]
    if len(values) >= 30:
        rec["annual_value"] = round(median(values), 2)
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("read_message", "route_exposure", "draft_reservice_booking", "draft_scheduling_reply",
          "bill_completed_service")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("customer:",))
