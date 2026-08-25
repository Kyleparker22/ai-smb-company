#!/usr/bin/env python3
"""Lab OS — the agents. Everything routes through `core.gate`. Stdlib only."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import iso

FLOOR_LINE = ("Where it says TOO EARLY TO KNOW, that is the answer — below the recorded "
              "sample floor there is no winner to report, and any number would just be "
              "confident noise. The counting continues either way.")


def handle_message(msg_id):
    m = store.by_id("messages", msg_id)
    if not m:
        return {"error": "no such message"}
    c = core.read_message(m.get("text", ""))
    out = {"message": msg_id, "classification": c, "steps": []}
    gate.act("read_message", "intake", msg_id, {"label": c["label"], "why": c["why"]})

    if c["label"] == "illness":
        inc = {"id": store.nid("inc"), "message_id": msg_id, "from": m.get("from"),
               "verbatim": m.get("text", ""), "at": m.get("at") or iso(),
               "path": "human + counsel — a person calls; counsel shapes the language"}
        store.upsert("incidents", inc)
        gate.act("escalate_illness", "intake", inc["id"], {"verbatim": inc["verbatim"]})
        r0 = gate.act("answer_illness_claim", "intake", inc["id"], {"from": m.get("from")})
        out["steps"].append({
            "action": "escalate_illness", "incident": inc["id"], "verbatim_logged": True,
            "refused": ("no written reply exists for this message — a human calls, with "
                        "counsel on the language; software drafts nothing, admits nothing"),
            "why": c["why"], "event": r0.get("event")})
    elif c["label"] == "gm_result_ask":
        body = _gm_copy()
        gate.act("draft_gm_result_reply", "desk", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_gm_result_reply", "draft": body,
                             "why": "the verdicts quoted verbatim — TOO EARLY is a real answer"})
    elif c["label"] == "experiment_proposal":
        body = _desk_ack(m)
        gate.act("draft_desk_ack", "desk", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_desk_ack", "draft": body,
                             "why": "logged for the desk — the overlap rule runs at creation"})
    elif c["label"] == "stockout_report":
        gate.act("log_stockout", "ops", msg_id, {"summary": m.get("text", "")[:80]})
        out["steps"].append({"action": "log_stockout",
                             "why": "recorded — on the ledger it prices from that unit's own "
                                    "recorded pace, or reads unmeasured; never estimated"})
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("messages", m)
    return out


def _gm_copy():
    lines = []
    for e in store.load("experiments"):
        if e.get("status") == "live":
            v = core.verdict(e)
            lines.append(f"“{e['hypothesis']}” — {v['verdict']}")
        elif e.get("status") == "concluded":
            v = e.get("verdict") or {}
            extra = (f", lift {v.get('lift_pct')}% (z={v.get('z')})"
                     if v.get("lift_pct") is not None else "")
            lines.append(f"“{e['hypothesis']}” — concluded {v.get('verdict')}{extra}")
    board = "; ".join(lines) if lines else "no experiments on the board yet"
    return (f"Straight from the desk, nothing massaged: {board}. {FLOOR_LINE}")


def _desk_ack(m):
    return ("Logged at the experiment desk, with the recorded sample floor attached. One "
            "rule before anything runs: one lever per dial — if this touches a metric a "
            "live test is already using on any of the same units, creation refuses it and "
            "the two tests get sequenced instead. A human starts every experiment; the "
            "desk just keeps it honest.")


def run_all():
    """The sweep. Demo fixtures are skipped — they exist to be walked through
    by hand and must never pollute the counted numbers."""
    handled = 0
    for m in store.load("messages"):
        if m.get("handled_at") or m.get("demo_tag"):
            continue
        handle_message(m["id"])
        handled += 1
    return {"messages": {"handled": handled}}
