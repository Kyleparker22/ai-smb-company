#!/usr/bin/env python3
"""Slip OS — the agents. Everything routes through `core.gate`. Stdlib only."""
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
    gate.act("read_message", "dockhouse", msg_id, {"label": c["label"], "why": c["why"]})

    if c["label"] == "spill":
        gate.act("escalate_spill", "dockhouse", msg_id,
                 {"verbatim": m.get("text", ""), "at": m.get("at"), "from": m.get("from")})
        ev = store.log_event("refused", msg_id, "agent:dockhouse", "R0",
                             {"action": "assert_spill_cause",
                              "why": "nothing asserted, nothing denied"})
        out["steps"].append({"action": "escalate_spill", "said": core.SPILL_PROTOCOL,
                             "why": c["why"], "event": ev["id"]})
    elif c["label"] == "work_request":
        wo = {"id": store.nid("wo"), "vessel_ref": m.get("vessel_ref"),
              "owner": m.get("from"), "scope_requested": m.get("text"), "opened_at": iso()}
        store.upsert("workorders", wo)
        body = _auth_request_copy(m)
        gate.act("draft_workorder", "yard", wo["id"],
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_workorder", "workorder": wo["id"], "draft": body,
                             "why": "the authorization request goes out — the crew clocks in "
                                    "only after the owner's recorded click"})
    elif c["label"] == "waitlist":
        body = _waitlist_copy(m)
        out["steps"].append({"action": "answer_waitlist", "draft": body,
                             "why": "the fit arithmetic answers; offers go in recorded order"})
    elif c["label"] == "billing":
        body = _billing_copy(m)
        gate.act("draft_billing_reply", "dockhouse", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_billing_reply", "why": "a human sends"})
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("messages", m)
    return out


def _auth_request_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — we can do that. Before anyone touches the boat you'll get a written "
            f"scope and rate to approve with one click — that's what keeps yard bills boring, "
            f"and boring is what you want from a yard bill. Work starts the moment you approve.")


def _waitlist_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — reply with length, beam, and draft, and you're on the recorded list "
            f"same-day. When a slip that FITS opens (we check the arithmetic, not the vibes), "
            f"you get first refusal for 48 hours before it goes to the next name. No shoebox, "
            f"no forgotten callbacks.")


def _billing_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — pulling your ledger now. Storage runs from recorded arrival to recorded "
            f"departure and stops the day you splash — you'll have the day-by-day in writing "
            f"today.")


def _offer_copy(w, slip):
    who = (w.get("name") or "there").split()[0]
    return (f"Hi {who} — a slip that fits your {w.get('length_ft')}ft boat just opened "
            f"({slip.get('dock')}, slip {slip.get('number')}). It's yours on first refusal for "
            f"48 hours; reply YES and the paperwork comes over, or pass and it goes to the next "
            f"name on the recorded list.")


def start_work(wo_id, by=None, scope=None, rate_basis=None):
    wo = store.by_id("workorders", wo_id)
    if not wo:
        return {"error": "no such work order"}
    if by and scope and rate_basis:
        wo["authorization"] = {"by": by, "scope": scope, "rate_basis": rate_basis, "at": iso()}
        store.upsert("workorders", wo)
    oks, why = core.can_start_work(wo)
    if not oks:
        ev = store.log_event("refused", wo_id, "agent:yard", "R0",
                             {"action": "start_work_unauthorized", "why": why})
        return {"refused": why, "event": ev["id"]}
    wo["started_at"] = iso()
    store.upsert("workorders", wo)
    store.log_event("work_started", wo_id, "human:yard", "R1", {"why": why})
    return {"started": True, "why": why}


def offer_slip(slip_id):
    slip = store.by_id("slips", slip_id)
    if not slip:
        return {"error": "no such slip"}
    ranked = core.ranked_waitlist(slip)
    for c in ranked["candidates"][:1]:
        w = store.by_id("waitlist", c["waitlist"])
        body = _offer_copy(w, slip)
        gate.act("draft_slip_offer", "dockhouse", c["waitlist"],
                 {"summary": f"slip {slip.get('number')} → {c['name']}", "preview": body[:110]})
        w["offered_at"] = iso()
        store.upsert("waitlist", w)
    return ranked


def run_all():
    handled = 0
    for m in store.load("messages"):
        if not m.get("handled_at"):
            handle_message(m["id"])
            handled += 1
    return {"messages": {"handled": handled}}
