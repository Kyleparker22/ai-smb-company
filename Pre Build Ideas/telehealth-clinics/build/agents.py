#!/usr/bin/env python3
"""Encounter OS — the agents. Everything routes through `core.gate`. Stdlib only."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import iso


def triage_intake(intake_id):
    """Read a submitted questionnaire. An urgent signal stops the async flow —
    it does not queue, and it does not get a chart prepared for it."""
    i = store.by_id("intakes", intake_id)
    if not i:
        return {"error": "no such intake"}
    prep = core.prepare_chart(intake_id)
    gate.act("read_intake", "triage", intake_id, {"label": prep["triage"]["label"]})
    if prep["triage"]["label"] == "urgent":
        gate.act("stop_async_urgent", "triage", intake_id, {"kind": prep["triage"]["kind"]})
        i.update(triaged_at=iso(), label="urgent")
        store.upsert("intakes", i)
        return {"intake": intake_id, "stopped": True, "kind": prep["triage"]["kind"],
                "said": core.URGENT_INSTRUCTION,
                "why": ("async care is not appropriate here; the flow stops and the patient is "
                        "told to seek care now — nothing was assessed")}
    gate.act("prepare_chart", "charting", intake_id,
             {"missing": prep["missing"], "complete": prep["complete"]})
    i.update(triaged_at=iso(), label="routable")
    store.upsert("intakes", i)
    return {"intake": intake_id, "stopped": False, "chart": prep}


def route_patient(patient_id, need=None):
    r = core.route(patient_id, need)
    if r.get("refused"):
        store.log_event("refused", patient_id, "agent:router", "R0",
                        {"action": "route_unlicensed", "state": r.get("state"),
                         "why": r["refused"]})
        return r
    if "error" in r:
        return r
    gate.act("route_patient", "router", patient_id,
             {"state": r["state"], "candidates": len(r["candidates"])})
    return r


def answer_clinical(text):
    gate.act("clinical_advice", "triage", "inbound", {"asked": text[:120]})
    return {"refused": True,
            "reply": ("I can't answer clinical questions. Your intake is with a clinician who will "
                      "respond. " + core.URGENT_INSTRUCTION),
            "why": "async software does not practise medicine"}


def draft_reengagement(encounter_id):
    """A patient who paid and never attended. The draft says nothing clinical and
    a human sends it."""
    e = store.by_id("encounters", encounter_id)
    if not e:
        return {"error": "no such encounter"}
    if e.get("started_at"):
        return {"skipped": "this patient has already been seen"}
    p = store.by_id("patients", e.get("patient")) or {}
    res = gate.act("draft_reengagement", "recovery", encounter_id, {"patient": e.get("patient")})
    return {"encounter": encounter_id,
            "draft": (f"Hi {p.get('name','').split(' ')[0]} — your visit is paid for and still "
                      f"waiting for you. Reply and we'll get you booked in."),
            "approval": res.get("approval"), "rung": res.get("rung"), "why": res.get("reason")}


def close(encounter_id, human):
    return core.close_encounter(encounter_id, human)


def run_all():
    out = {"triaged": 0, "urgent_stops": 0, "routed": 0, "coverage_refusals": 0,
           "reengagement_drafts": 0}
    for i in store.load("intakes"):
        if i.get("triaged_at"):
            continue
        r = triage_intake(i["id"])
        out["triaged"] += 1
        if r.get("stopped"):
            out["urgent_stops"] += 1
            continue
        rt = route_patient(i["patient"])
        if rt.get("refused"):
            out["coverage_refusals"] += 1
        elif rt.get("candidates"):
            out["routed"] += 1
    for e in core.paid_not_seen():
        draft_reengagement(e["encounter"])
        out["reengagement_drafts"] += 1
    out["gaps"] = core.coverage_gaps()
    out["note"] = ("a coverage refusal is not a failure of the sweep — it is the clinic being told "
                   "it has patients in a state nobody on the roster may see")
    return out
