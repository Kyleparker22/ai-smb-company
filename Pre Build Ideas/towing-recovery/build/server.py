#!/usr/bin/env python3
"""Hook OS — server. Stdlib only, 127.0.0.1:8854."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8854


def _executor(ap, human):
    def run():
        if ap["action"] == "process_release":
            pass  # the window records the release on the impound row itself
        store.log_event(ap["action"] + "_done", ap["subject"], f"human:{human}", "R1",
                        {"approval": ap["id"]})
        return ap["subject"]
    return run


def board(q, b):
    held = [i for i in store.load("impounds") if not i.get("released_at") and not i.get("demo_tag")]
    held_value = 0.0
    for i in held:
        sb = core.storage_bill(i)
        if sb.get("total"):
            held_value += sb["total"]
    calls_open = [c for c in store.load("calls") if not c.get("handled_at")]
    return {"config": store.load("config"),
            "board": {"vehicles_held": len(held),
                      "held_storage_value": round(held_value, 2),
                      "calls_open": len(calls_open),
                      "recovered": core.recovered_this_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending()),
            "card": core.rate_card()}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/calls"): lambda q, b: {"rows": sorted(store.load("calls"),
        key=lambda m: m.get("at") or "", reverse=True)[:60]},
    ("POST", "/api/calls/<id>/handle"): lambda q, b: agents.handle_call(q["id"]),
    ("GET", "/api/tows"): lambda q, b: {"rows": store.load("tows")[:50]},
    ("POST", "/api/tows/<id>/bill"): lambda q, b: agents.bill_tow(q["id"]),
    ("POST", "/api/tows/<id>/damage"): lambda q, b: agents.damage_dispute(q["id"]),
    ("GET", "/api/impounds"): lambda q, b: {"rows": [
        {**i, "storage": core.storage_bill(i), "lien": core.lien_calendar(i)}
        for i in store.load("impounds")][:40]},
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
    serve.run(ROOT / "app", ROUTES, PORT, "Hook OS")
