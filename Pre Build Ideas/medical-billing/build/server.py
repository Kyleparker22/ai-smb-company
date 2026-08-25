#!/usr/bin/env python3
"""Claim OS — server. Stdlib only, 127.0.0.1:8857."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8857


def _executor(ap, human):
    def run():
        store.log_event(ap["action"] + "_done", ap["subject"], f"human:{human}", "R1",
                        {"approval": ap["id"]})
        return ap["subject"]
    return run


def board(q, b):
    ar = core.at_risk_board()
    open_d = [d for d in store.load("denials") if not d.get("resolved_at") and not d.get("demo_tag")]
    return {"config": store.load("config"),
            "board": {"at_risk": ar, "open_denials": len(open_d),
                      "recovered": core.recovered_this_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/denials"): lambda q, b: {"rows": store.load("denials")[:50]},
    ("GET", "/api/claims"): lambda q, b: {"rows": store.load("claims")[:50]},
    ("POST", "/api/claims/<id>/recode"): lambda q, b: agents.recode(q["id"], b.get("code")),
    ("POST", "/api/claims/<id>/submit"): lambda q, b: agents.submit(q["id"]),
    ("GET", "/api/atrisk"): lambda q, b: core.at_risk_board(),
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
    serve.run(ROOT / "app", ROUTES, PORT, "Claim OS")
