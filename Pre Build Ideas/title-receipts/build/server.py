#!/usr/bin/env python3
"""Receipt OS — server. Stdlib only, 127.0.0.1:8894."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve

PORT = 8894


def _executor(ap, human):
    def run():
        store.log_event(ap.get("action", "") + "_done", ap.get("subject"), f"human:{human}",
                        "R1", {"approval": ap.get("id")})
        return ap.get("subject")
    return run


def board(q, b):
    cov = core.coverage_year()
    msgs = [m for m in store.load("messages") if not m.get("handled_at")]
    untested = [c for c, d in cov["drills"].items() if d["status"] == "UNTESTED"]
    return {"config": store.load("config"),
            "board": {"wires_moved": cov["wires_moved"],
                      "chains_complete": cov["chains_complete"],
                      "verifications": cov["verifications"],
                      "blocked_attempts": cov["blocked_attempts"],
                      "exceptions": len(cov["exceptions"]),
                      "untested_controls": untested,
                      "messages_open": len(msgs),
                      "week": core.receipts_this_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/messages"): lambda q, b: {"rows": sorted(store.load("messages"),
        key=lambda m: m.get("at") or "", reverse=True)[:60]},
    ("POST", "/api/messages/<id>/handle"): lambda q, b: agents.handle_message(q["id"]),
    ("POST", "/api/messages/<id>/act-on-change"): lambda q, b: agents.act_on_wire_change(q["id"]),
    ("GET", "/api/ledger"): lambda q, b: {"rows": core.ledger_entries()[-80:][::-1]},
    ("GET", "/api/coverage"): lambda q, b: core.coverage_year(),
    ("GET", "/api/wires/<id>/chain"): lambda q, b: core.wire_chain(q["id"]),
    ("GET", "/api/controls/<id>/status"): lambda q, b: core.drill_status(q["id"]),
    ("POST", "/api/controls/<id>/attest"): lambda q, b: agents.attest_control(q["id"]),
    ("POST", "/api/wires/<id>/callback"): lambda q, b: agents.record_callback(
        q["id"], b.get("who_called", "unnamed")),
    ("POST", "/api/wires/<id>/dual-control"): lambda q, b: agents.record_dual_control(
        q["id"], b.get("human_a"), b.get("human_b")),
    ("POST", "/api/packets/renewal"): lambda q, b: agents.draft_renewal_packet(),
    ("POST", "/api/packets/realtor"): lambda q, b: agents.draft_realtor_proof(),
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
    serve.run(ROOT / "app", ROUTES, PORT, "Receipt OS")
