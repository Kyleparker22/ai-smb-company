#!/usr/bin/env python3
"""Shine OS — the agents. Everything routes through `core.gate`. Stdlib only."""
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

    if c["label"] == "damage_claim":
        claim = {"id": store.nid("cl"), "message_id": msg_id, "text": m.get("text"),
                 "from": m.get("from"), "filed_at": m.get("at") or iso()}
        store.upsert("claims", claim)
        gate.act("log_damage_claim", "frontdesk", claim["id"],
                 {"verbatim": m.get("text", ""), "from": m.get("from")})
        gate.act("pull_footage_task", "frontdesk", claim["id"],
                 {"summary": f"pull tunnel footage for {m.get('from','the visit')}"})
        ev = store.log_event("refused", claim["id"], "agent:frontdesk", "R0",
                             {"action": "deny_damage_claim",
                              "why": "software never argues physics"})
        out["steps"].append({"action": "log_damage_claim", "said": core.CLAIM_PROTOCOL,
                             "why": c["why"], "event": ev["id"], "claim": claim["id"]})
    elif c["label"] == "cancellation":
        clock = core.cancellation_clock(m.get("at"))
        member = store.by_id("members", m.get("member_id")) if m.get("member_id") else None
        if member:
            member["cancel_requested_at"] = m.get("at") or iso()
            store.upsert("members", member)
        row = {"id": store.nid("cx"), "member_id": m.get("member_id"),
               "at": m.get("at") or iso(), "process_by": clock["process_by"]}
        store.upsert("cancellations", row)
        gate.act("start_cancel_clock", "frontdesk", row["id"],
                 {"summary": f"process by {clock['process_by'][:10]}", "rule": clock["rule_label"]})
        save = _save_copy(member or {})
        gate.act("draft_save_offer", "frontdesk", m.get("member_id") or msg_id,
                 {"summary": "optional save — processing does NOT wait", "preview": save[:110]})
        out["steps"].append({"action": "start_cancel_clock", "clock": clock,
                             "why": clock["rule_label"]})
    elif c["label"] == "billing":
        body = _billing_copy(m)
        gate.act("draft_billing_reply", "frontdesk", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_billing_reply", "why": "a human sends"})
    elif c["label"] == "detail":
        body = _detail_copy(m)
        gate.act("draft_detail_booking", "frontdesk", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_detail_booking", "why": "a human sends"})
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("messages", m)
    return out


def _save_copy(member):
    name = (member.get("name") or "there").split()[0]
    return (f"Hi {name} — your cancellation is processing as asked, no hoops. Before you go: if "
            f"it's the price, the basic plan is half the rate; if you moved, your membership "
            f"works at every location. If neither helps, no hard feelings — the lanes are open "
            f"whenever.")


def _billing_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — checking your charge history now. If we billed wrong it's refunded this "
            f"week, no forms; you'll have the ledger view by end of day either way.")


def _detail_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — reply with two windows that work and we'll hold one. Details are "
            f"weather-dependent: if the day turns, you'll get the next two open slots the same "
            f"morning, not a voicemail.")


def _weather_copy(d):
    who = (d.get("customer") or "there").split()[0]
    return (f"Hi {who} — today's weather isn't good enough for the {d.get('kind', 'detail')} you "
            f"booked, and a rushed job in the rain isn't worth your money. Two open slots: "
            f"tomorrow 9am or thursday 1pm — reply 1 or 2 and it's yours.")


def dunning_sweep(limit=25):
    out = {"drafted": 0, "to_human": 0, "skipped": 0}
    for mb in store.load("members"):
        if out["drafted"] >= limit or mb.get("demo_tag"):
            continue
        okc, why = core.can_charge(mb)
        if not okc:
            continue  # cancelled members never enter dunning
        plan = core.dunning_plan(mb)
        if plan["action"] == "draft":
            okt, whyt = core.dunning_text_ok(plan["text"])
            if not okt:
                store.log_event("refused", mb["id"], "agent:billing", "R0",
                                {"action": "threaten_in_dunning", "why": whyt})
                continue
            gate.act("draft_dunning", "billing", mb["id"],
                     {"summary": plan["text"][:70], "touch": plan["touch"],
                      "preview": plan["text"][:110]})
            mb.setdefault("dunning_touches", []).append({"at": iso(), "kind": "drafted",
                                                         "body": plan["text"]})
            store.upsert("members", mb)
            out["drafted"] += 1
        elif plan["action"] == "human":
            out["to_human"] += 1
        else:
            out["skipped"] += 1
    return out


def weather_sweep(ref=None):
    """Rained-out details get honest reschedule drafts, one per detail."""
    out = {"drafted": 0}
    already = {e["subject"] for e in store.events(kind="queued_for_approval", since_days=2)
               if (e.get("detail") or {}).get("action") == "draft_detail_booking"}
    for d in store.load("details"):
        if d.get("completed_at") or not d.get("rained_out") or d["id"] in already or d.get("demo_tag"):
            continue
        body = _weather_copy(d)
        gate.act("draft_detail_booking", "frontdesk", d["id"],
                 {"summary": f"weather reschedule: {d.get('kind')}", "preview": body[:110]})
        d["reschedule_drafted_at"] = iso()
        store.upsert("details", d)
        out["drafted"] += 1
    return out


def charge_member(member_id, amount):
    mb = store.by_id("members", member_id)
    if not mb:
        return {"error": "no such member"}
    okc, why = core.can_charge(mb)
    if not okc:
        ev = store.log_event("refused", member_id, "agent:billing", "R0",
                             {"action": "charge_after_cancel_request", "why": why})
        return {"refused": why, "event": ev["id"]}
    return gate.act("draft_dunning", "billing", member_id,
                    {"summary": f"charge ${amount} — active membership"})


def run_all():
    handled = 0
    for m in store.load("messages"):
        if not m.get("handled_at"):
            handle_message(m["id"])
            handled += 1
    return {"messages": {"handled": handled}, "dunning": dunning_sweep(),
            "weather": weather_sweep()}
