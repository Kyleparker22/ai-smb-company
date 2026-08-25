#!/usr/bin/env python3
"""Lot OS — the agents. Everything routes through `core.gate`. Stdlib only."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import iso, now, parse


def handle_message(msg_id):
    m = store.by_id("leads", msg_id)
    if not m:
        return {"error": "no such message"}
    c = core.read_message(m.get("text", ""))
    out = {"message": msg_id, "classification": c, "steps": []}
    gate.act("read_message", "desk", msg_id, {"label": c["label"], "why": c["why"]})

    if c["label"] == "lead":
        body = _lead_copy(m, 1)
        gate.act("draft_lead_reply", "desk", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m.setdefault("touches", []).append({"at": iso(), "kind": "drafted", "body": body})
        out["steps"].append({"action": "draft_lead_reply", "draft": body,
                             "why": "minutes matter — the draft is ready before the coffee is"})
    elif c["label"] == "condition_ask":
        unit = store.by_id("units", m.get("unit_id")) if m.get("unit_id") else None
        cs = core.condition_statement(unit or {})
        if cs.get("refused"):
            ev = store.log_event("refused", msg_id, "agent:desk", "R0",
                                 {"action": "assert_condition_beyond_record", "why": cs["refused"]})
            out["steps"].append({"action": "refuse_condition_copy", "refused": cs["refused"],
                                 "event": ev["id"]})
        else:
            body = _condition_copy(m, cs)
            gate.act("draft_condition_reply", "desk", msg_id,
                     {"summary": cs["statement"][:60], "preview": body[:110]})
            out["steps"].append({"action": "draft_condition_reply", "draft": body,
                                 "why": cs["note"]})
    elif c["label"] == "trade_ask":
        band = core.trade_band(m.get("model_key") or "unknown")
        if "_missing" in band:
            ev = store.log_event("refused", msg_id, "agent:desk", "R0",
                                 {"action": "guess_trade_value", "why": band["_missing"]})
            body = _trade_refuse_copy(m)
            out["steps"].append({"action": "refuse_trade_guess", "draft": body,
                                 "refused": band["_missing"], "event": ev["id"]})
        else:
            body = _trade_band_copy(m, band)
            gate.act("draft_lead_reply", "desk", msg_id,
                     {"summary": f"trade band {band['band']}", "preview": body[:110]})
            out["steps"].append({"action": "draft_trade_reply", "draft": body,
                                 "why": band["basis"]})
    elif c["label"] == "payment_ask":
        deal = store.by_id("deals", m.get("deal_id")) if m.get("deal_id") else None
        pq = core.payment_quote(deal or {})
        if pq.get("refused"):
            ev = store.log_event("refused", msg_id, "agent:desk", "R0",
                                 {"action": "quote_payment_without_terms", "why": pq["refused"]})
            body = _finance_copy(m)
            out["steps"].append({"action": "invite_finance_conversation", "draft": body,
                                 "refused": pq["refused"], "event": ev["id"]})
        else:
            body = f"{pq['disclosure']} That works out to about ${pq['monthly']:,.0f}/mo."
            gate.act("draft_payment_reply", "desk", msg_id,
                     {"summary": f"${pq['monthly']:,.0f}/mo from recorded terms",
                      "preview": body[:110]})
            out["steps"].append({"action": "draft_payment_reply", "draft": body,
                                 "why": pq["note"]})
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("leads", m)
    return out


def _lead_copy(m, touch_n):
    who = (m.get("from") or "there").split()[0]
    return {
        1: (f"Hi {who} — yes, it's here and available as of this minute. Want to hold it for a "
            f"look? Reply with a time today or tomorrow and it'll be pulled up front, keys ready. "
            f"— and if it sells first, we'll tell you straight away rather than let you drive over."),
        2: (f"Hi {who} — still available, and two other people have asked since you did. Not "
            f"pressure, just the honest state of it. A ten-minute look holds nothing over you."),
        3: (f"Hi {who} — last note on this one. If the timing's off, tell us what you're actually "
            f"hunting for and we'll flag you when one lands on the lot."),
    }.get(touch_n, f"Hi {who} — following up.")


def _condition_copy(m, cs):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — straight from the record: {cs['statement']} That report rides with the "
            f"car — you'll get the full copy before you sign anything, and the car is yours to "
            f"take to any mechanic first.")


def _trade_band_copy(m, band):
    who = (m.get("from") or "there").split()[0]
    lo, hi = band["band"]
    return (f"Hi {who} — from our own recent purchases of that model, the honest range is "
            f"${lo:,.0f}–${hi:,.0f} depending on miles and condition. The exact number takes "
            f"eyes on the car — bring it by and you'll have it in twenty minutes, no obligation.")


def _trade_refuse_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — honest answer: we haven't bought enough of that exact model recently to "
            f"give you a fair number by text, and a made-up one would just waste your trip. "
            f"Bring it by and the appraisal takes twenty minutes, no obligation.")


def _finance_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — payment numbers depend on the lender's actual terms for you, and "
            f"guessing them in a text helps nobody. Five minutes with our finance desk gets you "
            f"real numbers in writing — want morning or afternoon?")


def mark_delivered(deal_id):
    d = store.by_id("deals", deal_id)
    if not d:
        return {"error": "no such deal"}
    okd, why = core.can_deliver(d)
    if not okd:
        ev = store.log_event("refused", deal_id, "agent:desk", "R0",
                             {"action": "deliver_without_title_status", "why": why})
        return {"refused": why, "event": ev["id"]}
    return gate.act("mark_delivered", "desk", deal_id, {"summary": why})


def lead_sweep(limit=20):
    out = {"drafted": 0, "to_call": 0, "skipped": 0}
    for l in store.load("leads"):
        if out["drafted"] >= limit or l.get("label") not in ("lead", None):
            continue
        plan = core.lead_plan(l)
        if plan["action"] == "draft_touch":
            touch_n = len(l.get("touches") or []) + 1
            body = _lead_copy(l, touch_n)
            gate.act("draft_lead_reply", "desk", l["id"],
                     {"summary": f"lead touch {touch_n}", "preview": body[:110]})
            l.setdefault("touches", []).append({"at": iso(), "kind": "drafted", "body": body})
            store.upsert("leads", l)
            out["drafted"] += 1
        elif plan["action"] == "call":
            out["to_call"] += 1
        else:
            out["skipped"] += 1
    return out


def aging_sweep(limit=15):
    out = {"alerts": 0}
    already = {e["subject"] for e in store.events(kind="aging_alert", since_days=7)}
    for r in core.aged_board():
        if out["alerts"] >= limit or r.get("days") is None or r["days"] < 60 \
           or r["unit"] in already:
            continue
        gate.act("aging_alert", "desk", r["unit"],
                 {"summary": f"{r['desc']}: {r['days']}d on the lot" +
                             (f", ${r['interest_accrued']:,.0f} floorplan accrued"
                              if r.get("interest_accrued") else "")})
        out["alerts"] += 1
    return out


def run_all():
    handled = 0
    for m in store.load("leads"):
        if not m.get("handled_at"):
            handle_message(m["id"])
            handled += 1
    return {"messages": {"handled": handled}, "leads": lead_sweep(), "aging": aging_sweep()}
