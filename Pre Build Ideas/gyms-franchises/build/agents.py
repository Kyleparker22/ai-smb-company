#!/usr/bin/env python3
"""Member OS — the agents. Everything routes through `core.gate`. Stdlib only."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import iso, now


def handle_message(msg_id):
    """Triage one message. A cancellation starts the statutory clock at R2 —
    the retention draft is a SEPARATE queue row and processing never waits."""
    m = store.by_id("messages", msg_id)
    if not m:
        return {"error": "no such message"}
    c = core.read_message(m.get("text", ""))
    out = {"message": msg_id, "classification": c, "steps": []}
    gate.act("read_message", "frontdesk", msg_id, {"label": c["label"], "why": c["why"]})
    member = store.by_id("members", m.get("member_id")) if m.get("member_id") else None

    if c["label"] == "cancellation":
        clock = core.cancellation_clock(member or {}, m.get("at"))
        row = {"id": store.nid("cx"), "member_id": m.get("member_id"), "at": m.get("at") or iso(),
               "reason": "requested", "process_by": clock["process_by"], "state": clock["state"]}
        store.upsert("cancellations", row)
        gate.act("start_cancel_clock", "frontdesk", row["id"],
                 {"summary": f"process by {clock['process_by']} ({clock['days']}d window, {clock['state']})",
                  "rule": clock["rule_label"]})
        save_body = _retention_copy(member or {})
        gate.act("draft_retention_offer", "frontdesk", m.get("member_id") or msg_id,
                 {"summary": "optional save offer — processing does NOT wait on this",
                  "preview": save_body[:110]})
        out["steps"].append({"action": "start_cancel_clock", "clock": clock,
                             "why": "the clock starts at the request, not after a save attempt"})
        out["steps"].append({"action": "draft_retention_offer",
                             "why": "a separate row a human may use — or not; the cancel proceeds"})
    elif c["label"] == "injury":
        ev = store.log_event("refused", msg_id, "agent:frontdesk", "R0",
                             {"action": "respond_to_injury", "why": c["why"]})
        out["steps"].append({"action": "escalate_to_human", "kind": "injury",
                             "refused": "nothing drafted — a human calls", "why": c["why"],
                             "event": ev["id"]})
    elif c["label"] == "medical_question":
        ev = store.log_event("refused", msg_id, "agent:frontdesk", "R0",
                             {"action": "medical_claim", "why": c["why"]})
        out["steps"].append({"action": "route_to_human", "refused": "no health promise, ever",
                             "why": c["why"], "event": ev["id"]})
    elif c["label"] == "billing":
        body = _billing_reply_copy(m, member or {})
        gate.act("draft_billing_reply", "frontdesk", msg_id,
                 {"summary": f"draft: {m.get('text','')[:60]}", "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_billing_reply", "why": "a human sends"})
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("messages", m)
    return out


def dunning_sweep(limit=25):
    out = {"drafted": 0, "to_human": 0, "skipped": 0}
    for m in store.load("members"):
        if out["drafted"] >= limit:
            break
        if m.get("demo_tag"):
            continue
        plan = core.dunning_plan(m)
        if plan["action"] == "draft":
            okt, why = core.dunning_text_ok(plan["text"])
            if not okt:
                store.log_event("refused", m["id"], "agent:billing", "R0",
                                {"action": "threaten_collections", "why": why})
                continue
            gate.act("draft_dunning", "billing", m["id"],
                     {"summary": plan["text"][:80], "touch": len(m.get("dunning_touches") or []) + 1})
            m.setdefault("dunning_touches", []).append({"at": iso(), "kind": "drafted"})
            store.upsert("members", m)
            out["drafted"] += 1
        elif plan["action"] == "human":
            out["to_human"] += 1
        else:
            out["skipped"] += 1
    return out


def _retention_copy(member):
    """The save offer a human MAY send — the cancellation processes either way,
    and the copy says so out loud. No guilt, one concrete alternative."""
    name = (member.get("name") or "there").split()[0]
    return (f"Hi {name} — your cancellation is being processed as asked, no hoops. Before you go: "
            f"if the timing or price is the issue, we can freeze your membership free for up to "
            f"3 months or drop to the off-peak plan. If not, no hard feelings — door's open "
            f"whenever.")


def _billing_reply_copy(m, member):
    name = (member.get("name") or "there").split()[0]
    return (f"Hi {name} — looking at your billing note now. If we charged wrong, it's refunded "
            f"this week, no forms. I'll reply with exactly what the ledger shows by end of day.")


def _winback_copy(member):
    name = (member.get("name") or "there").split()[0]
    return (f"Hi {name} — we noticed you haven't been in lately, and this is just a check-in, not "
            f"a pitch. If something about the schedule, the space, or the plan stopped working, "
            f"tell us and we'll fix what's ours to fix. Your spot's here either way.")


WINBACK_COOLDOWN_DAYS = 21


def winback_sweep(limit=15):
    """One no-guilt check-in per at-risk member per 21 days, drafted at R1.
    Two signals is the floor — a list that flags everyone is a list nobody works."""
    out = {"drafted": 0, "skipped": 0}
    board = core.churn_board()
    for row in board["rows"]:
        if out["drafted"] >= limit:
            break
        member = store.by_id("members", row["member"])
        if not member or member.get("demo_tag"):
            continue
        last = member.get("winback_at")
        from _kit.store import parse
        if last and (now() - (parse(last) or now())).days < WINBACK_COOLDOWN_DAYS:
            out["skipped"] += 1
            continue
        body = _winback_copy(member)
        gate.act("draft_winback", "retention", member["id"],
                 {"summary": f"{row['count']} churn signals: " +
                             ", ".join(s["signal"] for s in row["signals"]),
                  "preview": body[:110]})
        member["winback_at"] = iso()
        store.upsert("members", member)
        out["drafted"] += 1
    return out


def run_all():
    handled = 0
    for m in store.load("messages"):
        if not m.get("handled_at"):
            handle_message(m["id"])
            handled += 1
    return {"messages": {"handled": handled}, "dunning": dunning_sweep(),
            "winback": winback_sweep()}
