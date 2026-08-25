#!/usr/bin/env python3
"""Rehab OS — server. Stdlib only, 127.0.0.1:8846."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8846


def _executor(ap, human):
    def run():
        store.log_event(ap["action"].replace("draft_", "") + "_done", ap["subject"],
                        f"human:{human}", "R1", {"approval": ap["id"]})
        return ap["subject"]
    return run


def board(q, b):
    db = core.dropout_board()
    over, unmeasured_auth = 0, 0
    for p in store.load("patients"):
        if p.get("status") != "active":
            continue
        s = core.auth_state(p)
        if s.get("over"):
            over += 1
        elif s.get("_missing"):
            unmeasured_auth += 1
    msgs = [m for m in store.load("messages") if not m.get("handled_at")]
    return {"config": store.load("config"),
            "board": {"at_risk": db["n"], "single_signal": db["single_signal"],
                      "over_auth": over, "auth_unmeasured": unmeasured_auth,
                      "messages_open": len(msgs), "recovered": core.recovered_this_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/messages"): lambda q, b: {"rows": sorted(store.load("messages"),
        key=lambda m: m.get("at") or "", reverse=True)[:60]},
    ("POST", "/api/messages/<id>/handle"): lambda q, b: agents.handle_message(q["id"]),
    ("GET", "/api/dropout"): lambda q, b: core.dropout_board(),
    ("GET", "/api/auth"): lambda q, b: {"rows": [
        {"patient": p["id"], "name": p.get("name"), **core.auth_state(p)}
        for p in store.load("patients") if p.get("status") == "active"][:50]},
    ("POST", "/api/patients/<id>/book"): lambda q, b: agents.book_visit(q["id"]),
    ("GET", "/api/roi"): lambda q, b: core.roi(q),
    ("GET", "/api/eval"): lambda q, b: {"triage": core.run_eval()},
    ("GET", "/api/autonomy"): lambda q, b: {"matrix": core.matrix.actions,
                                            "never_promote": core.matrix.never_promote(),
                                            "automation": core.automation()},
    ("GET", "/api/approvals"): lambda q, b: {"pending": gate.pending()},
    ("POST", "/api/approvals/<id>/decide"): lambda q, b: gate.decide(
        q["id"], b.get("human", "director"), b.get("approve", True),
        execute=_executor(store.by_id("approvals", q["id"]) or {}, b.get("human", "director"))),
    ("GET", "/api/events"): lambda q, b: {"events": store.events()[-120:]},
    ("POST", "/api/agents/run"): lambda q, b: agents.run_all(),
}

if __name__ == "__main__":
    serve.run(ROOT / "app", ROUTES, PORT, "Rehab OS")
