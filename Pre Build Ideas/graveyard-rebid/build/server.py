#!/usr/bin/env python3
"""Rebid OS — server. Stdlib only, 127.0.0.1:8888."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import is_missing

PORT = 8888


def _executor(ap, human):
    def run():
        store.log_event(ap["action"] + "_done", ap["subject"], f"human:{human}", "R1",
                        {"approval": ap["id"]})
        return ap["subject"]
    return run


def board(q, b):
    gb = core.graveyard_board()
    cap = core.capacity_board()
    counted = [r for r in cap["rows"] if not r.get("idle")]
    unmeasured_classes = sorted({r["machine_class"] for r in cap["rows"] if r.get("idle")})
    msgs = [m for m in store.load("messages") if not m.get("handled_at")]
    return {"config": store.load("config"),
            "board": {"graveyard": gb,
                      "idle_counted": round(sum(r["idle_hours"] for r in counted), 1),
                      "idle_held": round(sum(r.get("held_hours") or 0 for r in counted), 1),
                      "unmeasured_classes": unmeasured_classes,
                      "messages_open": len(msgs),
                      "week_counted": core.this_week_counted(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


def graveyard(q, b):
    rows = store.load("graveyard")
    rows.sort(key=lambda r: (not r.get("demo_tag"), r.get("lost_at") or ""), reverse=False)
    demo = [r for r in rows if r.get("demo_tag")]
    rest = sorted([r for r in rows if not r.get("demo_tag")],
                  key=lambda r: r.get("lost_at") or "", reverse=True)
    out = []
    for r in (demo + rest)[:48]:
        row = dict(r)
        row["status"] = core.quote_status(r)
        out.append(row)
    return {"board": core.graveyard_board(), "rows": out}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/graveyard"): graveyard,
    ("GET", "/api/graveyard/<id>/floor"): lambda q, b: core.floor_math(
        store.by_id("graveyard", q["id"]) or {}),
    ("POST", "/api/graveyard/<id>/rebid"): lambda q, b: agents.rebid(q["id"]),
    ("POST", "/api/graveyard/<id>/propose"): lambda q, b: agents.propose_bid(
        q["id"], b.get("price")),
    ("POST", "/api/graveyard"): lambda q, b: agents.record_loss(b),
    ("GET", "/api/capacity"): lambda q, b: core.capacity_board(),
    ("GET", "/api/messages"): lambda q, b: {"rows": sorted(store.load("messages"),
        key=lambda m: m.get("at") or "", reverse=True)[:60]},
    ("POST", "/api/messages/<id>/handle"): lambda q, b: agents.handle_message(q["id"]),
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
    serve.run(ROOT / "app", ROUTES, PORT, "Rebid OS")
