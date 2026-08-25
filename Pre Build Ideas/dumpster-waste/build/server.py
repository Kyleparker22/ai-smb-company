#!/usr/bin/env python3
"""Haul OS — server. Stdlib only, 127.0.0.1:8839."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8839


def _executor(ap, human):
    def run():
        store.log_event(ap["action"].replace("draft_", "") + "_sent", ap["subject"],
                        f"human:{human}", "R1", {"approval": ap["id"]})
        return ap["subject"]
    return run


def board(q, b):
    idle = core.idle_containers()
    missed = core.missed_pickups()
    msgs = [m for m in store.load("messages") if not m.get("handled_at")]
    return {"config": store.load("config"),
            "board": {"idle_flagged": sum(1 for r in idle if r.get("flagged")),
                      "idle_days": sum(r.get("days") or 0 for r in idle if r.get("flagged")),
                      "idle_top": idle[:10],
                      "missed_pickups": len(missed), "missed_top": missed[:8],
                      "messages_open": len(msgs), "recovered": core.recovered_this_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/messages"): lambda q, b: {"rows": sorted(store.load("messages"),
        key=lambda m: m.get("at") or "", reverse=True)[:60]},
    ("POST", "/api/messages/<id>/answer"): lambda q, b: agents.answer_item(q["id"]),
    ("GET", "/api/charges"): lambda q, b: {"rows": [
        dict(c, check=core.charge_check(c)) for c in store.load("charges")][-40:]},
    ("POST", "/api/charges/<id>/assert"): lambda q, b: agents.try_charge(q["id"]),
    ("GET", "/api/idle"): lambda q, b: {"rows": core.idle_containers(),
                                        "flag_days": core.IDLE_FLAG_DAYS},
    ("GET", "/api/missed"): lambda q, b: {"rows": core.missed_pickups()},
    ("GET", "/api/roi"): lambda q, b: core.roi(q),
    ("GET", "/api/eval"): lambda q, b: {"items": core.run_eval()},
    ("GET", "/api/autonomy"): lambda q, b: {"matrix": core.matrix.actions,
                                            "never_promote": core.matrix.never_promote(),
                                            "automation": core.automation()},
    ("GET", "/api/approvals"): lambda q, b: {"pending": gate.pending()},
    ("POST", "/api/approvals/<id>/decide"): lambda q, b: gate.decide(
        q["id"], b.get("human", "dispatcher"), b.get("approve", True),
        execute=_executor(store.by_id("approvals", q["id"]) or {}, b.get("human", "dispatcher"))),
    ("GET", "/api/events"): lambda q, b: {"events": store.events()[-120:]},
    ("POST", "/api/agents/run"): lambda q, b: agents.run_all(),
}

if __name__ == "__main__":
    serve.run(ROOT / "app", ROUTES, PORT, "Haul OS")
