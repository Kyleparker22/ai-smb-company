#!/usr/bin/env python3
"""Post OS — server. Stdlib only, 127.0.0.1:8862."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8862


def _executor(ap, human):
    def run():
        if ap["action"] == "fill_post":
            p = store.by_id("posts", ap["subject"])
            if p:
                p["filled_by"] = (ap.get("detail") or {}).get("guard")
                store.upsert("posts", p)
        store.log_event(ap["action"] + "_done", ap["subject"], f"human:{human}", "R1",
                        {"approval": ap["id"]})
        return ap["subject"]
    return run


def board(q, b):
    cb = core.coverage_board()
    cal = core.credential_calendar()
    msgs = [m for m in store.load("reports") if not m.get("handled_at")]
    return {"config": store.load("config"),
            "board": {"open_posts": len(cb), "coverage_top": cb[:8],
                      "creds_expiring": len(cal), "cred_top": cal[:8],
                      "messages_open": len(msgs),
                      "incidents": len(store.load("incidents")),
                      "recovered": core.recovered_this_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/reports"): lambda q, b: {"rows": sorted(store.load("reports"),
        key=lambda m: m.get("at") or "", reverse=True)[:60]},
    ("POST", "/api/reports/<id>/handle"): lambda q, b: agents.handle_message(q["id"]),
    ("GET", "/api/coverage"): lambda q, b: {"rows": core.coverage_board()},
    ("POST", "/api/posts/<id>/fill"): lambda q, b: agents.fill_post(q["id"], b.get("guard_id")),
    ("GET", "/api/incidents"): lambda q, b: {"rows": store.load("incidents")[:40]},
    ("POST", "/api/incidents/<id>/adjust"): lambda q, b: core.adjust_request(
        q["id"], b.get("requester", "client"), b.get("request", "")),
    ("POST", "/api/incidents/<id>/correct"): lambda q, b: core.correct_incident(
        q["id"], b.get("narrative", ""), b.get("guard_id", "")),
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
    serve.run(ROOT / "app", ROUTES, PORT, "Post OS")
