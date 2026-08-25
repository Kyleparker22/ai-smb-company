#!/usr/bin/env python3
"""Stone OS — server. Stdlib only, 127.0.0.1:8871."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8871


def _executor(ap, human):
    def run():
        if ap.get("action") == "schedule_setting":
            o = store.by_id("orders", ap["subject"])
            if o:
                o["setting_scheduled_at"] = iso()
                store.upsert("orders", o)
        store.log_event(str(ap.get("action")) + "_done", ap.get("subject"),
                        f"human:{human}", "R1", {"approval": ap.get("id")})
        return ap.get("subject")
    return run


def board(q, b):
    pb = core.pipeline_board()
    msgs = [m for m in store.load("messages") if not m.get("handled_at")]
    proofs_waiting = [p for p in store.load("proofs") if not p.get("approval")]
    open_bal = round(sum(o.get("balance_due") or 0 for o in store.load("orders")
                         if not o.get("demo_tag") and not o.get("balance_paid_at")), 2)
    return {"config": store.load("config"),
            "board": {"active": pb["active"], "stalled": pb["stalled"],
                      "by_stage": pb["by_stage"], "stalled_top": pb["rows"][:10],
                      "proofs_waiting_on_family": len(proofs_waiting),
                      "open_balances": open_bal, "messages_open": len(msgs),
                      "recovered": core.recovered_this_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/messages"): lambda q, b: {"rows": sorted(store.load("messages"),
        key=lambda m: m.get("at") or "", reverse=True)[:60]},
    ("POST", "/api/messages/<id>/handle"): lambda q, b: agents.handle_message(q["id"]),
    ("GET", "/api/pipeline"): lambda q, b: core.pipeline_board(),
    ("GET", "/api/cemeteries"): lambda q, b: {"rows": store.load("cemeteries")},
    ("GET", "/api/proofs"): lambda q, b: {"rows": [p for p in store.load("proofs")
                                                   if not p.get("approval")][:40]},
    ("GET", "/api/orders/<id>/compliance"): lambda q, b: core.compliance(
        store.by_id("orders", q["id"]) or {}),
    ("POST", "/api/proofs/<id>/approve-software"): lambda q, b: gate.act(
        "approve_proof", "probe", q["id"],
        {"why": "demo probe — software asked to approve a family's proof"}),
    ("POST", "/api/proofs/<id>/approve"): lambda q, b: agents.record_family_approval(
        q["id"], b.get("family_member"), b.get("signature_ref"), b.get("staff", "owner")),
    ("POST", "/api/orders/<id>/engrave"): lambda q, b: agents.start_engraving(q["id"]),
    ("POST", "/api/orders/<id>/set"): lambda q, b: agents.schedule_setting(q["id"]),
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
    serve.run(ROOT / "app", ROUTES, PORT, "Stone OS")
