#!/usr/bin/env python3
"""Well OS — server. Stdlib only, 127.0.0.1:8872."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8872


def _executor(ap, human):
    def run():
        store.log_event(ap["action"] + "_done", ap["subject"], f"human:{human}", "R1",
                        {"approval": ap["id"]})
        return ap["subject"]
    return run


def board(q, b):
    db = core.due_board()
    jb = core.job_board()
    msgs = [m for m in store.load("messages") if not m.get("handled_at")]
    pending_labs = [r for r in store.load("lab_reports") if not r.get("result")]
    alerts = [r for r in jb["rows"] if r.get("clock")]
    return {"config": store.load("config"),
            "board": {"due": {"count": len(db["rows"]), "value": db["due_value"],
                              "overdue": db["overdue_count"],
                              "overdue_value": db["overdue_value"],
                              "unknown_clocks": db["unknown_clocks"]},
                      "due_top": db["rows"][:10],
                      "permit_alerts": len(alerts), "alerts_top": alerts[:6],
                      "messages_open": len(msgs), "labs_pending": len(pending_labs),
                      "recovered": core.recovered_this_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/messages"): lambda q, b: {"rows": sorted(store.load("messages"),
        key=lambda m: m.get("at") or "", reverse=True)[:60]},
    ("POST", "/api/messages/<id>/handle"): lambda q, b: agents.handle_message(q["id"]),
    ("GET", "/api/systems"): lambda q, b: core.due_board(),
    ("POST", "/api/systems/<id>/protected"): lambda q, b: agents.claim_protected(q["id"]),
    ("GET", "/api/wells"): lambda q, b: {"rows": store.load("wells")[:50]},
    ("POST", "/api/wells/<id>/safe"): lambda q, b: agents.answer_water_safe(q["id"]),
    ("POST", "/api/wells/<id>/quote"): lambda q, b: agents.draft_quote(q["id"]),
    ("GET", "/api/jobs"): lambda q, b: core.job_board(),
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
    serve.run(ROOT / "app", ROUTES, PORT, "Well OS")
