#!/usr/bin/env python3
"""Pump OS — server. Stdlib only, 127.0.0.1:8853."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8853


def _executor(ap, human):
    def run():
        if ap["action"] == "draft_invoice":
            j = store.by_id("jobs", ap["subject"])
            if j:
                j["billed_at"] = iso()
                store.upsert("jobs", j)
        store.log_event(ap["action"] + "_done", ap["subject"], f"human:{human}", "R1",
                        {"approval": ap["id"]})
        return ap["subject"]
    return run


def board(q, b):
    due = core.due_systems()
    msgs = [m for m in store.load("messages") if not m.get("handled_at")]
    emergencies = [m for m in store.load("messages") if m.get("label") == "emergency"]
    unbilled = [j for j in store.load("jobs")
                if j.get("done_at") and not j.get("billed_at") and not j.get("demo_tag")]
    return {"config": store.load("config"),
            "board": {"due_systems": len([r for r in due if r.get("overdue_days") is not None]),
                      "unknowable": len([r for r in due if r.get("_missing")]),
                      "due_top": due[:10], "messages_open": len(msgs),
                      "emergencies": len(emergencies),
                      "unbilled_done": len(unbilled),
                      "recovered": core.recovered_this_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/messages"): lambda q, b: {"rows": sorted(store.load("messages"),
        key=lambda m: m.get("at") or "", reverse=True)[:60]},
    ("POST", "/api/messages/<id>/handle"): lambda q, b: agents.handle_message(q["id"]),
    ("GET", "/api/jobs"): lambda q, b: {"rows": [j for j in store.load("jobs")
                                                if j.get("done_at")][:50]},
    ("POST", "/api/jobs/<id>/bill"): lambda q, b: agents.bill_job(q["id"]),
    ("GET", "/api/due"): lambda q, b: {"rows": core.due_systems()[:40]},
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
    serve.run(ROOT / "app", ROUTES, PORT, "Pump OS")
