#!/usr/bin/env python3
"""Provenance OS — server. Stdlib only, 127.0.0.1:8896."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve

PORT = 8896


def board(q, b):
    oc = core.open_changes()
    return {"config": store.load("config"),
            "board": {"open_changes": len(oc),
                      "landing": sum(1 for c in oc if c["affected_n"]),
                      "top": oc[:6],
                      "readiness": core.packet_readiness(),
                      "review_lag": core.review_lag(),
                      "complaints_open": sum(1 for c in store.load("complaints")
                                             if c.get("label") == "adverse_event"),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/changes"): lambda q, b: {"rows": core.open_changes(), "scope": core.WATCH_SCOPE},
    ("POST", "/api/changes/sweep"): lambda q, b: agents.sweep_changes(),
    ("GET", "/api/batches"): lambda q, b: {"rows": [core.dossier(x["id"])
                                                    for x in store.load("batches")[:60]]},
    ("GET", "/api/batches/<id>"): lambda q, b: core.dossier(q["id"]),
    ("POST", "/api/batches/<id>/release"): lambda q, b: agents.release_batch(
        q["id"], b.get("human", "qa.lead")),
    ("GET", "/api/suppliers"): lambda q, b: {"rows": store.load("supplier_coas")[:60]},
    ("POST", "/api/suppliers/<id>/verify"): lambda q, b: agents.check_supplier(q["id"]),
    ("POST", "/api/complaints"): lambda q, b: agents.intake_complaint(b.get("text", "")),
    ("GET", "/api/complaints"): lambda q, b: {"rows": store.load("complaints")[-40:]},
    ("POST", "/api/ask"): lambda q, b: agents.answer_compliance_question(b.get("text", "")),
    ("GET", "/api/roi"): lambda q, b: core.roi(q),
    ("GET", "/api/eval"): lambda q, b: {"watcher": core.run_eval()},
    ("GET", "/api/autonomy"): lambda q, b: {"matrix": core.matrix.actions,
                                            "never_promote": core.matrix.never_promote(),
                                            "automation": core.automation()},
    ("GET", "/api/approvals"): lambda q, b: {"pending": gate.pending()},
    ("POST", "/api/approvals/<id>/decide"): lambda q, b: gate.decide(
        q["id"], b.get("human", "qa.lead"), b.get("approve", True)),
    ("GET", "/api/events"): lambda q, b: {"events": store.events()[-120:]},
    ("POST", "/api/agents/run"): lambda q, b: agents.run_all(),
}

if __name__ == "__main__":
    serve.run(ROOT / "app", ROUTES, PORT, "Provenance OS")
