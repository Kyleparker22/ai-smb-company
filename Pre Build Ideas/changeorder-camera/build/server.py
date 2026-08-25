#!/usr/bin/env python3
"""Delta OS — server. Stdlib only, 127.0.0.1:8883."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8883


def _executor(ap, human):
    def run():
        d = store.by_id("deltas", ap.get("subject"))
        if d:
            if ap.get("action") == "draft_change_order":
                d["priced_at"] = iso()
                core.advance_delta(d, "priced")
            elif ap.get("action") == "draft_notice_letter":
                d["noticed_at"] = iso()
                core.advance_delta(d, "noticed")
            store.upsert("deltas", d)
        store.log_event(ap["action"] + "_done", ap.get("subject"), f"human:{human}", "R1",
                        {"approval": ap["id"],
                         "amount": (ap.get("detail") or {}).get("amount")})
        return ap.get("subject")
    return run


def board(q, b):
    ds = store.load("deltas")
    open_d = [d for d in ds if d.get("state") not in ("signed", "rejected")]
    msgs = [m for m in store.load("messages") if not m.get("handled_at")]
    cl = core.closeout_ledger()
    return {"config": store.load("config"),
            "board": {"open_deltas": len(open_d),
                      "unconfirmed": sum(1 for d in open_d if not d.get("confirmed")),
                      "detection": cl["detection"],
                      "messages_open": len(msgs),
                      "week": core.this_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


def jobs(q, b):
    plans = store.load("plan_lines")
    ds = store.load("deltas")
    rows = []
    for j in store.load("jobs"):
        clause = core.clause_for_job(j["id"])
        rows.append({**j,
                     "notice_clause": (f"{clause['days']} days — {clause['method']}" if clause
                                       else "NO CLAUSE RECORDED — the notice letter will refuse "
                                            "and name this gap"),
                     "plan_lines": sum(1 for p in plans if p["job_id"] == j["id"]),
                     "open_deltas": sum(1 for d in ds if d["job_id"] == j["id"]
                                        and d.get("state") not in ("signed", "rejected")),
                     "verbal_notes": len(j.get("verbal_notes") or [])})
    return {"rows": rows}


def deltas(q, b):
    jobs_ix = store.index("jobs")
    rows = []
    for d in store.load("deltas"):
        rows.append({**d, "job_name": (jobs_ix.get(d["job_id"]) or {}).get("name")})
    rows.sort(key=lambda r: r.get("detected_at") or "", reverse=True)
    return {"rows": rows}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/jobs"): jobs,
    ("GET", "/api/deltas"): deltas,
    ("GET", "/api/closeout"): lambda q, b: core.closeout_ledger(),
    ("POST", "/api/diff/run"): lambda q, b: agents.run_diff_all(),
    ("POST", "/api/deltas/<id>/confirm"): lambda q, b: agents.confirm_delta(
        q["id"], human=b.get("human"), classification=b.get("classification")),
    ("POST", "/api/deltas/<id>/co"): lambda q, b: agents.draft_change_order(q["id"]),
    ("POST", "/api/deltas/<id>/notice"): lambda q, b: agents.draft_notice_letter(q["id"]),
    ("POST", "/api/deltas/<id>/signed"): lambda q, b: agents.record_co_signature(
        q["id"], human=b.get("human"), signed=b.get("signed", True)),
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
    serve.run(ROOT / "app", ROUTES, PORT, "Delta OS")
