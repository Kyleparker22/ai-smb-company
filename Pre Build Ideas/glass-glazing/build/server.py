#!/usr/bin/env python3
"""Pane OS — server. Stdlib only, 127.0.0.1:8879."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8879


def _executor(ap, human):
    def run():
        if ap.get("action") == "release_to_fabricator":
            o = store.by_id("orders", ap["subject"])
            if o:
                o["released_at"] = iso()
                o["stage"] = "fabrication"
                store.upsert("orders", o)
        store.log_event(ap["action"] + "_done", ap["subject"], f"human:{human}", "R1",
                        {"approval": ap["id"]})
        return ap["subject"]
    return run


def board(q, b):
    p = core.pipeline()
    msgs = [m for m in store.load("messages") if not m.get("handled_at")]
    return {"config": store.load("config"),
            "board": {"pipeline": p,
                      "deposits": core.deposits_uncollected(),
                      "remake_rate": core.remake_rate(),
                      "messages_open": len(msgs),
                      "recovered": core.recovered_this_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


def orders_rows(q, b):
    rows = []
    tol = core.tolerance()["inches"]
    for o in store.load("orders"):
        ms = o.get("measurements") or []
        state = "none"
        if len(ms) == 1:
            state = "single"
        elif len(ms) >= 2:
            a, b2 = ms[0], ms[1]
            state = "mismatched" if (abs(a["width_in"] - b2["width_in"]) > tol
                                     or abs(a["height_in"] - b2["height_in"]) > tol) else "matched"
        rows.append({"id": o["id"], "customer": o.get("customer_name"),
                     "job_type": o.get("job_type"), "stage": o.get("stage"),
                     "amount": o.get("amount", 0), "measurements": state,
                     "deposit": bool(o.get("deposit_paid_at")),
                     "fab_date": o.get("fabricator_promised_at"),
                     "demo_tag": o.get("demo_tag")})
    order_rank = {"deposit": 0, "fabrication": 1, "install": 2, "quote": 3, "done": 4}
    rows.sort(key=lambda r: (order_rank.get(r["stage"], 9), r["id"]))
    return {"rows": rows[:60], "tolerance_in": tol}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/messages"): lambda q, b: {"rows": sorted(store.load("messages"),
        key=lambda m: m.get("at") or "", reverse=True)[:60]},
    ("POST", "/api/messages/<id>/handle"): lambda q, b: agents.handle_message(q["id"]),
    ("GET", "/api/orders"): orders_rows,
    ("POST", "/api/orders/<id>/release"): lambda q, b: agents.release_order(q["id"]),
    ("GET", "/api/orders/<id>/leadtime"): lambda q, b: agents.answer_lead_time(q["id"]),
    ("POST", "/api/quotes/check"): lambda q, b: agents.check_quote(
        b.get("location"), b.get("glass_type")),
    ("GET", "/api/remakes"): lambda q, b: {"rate": core.remake_rate(),
                                           "rows": store.load("remakes")[:40]},
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
    serve.run(ROOT / "app", ROUTES, PORT, "Pane OS")
