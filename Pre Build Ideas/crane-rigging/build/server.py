#!/usr/bin/env python3
"""Rig OS — server. Stdlib only, 127.0.0.1:8867."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8867


def _executor(ap, human):
    def run():
        store.log_event(ap["action"] + "_done", ap["subject"], f"human:{human}", "R1",
                        {"approval": ap["id"]})
        return ap["subject"]
    return run


def board(q, b):
    lifts = [l for l in store.load("lifts") if not l.get("completed_at") and not l.get("demo_tag")]
    critical = [l for l in lifts if l.get("critical")]
    unplanned = [l for l in critical if not (l.get("lift_plan") or {}).get("ref")]
    rfqs_open = [r for r in store.load("rfqs") if not r.get("scanned_at")]
    return {"config": store.load("config"),
            "board": {"lifts_open": len(lifts), "critical_open": len(critical),
                      "critical_unplanned": len(unplanned),
                      "rfqs_open": len(rfqs_open),
                      "recovered": core.recovered_this_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/rfqs"): lambda q, b: {"rows": store.load("rfqs")[:40]},
    ("POST", "/api/rfqs/<id>/handle"): lambda q, b: agents.handle_rfq(q["id"]),
    ("GET", "/api/lifts"): lambda q, b: {"rows": store.load("lifts")[:40]},
    ("POST", "/api/lifts/<id>/schedule"): lambda q, b: agents.schedule_lift(q["id"]),
    ("POST", "/api/lifts/<id>/assign"): lambda q, b: agents.assign_operator(q["id"], b.get("operator_id")),
    ("POST", "/api/lifts/<id>/dispatch"): lambda q, b: agents.dispatch_today(
        q["id"], forecast_mph=b.get("forecast_mph")),
    ("GET", "/api/roi"): lambda q, b: core.roi(q),
    ("GET", "/api/eval"): lambda q, b: {"flags": core.run_eval()},
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
    serve.run(ROOT / "app", ROUTES, PORT, "Rig OS")
