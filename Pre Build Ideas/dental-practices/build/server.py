#!/usr/bin/env python3
"""Chair OS — server. Stdlib only, 127.0.0.1 only."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8823


def _executor(ap, human="office"):
    def run():
        if ap["action"] == "draft_reactivation":
            store.log_event("reactivation_sent", ap["subject"], f"human:{human}", "R1",
                            {"approval": ap["id"], "fee": (ap.get("detail") or {}).get("fee", 0)})
        return ap["subject"]
    return run


def _num(v):
    try:
        float(v)
        return True
    except (TypeError, ValueError):
        return False


ROUTES = {
    ("GET", "/api/board"): lambda q, b: {
        "config": store.load("config"), "board": core.chair_board(),
        "pending_approvals": len(gate.pending())},
    ("GET", "/api/unscheduled"): lambda q, b: {
        "total": core.unscheduled_total(),
        "rows": core.rank_unscheduled(limit=int(q.get("limit", 40)))},
    ("POST", "/api/reactivation/run"): lambda q, b: agents.reactivation(),
    ("GET", "/api/openings"): lambda q, b: {
        "openings": [a for a in store.load("appointments") if a.get("state") in ("open", "scheduled")
                     and a.get("demo_tag")],
        "note": "the two holes tomorrow and the appointment that cancels at 7:04am"},
    ("POST", "/api/openings/<id>/fill"): lambda q, b: agents.same_day_fill(q["id"]),
    ("POST", "/api/openings/<id>/accept"): lambda q, b: agents.accept_fill(q["id"], b.get("plan")),
    ("GET", "/api/benefits"): lambda q, b: agents.benefits_pack(),
    ("GET", "/api/recall"): lambda q, b: agents.recall_watchtower(),
    ("GET", "/api/approvals"): lambda q, b: {"pending": gate.pending()},
    ("POST", "/api/approvals/<id>/decide"): lambda q, b: (
        lambda ap, h: gate.decide(q["id"], h, approve=bool(b.get("approve", True)),
                                  execute=_executor(ap, h)) if ap else {"ok": False}
    )(store.by_id("approvals", q["id"]), b.get("human", "office")),
    ("GET", "/api/roi"): lambda q, b: core.roi({k: float(v) for k, v in (q or {}).items() if _num(v)}),
    ("GET", "/api/eval"): lambda q, b: core.eval_coverage(),
    ("GET", "/api/autonomy"): lambda q, b: {"matrix": core.MATRIX.actions,
                                            "never_promote": core.MATRIX.never_promote()},
    ("GET", "/api/events"): lambda q, b: {"events": store.load("events")[-300:]},
    ("POST", "/api/agents/run"): lambda q, b: agents.run_all(),
}

if __name__ == "__main__":
    if not store.load("config"):
        print("no data yet — run:  python3 seed.py")
    serve.run(ROOT / "app", ROUTES, PORT, "Chair OS")
