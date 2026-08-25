#!/usr/bin/env python3
"""Member OS — server. Stdlib only, 127.0.0.1:8837."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8837


def _executor(ap, human):
    def run():
        store.log_event(ap["action"].replace("draft_", "") + "_sent", ap["subject"],
                        f"human:{human}", "R1", {"approval": ap["id"]})
        return ap["subject"]
    return run


def board(q, b):
    cb = core.churn_board()
    split = core.churn_split()
    fails = [p for p in store.load("payments") if p.get("failed") and not p.get("recovered_at")]
    msgs = [m for m in store.load("messages") if not m.get("handled_at")]
    open_cancels = [c for c in store.load("cancellations") if c.get("reason") == "requested"
                    and not c.get("processed_at")]
    return {"config": store.load("config"),
            "board": {"open_failures": len({p["member_id"] for p in fails}),
                      "at_risk": cb["n"], "single_signal": cb["single_signal"],
                      "churn_split": split, "messages_open": len(msgs),
                      "cancel_queue": len(open_cancels),
                      "recovered": core.recovered_this_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/messages"): lambda q, b: {"rows": sorted(store.load("messages"),
        key=lambda m: m.get("at") or "", reverse=True)[:60]},
    ("POST", "/api/messages/<id>/handle"): lambda q, b: agents.handle_message(q["id"]),
    ("GET", "/api/churn"): lambda q, b: core.churn_board(),
    ("GET", "/api/dunning"): lambda q, b: {"rows": [
        {"member": m["id"], "name": m.get("name"), "touches": len(m.get("dunning_touches") or []),
         "plan": core.dunning_plan(m)}
        for m in store.load("members")
        if any(p.get("member_id") == m["id"] and p.get("failed") and not p.get("recovered_at")
               for p in store.load("payments"))][:40],
        "template": core.DUNNING_TEMPLATE, "max_touches": core.DUNNING_MAX_TOUCHES},
    ("GET", "/api/cancellations"): lambda q, b: {"rows": store.load("cancellations")[-40:],
                                                 "rules": core.cancel_rules()},
    ("GET", "/api/roi"): lambda q, b: core.roi(q),
    ("GET", "/api/eval"): lambda q, b: {"triage": core.run_eval()},
    ("GET", "/api/autonomy"): lambda q, b: {"matrix": core.matrix.actions,
                                            "never_promote": core.matrix.never_promote(),
                                            "automation": core.automation()},
    ("GET", "/api/approvals"): lambda q, b: {"pending": gate.pending()},
    ("POST", "/api/approvals/<id>/decide"): lambda q, b: gate.decide(
        q["id"], b.get("human", "owner"), b.get("approve", True),
        execute=_executor(store.by_id("approvals", q["id"]) or {}, b.get("human", "owner"))),
    ("GET", "/api/events"): lambda q, b: {"events": store.events()[-120:]},
    ("POST", "/api/agents/run"): lambda q, b: agents.run_all(),
}

if __name__ == "__main__":
    serve.run(ROOT / "app", ROUTES, PORT, "Member OS")
