#!/usr/bin/env python3
"""Slip OS — server. Stdlib only, 127.0.0.1:8868."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8868


def _executor(ap, human):
    def run():
        if ap["action"] == "draft_slip_offer":
            w = store.by_id("waitlist", ap["subject"])
            if w:
                w["placed_at"] = iso()
                store.upsert("waitlist", w)
        store.log_event(ap["action"] + "_done", ap["subject"], f"human:{human}", "R1",
                        {"approval": ap["id"]})
        return ap["subject"]
    return run


def board(q, b):
    slips = store.load("slips")
    open_slips = [s for s in slips if not s.get("occupied_by") and not s.get("demo_tag")]
    wl = [w for w in store.load("waitlist") if not w.get("placed_at")]
    msgs = [m for m in store.load("messages") if not m.get("handled_at")]
    in_yard = [v for v in store.load("vessels") if not v.get("departed_at") and not v.get("demo_tag")]
    return {"config": store.load("config"),
            "board": {"open_slips": len(open_slips), "waitlist_depth": len(wl),
                      "vessels_in_yard": len(in_yard), "messages_open": len(msgs),
                      "recovered": core.recovered_this_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/messages"): lambda q, b: {"rows": sorted(store.load("messages"),
        key=lambda m: m.get("at") or "", reverse=True)[:60]},
    ("POST", "/api/messages/<id>/handle"): lambda q, b: agents.handle_message(q["id"]),
    ("GET", "/api/workorders"): lambda q, b: {"rows": store.load("workorders")[:40]},
    ("POST", "/api/workorders/<id>/start"): lambda q, b: agents.start_work(
        q["id"], by=b.get("by"), scope=b.get("scope"), rate_basis=b.get("rate_basis")),
    ("GET", "/api/vessels/<id>/storage"): lambda q, b: core.storage_bill(
        store.by_id("vessels", q["id"]) or {}),
    ("POST", "/api/slips/<id>/offer"): lambda q, b: agents.offer_slip(q["id"]),
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
    serve.run(ROOT / "app", ROUTES, PORT, "Slip OS")
