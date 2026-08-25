#!/usr/bin/env python3
"""Unit OS — the agents. Everything routes through `core.gate`. Stdlib only."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import iso


def handle_message(msg_id):
    """Triage one message. The four dangerous classes escalate with NO reply
    drafted; a complaint gets an R1 draft."""
    m = store.by_id("messages", msg_id)
    if not m:
        return {"error": "no such message"}
    c = core.read_message(m.get("text", ""))
    out = {"message": msg_id, "classification": c, "steps": []}
    gate.act("read_message", "frontdoor", msg_id, {"label": c["label"], "why": c["why"]})

    if c["label"] in core.DANGEROUS:
        r0 = {"illness": "respond_to_illness_claim",
              "allergen_incident": "respond_to_illness_claim",
              "allergen_question": "answer_allergen_question",
              "health_dept": "respond_to_health_department"}[c["label"]]
        gate.act("escalate_dangerous", "frontdoor", msg_id,
                 {"summary": f"{c['label']}: {m.get('text','')[:60]}"})
        ev = store.log_event("refused", msg_id, "agent:frontdoor", "R0",
                             {"action": r0, "why": c["why"]})
        out["steps"].append({"action": "escalate_to_human", "kind": c["label"],
                             "refused": "no reply drafted — nothing in writing from software",
                             "why": c["why"], "event": ev["id"]})
    elif c["label"] == "complaint":
        body = _complaint_reply_copy(m)
        gate.act("draft_complaint_reply", "frontdoor", msg_id,
                 {"summary": f"draft reply: {m.get('text','')[:60]}", "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_complaint_reply",
                             "why": "a human reads and sends the draft"})
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("messages", m)
    return out


def _complaint_reply_copy(m):
    """Drafted for the unit manager to send. Owns the service failure plainly,
    offers the make-right, and never wanders into health or allergen territory
    — those classes never reach this function at all."""
    unit = store.by_id("units", m.get("unit_id")) or {}
    uname = unit.get("name", "our restaurant")
    return (f"You're right to be frustrated, and I'm sorry — that's not the visit we want at "
            f"{uname}. I'd like to make it right: your next order is on us, and I'm flagging "
            f"this with tonight's shift lead so it's fixed at the line, not just apologized for. "
            f"— Manager, {uname}")


def open_variance_brief(unit_id):
    """Open the flagged-unit brief and log that a human is walking it."""
    brief = core.variance_brief(unit_id)
    if brief.get("brief"):
        store.log_event("variance_brief_opened", unit_id, "agent:controller", "R2",
                        {"variance_pp": brief["variance_pp"]})
        ev = store.log_event("refused", unit_id, "agent:controller", "R0",
                             {"action": "attribute_variance_cause",
                              "why": "variance names a gap, never a thief"})
        brief["refusal_event"] = ev["id"]
    return brief


def run_all():
    handled = 0
    for m in store.load("messages"):
        if not m.get("handled_at"):
            handle_message(m["id"])
            handled += 1
    return {"messages": {"handled": handled}}
