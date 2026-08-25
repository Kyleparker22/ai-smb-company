#!/usr/bin/env python3
"""Halflife OS — server. Stdlib only, 127.0.0.1:8884."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve

PORT = 8884


def _executor(ap, human):
    """Approving an R1 letter draft IS the human send: the item goes on_notice
    and the clock keeps running — a letter is notice, not possession."""
    def run():
        if ap.get("action") == "draft_preservation_letter":
            return agents.letter_sent(ap["subject"], human)
        store.log_event(str(ap.get("action")) + "_done", ap.get("subject"),
                        f"human:{human}", "R1", {"approval": ap.get("id")})
        return ap.get("subject")
    return run


def board(q, b):
    qd = core.dies_first_queue()
    return {"config": store.load("config"),
            "board": {"at_large": len(qd["rows"]), "unknown": qd["unknown_count"],
                      "dying_14": qd["dying_14"], "lost": qd["lost_count"],
                      "secured": qd["secured_count"],
                      "week": core.ledger_this_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


def matter_detail(q, b):
    m = store.by_id("matters", q["id"])
    if not m:
        return {"error": "no such matter"}
    items = [dict(i, clock=core.clock(i)) for i in store.load("evidence")
             if i.get("matter_id") == q["id"]]
    return {"matter": m, "items": items}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/queue"): lambda q, b: core.dies_first_queue(),
    ("GET", "/api/matters"): lambda q, b: {"rows": store.load("matters")[:80]},
    ("GET", "/api/matters/<id>"): matter_detail,
    ("GET", "/api/messages"): lambda q, b: {"rows": sorted(store.load("messages"),
        key=lambda m: m.get("at") or "", reverse=True)[:60]},
    ("POST", "/api/messages/<id>/handle"): lambda q, b: agents.handle_message(q["id"]),
    ("POST", "/api/intake"): lambda q, b: agents.intake(b),
    ("POST", "/api/evidence/<id>/secure"): lambda q, b: agents.secure(
        q["id"], receipt_ref=b.get("receipt_ref"), human=b.get("human")),
    ("POST", "/api/evidence/<id>/witness_contact"): lambda q, b: agents.witness_contact(
        q["id"], b.get("human", "amerrick"), b.get("note")),
    ("GET", "/api/roi"): lambda q, b: core.roi(q),
    ("GET", "/api/eval"): lambda q, b: {"triage": core.run_eval()},
    ("GET", "/api/autonomy"): lambda q, b: {"matrix": core.matrix.actions,
                                            "never_promote": core.matrix.never_promote(),
                                            "automation": core.automation()},
    ("GET", "/api/approvals"): lambda q, b: {"pending": gate.pending()},
    ("POST", "/api/approvals/<id>/decide"): lambda q, b: gate.decide(
        q["id"], b.get("human", "amerrick"), b.get("approve", True),
        execute=_executor(store.by_id("approvals", q["id"]) or {},
                          b.get("human", "amerrick"))),
    ("GET", "/api/events"): lambda q, b: {"events": store.events()[-120:]},
    ("POST", "/api/agents/run"): lambda q, b: agents.run_all(),
}

if __name__ == "__main__":
    serve.run(ROOT / "app", ROUTES, PORT, "Halflife OS")
