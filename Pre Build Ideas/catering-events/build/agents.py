#!/usr/bin/env python3
"""Plate OS — the agents. Everything routes through `core.gate`. Stdlib only."""
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

    if c["label"] == "allergen":
        ev = store.log_event("refused", msg_id, "agent:frontdesk", "R0",
                             {"action": "answer_allergen_question", "why": c["why"]})
        out["steps"].append({"action": "route_to_trained_human",
                             "refused": "no answer drafted — a trained human calls",
                             "why": c["why"], "event": ev["id"]})
    elif c["label"] == "change_request":
        booking = store.by_id("bookings", m.get("booking_id")) if m.get("booking_id") else None
        if booking:
            chk = core.change_check(booking)
            ack = _change_ack_copy(booking, chk)
            if chk.get("locked"):
                ev = store.log_event("refused", booking["id"], "agent:beocontrol", "R0",
                                     {"action": "auto_apply_locked_change", "why": chk["refused"]})
                gate.act("draft_beo_change", "beocontrol", booking["id"],
                         {"summary": f"LOCKED-WINDOW change: {m.get('text','')[:50]}",
                          "kitchen_impact": "named for the human who confirms",
                          "preview": ack[:110]})
                out["steps"].append({"action": "queue_locked_change", "refused": chk["refused"],
                                     "draft": ack, "event": ev["id"]})
            else:
                gate.act("draft_beo_change", "beocontrol", booking["id"],
                         {"summary": m.get("text", "")[:60], "preview": ack[:110]})
                out["steps"].append({"action": "draft_beo_change", "draft": ack, "why": chk["note"]})
        else:
            out["steps"].append({"action": "route_human", "why": "no booking matched"})
    elif c["label"] == "inquiry":
        body = _availability_copy(m)
        gate.act("draft_availability_reply", "frontdesk", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_availability_reply",
                             "why": "availability comes from the calendar; a human sends"})
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("messages", m)
    return out


def _availability_copy(m):
    """The inquiry reply a human sends — the calendar's own facts, a tasting
    offer, and never a price by message (menus price per event)."""
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — thanks for thinking of us. The calendar answer comes from the person "
            f"who owns it, so you'll have real dates (not a form letter) within the day. If any "
            f"of them work, the next step is a tasting — that's where menus and numbers get real, "
            f"in person.")


def _change_ack_copy(booking, chk):
    """Change acknowledgment: inside the lock window the copy promises a call,
    never an application — nothing auto-applies inside 72 hours."""
    name = booking.get("name", "your event")
    if chk.get("locked"):
        return (f"Got your change for {name}. We're inside the {core.BEO_LOCK_HOURS}-hour window, "
                f"so nothing changes on paper until the event lead calls you — kitchen and "
                f"staffing are already in motion, and we'd rather confirm what's possible than "
                f"promise what isn't. Expect the call within the hour.")
    return (f"Got your change for {name} — outside the lock window, so it's drafted against the "
            f"BEO now and you'll get the updated sheet to confirm today.")


def book(space_id, date_iso, guests, name="new event"):
    okb, why = core.can_book(space_id, date_iso, guests)
    if not okb:
        ev = store.log_event("refused", space_id, "agent:calendar", "R0",
                             {"action": "double_book_space", "why": why})
        return {"refused": why, "event": ev["id"]}
    return gate.act("draft_booking", "calendar", space_id,
                    {"summary": f"{name}: {guests} guests on {date_iso[:10]} — {why}"})


def run_all():
    handled = 0
    for m in store.load("messages"):
        if not m.get("handled_at"):
            handle_message(m["id"])
            handled += 1
    return {"messages": {"handled": handled}}
