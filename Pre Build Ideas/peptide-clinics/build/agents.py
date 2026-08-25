#!/usr/bin/env python3
"""Protocol OS — the agents. Everything routes through `core.gate`. Stdlib only."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import iso


def handle_message(msg_id):
    m = store.by_id("messages", msg_id)
    if not m:
        return {"error": "no such message"}
    c = core.read_message(m.get("text", ""))
    out = {"message": msg_id, "classification": c, "steps": []}
    gate.act("read_message", "inbox", msg_id, {"label": c["label"]})

    if c["label"] == "urgent":
        gate.act("route_urgent", "inbox", msg_id, {"kind": c["kind"]})
        out["steps"].append({"action": "route_urgent", "kind": c["kind"],
                             "said": core.URGENT_INSTRUCTION,
                             "why": "a clinician was told immediately; nothing was assessed"})
    elif c["label"] == "clinical":
        ev = store.log_event("refused", msg_id, "agent:inbox", "R0",
                             {"action": "clinical_advice", "why": c["why"]})
        out["steps"].append({"action": "route_to_clinician", "refused": "routed unanswered",
                             "why": c["why"], "event": ev["id"]})
    else:
        out["steps"].append({"action": f"route_{c['label']}", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("messages", m)
    return out


def draft_refill_nudge(patient_id):
    """A refill reminder. The exclusion is checked here AND is structural in the
    query — belt and braces, because this is the one that ends a clinic."""
    p = store.by_id("patients", patient_id)
    if not p:
        return {"error": "no such patient"}
    if p.get("status") not in core.CONTACTABLE:
        ev = store.log_event("refused", patient_id, "agent:cycle", "R0",
                             {"action": "contact_excluded", "status": p.get("status")})
        return {"refused": "this patient can never receive outreach",
                "status": p.get("status"),
                "why": ("a patient who stopped for a medical reason, had an adverse event, opted "
                        "out, transferred or died is permanently outside every sweep"),
                "event": ev["id"]}
    res = gate.act("draft_refill_nudge", "cycle", patient_id, {"name": p.get("name")})
    return {"patient": patient_id,
            "draft": (f"Hi {p.get('name','').split(' ')[0]} — you're coming up on your next cycle. "
                      f"Reply here and we'll get it scheduled."),
            "approval": res.get("approval"), "rung": res.get("rung"),
            "why": res.get("reason"),
            "note": "no dose, no clinical content, and a human sends it"}


def answer_clinical(text):
    """The question the clinic's software must never answer."""
    gate.act("clinical_advice", "inbox", "inbound", {"asked": text[:120]})
    return {"refused": True,
            "reply": ("I can't advise on doses, symptoms or whether something is normal — I've sent "
                      "this to a clinician, who will reply. " + core.URGENT_INSTRUCTION),
            "why": "clinical advice is outside what this system may ever do"}


def adjust_dose(patient_id, change):
    gate.act("adjust_dose", "cycle", patient_id, {"attempted": change})
    return {"refused": True,
            "why": "a dose or titration change is a prescriber's decision, never software's"}


def run_all():
    """Sweep the inbox and draft nudges for the cycle. The sweep can only see
    contactable patients — the exclusion is in the query, not a later filter."""
    out = {"messages": 0, "urgent": 0, "nudges": 0, "excluded_unreachable": 0}
    for m in store.load("messages"):
        if m.get("handled_at"):
            continue
        r = handle_message(m["id"])
        out["messages"] += 1
        if r["classification"]["label"] == "urgent":
            out["urgent"] += 1
    reachable = {p["id"] for p in core.contactable()}
    out["excluded_unreachable"] = len(store.load("patients")) - len(reachable)
    for row in core.due_and_lapsing():
        if row.get("state") in ("due", "overdue", "lapsing") and row["patient"] in reachable:
            draft_refill_nudge(row["patient"])
            out["nudges"] += 1
    out["note"] = ("every nudge is a draft at the approval gate; the sweep never reaches an "
                   "excluded patient because it never loads one")
    return out
