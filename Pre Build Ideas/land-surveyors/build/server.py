#!/usr/bin/env python3
"""Plat OS — server. Stdlib only, 127.0.0.1:8873."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8873


def _executor(ap, human):
    def run():
        store.log_event(ap["action"] + "_done", ap["subject"], f"human:{human}", "R1",
                        {"approval": ap["id"]})
        return ap["subject"]
    return run


def board(q, b):
    db = core.deadline_board()
    msgs = [m for m in store.load("messages") if not m.get("handled_at")]
    return {"config": store.load("config"),
            "board": {"open_jobs": len(db["rows"]), "closing_week": db["closing_week"],
                      "deadline_top": db["rows"][:10],
                      "blocked": sum(1 for r in db["rows"] if r["blockers"]),
                      "messages_open": len(msgs),
                      "recovered": core.recovered_this_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


def job_detail(q, b):
    j = store.by_id("jobs", q["id"])
    if not j:
        return {"error": "no such job"}
    return {"job": j, "chain": core.chain_check(j), "day_sheet": core.day_sheet_status(j),
            "projection": core.closing_projection(j)}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/messages"): lambda q, b: {"rows": sorted(store.load("messages"),
        key=lambda m: m.get("at") or "", reverse=True)[:60]},
    ("POST", "/api/messages/<id>/handle"): lambda q, b: agents.handle_message(q["id"]),
    ("GET", "/api/deadlines"): lambda q, b: core.deadline_board(),
    ("GET", "/api/jobs/<id>"): job_detail,
    ("POST", "/api/jobs/<id>/seal"): lambda q, b: agents.seal_plat(
        q["id"], b.get("seal_number"), b.get("seal_date"), b.get("pls")),
    ("POST", "/api/jobs/<id>/draft"): lambda q, b: agents.begin_draft(q["id"]),
    ("POST", "/api/quote"): lambda q, b: core.quote_math(
        b.get("job_type", "boundary"), b.get("acreage")),
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
    serve.run(ROOT / "app", ROUTES, PORT, "Plat OS")
