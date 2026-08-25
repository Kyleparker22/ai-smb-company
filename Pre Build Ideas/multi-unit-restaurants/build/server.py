#!/usr/bin/env python3
"""Unit OS — server. Stdlib only, 127.0.0.1:8836."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8836


def _executor(ap, human):
    def run():
        store.log_event(ap["action"].replace("draft_", "") + "_sent", ap["subject"],
                        f"human:{human}", "R1", {"approval": ap["id"]})
        subj = store.by_id("messages", ap["subject"])
        if subj:
            subj["responded_at"] = iso()
            store.upsert("messages", subj)
        return ap["subject"]
    return run


def board(q, b):
    vb = core.variance_board()
    msgs = [m for m in store.load("messages") if not m.get("handled_at")]
    dangerous = [m for m in store.load("messages") if m.get("label") in core.DANGEROUS]
    return {"config": store.load("config"),
            "board": {"variance": vb,
                      "flagged_units": sum(1 for r in vb if r.get("flagged")),
                      "unmeasured_units": sum(1 for r in vb if r.get("_missing")),
                      "messages_open": len(msgs), "dangerous_seen": len(dangerous),
                      "recovered": core.recovered_this_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


ROUTES = {
    ("POST", "/api/units/<id>/brief"): lambda q, b: agents.open_variance_brief(q["id"]),
    ("GET", "/api/board"): board,
    ("GET", "/api/messages"): lambda q, b: {"rows": sorted(store.load("messages"),
        key=lambda m: m.get("at") or "", reverse=True)[:60]},
    ("POST", "/api/messages/<id>/handle"): lambda q, b: agents.handle_message(q["id"]),
    ("GET", "/api/variance"): lambda q, b: {"rows": core.variance_board(),
                                            "threshold_pp": core.VARIANCE_FLAG_PP},
    ("GET", "/api/scorecard"): lambda q, b: {"rows": core.scorecard()},
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
    serve.run(ROOT / "app", ROUTES, PORT, "Unit OS")
