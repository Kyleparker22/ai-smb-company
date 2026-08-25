#!/usr/bin/env python3
"""Closing OS — server. Stdlib only, 127.0.0.1:8840."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8840


def _executor(ap, human):
    def run():
        store.log_event(ap["action"].replace("draft_", "") + "_done", ap["subject"],
                        f"human:{human}", "R1", {"approval": ap["id"]})
        return ap["subject"]
    return run


def board(q, b):
    fb = core.file_board()
    msgs = [m for m in store.load("messages") if not m.get("handled_at")]
    wire_seen = [m for m in store.load("messages") if m.get("label") == "wire_signal"]
    return {"config": store.load("config"),
            "board": {"open_files": len(fb), "ready": sum(1 for r in fb if r["ready"]),
                      "files_top": fb[:12], "messages_open": len(msgs),
                      "wire_signals_seen": len(wire_seen),
                      "recovered": core.recovered_this_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/messages"): lambda q, b: {"rows": sorted(store.load("messages"),
        key=lambda m: m.get("at") or "", reverse=True)[:60]},
    ("POST", "/api/messages/<id>/handle"): lambda q, b: agents.handle_message(q["id"]),
    ("GET", "/api/files"): lambda q, b: {"rows": core.file_board()},
    ("POST", "/api/files/<id>/clear"): lambda q, b: agents.declare_clear(q["id"]),
    ("POST", "/api/files/<id>/wire"): lambda q, b: agents.request_wire_instructions(q["id"]),
    ("POST", "/api/files/<id>/status"): lambda q, b: core.status_draft(q["id"]),
    ("GET", "/api/roi"): lambda q, b: core.roi(q),
    ("GET", "/api/eval"): lambda q, b: {"triage": core.run_eval()},
    ("GET", "/api/autonomy"): lambda q, b: {"matrix": core.matrix.actions,
                                            "never_promote": core.matrix.never_promote(),
                                            "automation": core.automation()},
    ("GET", "/api/approvals"): lambda q, b: {"pending": gate.pending()},
    ("POST", "/api/approvals/<id>/decide"): lambda q, b: gate.decide(
        q["id"], b.get("human", "escrow_officer"), b.get("approve", True),
        execute=_executor(store.by_id("approvals", q["id"]) or {}, b.get("human", "escrow_officer"))),
    ("GET", "/api/events"): lambda q, b: {"events": store.events()[-120:]},
    ("POST", "/api/agents/run"): lambda q, b: agents.run_all(),
}

if __name__ == "__main__":
    serve.run(ROOT / "app", ROUTES, PORT, "Closing OS")
