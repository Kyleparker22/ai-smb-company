#!/usr/bin/env python3
"""Shift OS — server. Stdlib only, 127.0.0.1 only."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8830


def _executor(ap, human="scheduler"):
    def run():
        if ap["action"] == "assign_new_pairing":
            # Approving the PAIRING is not the same as filling the shift. Two
            # decisions, deliberately.
            store.log_event("pairing_approved", ap["subject"], f"human:{human}", "R1",
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
    ("GET", "/api/board"): lambda q, b: {"config": store.load("config"), "board": core.ops_board(),
                                         "pending_approvals": len(gate.pending())},
    ("GET", "/api/shifts/open"): lambda q, b: {
        "rows": [s for s in store.load("shifts") if s.get("state") in ("open", "scheduled")
                 and (s.get("demo_tag") or s.get("state") == "open")][:30]},
    ("POST", "/api/shifts/<id>/callout"): lambda q, b: agents.callout(q["id"]),
    ("POST", "/api/shifts/<id>/fill"): lambda q, b: agents.fill(q["id"]),
    ("POST", "/api/shifts/<id>/accept"): lambda q, b: agents.accept_fill(q["id"], b.get("caregiver")),
    ("GET", "/api/messages"): lambda q, b: {
        "live": sorted([m for m in store.load("messages") if not m.get("handled_at")],
                       key=lambda x: x["at"], reverse=True)[:30]},
    ("POST", "/api/messages/<id>/handle"): lambda q, b: agents.handle_message(q["id"]),
    ("GET", "/api/retention"): lambda q, b: agents.retention(),
    ("GET", "/api/evv"): lambda q, b: core.evv_board(),
    ("GET", "/api/approvals"): lambda q, b: {"pending": gate.pending()},
    ("POST", "/api/approvals/<id>/decide"): lambda q, b: (
        lambda ap, h: gate.decide(q["id"], h, approve=bool(b.get("approve", True)),
                                  execute=_executor(ap, h)) if ap else {"ok": False}
    )(store.by_id("approvals", q["id"]), b.get("human", "scheduler")),
    ("GET", "/api/roi"): lambda q, b: core.roi({k: float(v) for k, v in (q or {}).items() if _num(v)}),
    ("GET", "/api/eval"): lambda q, b: {"crisis": core.eval_crisis(),
                                        "clinical": core.eval_clinical()},
    ("GET", "/api/autonomy"): lambda q, b: {"matrix": core.MATRIX.actions,
                                            "never_promote": core.MATRIX.never_promote()},
    ("GET", "/api/events"): lambda q, b: {"events": store.load("events")[-300:]},
    ("POST", "/api/agents/run"): lambda q, b: agents.run_all(),
}

if __name__ == "__main__":
    if not store.load("config"):
        print("no data yet — run:  python3 seed.py")
    serve.run(ROOT / "app", ROUTES, PORT, "Shift OS")
