#!/usr/bin/env python3
"""Hours OS — server. Stdlib only, 127.0.0.1:8865."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8865


def _executor(ap, human):
    def run():
        if ap["action"] == "draft_detention_invoice":
            l = store.by_id("loads", ap["subject"])
            if l:
                l["detention_billed_at"] = iso()
                store.upsert("loads", l)
        store.log_event(ap["action"] + "_done", ap["subject"], f"human:{human}", "R1",
                        {"approval": ap["id"]})
        return ap["subject"]
    return run


def board(q, b):
    drivers = [d for d in store.load("drivers") if not d.get("demo_tag")]
    unknown = [d for d in drivers if d.get("hos_remaining_h") is None]
    mb = core.maintenance_board()
    msgs = [m for m in store.load("messages") if not m.get("handled_at")]
    return {"config": store.load("config"),
            "board": {"drivers": len(drivers), "clocks_unknown": len(unknown),
                      "trucks_overdue": len([r for r in mb if r.get("overdue")]),
                      "messages_open": len(msgs),
                      "recovered": core.recovered_this_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/messages"): lambda q, b: {"rows": sorted(store.load("messages"),
        key=lambda m: m.get("at") or "", reverse=True)[:60]},
    ("POST", "/api/messages/<id>/handle"): lambda q, b: agents.handle_message(q["id"]),
    ("GET", "/api/drivers"): lambda q, b: {"rows": store.load("drivers")},
    ("POST", "/api/dispatch"): lambda q, b: agents.dispatch(b.get("driver_id"), b.get("load_id")),
    ("GET", "/api/loads"): lambda q, b: {"rows": store.load("loads")[:40]},
    ("POST", "/api/loads/<id>/detention"): lambda q, b: (
        lambda l: core.detention_invoice(l) if l else {"error": "no such load"})(
        store.by_id("loads", q["id"])),
    ("GET", "/api/maintenance"): lambda q, b: {"rows": core.maintenance_board()},
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
    serve.run(ROOT / "app", ROUTES, PORT, "Hours OS")
