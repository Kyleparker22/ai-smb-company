#!/usr/bin/env python3
"""Pool OS — server. Stdlib only, 127.0.0.1:8851."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8851


def _executor(ap, human):
    def run():
        if ap["action"] == "draft_stop_invoice":
            s = store.by_id("stops", ap["subject"])
            if s:
                s["billed_at"] = iso()
                store.upsert("stops", s)
        store.log_event(ap["action"] + "_done", ap["subject"], f"human:{human}", "R1",
                        {"approval": ap["id"]})
        return ap["subject"]
    return run


def board(q, b):
    ub = core.unbilled_proven_stops()
    msgs = [m for m in store.load("messages") if not m.get("handled_at")]
    injuries = [m for m in store.load("messages") if m.get("label") == "injury"]
    open_q = [x for x in store.load("quotes")
              if not x.get("won_at") and not x.get("lost_at") and not x.get("demo_tag")]
    return {"config": store.load("config"),
            "board": {"unbilled": ub, "messages_open": len(msgs),
                      "injury_reports": len(injuries),
                      "open_quotes": len(open_q),
                      "open_quote_value": round(sum(x.get("amount", 0) for x in open_q), 2),
                      "recovered": core.recovered_this_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


def _reading(q, b):
    s = store.by_id("stops", q["id"]) or {}
    pool = store.by_id("pools", s.get("pool_id")) or {}
    return core.reading_report(pool, s)


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/messages"): lambda q, b: {"rows": sorted(store.load("messages"),
        key=lambda m: m.get("at") or "", reverse=True)[:60]},
    ("POST", "/api/messages/<id>/handle"): lambda q, b: agents.handle_message(q["id"]),
    ("GET", "/api/stops"): lambda q, b: {"rows": sorted(store.load("stops"),
        key=lambda s: s.get("arrived_at") or "", reverse=True)[:50]},
    ("POST", "/api/stops/<id>/bill"): lambda q, b: agents.bill_stop(q["id"]),
    ("GET", "/api/stops/<id>/reading"): _reading,
    ("GET", "/api/quotes"): lambda q, b: {"rows": store.load("quotes")[:50]},
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
    serve.run(ROOT / "app", ROUTES, PORT, "Pool OS")
