#!/usr/bin/env python3
"""Serve OS — server. Stdlib only, 127.0.0.1:8877."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8877


def _executor(ap, human):
    def run():
        if ap.get("action") == "propose_assignment":
            s = store.by_id("serves", ap["subject"])
            server_id = (ap.get("detail") or {}).get("server")
            if s and server_id:
                s["assigned_to"] = server_id
                store.upsert("serves", s)
        store.log_event(str(ap.get("action")) + "_done", ap.get("subject"),
                        f"human:{human}", "R1", {"approval": ap.get("id")})
        return ap.get("subject")
    return run


def board(q, b):
    db = core.deadline_board()
    msgs = [m for m in store.load("messages") if not m.get("handled_at")]
    due3 = [r for r in db["rows"] if r["days_to_deadline"] is not None
            and r["days_to_deadline"] <= 3]
    return {"config": store.load("config"),
            "board": {"open_serves": len(db["rows"]), "due_3_days": len(due3),
                      "top": db["rows"][:12], "messages_open": len(msgs),
                      "recovered": core.recovered_this_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


def serve_detail(q, b):
    s = store.by_id("serves", q["id"])
    if not s:
        return {"error": "no such serve"}
    atts = core.attempts_for(q["id"])
    return {"serve": s, "attempts": atts, "diligence": core.due_diligence(s, atts),
            "next_window": core.next_window(s, atts)}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/serves"): lambda q, b: core.deadline_board(),
    ("GET", "/api/serves/<id>"): serve_detail,
    ("POST", "/api/serves/<id>/attempt"): lambda q, b: core.record_attempt(
        q["id"], b.get("server", "srv_dre"), b.get("outcome", "no answer"),
        b.get("address", "address not given"), gps_ref=b.get("gps_ref"),
        who_answered=b.get("who_answered")),
    ("POST", "/api/serves/<id>/affidavit"): lambda q, b: agents.draft_affidavit(
        q["id"], extra_fact=b.get("extra_fact")),
    ("POST", "/api/serves/<id>/attest"): lambda q, b: agents.attest(q["id"]),
    ("POST", "/api/serves/<id>/substitute"): lambda q, b: agents.substitute(q["id"]),
    ("GET", "/api/servers"): lambda q, b: {"rows": store.load("servers")},
    ("GET", "/api/servers/<id>/day"): lambda q, b: core.day_list(q["id"]),
    ("GET", "/api/messages"): lambda q, b: {"rows": sorted(store.load("messages"),
        key=lambda m: m.get("at") or "", reverse=True)[:60]},
    ("POST", "/api/messages/<id>/handle"): lambda q, b: agents.handle_message(q["id"]),
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
    serve.run(ROOT / "app", ROUTES, PORT, "Serve OS")
