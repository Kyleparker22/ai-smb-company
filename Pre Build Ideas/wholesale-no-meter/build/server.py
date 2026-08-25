#!/usr/bin/env python3
"""Counter OS — server. Stdlib only, 127.0.0.1:8893."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8893


def _executor(ap, human):
    def run():
        if ap.get("action") == "draft_stocking_case":
            c = store.by_id("cases", ap["subject"])
            if c:
                c["state"] = "approved_to_stock"
                c["decided_at"] = iso()
                store.upsert("cases", c)
        store.log_event(ap["action"] + "_done", ap["subject"], f"human:{human}", "R1",
                        {"approval": ap["id"]})
        return ap.get("subject")
    return run


def board(q, b):
    return {"config": store.load("config"),
            "board": {"nos": core.no_board(),
                      "week": core.counted_week(),
                      "watch": core.stocking_candidates(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/nos"): lambda q, b: {"rows": sorted(store.load("nos"),
        key=lambda n: n.get("at") or "", reverse=True)[:80]},
    ("POST", "/api/nos"): lambda q, b: agents.report_no(b),
    ("GET", "/api/messages"): lambda q, b: {"rows": sorted(store.load("messages"),
        key=lambda m: m.get("at") or "", reverse=True)[:60]},
    ("POST", "/api/messages/<id>/handle"): lambda q, b: agents.handle_message(q["id"]),
    ("GET", "/api/cases"): lambda q, b: {"rows": store.load("cases")},
    ("POST", "/api/cases/draft"): lambda q, b: agents.draft_stocking_case(b.get("item", "")),
    ("POST", "/api/autopsy/<sku>"): lambda q, b: agents.draft_oos_autopsy(q["sku"]),
    ("GET", "/api/vendors"): lambda q, b: {"rows": store.load("vendors")},
    ("POST", "/api/vendors/<id>/packet"): lambda q, b: agents.draft_vendor_packet(q["id"]),
    ("GET", "/api/stock"): lambda q, b: core.stock_answer(q.get("q", "")),
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
    serve.run(ROOT / "app", ROUTES, PORT, "Counter OS")
