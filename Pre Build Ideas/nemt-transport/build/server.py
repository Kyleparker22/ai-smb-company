#!/usr/bin/env python3
"""Ride OS — server. Stdlib only, 127.0.0.1:8866."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8866


def _executor(ap, human):
    def run():
        if ap["action"] == "draft_invoice":
            t = store.by_id("trips", ap["subject"])
            if t:
                t["billed_at"] = iso()
                store.upsert("trips", t)
        store.log_event(ap["action"] + "_done", ap["subject"], f"human:{human}", "R1",
                        {"approval": ap["id"]})
        return ap["subject"]
    return run


def board(q, b):
    ub = core.unbillable_board()
    tb = core.tomorrow_board()
    msgs = [m for m in store.load("messages") if not m.get("handled_at")]
    return {"config": store.load("config"),
            "board": {"unbillable": ub, "tomorrow": len(tb),
                      "protected_tomorrow": len([r for r in tb if r["never_bump"]]),
                      "tomorrow_top": tb[:10], "messages_open": len(msgs),
                      "recovered": core.recovered_this_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/messages"): lambda q, b: {"rows": sorted(store.load("messages"),
        key=lambda m: m.get("at") or "", reverse=True)[:60]},
    ("POST", "/api/messages/<id>/handle"): lambda q, b: agents.handle_message(q["id"]),
    ("GET", "/api/trips"): lambda q, b: {"rows": store.load("trips")[:50]},
    ("POST", "/api/trips/<id>/bill"): lambda q, b: agents.bill_trip(q["id"]),
    ("POST", "/api/trips/<id>/bump"): lambda q, b: agents.bump_trip(q["id"]),
    ("POST", "/api/trips/<id>/assign"): lambda q, b: agents.assign_driver(q["id"], b.get("driver_id")),
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
    serve.run(ROOT / "app", ROUTES, PORT, "Ride OS")
