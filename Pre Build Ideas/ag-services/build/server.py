#!/usr/bin/env python3
"""Field OS — server. Stdlib only, 127.0.0.1:8850."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8850


def _executor(ap, human):
    def run():
        store.log_event(ap["action"].replace("draft_", "") + "_done", ap["subject"],
                        f"human:{human}", "R1", {"approval": ap["id"]})
        return ap["subject"]
    return run


def board(q, b):
    jb = core.job_board()
    msgs = [m for m in store.load("messages") if not m.get("handled_at")]
    complaints = [m for m in store.load("messages") if m.get("label") == "drift_exposure"]
    return {"config": store.load("config"),
            "board": {"open_jobs": len(jb),
                      "billable": sum(1 for r in jb if r["billable"]),
                      "unbillable": sum(1 for r in jb if not r["billable"]),
                      "rup_blocked": sum(1 for r in jb if not r["dispatchable"]),
                      "jobs_top": jb[:10], "messages_open": len(msgs),
                      "complaints_logged": len(complaints),
                      "recovered": core.recovered_this_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/messages"): lambda q, b: {"rows": sorted(store.load("messages"),
        key=lambda m: m.get("at") or "", reverse=True)[:60]},
    ("POST", "/api/messages/<id>/handle"): lambda q, b: agents.handle_message(q["id"]),
    ("GET", "/api/jobs"): lambda q, b: {"rows": core.job_board()[:40]},
    ("POST", "/api/jobs/<id>/bill"): lambda q, b: agents.bill_job(q["id"]),
    ("POST", "/api/jobs/<id>/dispatch"): lambda q, b: agents.dispatch_job(q["id"]),
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
    serve.run(ROOT / "app", ROUTES, PORT, "Field OS")
