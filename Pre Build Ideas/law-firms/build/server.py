#!/usr/bin/env python3
"""Case OS — server. Stdlib only, 127.0.0.1 only."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8826


def _executor(ap, human="attorney"):
    def run():
        if ap["action"] == "send_retainer":
            store.log_event("retainer_signed", ap["subject"], f"human:{human}", "R1",
                            {"approval": ap["id"]})
        if ap["action"] == "draft_demand_facts":
            store.log_event("demand_sent", ap["subject"], f"human:{human}", "R1",
                            {"approval": ap["id"]})
        return ap["subject"]
    return run


def _num(v):
    try:
        float(v)
        return True
    except (TypeError, ValueError):
        return False


ROUTES = {
    ("GET", "/api/board"): lambda q, b: {"config": store.load("config"), "board": core.case_board(),
                                         "pending_approvals": len(gate.pending())},
    ("GET", "/api/leads"): lambda q, b: {
        "live": sorted([l for l in store.load("leads") if not l.get("handled_at")],
                       key=lambda x: x["at"], reverse=True)[:30],
        "criteria": store.load("config").get("criteria")},
    ("POST", "/api/leads/<id>/intake"): lambda q, b: agents.intake(q["id"]),
    ("GET", "/api/records"): lambda q, b: core.records_board(),
    ("POST", "/api/records/sweep"): lambda q, b: agents.records_engine(),
    ("GET", "/api/demand/<id>"): lambda q, b: agents.demand_draft(q["id"]),
    ("GET", "/api/status"): lambda q, b: agents.client_status(),
    ("GET", "/api/approvals"): lambda q, b: {"pending": gate.pending()},
    ("POST", "/api/approvals/<id>/decide"): lambda q, b: (
        lambda ap, h: gate.decide(q["id"], h, approve=bool(b.get("approve", True)),
                                  execute=_executor(ap, h)) if ap else {"ok": False}
    )(store.by_id("approvals", q["id"]), b.get("human", "attorney")),
    ("GET", "/api/roi"): lambda q, b: core.roi({k: float(v) for k, v in (q or {}).items() if _num(v)}),
    ("GET", "/api/eval"): lambda q, b: {"upl": core.eval_upl(), "productions": core.eval_productions()},
    ("GET", "/api/autonomy"): lambda q, b: {"matrix": core.MATRIX.actions,
                                            "never_promote": core.MATRIX.never_promote()},
    ("GET", "/api/events"): lambda q, b: {"events": store.load("events")[-300:]},
    ("POST", "/api/agents/run"): lambda q, b: agents.run_all(),
}

if __name__ == "__main__":
    if not store.load("config"):
        print("no data yet — run:  python3 seed.py")
    serve.run(ROOT / "app", ROUTES, PORT, "Case OS")
