#!/usr/bin/env python3
"""Plate OS — server. Stdlib only, 127.0.0.1:8848."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso, now, parse

PORT = 8848


def _executor(ap, human):
    def run():
        store.log_event(ap["action"].replace("draft_", "") + "_done", ap["subject"],
                        f"human:{human}", "R1", {"approval": ap["id"]})
        return ap["subject"]
    return run


def board(q, b):
    from datetime import timedelta
    upcoming = sorted([e for e in store.load("bookings")
                       if not e.get("cancelled_at") and (parse(e.get("date")) or now()) >= now()],
                      key=lambda e: e.get("date") or "")
    locked = [e for e in upcoming if core.change_check(e).get("locked")]
    msgs = [m for m in store.load("messages") if not m.get("handled_at")]
    return {"config": store.load("config"),
            "board": {"upcoming": len(upcoming), "locked_window": len(locked),
                      "upcoming_top": [{"id": e["id"], "name": e.get("name"),
                                        "date": e.get("date"), "guests": e.get("guests"),
                                        "locked": core.change_check(e).get("locked")}
                                       for e in upcoming[:10]],
                      "messages_open": len(msgs), "recovered": core.recovered_this_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/messages"): lambda q, b: {"rows": sorted(store.load("messages"),
        key=lambda m: m.get("at") or "", reverse=True)[:60]},
    ("POST", "/api/messages/<id>/handle"): lambda q, b: agents.handle_message(q["id"]),
    ("GET", "/api/spaces"): lambda q, b: {"rows": store.load("spaces")},
    ("POST", "/api/book"): lambda q, b: agents.book(b.get("space_id"), b.get("date"),
                                                    int(b.get("guests", 0)), b.get("name", "demo")),
    ("POST", "/api/bookings/<id>/invoice"): lambda q, b: core.invoice(
        store.by_id("bookings", q["id"]) or {}),
    ("POST", "/api/bookings/<id>/change"): lambda q, b: core.change_check(
        store.by_id("bookings", q["id"]) or {}),
    ("GET", "/api/roi"): lambda q, b: core.roi(q),
    ("GET", "/api/eval"): lambda q, b: {"triage": core.run_eval()},
    ("GET", "/api/autonomy"): lambda q, b: {"matrix": core.matrix.actions,
                                            "never_promote": core.matrix.never_promote(),
                                            "automation": core.automation()},
    ("GET", "/api/approvals"): lambda q, b: {"pending": gate.pending()},
    ("POST", "/api/approvals/<id>/decide"): lambda q, b: gate.decide(
        q["id"], b.get("human", "director"), b.get("approve", True),
        execute=_executor(store.by_id("approvals", q["id"]) or {}, b.get("human", "director"))),
    ("GET", "/api/events"): lambda q, b: {"events": store.events()[-120:]},
    ("POST", "/api/agents/run"): lambda q, b: agents.run_all(),
}

if __name__ == "__main__":
    serve.run(ROOT / "app", ROUTES, PORT, "Plate OS")
