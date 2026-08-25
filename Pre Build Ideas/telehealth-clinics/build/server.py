#!/usr/bin/env python3
"""Encounter OS — server. Stdlib only, 127.0.0.1:8898."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve

PORT = 8898


def board(q, b):
    gaps = core.coverage_gaps()
    return {"config": store.load("config"),
            "board": {"gaps": gaps, "gap_states": len(gaps),
                      "gap_patients": sum(g["patients"] for g in gaps),
                      "conversion": core.conversion(),
                      "paid_not_seen": len(core.paid_not_seen()),
                      "doc_gaps": len(core.documentation_gaps()),
                      "intakes_open": sum(1 for i in store.load("intakes") if not i.get("triaged_at")),
                      "clinicians": sum(1 for c in store.load("clinicians") if c.get("active")),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/intakes"): lambda q, b: {"rows": store.load("intakes")[:60],
                                           "instruction": core.URGENT_INSTRUCTION},
    ("POST", "/api/intakes/<id>/triage"): lambda q, b: agents.triage_intake(q["id"]),
    ("GET", "/api/route/<id>"): lambda q, b: core.route(q["id"]),
    ("POST", "/api/route/<id>"): lambda q, b: agents.route_patient(q["id"], b.get("need")),
    ("GET", "/api/patients"): lambda q, b: {"rows": store.load("patients")[:60]},
    ("GET", "/api/clinicians"): lambda q, b: {"rows": store.load("clinicians")},
    ("GET", "/api/gaps"): lambda q, b: {"rows": core.coverage_gaps()},
    ("GET", "/api/unseen"): lambda q, b: {"rows": core.paid_not_seen()},
    ("POST", "/api/unseen/<id>/draft"): lambda q, b: agents.draft_reengagement(q["id"]),
    ("GET", "/api/documentation"): lambda q, b: {"rows": core.documentation_gaps()[:60],
                                                 "required": list(core.REQUIRED_DOC)},
    ("POST", "/api/encounters/<id>/close"): lambda q, b: agents.close(q["id"], b.get("human", "clinician")),
    ("POST", "/api/ask"): lambda q, b: agents.answer_clinical(b.get("text", "")),
    ("GET", "/api/roi"): lambda q, b: core.roi(q),
    ("GET", "/api/eval"): lambda q, b: {"routing": core.run_eval()},
    ("GET", "/api/autonomy"): lambda q, b: {"matrix": core.matrix.actions,
                                            "never_promote": core.matrix.never_promote(),
                                            "automation": core.automation()},
    ("GET", "/api/approvals"): lambda q, b: {"pending": gate.pending()},
    ("POST", "/api/approvals/<id>/decide"): lambda q, b: gate.decide(
        q["id"], b.get("human", "coordinator"), b.get("approve", True)),
    ("GET", "/api/events"): lambda q, b: {"events": store.events()[-120:]},
    ("POST", "/api/agents/run"): lambda q, b: agents.run_all(),
}

if __name__ == "__main__":
    serve.run(ROOT / "app", ROUTES, PORT, "Encounter OS")
