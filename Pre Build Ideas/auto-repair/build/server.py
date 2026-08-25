#!/usr/bin/env python3
"""Bay OS — server. Stdlib only, 127.0.0.1:8832."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8832


def _executor(ap, human):
    def run():
        if ap["action"] in ("draft_reoffer", "draft_approval_nudge"):
            store.log_event(ap["action"].replace("draft_", "") + "_sent", ap["subject"],
                            f"human:{human}", "R1", {"approval": ap["id"]})
        return ap["subject"]
    return run


def board(q, b):
    dv = core.declined_value()
    cb = core.comeback_rate()
    calls_open = [c for c in store.load("calls") if not c.get("handled_at")]
    safety_open = [d for d in store.load("declined")
                   if d.get("label") == "safety_critical" and not d.get("recovered_at")
                   and not d.get("demo_tag")]
    return {"config": store.load("config"),
            "board": {"declined": dv, "comebacks": cb,
                      "safety_open": len(safety_open),
                      "calls_open": len(calls_open),
                      "recovered": core.recovered_this_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/declined"): lambda q, b: {"rows": sorted(store.load("declined"),
        key=lambda d: (d.get("label") != "safety_critical", d.get("declined_at") or ""))[:100],
        "value": core.declined_value(), "rule": core.SAFETY_CONTACT_RULE},
    ("POST", "/api/declined/<id>/text"): lambda q, b: agents.send_text(q["id"]),
    ("POST", "/api/declined/<id>/plan"): lambda q, b: core.reoffer_plan(store.by_id("declined", q["id"]) or {}),
    ("GET", "/api/calls"): lambda q, b: {"rows": store.load("calls")},
    ("POST", "/api/calls/<id>/classify"): lambda q, b: dict(
        core.classify_call((store.by_id("calls", q["id"]) or {}).get("transcript", "")), call=q["id"]),
    ("GET", "/api/comebacks"): lambda q, b: core.comeback_rate(),
    ("GET", "/api/band/<kind>"): lambda q, b: core.price_band(q["kind"]),
    ("GET", "/api/quote/<kind>"): lambda q, b: agents.price_quote(q["kind"]),
    ("GET", "/api/roi"): lambda q, b: core.roi(q),
    ("GET", "/api/eval"): lambda q, b: {"items": core.run_eval()},
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
    serve.run(ROOT / "app", ROUTES, PORT, "Bay OS")
