#!/usr/bin/env python3
"""Central OS — the agents. Everything routes through `core.gate`. Stdlib only."""
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
    gate.act("read_message", "operator", msg_id, {"label": c["label"], "why": c["why"]})

    if c["label"] == "test_mode_request":
        ev = store.log_event("refused", msg_id, "agent:operator", "R0",
                             {"action": "enter_test_mode_from_message",
                              "verbatim": m.get("text", ""), "from": m.get("from"),
                              "why": "an account never changes state from a message thread"})
        gate.act("open_callback_task", "operator", m.get("account_id") or msg_id,
                 {"summary": f"verified callback re: {m.get('text','')[:50]}",
                  "rule": core.CALLBACK_RULE})
        body = _callback_copy(m)
        out["steps"].append({"action": "refuse_and_open_callback", "draft": body,
                             "refused": "no account state changes from this thread — a verified "
                                        "callback to the number on file settles it in minutes",
                             "why": c["why"], "event": ev["id"]})
    elif c["label"] == "passcode_in_text":
        ev = store.log_event("refused", msg_id, "agent:operator", "R0",
                             {"action": "accept_passcode_in_text",
                              "why": "a passcode in a thread is never accepted or compared"})
        gate.act("open_callback_task", "operator", m.get("account_id") or msg_id,
                 {"summary": "passcode offered in text — callback required",
                  "rule": core.CALLBACK_RULE})
        body = _passcode_copy(m)
        out["steps"].append({"action": "refuse_passcode", "draft": body,
                             "refused": "never over text — the callback rule holds",
                             "why": c["why"], "event": ev["id"]})
    elif c["label"] == "fire_signal":
        out["steps"].append({"action": "dispatch_proceeds",
                             "why": "fire dispatch proceeds and cannot be cancelled by software"})
    elif c["label"] == "burglary_signal":
        gate.act("open_callback_task", "operator", m.get("account_id") or msg_id,
                 {"summary": f"burglary signal: {m.get('text','')[:50]}",
                  "rule": core.CALLBACK_RULE})
        out["steps"].append({"action": "operator_flow",
                             "why": "a cancel is a human decision after verified callback"})
    elif c["label"] == "billing":
        body = _billing_copy(m)
        gate.act("draft_billing_reply", "operator", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_billing_reply", "why": "a human sends"})
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("messages", m)
    return out


def _callback_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — for your protection we never change an account's state from a message "
            f"thread, no matter who's asking (that includes you, and that's the point). We're "
            f"calling the number on file right now; answer that call and this takes two minutes.")


def _passcode_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — please never send a passcode by text; we don't read them, compare them, "
            f"or act on them here, and you should treat any company that does as a red flag. "
            f"We're calling the number on file — the code belongs on that call.")


def _billing_copy(m):
    who = (m.get("from") or "there").split()[0]
    return f"Hi {who} — pulling your account ledger; you'll have the answer in writing today."


def cancel_dispatch(signal_id, human=None, verified_callback=False):
    s = store.by_id("signals", signal_id)
    if not s:
        return {"error": "no such signal"}
    okc, why = core.can_cancel_dispatch(s, human=human, verified_callback=verified_callback)
    if not okc:
        action = ("cancel_fire_dispatch" if s.get("kind") == "fire"
                  else "cancel_burglary_dispatch")
        ev = store.log_event("refused", signal_id, "agent:operator", "R0",
                             {"action": action, "why": why})
        return {"refused": why, "event": ev["id"]}
    store.log_event("dispatch_cancelled", signal_id, f"human:{human}", "R1",
                    {"verified_callback": True})
    return {"cancelled": True, "why": why}


def verify_callback(account_id, operator):
    store.log_event("callback_verified", account_id, f"human:{operator}", "R1",
                    {"rule": core.CALLBACK_RULE})
    return {"verified": True}


def permit_sweep(limit=20):
    out = {"alerts": 0, "renewal_drafts": 0}
    already = {e["subject"] for e in store.events(kind="permit_alert", since_days=14)}
    for a in store.load("accounts"):
        if out["alerts"] >= limit or a.get("demo_tag") or a["id"] in already:
            continue
        ps = core.permit_state(a)
        if ps.get("state") in ("expired", "expiring", "unregistered"):
            gate.act("permit_alert", "compliance", a["id"],
                     {"summary": f"{a.get('name')}: permit {ps.get('state')}",
                      "state": ps.get("state")})
            out["alerts"] += 1
            if ps["state"] in ("expired", "unregistered"):
                gate.act("draft_permit_renewal", "compliance", a["id"],
                         {"summary": f"renewal filing for {a.get('name')} ({a.get('city')})"})
                out["renewal_drafts"] += 1
    return out


def run_all():
    handled = 0
    for m in store.load("messages"):
        if not m.get("handled_at"):
            handle_message(m["id"])
            handled += 1
    return {"messages": {"handled": handled}, "permits": permit_sweep()}
