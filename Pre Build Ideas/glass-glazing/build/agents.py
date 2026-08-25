#!/usr/bin/env python3
"""Pane OS — the agents. Everything routes through `core.gate`. Stdlib only."""
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

    if c["label"] == "breakin_boardup":
        # The dispatch goes FIRST — an open storefront is a security event, and
        # the crew moves before any reply copy exists.
        r = gate.act("dispatch_board_up", "dispatch", msg_id,
                     {"summary": "board-up crew dispatched — storefront open to the street",
                      "security_event": True, "from": m.get("from")})
        out["steps"].append({"action": "dispatch_board_up", "gate": r,
                             "why": "a security event — the board-up dispatches first; the "
                                    "glass order comes second"})
        body = _boardup_copy(m)
        gate.act("draft_boardup_reply", "dispatch", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_boardup_reply", "draft": body,
                             "why": "the customer hears what already moved, not what might"})
    elif c["label"] == "quote_ask":
        qr = m.get("quote_request") or {}
        if qr.get("location") and qr.get("glass_type"):
            sc = core.safety_check(qr["location"], qr["glass_type"])
            if "refused" in sc:
                ev = store.log_event("refused", msg_id, "agent:estimator", "R0",
                                     {"action": "quote_annealed_in_safety_location",
                                      "why": sc["refused"]})
                body = _quote_safety_copy(m, sc)
                gate.act("draft_quote", "estimator", msg_id,
                         {"summary": m.get("text", "")[:60], "preview": body[:110]})
                m["draft_reply"] = body
                out["steps"].append({"action": "draft_quote", "draft": body,
                                     "refused": sc["refused"], "event": ev["id"],
                                     "why": "the recorded rule is cited; the quote drafts as "
                                            "safety glazing instead"})
            else:
                body = _quote_copy(m)
                gate.act("draft_quote", "estimator", msg_id,
                         {"summary": m.get("text", "")[:60], "preview": body[:110]})
                m["draft_reply"] = body
                out["steps"].append({"action": "draft_quote", "draft": body,
                                     "why": "safety check passed — the quote still waits on "
                                            "two recorded measurements"})
        else:
            body = _quote_copy(m)
            gate.act("draft_quote", "estimator", msg_id,
                     {"summary": m.get("text", "")[:60], "preview": body[:110]})
            m["draft_reply"] = body
            out["steps"].append({"action": "draft_quote", "draft": body,
                                 "why": "location and glass type set what the code allows — "
                                        "the draft asks before it prices"})
    elif c["label"] == "status":
        o = store.by_id("orders", m.get("order_id")) if m.get("order_id") else None
        if not o:
            out["steps"].append({"action": "route_human",
                                 "why": "status ask with no matched order — a person confirms "
                                        "which job before anything is promised"})
        else:
            lt = core.lead_time(o)
            if "_missing" in lt:
                ev = store.log_event("refused", o["id"], "agent:frontdesk", "R0",
                                     {"action": "promise_undated_lead_time",
                                      "why": lt["_missing"]})
                body = _nodate_copy(m)
                gate.act("draft_status_reply", "frontdesk", msg_id,
                         {"summary": m.get("text", "")[:60], "preview": body[:110]})
                m["draft_reply"] = body
                out["steps"].append({"action": "draft_status_reply", "draft": body,
                                     "refused": lt["_missing"], "event": ev["id"],
                                     "why": "no recorded fabricator date — the reply says so "
                                            "instead of inventing one"})
            else:
                body = _status_copy(m, lt)
                gate.act("draft_status_reply", "frontdesk", msg_id,
                         {"summary": m.get("text", "")[:60], "preview": body[:110]})
                m["draft_reply"] = body
                out["steps"].append({"action": "draft_status_reply", "draft": body,
                                     "why": "the fabricator's recorded date is cited — nothing "
                                            "promised from hope"})
    elif c["label"] == "warranty_claim":
        body = _warranty_copy(m)
        gate.act("draft_warranty_reply", "frontdesk", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_warranty_reply", "draft": body,
                             "why": "the order record and the fabricator's warranty terms do "
                                    "the talking"})
    elif c["label"] == "change_request":
        o = store.by_id("orders", m.get("order_id")) if m.get("order_id") else None
        body = _change_copy(m, o)
        gate.act("draft_change_reply", "frontdesk", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_change_reply", "draft": body,
                             "why": "priced against where the order sits — after release, a "
                                    "change is a new unit, said out loud"})
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("messages", m)
    return out


# ---------------------------------------------------------------- drafted copy

def _boardup_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — the board-up crew is dispatched now to seal the opening; we treat an "
            f"open storefront as a security event, not a glass order yet. Photos for your "
            f"insurance get taken before we touch anything. The replacement gets measured once "
            f"the storefront is secure — twice, actually, because that's the only way we order "
            f"custom glass.")


def _quote_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — happy to quote it, and two things come before a number: where the "
            f"glass lives (a door, a shower, near the floor, or by stairs changes what the "
            f"code allows), and a measure visit — we quote from recorded measurements, taken "
            f"twice, because a remake off a guessed size costs everyone more than the quote.")


def _quote_safety_copy(m, sc):
    who = (m.get("from") or "there").split()[0]
    rule = sc["rule"]
    return (f"Hi {who} — one honest correction before the price: that opening counts as "
            f"{rule['label']}, and the rule we work to says {rule['rule'].lower()}. So the "
            f"quote you'll get is for {sc['required']} — we don't sell code violations "
            f"cheaper. Annealed there is the lower number right up until it breaks on "
            f"someone.")


def _status_copy(m, lt):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — straight from the record: {lt['basis']} for your glass is "
            f"{str(lt['date'])[:10]}. Install gets scheduled off that date the day the glass "
            f"lands, and if the fabricator moves it, you hear it from us the same day — not "
            f"after.")


def _nodate_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — honest answer: the fabricator hasn't confirmed a date for your glass "
            f"yet, and we don't promise dates we don't hold. The moment their confirmation "
            f"lands you get it verbatim. What we won't do is guess — a made-up date helps for "
            f"exactly one phone call.")


def _warranty_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — fog between the panes is a failed seal, and that's a unit "
            f"replacement, not a cleaning. We're pulling your order record for the glass spec "
            f"and the fabricator's warranty terms; if it's inside the seal warranty the claim "
            f"goes in this week and you'll see their answer word for word. Nothing about this "
            f"gets guessed at the counter.")


def _change_copy(m, order):
    who = (m.get("from") or "there").split()[0]
    if order and order.get("released_at"):
        return (f"Hi {who} — straight answer: your glass is already released to the "
                f"fabricator, so a size or spec change from here is a new unit, not an edit — "
                f"we'd rather say that now than surprise you on the invoice. If the change "
                f"matters, we'll price it today and you decide with real numbers.")
    return (f"Hi {who} — good timing: nothing has gone to the fabricator yet, so this is an "
            f"edit, not a remake. We'll update the order and re-run the measure check — two "
            f"recorded readings on the new size before anything releases.")


# ---------------------------------------------------------------- the release path

def release_order(order_id):
    """The only path to the fabricator. Measure-twice gate, then the deposit
    wall, then the R1 click. There is no force path."""
    o = store.by_id("orders", order_id)
    if not o:
        return {"error": "no such order"}
    okm, why = core.measure_check(o)
    if not okm:
        ev = store.log_event("refused", order_id, "agent:orders", "R0",
                             {"action": "release_order_without_matching_measurements",
                              "why": why})
        return {"refused": why, "event": ev["id"]}
    okd, whyd = core.deposit_check(o)
    if not okd:
        ev = store.log_event("refused", order_id, "agent:orders", "R0",
                             {"action": "release_fabrication_without_deposit", "why": whyd})
        return {"refused": whyd, "event": ev["id"]}
    return gate.act("release_to_fabricator", "orders", order_id,
                    {"summary": f"{why[:90]} · {whyd[:60]}"})


def answer_lead_time(order_id):
    o = store.by_id("orders", order_id)
    if not o:
        return {"error": "no such order"}
    lt = core.lead_time(o)
    if "_missing" in lt:
        ev = store.log_event("refused", order_id, "agent:frontdesk", "R0",
                             {"action": "promise_undated_lead_time", "why": lt["_missing"]})
        return {"refused": lt["_missing"], "event": ev["id"]}
    return lt


def check_quote(location, glass_type):
    sc = core.safety_check(location, glass_type)
    if "refused" in sc:
        ev = store.log_event("refused", f"quote:{location}", "agent:estimator", "R0",
                             {"action": "quote_annealed_in_safety_location",
                              "why": sc["refused"]})
        return {"refused": sc["refused"], "rule": sc["rule"],
                "rules_source": sc["rules_source"], "event": ev["id"]}
    return sc


def release_sweep(limit=15):
    """Queue the R1 release for every order that clears both gates. Demo
    fixtures are skipped — the sweep never touches staged scenes."""
    out = {"queued": 0, "held": 0, "skipped": 0}
    for o in store.load("orders"):
        if out["queued"] >= limit:
            break
        if o.get("demo_tag") or o.get("stage") != "deposit" or o.get("released_at") \
           or o.get("release_queued_at") or not o.get("deposit_paid_at"):
            out["skipped"] += 1
            continue
        okm, why = core.measure_check(o)
        if not okm:
            out["held"] += 1
            continue
        gate.act("release_to_fabricator", "orders", o["id"], {"summary": why[:100]})
        o["release_queued_at"] = iso()
        store.upsert("orders", o)
        out["queued"] += 1
    return out


def run_all():
    handled = 0
    for m in store.load("messages"):
        if not m.get("handled_at"):
            handle_message(m["id"])
            handled += 1
    return {"messages": {"handled": handled}, "releases": release_sweep()}
