#!/usr/bin/env python3
"""Marquee OS — server. Stdlib only, 127.0.0.1:8875."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8875


def _executor(ap, human):
    def run():
        if ap.get("action") in ("draft_deposit_refund", "draft_deposit_deduction"):
            b = store.by_id("bookings", ap["subject"])
            if b:
                b["deposit_settled_at"] = iso()
                store.upsert("bookings", b)
        store.log_event(ap["action"] + "_done", ap["subject"], f"human:{human}", "R1",
                        {"approval": ap["id"]})
        return ap["subject"]
    return run


def board(q, b):
    cb = core.capacity_board()
    pb = core.permit_board()
    msgs = [m for m in store.load("messages") if not m.get("handled_at")]
    flags = sum(1 for bk in store.load("bookings")
                if bk.get("status") == "confirmed"
                and core.wind_check(bk).get("flag"))
    due = sum(1 for r in pb["rows"] if r.get("permit") == "NOT FILED")
    return {"config": store.load("config"),
            "board": {"weekends": cb["weekends"], "capacity_note": cb["note"],
                      "wind_flags": flags, "permits_unfiled": due,
                      "messages_open": len(msgs),
                      "recovered": core.recovered_this_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


def wind(q, b):
    bk = store.by_id("bookings", q["id"])
    if not bk:
        return {"error": "no such booking"}
    return {"booking": q["id"], "customer": bk.get("customer_name"),
            "event_date": bk.get("event_date"), "wind": core.wind_check(bk),
            "weather_call": bk.get("weather_call")}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/messages"): lambda q, b: {"rows": sorted(store.load("messages"),
        key=lambda m: m.get("at") or "", reverse=True)[:60]},
    ("POST", "/api/messages/<id>/handle"): lambda q, b: agents.handle_message(q["id"]),
    ("GET", "/api/capacity"): lambda q, b: core.capacity_board(),
    ("GET", "/api/availability"): lambda q, b: {"date": q.get("date"),
                                                "items": core.availability(q.get("date"))},
    ("POST", "/api/bookings/reserve"): lambda q, b: core.reserve(
        b.get("customer", "walk-in"), b.get("event_date"), b.get("items") or {},
        site=b.get("site"), municipality=b.get("municipality"),
        deposit=b.get("deposit"), demo_tag=b.get("demo_tag")),
    ("GET", "/api/bookings"): lambda q, b: {"rows": sorted(store.load("bookings"),
        key=lambda x: x.get("event_date") or "")[:80]},
    ("GET", "/api/bookings/<id>/wind"): wind,
    ("POST", "/api/bookings/<id>/weather-call"): lambda q, b: core.weather_call(
        q["id"], human=b.get("human"), decision=b.get("decision"), note=b.get("note")),
    ("POST", "/api/bookings/<id>/install"): lambda q, b: agents.install(
        q["id"], human=b.get("human")),
    ("POST", "/api/bookings/<id>/deposit"): lambda q, b: agents.settle_deposit(q["id"]),
    ("GET", "/api/permits"): lambda q, b: core.permit_board(),
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
    serve.run(ROOT / "app", ROUTES, PORT, "Marquee OS")
