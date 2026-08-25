#!/usr/bin/env python3
"""Inspect OS — server. Stdlib only, 127.0.0.1:8856."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8856


def _executor(ap, human):
    def run():
        store.log_event(ap["action"] + "_done", ap["subject"], f"human:{human}", "R1",
                        {"approval": ap["id"]})
        return ap["subject"]
    return run


def board(q, b):
    msgs = [m for m in store.load("messages") if not m.get("handled_at")]
    soften = [m for m in store.load("messages") if m.get("label") == "soften_request"]
    open_reports = [i for i in store.load("inspections")
                    if i.get("inspected_at") and not i.get("report_sent_at")
                    and not i.get("demo_tag")]
    overdue = [i for i in open_reports if core.report_clock(i).get("overdue")]
    return {"config": store.load("config"),
            "board": {"reports_open": len(open_reports), "reports_overdue": len(overdue),
                      "soften_requests": len(soften),
                      "messages_open": len(msgs),
                      "referrals": core.referral_ledger(),
                      "recovered": core.recovered_this_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/messages"): lambda q, b: {"rows": sorted(store.load("messages"),
        key=lambda m: m.get("at") or "", reverse=True)[:60]},
    ("POST", "/api/messages/<id>/handle"): lambda q, b: agents.handle_message(q["id"]),
    ("GET", "/api/inspections/<id>/findings"): lambda q, b: core.findings_for(q["id"]),
    ("POST", "/api/findings/<id>/revise"): lambda q, b: core.revise_finding(
        q["id"], b.get("text", ""), b.get("severity", "minor"), b.get("actor", "inspector")),
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
    serve.run(ROOT / "app", ROUTES, PORT, "Inspect OS")
