#!/usr/bin/env python3
"""Yard OS — server. Stdlib only, 127.0.0.1:8835."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8835


def _executor(ap, human):
    def run():
        store.log_event(ap["action"].replace("draft_", "") + "_done", ap["subject"],
                        f"human:{human}", "R1", {"approval": ap["id"]})
        return ap["subject"]
    return run


def board(q, b):
    q_rows = core.pickup_queue()
    util = core.utilization()
    calls_open = [c for c in store.load("calls") if not c.get("handled_at")]
    return {"config": store.load("config"),
            "board": {"pickup_queue": len(q_rows), "queue_days": sum(r["days_waiting"] for r in q_rows),
                      "queue_top": q_rows[:10], "utilization": util,
                      "calls_open": len(calls_open), "recovered": core.recovered_this_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/calls"): lambda q, b: {"rows": store.load("calls")},
    ("POST", "/api/calls/<id>/handle"): lambda q, b: agents.handle_call(q["id"]),
    ("GET", "/api/rentals"): lambda q, b: {"rows": [r for r in store.load("rentals")][-40:]},
    ("POST", "/api/rentals/<id>/invoice"): lambda q, b: core.invoice_preview(
        store.by_id("rentals", q["id"]) or {}, through=b.get("through")),
    ("POST", "/api/rentals/<id>/damage"): lambda q, b: agents.try_damage_claim(q["id"]),
    ("POST", "/api/rentals/<id>/waiver"): lambda q, b: agents.waiver(q["id"], float(b.get("amount", 0))),
    ("GET", "/api/pickup"): lambda q, b: {"rows": core.pickup_queue()},
    ("GET", "/api/utilization"): lambda q, b: {"rows": core.utilization()},
    ("GET", "/api/roi"): lambda q, b: core.roi(q),
    ("GET", "/api/eval"): lambda q, b: {"calls": core.run_eval()},
    ("GET", "/api/autonomy"): lambda q, b: {"matrix": core.matrix.actions,
                                            "never_promote": core.matrix.never_promote(),
                                            "automation": core.automation()},
    ("GET", "/api/approvals"): lambda q, b: {"pending": gate.pending()},
    ("POST", "/api/approvals/<id>/decide"): lambda q, b: gate.decide(
        q["id"], b.get("human", "manager"), b.get("approve", True),
        execute=_executor(store.by_id("approvals", q["id"]) or {}, b.get("human", "manager"))),
    ("GET", "/api/events"): lambda q, b: {"events": store.events()[-120:]},
    ("POST", "/api/agents/run"): lambda q, b: agents.run_all(),
}

if __name__ == "__main__":
    serve.run(ROOT / "app", ROUTES, PORT, "Yard OS")
