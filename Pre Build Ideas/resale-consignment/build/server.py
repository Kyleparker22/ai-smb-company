#!/usr/bin/env python3
"""Consign OS — server. Stdlib only, 127.0.0.1:8870."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8870


def _executor(ap, human):
    def run():
        if ap["action"] == "draft_payout":
            pass  # the pay run itself lives outside the demo
        if ap["action"] == "publish_listing":
            it = store.by_id("items", ap["subject"])
            if it and it.get("status") == "intake":
                it["status"] = "listed"
                it["listed_at"] = iso()
                store.upsert("items", it)
        store.log_event(ap["action"] + "_done", ap["subject"], f"human:{human}", "R1",
                        {"approval": ap["id"]})
        return ap["subject"]
    return run


def board(q, b):
    fb = core.floor_board()
    msgs = [m for m in store.load("messages") if not m.get("handled_at")]
    return {"config": store.load("config"),
            "board": {"unlisted": fb["unlisted_count"], "aged": len(fb["aged"]),
                      "owed_total": fb["owed_total"], "owed_unpayable": fb["owed_unpayable"],
                      "messages_open": len(msgs),
                      "recovered": core.recovered_this_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/floor"): lambda q, b: core.floor_board(),
    ("GET", "/api/messages"): lambda q, b: {"rows": sorted(store.load("messages"),
        key=lambda m: m.get("at") or "", reverse=True)[:60]},
    ("POST", "/api/messages/<id>/handle"): lambda q, b: agents.handle_message(q["id"]),
    ("POST", "/api/items/<id>/list"): lambda q, b: agents.list_item(q["id"]),
    ("POST", "/api/items/<id>/donate"): lambda q, b: agents.donate(q["id"], human=b.get("human")),
    ("GET", "/api/items/<id>/payout"): lambda q, b: core.payout_math(
        store.by_id("items", q["id"]) or {}),
    ("GET", "/api/items/<id>/brand"): lambda q, b: core.brand_line(
        store.by_id("items", q["id"]) or {}),
    ("GET", "/api/roi"): lambda q, b: core.roi(q),
    ("GET", "/api/eval"): lambda q, b: {"triage": core.run_eval()},
    ("GET", "/api/autonomy"): lambda q, b: {"matrix": core.matrix.actions,
                                            "never_promote": core.matrix.never_promote(),
                                            "automation": core.automation(),
                                            "channels": list(core.CHANNELS)},
    ("GET", "/api/approvals"): lambda q, b: {"pending": gate.pending()},
    ("POST", "/api/approvals/<id>/decide"): lambda q, b: gate.decide(
        q["id"], b.get("human", "owner"), b.get("approve", True),
        execute=_executor(store.by_id("approvals", q["id"]) or {}, b.get("human", "owner"))),
    ("GET", "/api/events"): lambda q, b: {"events": store.events()[-120:]},
    ("POST", "/api/agents/run"): lambda q, b: agents.run_all(),
}

if __name__ == "__main__":
    serve.run(ROOT / "app", ROUTES, PORT, "Consign OS")
