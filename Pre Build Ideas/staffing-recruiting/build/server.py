#!/usr/bin/env python3
"""Redeploy OS — server. Stdlib only, 127.0.0.1 only."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8829


def _executor(ap, human="recruiter"):
    def run():
        if ap["action"] == "submit_to_client":
            sub = store.by_id("submissions", ap["subject"])
            if sub:
                sub["state"] = "submitted"
                sub["submitted_at"] = iso()
                store.upsert("submissions", sub)
                store.log_event("submitted", sub["id"], f"human:{human}", "R1",
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
    ("GET", "/api/board"): lambda q, b: {"config": store.load("config"), "board": core.desk_board(),
                                         "pending_approvals": len(gate.pending())},
    ("GET", "/api/reqs"): lambda q, b: {
        "open": [r for r in store.load("reqs") if r.get("state") == "open"][:40]},
    ("POST", "/api/reqs/<id>/shortlist"): lambda q, b: agents.shortlist(q["id"]),
    ("POST", "/api/screen"): lambda q, b: agents.screen(b.get("candidate"), b.get("req")),
    ("POST", "/api/submissions/<id>/packet"): lambda q, b: agents.packet(q["id"]),
    ("POST", "/api/submissions/<id>/present"): lambda q, b: agents.present(q["id"]),
    ("GET", "/api/redeploy"): lambda q, b: {"due": core.redeploy_due(),
                                            "rate": core.redeploy_rate()},
    ("POST", "/api/redeploy/sweep"): lambda q, b: agents.redeploy(),
    ("GET", "/api/credentials"): lambda q, b: agents.credentials(),
    ("GET", "/api/approvals"): lambda q, b: {"pending": gate.pending()},
    ("POST", "/api/approvals/<id>/decide"): lambda q, b: (
        lambda ap, h: gate.decide(q["id"], h, approve=bool(b.get("approve", True)),
                                  execute=_executor(ap, h)) if ap else {"ok": False}
    )(store.by_id("approvals", q["id"]), b.get("human", "recruiter")),
    ("GET", "/api/roi"): lambda q, b: core.roi({k: float(v) for k, v in (q or {}).items() if _num(v)}),
    ("GET", "/api/eval"): lambda q, b: {"shortlist": core.eval_shortlist(),
                                        "excluded": core.eval_excluded_factors(),
                                        "render": core.eval_render_honesty(),
                                        "permitted": list(core.PERMITTED_FACTORS),
                                        "excluded_list": list(core.EXCLUDED_FACTORS)},
    ("GET", "/api/autonomy"): lambda q, b: {"matrix": core.MATRIX.actions,
                                            "never_promote": core.MATRIX.never_promote()},
    ("GET", "/api/events"): lambda q, b: {"events": store.load("events")[-300:]},
    ("POST", "/api/agents/run"): lambda q, b: agents.run_all(),
}

if __name__ == "__main__":
    if not store.load("config"):
        print("no data yet — run:  python3 seed.py")
    serve.run(ROOT / "app", ROUTES, PORT, "Redeploy OS")
