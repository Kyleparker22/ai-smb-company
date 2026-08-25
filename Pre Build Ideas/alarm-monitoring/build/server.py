#!/usr/bin/env python3
"""Central OS — server. Stdlib only, 127.0.0.1:8864."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8864


def _executor(ap, human):
    def run():
        if ap["action"] == "draft_permit_renewal":
            a = store.by_id("accounts", ap["subject"])
            if a:
                a["permit_renewed_at"] = iso()
                store.upsert("accounts", a)
        store.log_event(ap["action"] + "_done", ap["subject"], f"human:{human}", "R1",
                        {"approval": ap["id"]})
        return ap["subject"]
    return run


def board(q, b):
    accounts = store.load("accounts")
    exposure = 0.0
    lapses = 0
    for a in accounts:
        fe = core.fine_exposure(a)
        if fe.get("accrued"):
            exposure += fe["accrued"]
        ps = core.permit_state(a)
        if ps.get("state") in ("expired", "unregistered"):
            lapses += 1
    msgs = [m for m in store.load("messages") if not m.get("handled_at")]
    return {"config": store.load("config"),
            "board": {"fine_exposure": round(exposure, 2), "permit_lapses": lapses,
                      "messages_open": len(msgs),
                      "recovered": core.recovered_this_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/messages"): lambda q, b: {"rows": sorted(store.load("messages"),
        key=lambda m: m.get("at") or "", reverse=True)[:60]},
    ("POST", "/api/messages/<id>/handle"): lambda q, b: agents.handle_message(q["id"]),
    ("GET", "/api/signals"): lambda q, b: {"rows": store.load("signals")},
    ("POST", "/api/signals/<id>/cancel"): lambda q, b: agents.cancel_dispatch(
        q["id"], human=b.get("human"), verified_callback=bool(b.get("verified_callback"))),
    ("POST", "/api/accounts/<id>/verify"): lambda q, b: agents.verify_callback(
        q["id"], b.get("operator", "operator")),
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
    serve.run(ROOT / "app", ROUTES, PORT, "Central OS")
