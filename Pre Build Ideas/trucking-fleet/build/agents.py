#!/usr/bin/env python3
"""Hours OS — the agents. Everything routes through `core.gate`. Stdlib only."""
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

    if c["label"] == "accident":
        gate.act("brief_safety_director", "dispatch", msg_id,
                 {"summary": m.get("text", "")[:60], "verbatim": m.get("text", ""),
                  "brief": core.PRESERVATION_BRIEF})
        ev = store.log_event("refused", msg_id, "agent:dispatch", "R0",
                             {"action": "draft_outward_after_accident",
                              "why": "nothing outward from software after an accident"})
        out["steps"].append({"action": "brief_safety_director",
                             "brief": core.PRESERVATION_BRIEF,
                             "why": c["why"], "event": ev["id"]})
    elif c["label"] == "log_ask":
        r = core.log_request(m.get("driver_id") or msg_id, m.get("from", "requester"),
                             m.get("text", ""))
        out["steps"].append({"action": "refuse_log_edit", "refused": r["refused"],
                             "why": c["why"], "event": r["event"]})
    elif c["label"] == "detention":
        load = store.by_id("loads", m.get("load_id")) if m.get("load_id") else None
        if load:
            inv = core.detention_invoice(load)
            if "refused" in inv:
                out["steps"].append({"action": "detention_incomplete", "refused": inv["refused"],
                                     "why": "the stamps make the invoice — get them recorded"})
            else:
                gate.act("draft_detention_invoice", "billing", load["id"],
                         {"summary": f"${inv['total']:,.0f} — {inv['basis'][:60]}"})
                out["steps"].append({"action": "draft_detention_invoice", "invoice": inv,
                                     "why": inv["basis"]})
        else:
            out["steps"].append({"action": "route_human", "why": "no load matched — a person confirms"})
    elif c["label"] == "dispatch_ask":
        out["steps"].append({"action": "route_to_clock_gate",
                             "why": "the dispatch path runs the clock arithmetic — see the gate"})
    elif c["label"] == "hours_ask":
        driver = store.by_id("drivers", m.get("driver_id")) if m.get("driver_id") else None
        body = _hours_copy(m, driver)
        out["steps"].append({"action": "answer_from_eld", "draft": body,
                             "why": "answered from the recorded ELD, never from memory"})
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("messages", m)
    return out


def _hours_copy(m, driver):
    who = (m.get("from") or "there").split()[0]
    if driver and driver.get("hos_remaining_h") is not None:
        return (f"Hi {who} — the recorded ELD shows {driver['hos_remaining_h']}h remaining on "
                f"{driver.get('name', 'the driver')}'s clock. That number, minus the 1h buffer, "
                f"is what dispatch can plan against.")
    return (f"Hi {who} — no synced clock on record for that driver, which means the honest "
            f"answer is UNKNOWN until the ELD syncs. We don't dispatch on a guess.")


def dispatch(driver_id, load_id):
    d = store.by_id("drivers", driver_id)
    l = store.by_id("loads", load_id)
    if not d or not l:
        return {"error": "no such driver or load"}
    okd, why = core.can_dispatch(d, l)
    if not okd:
        ev = store.log_event("refused", load_id, "agent:dispatch", "R0",
                             {"action": "dispatch_beyond_hours", "driver": driver_id, "why": why})
        return {"refused": why, "event": ev["id"]}
    truck = store.by_id("trucks", l.get("truck_id")) if l.get("truck_id") else None
    if truck:
        okt, whyt = core.can_assign_truck(truck)
        if not okt:
            ev = store.log_event("refused", load_id, "agent:dispatch", "R0",
                                 {"action": "assign_oos_truck", "why": whyt})
            return {"refused": whyt, "event": ev["id"]}
    return gate.act("dispatch_load", "dispatch", load_id,
                    {"summary": f"{d.get('name')} → {l.get('lane')} ({why})", "driver": driver_id})


def maintenance_sweep(limit=15):
    out = {"alerts": 0}
    already = {e["subject"] for e in store.events(kind="maintenance_alert", since_days=7)}
    for r in core.maintenance_board():
        if out["alerts"] >= limit or r.get("miles_to_service") is None:
            continue
        if (r["miles_to_service"] < 2000 or r["overdue"]) and r["truck"] not in already:
            gate.act("maintenance_alert", "shop", r["truck"],
                     {"summary": f"{r['truck']}: {'OVERDUE' if r['overdue'] else str(r['miles_to_service']) + ' mi to service'}"})
            out["alerts"] += 1
    return out


def run_all():
    handled = 0
    for m in store.load("messages"):
        if not m.get("handled_at"):
            handle_message(m["id"])
            handled += 1
    return {"messages": {"handled": handled}, "maintenance": maintenance_sweep()}
