#!/usr/bin/env python3
"""Ratio OS — the agents. Everything routes through `core.gate`. Stdlib only."""
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
    gate.act("read_message", "frontdesk", msg_id, {"label": c["label"], "why": c["why"]})

    if c["label"] == "pickup_change":
        gate.act("open_verification", "frontdesk", m.get("child_id") or msg_id,
                 {"summary": f"pickup change: {m.get('text','')[:50]}",
                  "checklist": verification_checklist(m)})
        ev = store.log_event("refused", msg_id, "agent:frontdesk", "R0",
                             {"action": "confirm_unlisted_pickup", "why": core.RELEASE_RULE})
        out["steps"].append({"action": "open_verification",
                             "refused": "software confirms nothing — a human verifies per the "
                                        "written policy (ID + parent phone verification)",
                             "why": c["why"], "event": ev["id"]})
    elif c["label"] == "incident":
        ev = store.log_event("refused", msg_id, "agent:frontdesk", "R0",
                             {"action": "respond_to_incident", "why": c["why"]})
        out["steps"].append({"action": "escalate_to_director",
                             "refused": "nothing drafted — the director calls",
                             "why": c["why"], "event": ev["id"]})
    elif c["label"] == "illness_question":
        ev = store.log_event("refused", msg_id, "agent:frontdesk", "R0",
                             {"action": "answer_medical_exclusion", "why": c["why"]})
        out["steps"].append({"action": "route_with_policy",
                             "refused": "the policy text goes with it — software adds no advice",
                             "why": c["why"], "event": ev["id"]})
    elif c["label"] == "enrollment":
        body = _tour_copy(m)
        gate.act("draft_tour_offer", "frontdesk", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_tour_offer", "why": "a human sends"})
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("messages", m)
    return out


def verification_checklist(m):
    """What the human at the desk actually does — the software's whole
    contribution is opening the task and holding the list steady."""
    return ["call the parent at the number ON FILE (never the number in this message)",
            "photo ID at the door, matched to the name the parent gave by phone",
            "log who released, who received, and the time",
            "if anything is off, the child stays — comfort over apology, every time"]


def _tour_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — we'd love to show you around. Tours run weekday mornings while the "
            f"rooms are in full swing (that's the honest view). Reply with two times that work "
            f"and the director will hold one. We'll have current openings and rates on paper "
            f"when you visit.")


def _waitlist_copy(w):
    fam = (w.get("family") or "there").split()[0]
    age = w.get("age_group", "your child's")
    return (f"Hi {fam} — you're still on our {age} waitlist and we haven't forgotten you. "
            f"Nothing has opened yet; when a spot does, you'll get first call and 48 hours to "
            f"decide. If your plans changed and you'd like off the list, just reply and we'll "
            f"close it out.")


def check_release(child_id, person):
    """The release check surface — a lookup and, when unlisted, a refusal."""
    v = core.release_check(child_id, person)
    if v.get("refused"):
        ev = store.log_event("refused", child_id, "agent:frontdesk", "R0",
                             {"action": "confirm_unlisted_pickup", "person": person,
                              "why": v["refused"]})
        gate.act("open_verification", "frontdesk", child_id,
                 {"summary": f"unlisted pickup attempt: {person}"})
        return {**v, "event": ev["id"]}
    return v


def waitlist_sweep(limit=15):
    out = {"drafted": 0}
    recent = {e["subject"] for e in store.events(kind="queued_for_approval", since_days=7)
              if (e.get("detail") or {}).get("action") == "draft_waitlist_followup"}
    for w in store.load("waitlist"):
        if out["drafted"] >= limit:
            break
        if w.get("enrolled_at") or w.get("offered_at") or w["id"] in recent or w.get("demo_tag"):
            continue
        body = _waitlist_copy(w)
        gate.act("draft_waitlist_followup", "enrollment", w["id"],
                 {"summary": f"follow up with {w.get('family','family')} ({w.get('age_group')})",
                  "preview": body[:110]})
        out["drafted"] += 1
    return out


def run_all():
    handled = 0
    for m in store.load("messages"):
        if not m.get("handled_at"):
            handle_message(m["id"])
            handled += 1
    return {"messages": {"handled": handled}, "waitlist": waitlist_sweep()}
