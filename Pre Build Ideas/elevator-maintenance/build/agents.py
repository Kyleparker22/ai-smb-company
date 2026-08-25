#!/usr/bin/env python3
"""Cab OS — the agents. Everything routes through `core.gate`. Stdlib only."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import iso, now, parse


def handle_call(call_id):
    m = store.by_id("calls", call_id)
    if not m:
        return {"error": "no such call"}
    c = core.read_call(m.get("text", ""))
    out = {"call": call_id, "classification": c, "steps": []}
    gate.act("read_call", "dispatch", call_id, {"label": c["label"], "why": c["why"]})

    if c["label"] == "entrapment":
        gate.act("dispatch_entrapment", "dispatch", call_id,
                 {"summary": m.get("text", "")[:60], "verbatim": m.get("text", "")})
        ev = store.log_event("refused", call_id, "agent:dispatch", "R0",
                             {"action": "advise_self_evacuation",
                              "why": "the words cannot be produced"})
        out["steps"].append({"action": "dispatch_entrapment", "said": core.ENTRAPMENT_SCRIPT,
                             "why": c["why"], "event": ev["id"]})
    elif c["label"] == "unit_down":
        body = _dispatch_copy(m)
        gate.act("draft_dispatch", "dispatch", call_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_dispatch", "why": "a human dispatches"})
    elif c["label"] == "noise":
        body = _noise_copy(m)
        gate.act("draft_dispatch", "dispatch", call_id,
                 {"summary": f"ride-quality: {m.get('text','')[:50]}", "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_dispatch",
                             "why": "a noise today is a shutdown next month — the visit drafts"})
    elif c["label"] == "inspection":
        body = _test_copy(m)
        gate.act("draft_test_booking", "dispatch", call_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_test_booking", "why": "from the unit calendar"})
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("calls", m)
    return out


def _dispatch_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — mechanic assigned; you'll get a name and ETA within the hour. If the "
            f"unit is gated or the machine room is locked, reply with access details and we're "
            f"faster.")


def _noise_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — thanks for flagging it; a noise today is usually a part telling us "
            f"something before it becomes a shutdown. A mechanic will ride the car this week and "
            f"you'll get the finding in writing either way.")


def _test_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — pulling your units' test calendar now; anything due or overdue gets "
            f"offered first, and the state filing follows the test automatically on our side. "
            f"Reply with two windows and we'll lock one.")


def scope_ticket(unit_id, work_desc):
    u = store.by_id("units", unit_id)
    if not u:
        return {"error": "no such unit"}
    v = core.scope_check(u, work_desc)
    if v["verdict"] == "billable":
        body = _billable_copy(u, v, work_desc)
        gate.act("draft_billable", "office", unit_id,
                 {"summary": f"{v['category']} excluded by {v['clause']}",
                  "clause": v["clause"], "preview": body[:110]})
        return {**v, "draft": body}
    if v["verdict"] == "ambiguous":
        ev = store.log_event("refused", unit_id, "agent:office", "R0",
                             {"action": "assert_billable_off_silence", "why": v["why"]})
        return {**v, "event": ev["id"]}
    return v


def _billable_copy(u, v, work_desc):
    return (f"On unit {u['id']}: \"{work_desc[:50]}\" falls outside the maintenance contract — "
            f"clause {v['clause']} reads \"{v.get('clause_text', '')}\". Happy to do the work; "
            f"a small quote comes first so there are no surprise line items.")


def reactivate(unit_id, mechanic_signoff=None):
    u = store.by_id("units", unit_id)
    if not u:
        return {"error": "no such unit"}
    okr, why = core.can_reactivate(u, mechanic_signoff)
    if not okr:
        ev = store.log_event("refused", unit_id, "agent:dispatch", "R0",
                             {"action": "reactivate_red_tagged", "why": why})
        return {"refused": why, "event": ev["id"]}
    if u.get("red_tagged_at"):
        u["red_tagged_at"] = None
        u["cleared_by"] = mechanic_signoff
        store.upsert("units", u)
        store.log_event("unit_cleared", unit_id, f"human:{mechanic_signoff}", "R1", {})
    return {"reactivated": True, "why": why}


def test_sweep(limit=20):
    out = {"alerts": 0}
    already = {e["subject"] for e in store.events(kind="queued_for_approval", since_days=14)
               if (e.get("detail") or {}).get("action") == "draft_test_booking"}
    for u in store.load("units"):
        if out["alerts"] >= limit or u["id"] in already or u.get("demo_tag"):
            continue
        st = core.unit_state(u)
        worst = [t for t in st["tests"].values() if t["state"] in ("overdue", "unknown")]
        if not worst:
            continue
        gate.act("draft_test_booking", "calendar", u["id"],
                 {"summary": f"unit {u['id']}: " +
                             ", ".join(f"{k} {v['state']}" for k, v in st["tests"].items()
                                       if v["state"] != "current")})
        out["alerts"] += 1
    return out


def run_all():
    handled = 0
    for m in store.load("calls"):
        if not m.get("handled_at"):
            handle_call(m["id"])
            handled += 1
    return {"calls": {"handled": handled}, "tests": test_sweep()}
