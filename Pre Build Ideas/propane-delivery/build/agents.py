#!/usr/bin/env python3
"""Fuel OS — the agents. Everything routes through `core.gate`. Stdlib only."""
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

    if c["label"] == "gas_smell":
        gate.act("dispatch_gas_smell", "dispatch", call_id,
                 {"summary": m.get("text", "")[:60], "verbatim": m.get("text", "")})
        ev = store.log_event("refused", call_id, "agent:dispatch", "R0",
                             {"action": "troubleshoot_gas_smell",
                              "why": "nothing about a gas smell is troubleshot by phone"})
        out["steps"].append({"action": "dispatch_gas_smell", "said": core.EVACUATE_SCRIPT,
                             "why": c["why"], "event": ev["id"]})
    elif c["label"] == "out_of_gas":
        ticket = {"id": store.nid("tk"), "kind": "out_of_gas", "call_id": call_id,
                  "customer_name": m.get("from"), "opened_at": iso()}
        store.upsert("tickets", ticket)
        body = _outage_copy(m)
        gate.act("draft_delivery", "dispatch", ticket["id"],
                 {"summary": f"OUTAGE: {m.get('from','customer')}", "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "open_outage_ticket", "ticket": ticket["id"],
                             "draft": body,
                             "why": "the ticket carries the leak-check gate — it cannot close "
                                    "without the tech's recorded result"})
    elif c["label"] == "delivery":
        body = _delivery_copy(m)
        gate.act("draft_delivery", "dispatch", call_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_delivery", "why": "a human routes it"})
    elif c["label"] == "price":
        cust = store.by_id("customers", m.get("customer_id")) if m.get("customer_id") else None
        pf = core.price_for(cust or {})
        body = _price_copy(m, pf)
        gate.act("draft_price_reply", "dispatch", call_id,
                 {"summary": f"price reply ({pf.get('basis', 'unknown')})", "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_price_reply", "price": pf, "draft": body,
                             "why": pf.get("note") or pf.get("basis") or pf.get("_missing")})
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("calls", m)
    return out


def _outage_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — you're on today's board as an out-of-gas priority. Important and "
            f"non-negotiable: because the system ran dry, the technician performs a leak check "
            f"before anything relights — it's regulation and it's what keeps this routine. "
            f"Someone needs to be home for that part. You'll get a window within the hour.")


def _delivery_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — on the route list. You'll get a day-before text and the driver's "
            f"window that morning. If the tank gauge drops under 15% before then, call and "
            f"we'll bump you up.")


def _price_copy(m, pf):
    who = (m.get("from") or "there").split()[0]
    if pf.get("_missing"):
        return f"Hi {who} — a human will call with today's number; we don't guess prices."
    if pf.get("clamped"):
        return (f"Hi {who} — your price is your contract price: ${pf['per_gallon']:.2f}/gal, "
                f"locked {pf['basis']}. Whatever the market does, that's your number.")
    return (f"Hi {who} — today's posted price is ${pf['per_gallon']:.2f}/gal. If you want "
            f"protection from winter swings, ask about a contract lock when we deliver.")


def close_outage(ticket_id, leak_result=None, tech=None):
    t = store.by_id("tickets", ticket_id)
    if not t:
        return {"error": "no such ticket"}
    if leak_result and tech:
        t["leak_check"] = {"result": leak_result, "tech": tech, "at": iso()}
        store.upsert("tickets", t)
    okc, why = core.can_close_outage(t)
    if not okc:
        ev = store.log_event("refused", ticket_id, "agent:dispatch", "R0",
                             {"action": "close_outage_without_leak_check", "why": why})
        return {"refused": why, "event": ev["id"]}
    t["closed_at"] = iso()
    store.upsert("tickets", t)
    store.log_event("outage_closed", ticket_id, f"human:{tech or 'dispatch'}", "R1",
                    {"leak_check": t.get("leak_check")})
    return {"closed": True, "why": why}


def fill_tank(tank_id):
    t = store.by_id("tanks", tank_id)
    if not t:
        return {"error": "no such tank"}
    okf, why = core.can_fill_tank(t)
    if not okf:
        ev = store.log_event("refused", tank_id, "agent:dispatch", "R0",
                             {"action": "fill_unqualified_tank", "why": why})
        return {"refused": why, "event": ev["id"]}
    return gate.act("draft_delivery", "dispatch", tank_id, {"summary": why})


def runout_sweep(limit=15):
    out = {"alerts": 0}
    already = {e["subject"] for e in store.events(kind="runout_alert", since_days=3)}
    for r in core.runout_board():
        if out["alerts"] >= limit or r.get("risk") != "critical" or r["tank"] in already:
            continue
        gate.act("runout_alert", "dispatch", r["tank"],
                 {"summary": f"{r['customer']}: {r['days_to_empty']}d to empty at recorded usage"})
        out["alerts"] += 1
    return out


def run_all():
    handled = 0
    for m in store.load("calls"):
        if not m.get("handled_at"):
            handle_call(m["id"])
            handled += 1
    return {"calls": {"handled": handled}, "runouts": runout_sweep()}
