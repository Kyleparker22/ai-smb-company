#!/usr/bin/env python3
"""Move OS — server. Stdlib only, 127.0.0.1:8842."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8842


def _executor(ap, human):
    def run():
        store.log_event(ap["action"].replace("draft_", "") + "_done", ap["subject"],
                        f"human:{human}", "R1", {"approval": ap["id"]})
        return ap["subject"]
    return run


def board(q, b):
    cb = core.claims_board()
    msgs = [m for m in store.load("messages") if not m.get("handled_at")]
    binding = [m for m in store.load("moves") if m.get("estimate_type") == "binding"
               and not m.get("demo_tag")]
    surveyed = [m for m in binding if m.get("survey_id")]
    return {"config": store.load("config"),
            "board": {"open_claims": len(cb), "claims_top": cb[:8],
                      "binding_moves": len(binding), "surveyed": len(surveyed),
                      "messages_open": len(msgs), "recovered": core.recovered_this_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/messages"): lambda q, b: {"rows": sorted(store.load("messages"),
        key=lambda m: m.get("at") or "", reverse=True)[:60]},
    ("POST", "/api/messages/<id>/handle"): lambda q, b: agents.handle_message(q["id"]),
    ("GET", "/api/moves"): lambda q, b: {"rows": store.load("moves")[-30:]},
    ("POST", "/api/moves/<id>/binding"): lambda q, b: agents.issue_binding(q["id"]),
    ("POST", "/api/moves/<id>/charges"): lambda q, b: core.final_charges(
        store.by_id("moves", q["id"]) or {}),
    ("GET", "/api/claims"): lambda q, b: {"rows": core.claims_board(),
                                          "rules": core.claim_rules()},
    ("POST", "/api/claims/<id>/settle"): lambda q, b: agents.settle_claim(q["id"]),
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
    serve.run(ROOT / "app", ROUTES, PORT, "Move OS")
