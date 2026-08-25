#!/usr/bin/env python3
"""Flue OS — the agents. Everything routes through `core.gate`. Stdlib only."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import iso, now, parse


def household_for(m):
    name = (m or {}).get("from")
    if not name:
        return None
    for hh in store.load("households"):
        if hh.get("name") == name:
            return hh
    return None


def handle_message(msg_id):
    m = store.by_id("messages", msg_id)
    if not m:
        return {"error": "no such message"}
    c = core.read_message(m.get("text", ""))
    out = {"message": msg_id, "classification": c, "steps": []}
    gate.act("read_message", "intake", msg_id, {"label": c["label"], "why": c["why"]})
    label = c["label"]

    if label == "co_smoke_event":
        gate.act("escalate_co_event", "intake", msg_id,
                 {"from": m.get("from"), "verbatim": m.get("text", "")})
        r0 = gate.act("co_event_as_booking", "intake", msg_id,
                      {"why": "an active CO/smoke event is never a booking"})
        m["draft_reply"] = core.EVACUATE_SCRIPT
        out["steps"].append({"action": "escalate_co_event", "draft": core.EVACUATE_SCRIPT,
                             "refused": "nothing is scheduled by this message — the evacuate "
                                        "script and 911 are the whole reply; a tech follows up "
                                        "only after the house is cleared",
                             "why": c["why"], "event": r0.get("event")})
    elif label == "safe_to_burn_ask":
        hh = household_for(m)
        v = core.burn_verdict(hh) if hh else \
            {"verdict": "book_the_inspection",
             "why": "no household record matched this sender — no record, no verdict"}
        if v["verdict"] == "book_the_inspection":
            r0 = gate.act("declare_safe_to_burn", "hearth", msg_id, {"why": v["why"]})
            body = _book_inspection_copy(m)
            m["draft_reply"] = body
            out["steps"].append({"action": "book_the_inspection", "draft": body,
                                 "refused": v["why"], "event": r0.get("event"),
                                 "why": c["why"]})
        else:
            insp = core.latest_inspection(hh)
            body = _citation_copy(m, v)
            okv, whyv = core.hazard_verbatim_ok(body, insp.get("findings") or [])
            assert okv, whyv  # structural: the shipped copy passes its own check
            oks, whys = core.soften_ok(body)
            assert oks, whys
            gate.act("draft_burn_reply", "hearth", msg_id,
                     {"summary": f"L{v['citation']['level']} cited to {m.get('from')}",
                      "preview": body[:110]})
            m["draft_reply"] = body
            out["steps"].append({"action": "draft_burn_reply", "draft": body, "why": v["why"]})
    elif label == "chimney_fire_aftermath":
        rule = core.aftermath_rule()
        r0 = gate.act("sweep_after_chimney_fire", "hearth", msg_id,
                      {"why": "a sweep is not the response to a chimney fire"})
        body = _aftermath_copy(m, rule)
        gate.act("draft_booking_reply", "scheduler", msg_id,
                 {"summary": f"Level {rule['required_level']} after chimney fire",
                  "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "book_level3", "draft": body,
                             "refused": "a sweep alone cannot be booked for this — the recorded "
                                        "rule requires the Level 3 first",
                             "event": r0.get("event"), "why": c["why"]})
    elif label == "booking":
        body = _booking_copy(m)
        gate.act("draft_booking_reply", "scheduler", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_booking_reply", "draft": body,
                             "why": "drafted against the season book"})
    elif label == "quote":
        body = _quote_copy(m)
        gate.act("draft_quote_reply", "scheduler", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_quote_reply", "draft": body,
                             "why": "the recorded price book does the talking"})
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=label)
    store.upsert("messages", m)
    return out


def _citation_copy(m, v):
    who = (m.get("from") or "there").split()[0]
    cite = v["citation"]
    date = str(cite["date"])[:10]
    if v["verdict"] == "hazard_on_record":
        hz = " ".join(v["hazards"])
        return (f"Hi {who} — we won't soften this. Your recorded Level {cite['level']} "
                f"inspection on {date} ({cite['tech']}) found: {hz} Do not light a fire until "
                f"that is remediated — reply and we'll book the remediation and the follow-up "
                f"inspection now.")
    findings = "; ".join(cite["findings"]) if cite["findings"] else "no findings recorded"
    return (f"Hi {who} — here is the record, and the record is the answer: Level "
            f"{cite['level']} inspection on {date} by {cite['tech']}. Findings: {findings}. "
            f"That record is {cite['age_days']} days old — current against the annual standard. "
            f"Nothing beyond that record is declared by this message; if anything has changed "
            f"since (a new appliance, storm damage, an odor), tell us before you light and "
            f"we'll look.")


def _book_inspection_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — honest answer: we don't have a current inspection on record for your "
            f"chimney, and 'safe to burn' without the record is a guess we won't put in "
            f"writing. Book the inspection — a Level 1 if nothing about the system has "
            f"changed — and you'll have a real answer with the findings in writing, usually "
            f"the same week.")


def _aftermath_copy(m, rule):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — glad you're safe. If anything is still smoldering or you smell smoke "
            f"right now, that's 911 first, before anything else. After a chimney fire the "
            f"recorded rule is a Level {rule['required_level']} inspection before the next "
            f"fire is lit — not a sweep. ({rule['_source']}) We're holding a Level 3 slot; "
            f"reply with a day and it's booked.")


def _booking_copy(m, ref=None):
    who = (m.get("from") or "there").split()[0]
    body = (f"Hi {who} — annual sweep, let's set it. Reply with two days that work and the "
            f"earlier open tech-day is yours.")
    sb = core.season_board(ref)
    offer = sb.get("offer") if isinstance(sb, dict) else None
    if offer:
        body += " " + _offer_line(sb, offer)
    return body


def _offer_line(sb, offer):
    if offer.get("discount_pct"):
        return (f"Heads up: the season book is at capacity ({sb['due_book']} due vs "
                f"{sb['month_capacity']} slots this month) — the recorded off-season rate "
                f"takes {offer['discount_pct']}% off a February slot if you'd rather skip "
                f"the crush.")
    return ("Heads up: the season book is at capacity — a February slot is open if you'd "
            "rather skip the crush.")


def _quote_copy(m):
    who = (m.get("from") or "there").split()[0]
    pb = store.load("config").get("price_book") or {}
    if pb.get("sweep"):
        return (f"Hi {who} — from the recorded price book: a standard sweep is "
                f"${pb['sweep']:,.0f}. Anything structural — cap, liner, crown — gets eyes on "
                f"it before a number; the figure you get is the figure recorded, not a guess "
                f"over text.")
    return (f"Hi {who} — a person follows up with the number: no recorded price covers this "
            f"ask, and we don't invent one over text.")


def _recall_copy(hh, touch_n, offer=None, sb=None):
    who = (hh.get("name") or "there").split()[0]
    age = core.service_age_days(hh) or 0
    months = max(12, age // 30)
    body = {
        1: (f"Hi {who} — it's been {months} months since your chimney's last recorded "
            f"service; the annual is due. Reply with a day that works and we'll set it."),
        2: (f"Hi {who} — second note on the annual: the season book fills front to back, and "
            f"your record shows {months} months since service. Two minutes now saves the "
            f"January scramble."),
        3: (f"Hi {who} — last note from us this season on the annual. If now isn't the time, "
            f"that's a real answer and we'll leave it here."),
    }.get(touch_n, f"Hi {who} — your annual sweep is due.")
    if offer and sb:
        body += " " + _offer_line(sb, offer)
    return body


def draft_report(hh_id):
    hh = store.by_id("households", hh_id)
    rep = core.report_draft(hh)
    if "refused" in rep:
        ev = store.log_event("refused", hh_id, "agent:reports", "R0",
                             {"action": "draft_report", "why": rep["refused"]})
        return {"refused": rep["refused"], "event": ev["id"]}
    r = gate.act("draft_report", "reports", hh_id,
                 {"summary": f"Level {rep['level']} report — {hh.get('name')}",
                  "preview": rep["body"][:110]})
    return {"body": rep["body"], "gate": r}


def recall_sweep(limit=20, ref=None):
    sb = core.season_board(ref)
    offer = sb.get("offer") if isinstance(sb, dict) else None
    out = {"drafted": 0, "skipped": 0}
    for hh in store.load("households"):
        if out["drafted"] >= limit:
            break
        plan = core.recall_plan(hh, ref)
        if plan["action"] != "draft_recall":
            out["skipped"] += 1
            continue
        touch_n = len(hh.get("recall_touches") or []) + 1
        body = _recall_copy(hh, touch_n, offer=offer, sb=sb if offer else None)
        gate.act("draft_recall", "recall", hh["id"],
                 {"summary": f"{hh.get('name')} — {plan.get('age_days')}d since service, "
                             f"touch {touch_n}",
                  "preview": body[:110]})
        hh.setdefault("recall_touches", []).append({"at": iso(), "kind": "drafted",
                                                    "body": body})
        store.upsert("households", hh)
        out["drafted"] += 1
    return out


def run_all():
    handled = 0
    for m in store.load("messages"):
        if not m.get("handled_at"):
            handle_message(m["id"])
            handled += 1
    return {"messages": {"handled": handled}, "recall": recall_sweep()}
