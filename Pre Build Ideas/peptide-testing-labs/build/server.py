#!/usr/bin/env python3
"""Assay OS — server. Stdlib only, 127.0.0.1:8895."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve

PORT = 8895


def board(q, b):
    flight = core.in_flight()
    coas = store.load("coas")
    released = [c for c in coas if c.get("state") == "released"]
    return {"config": store.load("config"),
            "board": {"in_flight": len(flight), "oldest": flight[:8],
                      "turnaround": core.turnaround(),
                      "released": len(released),
                      "superseded": sum(1 for c in coas if c.get("state") == "superseded"),
                      "drafts": sum(1 for c in coas if c.get("state") == "draft"),
                      "lookups": len(store.events(kind="verification_lookup")),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


def release(q, b):
    return agents.release_coa(q["id"], b.get("human", "lab.manager"))


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/queue"): lambda q, b: {"rows": core.in_flight()},
    ("POST", "/api/samples/<id>/grade"): lambda q, b: agents.grade_sample(q["id"]),
    ("POST", "/api/samples/<id>/draft"): lambda q, b: agents.draft_coa(q["id"]),
    ("GET", "/api/coas"): lambda q, b: {"rows": sorted(store.load("coas"),
                                                       key=lambda c: c.get("released_at") or "",
                                                       reverse=True)[:60],
                                        "scope": core.SCOPE_NOTE},
    ("POST", "/api/coas/<id>/release"): release,
    ("POST", "/api/coas/<id>/supersede"): lambda q, b: agents.supersede(
        q["id"], b.get("human", "lab.manager"), b.get("reason", "corrected result")),
    ("GET", "/api/verify/<token>"): lambda q, b: core.verify(q["token"]),
    ("POST", "/api/ask"): lambda q, b: agents.answer_client(b.get("text", "")),
    ("GET", "/api/spec"): lambda q, b: {"spec": core.SPEC, "scope": core.SCOPE_NOTE},
    ("GET", "/api/roi"): lambda q, b: core.roi(q),
    ("GET", "/api/eval"): lambda q, b: {"grading": core.run_eval()},
    ("GET", "/api/autonomy"): lambda q, b: {"matrix": core.matrix.actions,
                                            "never_promote": core.matrix.never_promote(),
                                            "automation": core.automation()},
    ("GET", "/api/approvals"): lambda q, b: {"pending": gate.pending()},
    ("POST", "/api/approvals/<id>/decide"): lambda q, b: gate.decide(
        q["id"], b.get("human", "lab.manager"), b.get("approve", True)),
    ("GET", "/api/events"): lambda q, b: {"events": store.events()[-120:]},
    ("POST", "/api/agents/run"): lambda q, b: agents.run_all(),
}

if __name__ == "__main__":
    serve.run(ROOT / "app", ROUTES, PORT, "Assay OS")
