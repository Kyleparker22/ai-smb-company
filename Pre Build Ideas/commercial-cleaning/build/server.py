#!/usr/bin/env python3
"""Crew OS — server. Stdlib only, 127.0.0.1:8841."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8841


def _executor(ap, human):
    def run():
        store.log_event(ap["action"].replace("draft_", "") + "_sent", ap["subject"],
                        f"human:{human}", "R1", {"approval": ap["id"]})
        return ap["subject"]
    return run


def board(q, b):
    cb = core.coverage_board()
    sec_open = [r for r in store.load("reports")
                if r.get("label") == "security" and not r.get("closed_at") and not r.get("demo_tag")]
    msgs = [r for r in store.load("reports") if not r.get("handled_at")]
    return {"config": store.load("config"),
            "board": {"covered": cb["covered"], "uncovered": len(cb["uncovered"]),
                      "uncovered_rows": cb["uncovered"][:8],
                      "security_open": len(sec_open), "reports_open": len(msgs),
                      "recovered": core.recovered_this_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/reports"): lambda q, b: {"rows": sorted(store.load("reports"),
        key=lambda m: m.get("at") or "", reverse=True)[:60]},
    ("POST", "/api/reports/<id>/handle"): lambda q, b: agents.handle_report(q["id"]),
    ("POST", "/api/reports/<id>/close"): lambda q, b: agents.close_incident(q["id"], human=b.get("human")),
    ("POST", "/api/contracts/<id>/claim"): lambda q, b: core.clean_claim(q["id"]),
    ("GET", "/api/coverage"): lambda q, b: core.coverage_board(),
    ("GET", "/api/roi"): lambda q, b: core.roi(q),
    ("GET", "/api/eval"): lambda q, b: {"triage": core.run_eval()},
    ("GET", "/api/autonomy"): lambda q, b: {"matrix": core.matrix.actions,
                                            "never_promote": core.matrix.never_promote(),
                                            "automation": core.automation()},
    ("GET", "/api/approvals"): lambda q, b: {"pending": gate.pending()},
    ("POST", "/api/approvals/<id>/decide"): lambda q, b: gate.decide(
        q["id"], b.get("human", "supervisor"), b.get("approve", True),
        execute=_executor(store.by_id("approvals", q["id"]) or {}, b.get("human", "supervisor"))),
    ("GET", "/api/events"): lambda q, b: {"events": store.events()[-120:]},
    ("POST", "/api/agents/run"): lambda q, b: agents.run_all(),
}

if __name__ == "__main__":
    serve.run(ROOT / "app", ROUTES, PORT, "Crew OS")
