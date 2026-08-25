#!/usr/bin/env python3
"""Protocol OS — server. Stdlib only, 127.0.0.1:8897."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve

PORT = 8897


def board(q, b):
    rows = core.due_and_lapsing()
    sil = core.silent_after_change()
    return {"config": store.load("config"),
            "board": {"lapsing": sum(1 for r in rows if r.get("state") == "lapsing"),
                      "overdue": sum(1 for r in rows if r.get("state") == "overdue"),
                      "due": sum(1 for r in rows if r.get("state") == "due"),
                      "silent": len(sil), "silent_top": sil[:6],
                      "continuation": core.continuation_rate(),
                      "contactable": len(core.contactable()),
                      "excluded": len(store.load("patients")) - len(core.contactable()),
                      "labs_waiting": len(core.labs_waiting()),
                      "messages_open": sum(1 for m in store.load("messages") if not m.get("handled_at")),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/messages"): lambda q, b: {"rows": store.load("messages"),
                                            "instruction": core.URGENT_INSTRUCTION},
    ("POST", "/api/messages/<id>/handle"): lambda q, b: agents.handle_message(q["id"]),
    ("GET", "/api/cycle"): lambda q, b: {"rows": core.due_and_lapsing()[:80],
                                         "excluded": len(store.load("patients")) - len(core.contactable())},
    ("POST", "/api/cycle/<id>/nudge"): lambda q, b: agents.draft_refill_nudge(q["id"]),
    ("GET", "/api/silent"): lambda q, b: {"rows": core.silent_after_change()},
    ("GET", "/api/labs"): lambda q, b: {"rows": core.labs_waiting()},
    ("GET", "/api/excluded"): lambda q, b: {"rows": [
        {"id": p["id"], "name": p["name"], "status": p["status"]}
        for p in store.load("patients") if p.get("status") in core.NEVER_CONTACT][:40],
        "why": "these patients are outside every sweep by construction"},
    ("POST", "/api/ask"): lambda q, b: agents.answer_clinical(b.get("text", "")),
    ("POST", "/api/dose"): lambda q, b: agents.adjust_dose(b.get("patient", "pt0001"), b.get("change", "+1 step")),
    ("GET", "/api/roi"): lambda q, b: core.roi(q),
    ("GET", "/api/eval"): lambda q, b: {"triage": core.run_eval()},
    ("GET", "/api/autonomy"): lambda q, b: {"matrix": core.matrix.actions,
                                            "never_promote": core.matrix.never_promote(),
                                            "automation": core.automation()},
    ("GET", "/api/approvals"): lambda q, b: {"pending": gate.pending()},
    ("POST", "/api/approvals/<id>/decide"): lambda q, b: gate.decide(
        q["id"], b.get("human", "frontdesk"), b.get("approve", True)),
    ("GET", "/api/events"): lambda q, b: {"events": store.events()[-120:]},
    ("POST", "/api/agents/run"): lambda q, b: agents.run_all(),
}

if __name__ == "__main__":
    serve.run(ROOT / "app", ROUTES, PORT, "Protocol OS")
