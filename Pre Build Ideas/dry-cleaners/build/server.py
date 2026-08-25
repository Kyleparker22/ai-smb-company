#!/usr/bin/env python3
"""Garment OS — server. Stdlib only, 127.0.0.1:8869."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8869


def _executor(ap, human):
    def run():
        if ap["action"] == "draft_settlement":
            c = store.by_id("claims", ap["subject"])
            if c:
                c["settled_at"] = iso()
                store.upsert("claims", c)
        store.log_event(ap["action"] + "_done", ap["subject"], f"human:{human}", "R1",
                        {"approval": ap["id"]})
        return ap["subject"]
    return run


def board(q, b):
    rb = core.rack_board()
    msgs = [m for m in store.load("messages") if not m.get("handled_at")]
    open_claims = [c for c in store.load("claims") if not c.get("settled_at")]
    return {"config": store.load("config"),
            "board": {"rack": {"value": rb["value"], "count": len(rb["rows"])},
                      "rack_top": rb["rows"][:10],
                      "open_claims": len(open_claims), "messages_open": len(msgs),
                      "recovered": core.recovered_this_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/messages"): lambda q, b: {"rows": sorted(store.load("messages"),
        key=lambda m: m.get("at") or "", reverse=True)[:60]},
    ("POST", "/api/messages/<id>/handle"): lambda q, b: agents.handle_message(q["id"]),
    ("GET", "/api/rack"): lambda q, b: core.rack_board(),
    ("GET", "/api/claims"): lambda q, b: {"rows": store.load("claims")[:40]},
    ("POST", "/api/claims/<id>/settle"): lambda q, b: agents.draft_settlement(q["id"]),
    ("POST", "/api/orders/<id>/dispose"): lambda q, b: agents.dispose(q["id"], human=b.get("human")),
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
    serve.run(ROOT / "app", ROUTES, PORT, "Garment OS")
