#!/usr/bin/env python3
"""Ride OS — the agents. Everything routes through `core.gate`. Stdlib only."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import iso, now, parse


def handle_message(msg_id):
    m = store.by_id("messages", msg_id)
    if not m:
        return {"error": "no such message"}
    c = core.read_message(m.get("text", ""))
    out = {"message": msg_id, "classification": c, "steps": []}
    gate.act("read_message", "dispatch", msg_id, {"label": c["label"], "why": c["why"]})

    if c["label"] == "condition_change":
        gate.act("escalate_condition", "dispatch", msg_id,
                 {"verbatim": m.get("text", ""), "from": m.get("from"),
                  "route": "human + the receiving facility, verbatim"})
        ev = store.log_event("refused", msg_id, "agent:dispatch", "R0",
                             {"action": "assess_patient_condition",
                              "why": "software never assesses"})
        body = _condition_ack(m)
        out["steps"].append({"action": "escalate_condition", "draft": body,
                             "refused": "no assessment, no reassurance — the words go to a "
                                        "human and the facility exactly as written",
                             "why": c["why"], "event": ev["id"]})
    elif c["label"] == "schedule":
        trip = store.by_id("trips", m.get("trip_id")) if m.get("trip_id") else None
        if trip and "cancel" not in (m.get("text") or "").lower():
            okb, whyb = core.can_bump(trip)
            if not okb:
                ev = store.log_event("refused", trip["id"], "agent:dispatch", "R0",
                                     {"action": "bump_protected_trip", "why": whyb})
                out["steps"].append({"action": "escalate_conflict", "refused": whyb,
                                     "why": "a human resolves protected-trip conflicts",
                                     "event": ev["id"]})
                m.update(handled_at=iso(), label=c["label"])
                store.upsert("messages", m)
                return out
        body = _schedule_copy(m)
        gate.act("draft_schedule_reply", "dispatch", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_schedule_reply", "why": "a human sends"})
    elif c["label"] == "complaint":
        body = _complaint_copy(m)
        out["steps"].append({"action": "human_calls_with_log", "draft": body,
                             "why": "a human calls with the trip log open — the stamps talk"})
    elif c["label"] == "billing":
        out["steps"].append({"action": "route_to_log_gate",
                             "why": "the trip-log gate decides what can bill"})
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("messages", m)
    return out


def _condition_ack(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — thank you for telling us; your words are going to our coordinator and "
            f"the facility right now, exactly as you wrote them. We're drivers, not clinicians, "
            f"so we won't guess at what it means — the people who should judge it will have it "
            f"within minutes.")


def _schedule_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — noted; the schedule updates today and you'll get the confirmed window "
            f"by text. Standing medical trips (dialysis, chemo) hold their slots no matter what "
            f"else moves.")


def _complaint_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — that shouldn't have happened, and a person will call you today with "
            f"the trip record open so we're both looking at the same facts. If we were late, "
            f"you'll hear it from us plainly, with what we're changing.")


def bill_trip(trip_id):
    t = store.by_id("trips", trip_id)
    if not t:
        return {"error": "no such trip"}
    okb, why = core.can_bill(t)
    if not okb:
        ev = store.log_event("refused", trip_id, "agent:billing", "R0",
                             {"action": "bill_without_trip_log", "why": why})
        return {"refused": why, "event": ev["id"]}
    return gate.act("draft_invoice", "billing", trip_id, {"summary": why})


def bump_trip(trip_id):
    t = store.by_id("trips", trip_id)
    if not t:
        return {"error": "no such trip"}
    okb, why = core.can_bump(t)
    if not okb:
        ev = store.log_event("refused", trip_id, "agent:scheduler", "R0",
                             {"action": "bump_protected_trip", "why": why})
        return {"refused": why, "event": ev["id"]}
    return {"bumpable": True, "why": why}


def assign_driver(trip_id, driver_id):
    t = store.by_id("trips", trip_id)
    d = store.by_id("drivers", driver_id)
    if not t or not d:
        return {"error": "no such trip or driver"}
    oka, why = core.can_assign(d)
    if not oka:
        ev = store.log_event("refused", trip_id, "agent:scheduler", "R0",
                             {"action": "assign_uncredentialed_driver", "driver": driver_id,
                              "why": why})
        return {"refused": why, "event": ev["id"]}
    return gate.act("assign_driver", "scheduler", trip_id,
                    {"summary": f"{d.get('name')} → trip {trip_id} ({why})", "driver": driver_id})


def run_all():
    handled = 0
    for m in store.load("messages"):
        if not m.get("handled_at"):
            handle_message(m["id"])
            handled += 1
    return {"messages": {"handled": handled}}
