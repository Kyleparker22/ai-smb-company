#!/usr/bin/env python3
"""Fuel OS — server. Stdlib only, 127.0.0.1:8863."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8863


def _executor(ap, human):
    def run():
        store.log_event(ap["action"] + "_done", ap["subject"], f"human:{human}", "R1",
                        {"approval": ap["id"]})
        return ap["subject"]
    return run


def board(q, b):
    rb = core.runout_board()
    calls_open = [c for c in store.load("calls") if not c.get("handled_at")]
    outages = [t for t in store.load("tickets")
               if t.get("kind") == "out_of_gas" and not t.get("closed_at")]
    return {"config": store.load("config"),
            "board": {"critical": len([r for r in rb if r.get("risk") == "critical"]),
                      "unknown": len([r for r in rb if r.get("_missing")]),
                      "runout_top": rb[:10], "open_outages": len(outages),
                      "calls_open": len(calls_open),
                      "recovered": core.recovered_this_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/calls"): lambda q, b: {"rows": sorted(store.load("calls"),
        key=lambda m: m.get("at") or "", reverse=True)[:60]},
    ("POST", "/api/calls/<id>/handle"): lambda q, b: agents.handle_call(q["id"]),
    ("GET", "/api/tickets"): lambda q, b: {"rows": store.load("tickets")[:40]},
    ("POST", "/api/tickets/<id>/close"): lambda q, b: agents.close_outage(
        q["id"], leak_result=b.get("leak_result"), tech=b.get("tech")),
    ("POST", "/api/tanks/<id>/fill"): lambda q, b: agents.fill_tank(q["id"]),
    ("GET", "/api/runouts"): lambda q, b: {"rows": core.runout_board()[:40]},
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
    serve.run(ROOT / "app", ROUTES, PORT, "Fuel OS")
