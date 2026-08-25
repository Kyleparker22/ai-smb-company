#!/usr/bin/env python3
"""Move OS — the agents. Everything routes through `core.gate`. Stdlib only."""
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

    if c["label"] == "claim_report":
        claim = {"id": store.nid("cm"), "move_id": m.get("move_id"),
                 "item": m.get("item") or "reported item", "filed_at": m.get("at") or iso(),
                 "text": m.get("text")}
        store.upsert("claims", claim)
        gate.act("start_claim_clock", "claimsdesk", claim["id"],
                 {"summary": f"claim filed — ack clock running: {m.get('text','')[:50]}"})
        check = core.claim_check(claim)
        ack = _ack_copy(claim, core.claim_clock(claim))
        gate.act("draft_claim_ack", "claimsdesk", claim["id"],
                 {"summary": "acknowledgment draft — no fault taken, no claim denied",
                  "preview": ack[:110]})
        claim["ack_draft"] = ack
        store.upsert("claims", claim)
        out["steps"].append({"action": "start_claim_clock", "claim": claim["id"],
                             "clock": core.claim_clock(claim),
                             "why": "the clock starts at the report, not at the assessment"})
        out["steps"].append({"action": "evidence_check",
                             "refused": check.get("refused"),
                             "evidence": check.get("evidence"), "why": check["note"]
                             if check.get("assessable") else check["refused"]})
    elif c["label"] == "quote_request":
        body = _survey_copy()
        gate.act("draft_survey_offer", "sales", msg_id,
                 {"summary": "survey-first reply", "preview": body[:110]})
        out["steps"].append({"action": "route_to_survey", "draft": body,
                             "why": "survey first, binding second — a guess is not a binding number"})
    elif c["label"] == "date_change":
        gate.act("draft_scheduling_reply", "frontdesk", msg_id,
                 {"summary": m.get("text", "")[:60]})
        out["steps"].append({"action": "draft_scheduling_reply", "why": "a human sends"})
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("messages", m)
    return out


def _ack_copy(claim, clock):
    """The acknowledgment: the clock date out loud, the process named, no
    fault taken and no claim denied — both of those are human calls later."""
    return (f"We received your damage report and it's in our claims process as of "
            f"{str(claim.get('filed_at', ''))[:10]}. You'll have our written response by "
            f"{str(clock.get('ack_due', ''))[:10]}. Photos of the item and the inventory "
            f"sticker (if visible) speed this up. This note confirms receipt — the assessment "
            f"comes from the claims adjuster, not from this message.")


def _survey_copy():
    return ("Happy to price your move properly. A binding number needs a quick survey — video "
            "or in-home, about 20 minutes — because a guess that's wrong becomes YOUR problem "
            "on delivery day, and we don't do that. What works this week?")


def deadline_sweep(ref=None):
    """Internal alarm on claim clocks: any claim inside 5 days of its response
    deadline (or past it) gets one R2 alert per 3 days."""
    from _kit.store import now as _now
    ref = ref or _now()
    out = {"alerts": 0}
    already = {e["subject"] for e in store.events(kind="claim_deadline_alert", since_days=3)}
    for c in store.load("claims"):
        if c.get("settled_at") or c.get("demo_tag") or c["id"] in already:
            continue
        clock = core.claim_clock(c, ref)
        days_left = clock.get("ack_days_left")
        if days_left is None or days_left > 5:
            continue
        gate.act("claim_deadline_alert", "claimsdesk", c["id"],
                 {"summary": f"{'OVERDUE' if days_left < 0 else f'{days_left}d left'} on the "
                             f"written-response clock", "days_left": days_left})
        out["alerts"] += 1
    return out


def issue_binding(move_id):
    """Binding estimate path — refused without a survey + inventory."""
    m = store.by_id("moves", move_id)
    if not m:
        return {"error": "no such move"}
    okb, why = core.can_issue_binding(m)
    if not okb:
        ev = store.log_event("refused", move_id, "agent:sales", "R0",
                             {"action": "issue_binding_without_survey", "why": why})
        return {"refused": why, "event": ev["id"]}
    return gate.act("draft_binding_estimate", "sales", move_id,
                    {"summary": f"binding estimate for {m.get('desc','move')} — {why}"})


def settle_claim(claim_id):
    c = store.by_id("claims", claim_id)
    if not c:
        return {"error": "no such claim"}
    check = core.claim_check(c)
    if not check["assessable"]:
        ev = store.log_event("refused", claim_id, "agent:claimsdesk", "R1",
                             {"action": "draft_claim_settlement", "why": check["refused"]})
        return {**check, "event": ev["id"]}
    r = gate.act("draft_claim_settlement", "claimsdesk", claim_id,
                 {"summary": f"settlement draft: {', '.join(check['new_damage']) or 'no new damage'}",
                  "evidence": check["evidence"]})
    return {**check, "gate": r}


def run_all():
    handled = 0
    for m in store.load("messages"):
        if not m.get("handled_at"):
            handle_message(m["id"])
            handled += 1
    return {"messages": {"handled": handled}, "deadlines": deadline_sweep()}
