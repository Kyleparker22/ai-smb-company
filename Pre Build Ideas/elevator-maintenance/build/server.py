#!/usr/bin/env python3
"""Cab OS — server. Stdlib only, 127.0.0.1:8860."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8860


def _executor(ap, human):
    def run():
        store.log_event(ap["action"] + "_done", ap["subject"], f"human:{human}", "R1",
                        {"approval": ap["id"]})
        return ap["subject"]
    return run


def board(q, b):
    units = store.load("units")
    states = [core.unit_state(u) for u in units if not u.get("demo_tag")]
    overdue = sum(1 for s in states for t in s["tests"].values() if t["state"] == "overdue")
    unknown = sum(1 for s in states for t in s["tests"].values() if t["state"] == "unknown")
    red = [u for u in units if u.get("red_tagged_at")]
    calls_open = [c for c in store.load("calls") if not c.get("handled_at")]
    return {"config": store.load("config"),
            "board": {"units": len(units), "tests_overdue": overdue, "tests_unknown": unknown,
                      "red_tagged": len(red), "calls_open": len(calls_open),
                      "callbacks": core.callback_rate(),
                      "recovered": core.recovered_this_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/calls"): lambda q, b: {"rows": sorted(store.load("calls"),
        key=lambda m: m.get("at") or "", reverse=True)[:60]},
    ("POST", "/api/calls/<id>/handle"): lambda q, b: agents.handle_call(q["id"]),
    ("GET", "/api/units"): lambda q, b: {"rows": [core.unit_state(u)
                                                 for u in store.load("units")[:40]]},
    ("POST", "/api/units/<id>/reactivate"): lambda q, b: agents.reactivate(
        q["id"], b.get("mechanic_signoff")),
    ("POST", "/api/units/<id>/scope"): lambda q, b: agents.scope_ticket(q["id"], b.get("work", "")),
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
    serve.run(ROOT / "app", ROUTES, PORT, "Cab OS")
