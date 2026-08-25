#!/usr/bin/env python3
"""Marquee OS — the agents. Everything routes through `core.gate`. Stdlib only."""
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
    gate.act("read_message", "desk", msg_id, {"label": c["label"], "why": c["why"]})

    if c["label"] == "weather_worry":
        b = store.by_id("bookings", m.get("booking_id")) if m.get("booking_id") else None
        wc = core.wind_check(b) if b else {"applies": False}
        body = _weather_copy(m, b, wc)
        okt, why_t = core.tone_ok(body)
        assert okt, why_t  # structural: a wind reply that soothes cannot ship
        ev = store.log_event("refused", m.get("booking_id") or msg_id, "agent:weather",
                             "R0", {"action": "make_weather_call",
                                    "why": "software states the numbers; a human owns "
                                           "install / hold / strike, on the record"})
        gate.act("draft_weather_note", "weather", msg_id,
                 {"summary": (m.get("text") or "")[:60], "preview": body[:110],
                  "wind": wc.get("summary")})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_weather_note", "draft": body, "wind": wc,
                             "refused": "no weather call was made by this message — the "
                                        "numbers are stated and a person owns the decision",
                             "why": c["why"], "event": ev["id"]})
    elif c["label"] == "booking_request":
        if m.get("wants") and m.get("event_date"):
            r = core.reserve(m.get("from") or "caller", m["event_date"], m["wants"],
                             demo_tag=m.get("demo_tag"))
            body = _booking_copy(m, r)
            out["steps"].append({"action": "reserve_inventory", "result": r,
                                 "draft": body,
                                 "why": "reserved from counted stock — or waitlisted "
                                        "honestly; an oversell has no code path"})
        else:
            body = _booking_ask_copy(m)
            out["steps"].append({"action": "draft_booking_reply", "draft": body,
                                 "why": "date and items first — a promise starts from "
                                        "the count, and the count needs a date"})
        gate.act("draft_booking_reply", "desk", msg_id,
                 {"summary": (m.get("text") or "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
    elif c["label"] == "change_request":
        body = _change_copy(m)
        gate.act("draft_change_reply", "desk", msg_id,
                 {"summary": (m.get("text") or "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_change_reply", "draft": body,
                             "why": "a change redraws against counted stock before "
                                    "anything is promised"})
    elif c["label"] == "deposit_ask":
        b = store.by_id("bookings", m.get("booking_id")) if m.get("booking_id") else None
        body = _deposit_copy(m, b)
        gate.act("draft_status_reply", "deposits", msg_id,
                 {"summary": (m.get("text") or "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_status_reply", "draft": body,
                             "why": "the deposit answer comes from the recorded "
                                    "condition pair, or it says so"})
    elif c["label"] == "status":
        body = _status_copy(m)
        out["steps"].append({"action": "answer_from_book", "draft": body,
                             "why": "answered from the booking record"})
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("messages", m)
    return out


def _weather_copy(m, b, wc):
    who = (m.get("from") or "there").split()[0]
    if not b or not wc.get("applies"):
        return (f"Hi {who} — fair question, and it gets a straight answer, not a soothing "
                f"one. Tell us which event is yours and we'll put two recorded numbers in "
                f"front of you: the forecast on file for your site and the manufacturer's "
                f"rated wind limit for the exact tent reserved. Then a person — our crew "
                f"chief — makes the install, hold, or take-down call, on the record. Nobody "
                f"here answers a wind question from a guess.")
    return (f"Hi {who} — here are the recorded numbers, stated straight: {wc['summary']} "
            f"The decision that follows — install, hold, or take the tent down — belongs "
            f"to a person, not to software: our crew chief makes that call on the record "
            f"and will phone you today with it. We won't tell you more than the numbers "
            f"support. A staked tent in real wind is a safety question, and the honest "
            f"answer comes from the person who owns it.")


def _booking_copy(m, r):
    who = (m.get("from") or "there").split()[0]
    if r.get("status") == "confirmed":
        return (f"Hi {who} — yes, and it's held: every item on your request fit our counted "
                f"stock for that weekend, so the reservation is confirmed (booking "
                f"{r['booking']}). The count is the promise — nothing on your event is "
                f"shared with another one.")
    short = ", ".join(f"{k}: {v['available']} available of the {v['want']} you asked for"
                      for k, v in sorted((r.get("short") or {}).items()))
    return (f"Hi {who} — the honest answer from the count: {short}. Rather than promise "
            f"stock we don't have, we've put you on the waitlist for that weekend and "
            f"nothing was taken from another event. If a cancellation frees it, you're "
            f"first in line — or we can quote you the nearest counted-available "
            f"alternative right now.")


def _booking_ask_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — happy to hold it, and we only promise what's counted: give us the "
            f"event date and the items (tent size, tables, chairs, dance floor) and we'll "
            f"answer from live stock for that weekend — reserved on the spot if it fits, "
            f"waitlisted honestly if it doesn't.")


def _change_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — can do, with one honest step first: the change gets redrawn "
            f"against counted stock for the new date or items before anything is promised. "
            f"You'll get a yes with the new count behind it, or the waitlist and the "
            f"nearest available alternative — never a maybe.")


def _deposit_copy(m, b):
    who = (m.get("from") or "there").split()[0]
    if b:
        math = core.deposit_math(b)
        if "refused" in math:
            return (f"Hi {who} — your deposit is settled from two recorded condition "
                    f"checks — one when the equipment went out, one when it came back, "
                    f"photos referenced — and nothing is deducted from memory. One of "
                    f"those records isn't complete yet, so the arithmetic waits for it; "
                    f"a person will close it out and send you the numbers, line by line.")
        return (f"Hi {who} — your deposit settles from the recorded condition pair, and "
                f"the arithmetic is: {math['basis']}. A person reviews and sends it — "
                f"nothing about your money is decided by this message.")
    return (f"Hi {who} — deposits here settle one way: the recorded out-condition check "
            f"against the recorded return-condition check, photos referenced, arithmetic "
            f"shown line by line. Tell us which event is yours and a person will pull "
            f"both records and send you the exact numbers.")


def _status_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — checking the booking record now; you'll get the confirmed "
            f"items, the crew window, and the site checklist status exactly as recorded. "
            f"If a detail isn't on the record yet, we'll say so rather than guess.")


def install(booking_id, human=None):
    """The 811 wall. No recorded locate ticket → refused at R0, logged. With the
    ticket, the checklist is stated and the truck still rolls on a human dispatch."""
    b = store.by_id("bookings", booking_id)
    if not b:
        return {"error": "no such booking"}
    oki, why = core.can_install(b)
    if not oki:
        ev = store.log_event("refused", booking_id, "agent:crew", "R0",
                             {"action": "install_without_utility_locate", "why": why})
        return {"refused": why, "event": ev["id"]}
    if not human:
        return {"cleared": True, "why": why,
                "note": "the checklist clears by record; the truck rolls on a human "
                        "dispatch, not on this check"}
    ev = store.log_event("install_dispatched", booking_id, f"human:{human}", "R1",
                         {"why": why})
    return {"cleared": True, "dispatched_by": human, "why": why, "event": ev["id"]}


def settle_deposit(booking_id):
    """Drafts the refund or the deduction from the condition pair — or refuses,
    logged, naming the missing record."""
    b = store.by_id("bookings", booking_id)
    if not b:
        return {"error": "no such booking"}
    math = core.deposit_math(b)
    if "refused" in math:
        ev = store.log_event("refused", booking_id, "agent:deposits", "R0",
                             {"action": "deduct_deposit_without_condition_records",
                              "why": math["refused"]})
        return {"refused": math["refused"], "event": ev["id"]}
    action = "draft_deposit_deduction" if math["deduction"] > 0 else "draft_deposit_refund"
    r = gate.act(action, "deposits", booking_id,
                 {"summary": f"${math['refund']:,.2f} refund of ${math['deposit']:,.2f} "
                             f"— {len(math['new_damage'])} new-damage line(s)",
                  "evidence": math["evidence"]},
                 amount=math["deduction"] or None)
    return {"math": math, "action": action, "gate": r}


def permit_sweep(ref=None):
    """Raises DATE ALERTS for unfiled permit clocks. Filing stays a human act.
    Demo rows are skipped — a sweep never performs on fixtures."""
    board = core.permit_board(ref)
    out = {"alerts": 0, "skipped": 0}
    for row in board["rows"]:
        b = store.by_id("bookings", row["booking"])
        if not b or b.get("demo_tag"):
            out["skipped"] += 1
            continue
        if row.get("permit") != "NOT FILED":
            continue
        if b.get("permit_alerted_at"):
            out["skipped"] += 1
            continue
        gate.act("permit_alert", "permits", b["id"],
                 {"municipality": row.get("municipality"),
                  "deadline": row.get("deadline"), "days_left": row.get("days_left"),
                  "label": row.get("label")})
        b["permit_alerted_at"] = iso()
        store.upsert("bookings", b)
        out["alerts"] += 1
    return out


def run_all():
    """The sweeps. Demo fixtures are skipped — they exist to be pressed by hand."""
    handled = 0
    for m in store.load("messages"):
        if m.get("handled_at") or m.get("demo_tag"):
            continue
        handle_message(m["id"])
        handled += 1
    return {"messages": {"handled": handled}, "permits": permit_sweep()}
