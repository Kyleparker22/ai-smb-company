#!/usr/bin/env python3
"""Visit OS — server. Stdlib only, 127.0.0.1:8833."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8833


def _executor(ap, human):
    def run():
        store.log_event(ap["action"].replace("draft_", "") + "_sent", ap["subject"],
                        f"human:{human}", "R1", {"approval": ap["id"]})
        return ap["subject"]
    return run


def board(q, b):
    lp = core.lapsed()
    bf = core.backfill_stats()
    msgs = [m for m in store.load("messages") if not m.get("handled_at")]
    return {"config": store.load("config"),
            "board": {"lapsed": len(lp), "lapsed_top": lp[:10],
                      "backfill": bf, "messages_open": len(msgs),
                      "active_patients": len(core.contactable_patients()),
                      "recovered": core.recovered_this_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/messages"): lambda q, b: {"rows": store.load("messages"),
                                            "instruction": core.EMERGENCY_INSTRUCTION},
    ("POST", "/api/messages/<id>/handle"): lambda q, b: agents.handle_message(q["id"]),
    ("GET", "/api/lapsed"): lambda q, b: {"rows": core.lapsed()[:60]},
    ("POST", "/api/lapsed/<id>/plan"): lambda q, b: core.reminder_plan(store.by_id("patients", q["id"]) or {}),
    ("GET", "/api/slots"): lambda q, b: {"rows": [a for a in store.load("appointments")
                                                  if not a.get("cancelled_at")][-20:]},
    ("POST", "/api/slots/<id>/cancel"): lambda q, b: agents.cancel_and_rank(q["id"]),
    ("GET", "/api/roi"): lambda q, b: core.roi(q),
    ("GET", "/api/eval"): lambda q, b: {"triage": core.run_eval()},
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
    serve.run(ROOT / "app", ROUTES, PORT, "Visit OS")
