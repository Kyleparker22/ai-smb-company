#!/usr/bin/env python3
"""Pump OS — the agents. Everything routes through `core.gate`. Stdlib only."""
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
    gate.act("read_message", "frontdesk", msg_id, {"label": c["label"], "why": c["why"]})

    if c["label"] == "emergency":
        gate.act("route_emergency", "frontdesk", msg_id,
                 {"summary": m.get("text", "")[:60], "verbatim": m.get("text", "")})
        out["steps"].append({"action": "route_emergency", "said": core.EMERGENCY_ACK,
                             "why": c["why"]})
    elif c["label"] == "diagnosis_ask":
        ev = store.log_event("refused", msg_id, "agent:frontdesk", "R0",
                             {"action": "diagnose_by_phone", "why": c["why"]})
        body = _visit_copy(m)
        gate.act("draft_visit_booking", "frontdesk", msg_id,
                 {"summary": f"tech visit: {m.get('text','')[:50]}", "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_visit_booking", "draft": body,
                             "refused": "no phone diagnosis — the visit is the answer",
                             "why": c["why"], "event": ev["id"]})
    elif c["label"] == "due_service":
        body = _booking_copy(m)
        gate.act("draft_visit_booking", "frontdesk", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_visit_booking", "why": "a human sends"})
    elif c["label"] == "portable":
        body = _portable_copy(m)
        gate.act("draft_portable_order", "frontdesk", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_portable_order", "why": "a human sends"})
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("messages", m)
    return out


def _visit_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — honest answer: guessing from here helps nobody, and a wrong guess costs "
            f"you money. A tech can open it up this week, check the baffle, the filter and the "
            f"field, and tell you exactly what's what with photos. Morning or afternoon?")


def _booking_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — good timing to ask. Reply with two days that work and gate/dog details, "
            f"and we'll confirm a window. The truck logs gallons and the disposal manifest, so "
            f"your file shows exactly what was done.")


def _portable_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — we can cover that. Reply with the dates, the address, and roughly how "
            f"many people, and we'll confirm units and the service schedule. Delivery is a day "
            f"ahead so you're never waiting on us.")


def _recall_copy(s, row, touch_n):
    who = (s.get("customer_name") or "there").split()[0]
    yrs = s.get("interval_years", 3)
    return {
        1: (f"Hi {who} — your tank's last recorded pump-out was over {yrs} years ago, which is "
            f"the interval your system is on. Catching it now is a routine visit; letting it go "
            f"is how fields fail. Want a window this month?"),
        2: (f"Hi {who} — second nudge on the pump-out. If someone else serviced it since, tell "
            f"us the date and we'll fix our records — that's useful either way."),
        3: (f"Hi {who} — last reminder from us; we'll leave it here. The interval record stays "
            f"on your file whenever you're ready."),
    }.get(touch_n, f"Hi {who} — your pump-out is due.")


def bill_job(job_id):
    j = store.by_id("jobs", job_id)
    if not j:
        return {"error": "no such job"}
    okb, why = core.can_bill(j)
    if not okb:
        ev = store.log_event("refused", job_id, "agent:office", "R0",
                             {"action": "bill_without_manifest", "why": why})
        return {"refused": why, "event": ev["id"]}
    okl, whyl = core.can_land_apply(j)
    if not okl:
        ev = store.log_event("refused", job_id, "agent:office", "R0",
                             {"action": "schedule_land_application_unpermitted", "why": whyl})
        return {"refused": whyl, "event": ev["id"]}
    return gate.act("draft_invoice", "office", job_id, {"summary": why})


def recall_sweep(limit=15):
    out = {"drafted": 0, "skipped": 0}
    for row in core.due_systems():
        if out["drafted"] >= limit or row.get("overdue_days") is None:
            continue
        s = store.by_id("systems", row["system"])
        plan = core.recall_plan(s)
        if plan["action"] != "draft_recall":
            out["skipped"] += 1
            continue
        touch_n = len(s.get("recalls") or []) + 1
        body = _recall_copy(s, row, touch_n)
        gate.act("draft_recall", "recall", s["id"],
                 {"summary": f"{s.get('customer_name')} {row['overdue_days']}d overdue, touch {touch_n}",
                  "preview": body[:110]})
        s.setdefault("recalls", []).append({"at": iso(), "kind": "drafted", "body": body})
        store.upsert("systems", s)
        out["drafted"] += 1
    return out


def run_all():
    handled = 0
    for m in store.load("messages"):
        if not m.get("handled_at"):
            handle_message(m["id"])
            handled += 1
    return {"messages": {"handled": handled}, "recalls": recall_sweep()}
