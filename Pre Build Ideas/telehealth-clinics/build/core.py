#!/usr/bin/env python3
"""Encounter OS — domain core (multi-state telehealth clinic).

What separates a telehealth clinic from every other clinic in this folder is not
the medicine — it is that **the patient's location decides who is allowed to see
them**, and the scarce resource is clinician minutes rather than leads.

So the core is three things:

  1. **Licensure-aware routing.** A clinician who is not licensed in the
     patient's state is not a slow option or a low-ranked one. They are
     structurally absent from the candidate list, and the router refuses rather
     than degrade.
  2. **Async triage that hands over a prepared chart**, so a clinician opens a
     complete picture instead of a raw questionnaire.
  3. **The leak between paying and attending**, which in telehealth is larger
     than the leak before paying.

Nothing here gives clinical advice or completes an encounter that is not
documented.

Stdlib only. Honesty rules come from `_kit`.
"""
import re, sys
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent))

from _kit.moat import Eval, Gate, Matrix, Roi                       # noqa: E402
from _kit.store import (Store, automation_rate, days_until, iso,    # noqa: E402
                        median, now, parse, unmeasured)

TABLES = ("config", "clinicians", "patients", "intakes", "encounters",
          "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="ENCOS_DATA_ROOT")

URGENT_INSTRUCTION = ("If this is an emergency — chest pain, trouble breathing, thoughts of harming "
                      "yourself, or anything you feel cannot wait — call 911 or go to the nearest "
                      "emergency room now. Do not wait for a reply here.")

# Everything an encounter must carry before it can be closed. A telehealth note
# is the only artifact that survives a complaint, so an undocumented encounter is
# not a tidy-up task — it is an unclosable one.
REQUIRED_DOC = ("chief_complaint", "history", "assessment", "plan",
                "patient_location", "consent", "clinician_licence")


# ---------------------------------------------------------------- licensure

def eligible_clinicians(state, need=None):
    """Who may lawfully see a patient in this state, right now.

    The exclusion is at the query, not a ranking penalty. There is deliberately
    no 'best available anyway' fallback: a clinic under pressure is exactly when
    someone would click it.
    """
    out = []
    for c in store.load("clinicians"):
        if not c.get("active"):
            continue
        if state not in (c.get("licences") or []):
            continue
        if need and need not in (c.get("modalities") or []):
            continue
        out.append(c)
    return out


def route(patient_id, need=None):
    """Route one patient. Returns candidates, or a refusal that names the gap."""
    p = store.by_id("patients", patient_id)
    if not p:
        return {"error": "no such patient"}
    state = p.get("state")
    if not state:
        return {"refused": "the patient's state is not recorded",
                "why": ("location decides who may lawfully provide care — this is asked before "
                        "anything else, and guessed never"),
                "patient": patient_id}
    cands = eligible_clinicians(state, need)
    if not cands:
        licensed_anywhere = [c for c in store.load("clinicians")
                             if c.get("active") and need in (c.get("modalities") or [])] if need else \
                            [c for c in store.load("clinicians") if c.get("active")]
        return {"refused": f"no active clinician is licensed in {state}"
                           + (f" for {need}" if need else ""),
                "why": ("routing to an unlicensed clinician is the failure this module exists to "
                        "prevent — there is no 'closest match' fallback, on purpose"),
                "patient": patient_id, "state": state,
                "coverage_gap": True,
                "clinicians_available_elsewhere": len(licensed_anywhere),
                "action": "this is a licensing decision for the clinic, not a routing problem"}
    ranked = []
    for c in cands:
        load = sum(1 for e in store.load("encounters")
                   if e.get("clinician") == c["id"] and not e.get("closed_at"))
        ranked.append({"clinician": c["id"], "name": c.get("name"),
                       "open_encounters": load,
                       "licences": len(c.get("licences") or []),
                       "why": f"licensed in {state}; {load} open encounters"})
    ranked.sort(key=lambda r: r["open_encounters"])
    return {"patient": patient_id, "state": state, "candidates": ranked,
            "note": f"only clinicians licensed in {state} were ever considered"}


def coverage_gaps(floor=1):
    """States where patients exist and no clinician is licensed. The clinic's
    real growth constraint, and usually invisible."""
    have = {}
    for p in store.load("patients"):
        s = p.get("state")
        if s:
            have[s] = have.get(s, 0) + 1
    out = []
    for state, n in sorted(have.items(), key=lambda kv: -kv[1]):
        if n >= floor and not eligible_clinicians(state):
            out.append({"state": state, "patients": n,
                        "why": "patients here cannot be seen by anyone on the roster"})
    return out


# ---------------------------------------------------------------- async triage

URGENT = (
    ("cardiac", r"\bchest pain\b|\bheart (is )?racing\b|\bpressure in my chest\b"),
    ("breathing", r"\bcan'?t breathe\b|\bshort(ness)? of breath\b|\bwheez\w*"),
    ("self_harm", r"\bhurt(ing)? myself\b|\bkill myself\b|\bsuicid\w*|\bend it all\b|"
                  r"\bdon'?t want to (be here|live)\b"),
    # "slurred speech" and "speech went slurred" are the same emergency; match the
    # word, not one phrasing. (The suite caught the narrow version.)
    ("neuro", r"\bslurr\w*|\bspeech\b[^.!?]{0,20}\bslur\w*|\bface (is |has )?droop\w*|"
              r"\bnumb\w*[^.!?]{0,20}\bone side\b|\bseizur\w*|\bstroke\b"),
    ("obstetric", r"\bbleeding heavily\b|\bpregnan\w*[^.!?]{0,25}\bpain\b"),
)


def read_intake(text):
    t = (text or "").lower()
    for kind, pat in URGENT:
        if re.search(pat, t):
            return {"label": "urgent", "kind": kind,
                    "why": f"an urgent {kind.replace('_',' ')} signal — async care is not appropriate",
                    "route": "stop the async flow and tell the patient to seek care now"}
    return {"label": "routable", "kind": None,
            "why": "no urgent signal matched — safe to prepare a chart for a clinician",
            "route": "prepare the chart"}


def prepare_chart(intake_id):
    """Turn a submitted questionnaire into something a clinician can act on —
    and name every gap rather than presenting a tidy chart with holes."""
    i = store.by_id("intakes", intake_id)
    if not i:
        return {"error": "no such intake"}
    triage = read_intake(i.get("narrative", ""))
    answers = i.get("answers") or {}
    required = ("chief_complaint", "duration", "medications", "allergies",
                "conditions", "pregnancy_status")
    missing = [k for k in required if not answers.get(k)]
    p = store.by_id("patients", i.get("patient")) or {}
    return {"intake": intake_id, "patient": i.get("patient"), "state": p.get("state"),
            "triage": triage,
            "complete": not missing and triage["label"] != "urgent",
            "missing": missing,
            "chart": {k: answers.get(k) for k in required},
            "narrative": i.get("narrative"),
            "note": ("a clinician opens a prepared chart, not a raw form — and every unanswered "
                     "question is listed rather than left blank in the middle of it")}


# ---------------------------------------------------------------- the leak

def paid_not_seen(days=3):
    """Patients who paid and have not attended. In telehealth this leak is
    bigger than the one before payment, and almost nobody measures it."""
    out = []
    for e in store.load("encounters"):
        if e.get("paid_at") and not e.get("started_at"):
            waited = -(days_until(e["paid_at"]) or 0)
            if waited >= days:
                p = store.by_id("patients", e.get("patient")) or {}
                out.append({"encounter": e["id"], "patient": e.get("patient"),
                            "name": p.get("name"), "state": p.get("state"),
                            "days_since_paid": waited, "amount": e.get("amount")})
    out.sort(key=lambda r: -r["days_since_paid"])
    return out


def conversion(floor=25):
    """Paid → actually seen. Counted, and refused below the floor."""
    paid = [e for e in store.load("encounters") if e.get("paid_at")]
    if len(paid) < floor:
        return unmeasured(f"only {len(paid)} paid encounters — need {floor}",
                          field="rate", n=len(paid))
    seen = [e for e in paid if e.get("started_at")]
    return {"rate": round(len(seen) / len(paid), 3), "paid": len(paid), "seen": len(seen),
            "note": "counted from the encounter log"}


# ---------------------------------------------------------------- documentation

def documentation_gaps():
    """Closed-or-closable encounters missing a required element."""
    out = []
    for e in store.load("encounters"):
        if not e.get("started_at"):
            continue
        doc = e.get("documentation") or {}
        missing = [k for k in REQUIRED_DOC if not doc.get(k)]
        if missing:
            out.append({"encounter": e["id"], "patient": e.get("patient"),
                        "closed": bool(e.get("closed_at")), "missing": missing})
    out.sort(key=lambda r: (not r["closed"], -len(r["missing"])))
    return out


def close_encounter(encounter_id, human):
    """An encounter cannot be closed with documentation missing. This is a hard
    stop, not a nag — the note is the only thing that survives a complaint."""
    e = store.by_id("encounters", encounter_id)
    if not e:
        return {"error": "no such encounter"}
    doc = e.get("documentation") or {}
    missing = [k for k in REQUIRED_DOC if not doc.get(k)]
    if missing:
        ev = store.log_event("refused", encounter_id, "agent:charting", "R0",
                             {"action": "close_undocumented", "missing": missing})
        return {"refused": "the encounter is not fully documented", "missing": missing,
                "why": "the note is the only artifact that survives a complaint",
                "event": ev["id"]}
    e.update(closed_at=iso(), closed_by=human)
    store.upsert("encounters", e)
    store.log_event("close_encounter", encounter_id, f"human:{human}", "R1", {})
    return {"encounter": encounter_id, "closed_by": human, "note": "documentation complete"}


# ---------------------------------------------------------------- eval

routing_eval = Eval(
    "licensure routing",
    costly_label="unlicensed",
    costly_note=("ROUTING A PATIENT TO A CLINICIAN NOT LICENSED IN THEIR STATE is the failure "
                 "that closes a telehealth clinic. It is reported on its own, and the router has "
                 "no 'best available anyway' path for anyone to click under pressure."))

EVAL_CLINICIANS = [
    {"id": "c1", "name": "A", "active": True, "licences": ["FL", "GA"], "modalities": ["general"]},
    {"id": "c2", "name": "B", "active": True, "licences": ["TX"], "modalities": ["general"]},
    {"id": "c3", "name": "C", "active": False, "licences": ["NY"], "modalities": ["general"]},
]
EVAL_CASES = [
    {"input": "FL", "label": "ok"},
    {"input": "GA", "label": "ok"},
    {"input": "TX", "label": "ok"},
    {"input": "NY", "label": "unlicensed"},   # licensed clinician is inactive
    {"input": "CA", "label": "unlicensed"},
    {"input": "WY", "label": "unlicensed"},
    {"input": "", "label": "unlicensed"},
]


def run_eval():
    def predict(state):
        elig = [c for c in EVAL_CLINICIANS
                if c["active"] and state and state in c["licences"]]
        return "ok" if elig else "unlicensed"
    return routing_eval.run(EVAL_CASES, predict)


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_intake":        {"rung": "R3", "reason": "classification only; the urgent stop is the point"},
    "prepare_chart":      {"rung": "R3", "reason": "assembles what the patient already answered and lists the gaps"},
    "route_patient":      {"rung": "R2", "reason": "only ever offers clinicians licensed in the patient's state"},
    "route_unlicensed":   {"rung": "R0", "reason": "routing across a licence boundary is the clinic-ending failure",
                           "never_promote": True},
    "clinical_advice":    {"rung": "R0", "reason": "async software does not answer clinical questions",
                           "never_promote": True},
    "close_undocumented": {"rung": "R0", "reason": "an encounter without its note cannot be closed by anyone",
                           "never_promote": True},
    "stop_async_urgent":  {"rung": "R2", "reason": "tell the patient to seek care now — a click would delay it"},
    "draft_reengagement": {"rung": "R1", "reason": "outward message to a patient who paid — a human sends"},
    "close_encounter":    {"rung": "R1", "reason": "closing a chart is a clinician's attestation"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Encounter OS — what it computes to")
        .line("Paid-but-unseen patients recovered", "revenue",
              "unseen × your recovery rate × visit value",
              ["unseen_count", "recovery_rate", "visit_value"],
              lambda g: float(g["unseen_count"]) * float(g["recovery_rate"]) * float(g["visit_value"]),
              note="the unseen count is counted; the recovery rate is yours")
        .line("Clinician minutes returned by prepared charts", "time_saved",
              "min/encounter × encounters/yr ÷ 60 × clinician rate",
              ["minutes_saved", "encounters_year", "clinician_rate"],
              lambda g: float(g["minutes_saved"]) * float(g["encounters_year"]) / 60.0
                        * float(g["clinician_rate"]),
              note=("reported as time, never as revenue — whether returned minutes become visits "
                    "is a staffing decision, not an arithmetic one"))
        .line("Coordination time on routing", "time_saved", "hrs/wk × 52 × rate",
              ["routing_hours_wk", "staff_rate"],
              lambda g: float(g["routing_hours_wk"]) * 52 * float(g["staff_rate"]))
        .line("Licence coverage gaps closed", "scenario", "you decide what this is worth",
              ["coverage_value"], lambda g: float(g["coverage_value"]),
              assumption=("we surface the states where you have patients and no licensed "
                          "clinician; what that market is worth is your number, and adding a "
                          "licence is your decision"))
        .line("An unlicensed encounter never happening", "scenario",
              "you decide what this is worth",
              ["exposure_value"], lambda g: float(g["exposure_value"]),
              assumption=("prevented regulatory exposure cannot be counted — we will not put a "
                          "number on it for you")))


def roi(given):
    rec = {}
    unseen = paid_not_seen()
    if unseen:
        rec["unseen_count"] = len(unseen)
    enc = store.load("encounters")
    if len(enc) >= 25:
        rec["encounters_year"] = len(enc)
    amts = [e.get("amount") for e in enc if e.get("amount")]
    if len(amts) >= 25:
        rec["visit_value"] = round(median(amts), 2)
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("read_intake", "prepare_chart", "route_patient", "stop_async_urgent",
          "draft_reengagement", "close_encounter")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("patient:",))
