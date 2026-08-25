#!/usr/bin/env python3
"""Pool OS — the agents. Everything routes through `core.gate`. Stdlib only."""
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

    if c["label"] == "injury":
        gate.act("log_injury_report", "frontdesk", msg_id,
                 {"verbatim": m.get("text", ""), "at": m.get("at"),
                  "caller": m.get("from") or "unknown"})
        ev = store.log_event("refused", msg_id, "agent:frontdesk", "R0",
                             {"action": "respond_to_injury_report",
                              "why": "software drafts nothing on an injury"})
        out["steps"].append({"action": "log_injury_report", "said": core.INJURY_PROTOCOL,
                             "why": c["why"], "event": ev["id"]})
    elif c["label"] == "chemical_question":
        ev = store.log_event("refused", msg_id, "agent:frontdesk", "R0",
                             {"action": "answer_chemical_dosing", "why": c["why"]})
        out["steps"].append({"action": "route_to_tech", "refused": "routed unanswered",
                             "why": c["why"], "event": ev["id"]})
    elif c["label"] == "green_pool":
        body = _recovery_copy(m)
        gate.act("draft_recovery_visit", "frontdesk", msg_id,
                 {"summary": f"recovery visit: {m.get('text','')[:50]}", "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_recovery_visit", "draft": body,
                             "why": "honest multi-visit copy — no clear-by date promised"})
    elif c["label"] == "schedule":
        body = _schedule_copy(m)
        gate.act("draft_schedule_reply", "frontdesk", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_schedule_reply", "why": "a human sends"})
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("messages", m)
    return out


def _recovery_copy(m):
    """Green-pool copy: owns the state, promises visits and readings — never a
    date the water clears, never a swim verdict."""
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — thanks for flagging it; a green pool is ours to fix. Recovery is "
            f"usually 2–4 visits over about a week: heavy treatment first, then filtering and "
            f"retesting until the readings hold in range. We'll record readings every visit so "
            f"you can watch it turn. First visit: tomorrow. We'll tell you what the numbers say "
            f"— your call on swimming rests on those numbers and your comfort.")


def _schedule_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — noted and on the route sheet. You'll get a text when the tech is two "
            f"stops away. Anything else about access, reply here.")


def _quote_chase_copy(q, touch_n):
    """Equipment quote follow-up. The finding and the number, no scare copy."""
    who = (q.get("customer_name") or "there").split()[0]
    item = q.get("item", "the equipment work")
    amt = f"${q.get('amount', 0):,.0f}"
    return {
        1: (f"Hi {who} — following up on the {item} quote ({amt}) from the tech's visit. The "
            f"finding and photos are on the quote; happy to walk through it. Want it on the "
            f"schedule?"),
        2: (f"Hi {who} — second note on the {item} quote ({amt}). Price holds 30 days from the "
            f"visit; reply Y and we'll book it on a regular service day so there's no extra trip "
            f"charge."),
        3: (f"Hi {who} — last note on the {item} quote ({amt}); we'll leave it on your file. If "
            f"the finding changes at a future visit, we'll tell you either way."),
    }.get(touch_n, f"Hi {who} — following up on the {item} quote ({amt}).")


def bill_stop(stop_id):
    s = store.by_id("stops", stop_id)
    if not s:
        return {"error": "no such stop"}
    okb, why = core.can_bill_stop(s)
    if not okb:
        ev = store.log_event("refused", stop_id, "agent:office", "R0",
                             {"action": "bill_unproven_stop", "why": why})
        return {"refused": why, "event": ev["id"]}
    return gate.act("draft_stop_invoice", "office", stop_id, {"summary": why})


def quote_sweep(limit=15):
    out = {"drafted": 0, "skipped": 0}
    for q in store.load("quotes"):
        if out["drafted"] >= limit:
            break
        plan = core.quote_plan(q)
        if plan["action"] != "draft_chase":
            out["skipped"] += 1
            continue
        touch_n = len(q.get("touches") or []) + 1
        body = _quote_chase_copy(q, touch_n)
        gate.act("draft_quote_chase", "sales", q["id"],
                 {"summary": f"{q.get('item','quote')} ${q.get('amount',0):,.0f} touch {touch_n}",
                  "preview": body[:110]})
        q.setdefault("touches", []).append({"at": iso(), "kind": "drafted", "body": body})
        store.upsert("quotes", q)
        out["drafted"] += 1
    return out


def run_all():
    handled = 0
    for m in store.load("messages"):
        if not m.get("handled_at"):
            handle_message(m["id"])
            handled += 1
    return {"messages": {"handled": handled}, "quotes": quote_sweep()}
