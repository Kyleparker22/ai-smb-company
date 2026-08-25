#!/usr/bin/env python3
"""Canopy OS — server. Stdlib only, 127.0.0.1:8852."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8852


def _executor(ap, human):
    def run():
        store.log_event(ap["action"] + "_done", ap["subject"], f"human:{human}", "R1",
                        {"approval": ap["id"]})
        return ap["subject"]
    return run


def board(q, b):
    oe = core.open_estimate_value()
    msgs = [m for m in store.load("messages") if not m.get("handled_at")]
    emergencies = [m for m in store.load("messages") if m.get("label") == "emergency"]
    blocked = [j for j in store.load("jobs")
               if j.get("near_powerlines") and not j.get("utility_clearance_ref")
               and not j.get("demo_tag")]
    return {"config": store.load("config"),
            "board": {"open_estimates": oe, "messages_open": len(msgs),
                      "emergencies": len(emergencies),
                      "powerline_blocked": len(blocked),
                      "phc_due": len(core.phc_due()),
                      "recovered": core.recovered_this_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/messages"): lambda q, b: {"rows": sorted(store.load("messages"),
        key=lambda m: m.get("at") or "", reverse=True)[:60]},
    ("POST", "/api/messages/<id>/handle"): lambda q, b: agents.handle_message(q["id"]),
    ("GET", "/api/jobs"): lambda q, b: {"rows": store.load("jobs")[:50]},
    ("POST", "/api/jobs/<id>/schedule"): lambda q, b: agents.schedule_job(q["id"]),
    ("GET", "/api/estimates"): lambda q, b: {"rows": store.load("estimates")[:50]},
    ("GET", "/api/phc"): lambda q, b: {"rows": core.phc_due()},
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
    serve.run(ROOT / "app", ROUTES, PORT, "Canopy OS")
