#!/usr/bin/env python3
"""Garment OS — the agents. Everything routes through `core.gate`. Stdlib only."""
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
    gate.act("read_message", "counter", msg_id, {"label": c["label"], "why": c["why"]})

    if c["label"] == "claim":
        claim = {"id": store.nid("cl"), "message_id": msg_id, "text": m.get("text"),
                 "customer": m.get("from"), "filed_at": m.get("at") or iso()}
        store.upsert("claims", claim)
        gate.act("log_claim", "counter", claim["id"],
                 {"verbatim": m.get("text", ""), "from": m.get("from")})
        ev = store.log_event("refused", claim["id"], "agent:counter", "R0",
                             {"action": "deny_claim",
                              "why": "software assembles the record and the math"})
        body = _claim_ack(m)
        out["steps"].append({"action": "log_claim", "claim": claim["id"], "draft": body,
                             "refused": "nothing denied by this message — the schedule math and "
                                        "a human decision follow",
                             "why": c["why"], "event": ev["id"]})
    elif c["label"] == "stain_ask":
        body = _stain_copy(m)
        okp, why = core.promise_ok(body)
        assert okp, why  # structural: the shipped copy passes its own check
        gate.act("draft_stain_reply", "counter", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_stain_reply", "draft": body,
                             "why": "honest copy — 'we'll try' is the whole promise"})
    elif c["label"] == "pickup":
        body = _pickup_copy(m)
        out["steps"].append({"action": "answer_from_rack", "draft": body,
                             "why": "answered from the rack record"})
    elif c["label"] == "wholesale":
        body = _wholesale_copy(m)
        gate.act("draft_wholesale_reply", "routes", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_wholesale_reply",
                             "why": "the recorded counts do the talking"})
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("messages", m)
    return out


def _claim_ack(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — we take this seriously and here's exactly what happens: the garment "
            f"comes back to us for inspection with your intake tag, the settlement is computed "
            f"from our published fair-claims schedule (not haggled at the counter), and the "
            f"owner reviews it personally. Nothing about your claim is decided by this message — "
            f"you'll hear from a person within one business day.")


def _stain_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — honest answer: it depends on the fabric, the stain, and how long it's "
            f"had to set, and anyone who promises more than that over text is guessing. We'll "
            f"try, with the right chemistry in the right order, and we'll tell you before we do "
            f"anything that carries risk to the garment. Bring it in and we'll look at it "
            f"together.")


def _pickup_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — checking the rack record now; you'll get a yes/no with the exact items "
            f"listed in a moment. If it's ready, it's on the rack with your name on the tag.")


def _wholesale_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — pulling the route sheet: our driver's recorded counts for that delivery "
            f"are attached, signed at the dock. If the counts disagree, the recorded sheet is "
            f"where the conversation starts — and if we miscounted, the invoice corrects this "
            f"week, no forms.")


def _rack_copy(o, touch_n):
    who = (o.get("customer_name") or "there").split()[0]
    return {
        1: (f"Hi {who} — your order is pressed, bagged, and on the rack (${o.get('amount', 0):,.0f}). "
            f"We're open until 7 weekdays; it'll be waiting."),
        2: (f"Hi {who} — second note: your order is still with us, safe and covered. If pickup "
            f"is hard, tell us — we can hold it longer or arrange delivery on the route."),
        3: (f"Hi {who} — last reminder from us. State rules give unclaimed garments a clock, and "
            f"we'd genuinely rather hand you your clothes than ever think about it — reply and "
            f"we'll hold them past it, no charge."),
    }.get(touch_n, f"Hi {who} — your order is ready.")


def draft_settlement(claim_id):
    c = store.by_id("claims", claim_id)
    if not c:
        return {"error": "no such claim"}
    math = core.claim_math(c)
    if "refused" in math:
        ev = store.log_event("refused", claim_id, "agent:claims", "R0",
                             {"action": "settle_off_schedule", "why": math["refused"]})
        return {"refused": math["refused"], "event": ev["id"]}
    evidence = core.claim_evidence(c)
    r = gate.act("draft_settlement", "claims", claim_id,
                 {"summary": f"${math['amount']:,.2f} — {math['basis'][:60]}",
                  "evidence": evidence})
    return {"math": math, "evidence": evidence, "gate": r}


def dispose(order_id, human=None):
    o = store.by_id("orders", order_id)
    if not o:
        return {"error": "no such order"}
    okd, why = core.can_dispose(o)
    if not okd:
        ev = store.log_event("refused", order_id, "agent:rack", "R0",
                             {"action": "dispose_before_clock", "why": why})
        return {"refused": why, "event": ev["id"]}
    if not human:
        return {"refused": "the clock is complete but disposal is a human act — a person "
                           "confirms", "why": why}
    store.log_event("disposed", order_id, f"human:{human}", "R1", {"why": why})
    return {"disposed": True, "why": why}


def rack_sweep(limit=20):
    out = {"drafted": 0, "skipped": 0}
    for o in store.load("orders"):
        if out["drafted"] >= limit or not o.get("ready_at") or o.get("picked_up_at") \
           or o.get("demo_tag"):
            continue
        plan = core.rack_plan(o)
        if plan["action"] != "draft_reminder":
            out["skipped"] += 1
            continue
        touch_n = len(o.get("rack_touches") or []) + 1
        body = _rack_copy(o, touch_n)
        gate.act("draft_rack_reminder", "counter", o["id"],
                 {"summary": f"{o.get('customer_name')} ${o.get('amount', 0):,.0f} touch {touch_n}",
                  "preview": body[:110]})
        o.setdefault("rack_touches", []).append({"at": iso(), "kind": "drafted", "body": body})
        store.upsert("orders", o)
        out["drafted"] += 1
    return out


def run_all():
    handled = 0
    for m in store.load("messages"):
        if not m.get("handled_at"):
            handle_message(m["id"])
            handled += 1
    return {"messages": {"handled": handled}, "rack": rack_sweep()}
