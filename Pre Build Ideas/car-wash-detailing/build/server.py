#!/usr/bin/env python3
"""Shine OS — server. Stdlib only, 127.0.0.1:8858."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8858


def _executor(ap, human):
    def run():
        store.log_event(ap["action"] + "_done", ap["subject"], f"human:{human}", "R1",
                        {"approval": ap["id"]})
        return ap["subject"]
    return run


def board(q, b):
    msgs = [m for m in store.load("messages") if not m.get("handled_at")]
    claims_open = [c for c in store.load("claims") if not c.get("resolved_at")]
    failures = [p for p in store.load("payments") if p.get("failed") and not p.get("recovered_at")]
    rained = [d for d in store.load("details") if d.get("rained_out") and not d.get("completed_at")]
    return {"config": store.load("config"),
            "board": {"claims_open": len(claims_open), "failed_payments": len(failures),
                      "failed_value": round(sum(p.get("amount", 0) for p in failures), 2),
                      "rained_out": len(rained), "messages_open": len(msgs),
                      "recovered": core.recovered_this_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/messages"): lambda q, b: {"rows": sorted(store.load("messages"),
        key=lambda m: m.get("at") or "", reverse=True)[:60]},
    ("POST", "/api/messages/<id>/handle"): lambda q, b: agents.handle_message(q["id"]),
    ("GET", "/api/claims"): lambda q, b: {"rows": store.load("claims")[:40]},
    ("POST", "/api/members/<id>/charge"): lambda q, b: agents.charge_member(q["id"], b.get("amount", 29)),
    ("GET", "/api/members"): lambda q, b: {"rows": store.load("members")[:40]},
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
    serve.run(ROOT / "app", ROUTES, PORT, "Shine OS")
