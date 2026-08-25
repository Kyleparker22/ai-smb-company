#!/usr/bin/env python3
"""Hook OS — the agents. Everything routes through `core.gate`. Stdlib only."""
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

    if c["label"] == "rotation":
        gate.act("record_rotation_call", "dispatch", call_id,
                 {"summary": m.get("text", "")[:60], "clock": "started at this record"})
        gate.act("draft_dispatch", "dispatch", call_id,
                 {"summary": f"ROTATION: {m.get('text','')[:50]}"})
        out["steps"].append({"action": "record_rotation_call",
                             "why": "the clock started at this record — the truck assignment "
                                    "queues for the dispatcher in the same breath"})
    elif c["label"] == "breakdown":
        body = _dispatch_copy(m)
        gate.act("draft_dispatch", "dispatch", call_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_dispatch", "why": "a human dispatches"})
    elif c["label"] == "price_question":
        answer = _price_copy()
        out["steps"].append({"action": "answer_from_card", "draft": answer,
                             "why": "answered FROM the filed card, never around it"})
    elif c["label"] == "release_request":
        body = _release_copy(m)
        gate.act("process_release", "window", call_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "process_release",
                             "why": "ID + payment recorded at the window; the meter stops at "
                                    "the recorded release"})
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("calls", m)
    return out


def _dispatch_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — truck assigned, you'll get the driver's name and an ETA text in a "
            f"minute. Stay with the vehicle if it's safe, away from traffic if it isn't. The "
            f"price is the filed rate card — hookup plus mileage — and the driver carries a copy.")


def _price_copy():
    card = core.rate_card()
    return (f"Straight off the filed card: hookup ${card['hookup']}, ${card['per_mile']}/mile, "
            f"storage ${card['storage_per_day']}/day. That card is filed with the city and "
            f"posted at the lot — the invoice can't say anything different.")


def _release_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — your vehicle is at the lot. Bring photo ID matching the registration "
            f"and payment for the balance on the posted card; the storage meter stops the moment "
            f"the release is recorded, not the end of the day. Office hours 8–6; after-hours "
            f"release adds the posted gate fee only.")


def bill_tow(tow_id):
    t = store.by_id("tows", tow_id)
    if not t:
        return {"error": "no such tow"}
    inv = core.tow_invoice(t)
    if "_missing" in inv:
        return {"refused": inv["_missing"]}
    asked = t.get("requested_total")
    if asked and asked > inv["total"]:
        ev = store.log_event("refused", tow_id, "agent:office", "R0",
                             {"action": "charge_above_rate_card",
                              "why": f"requested ${asked:,.2f} exceeds the card total "
                                     f"${inv['total']:,.2f} — no number above the card exists"})
        return {"refused": f"requested ${asked:,.2f} exceeds the filed-card total "
                           f"${inv['total']:,.2f} — the invoice is the card's number, clamped",
                "event": ev["id"], "invoice": inv}
    r = gate.act("draft_invoice", "office", tow_id,
                 {"summary": f"${inv['total']:,.2f} from the filed card"})
    return {"invoice": inv, "gate": r}


def damage_dispute(tow_id):
    t = store.by_id("tows", tow_id)
    if not t:
        return {"error": "no such tow"}
    v = core.damage_response(t)
    if not v["assertable"]:
        ev = store.log_event("refused", tow_id, "agent:office", "R0",
                             {"action": "assert_no_damage_without_photos", "why": v["refused"]})
        return {**v, "event": ev["id"]}
    return v


def lien_sweep(limit=20):
    out = {"alerts": 0}
    already = {e["subject"] for e in store.events(kind="lien_date_alert", since_days=7)}
    for imp in store.load("impounds"):
        if imp.get("released_at") or imp.get("demo_tag") or imp["id"] in already:
            continue
        cal = core.lien_calendar(imp)
        for s in (cal.get("steps") or [])[:1]:
            if s["days_left"] <= 7:
                gate.act("lien_date_alert", "lot", imp["id"],
                         {"step": s["step"], "due": s["due"], "days_left": s["days_left"],
                          "label": s["label"]})
                out["alerts"] += 1
                if out["alerts"] >= limit:
                    return out
    return out


def run_all():
    handled = 0
    for m in store.load("calls"):
        if not m.get("handled_at"):
            handle_call(m["id"])
            handled += 1
    return {"calls": {"handled": handled}, "liens": lien_sweep()}
