#!/usr/bin/env python3
"""Lot OS — server. Stdlib only, 127.0.0.1:8861."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8861


def _executor(ap, human):
    def run():
        if ap["action"] == "mark_delivered":
            d = store.by_id("deals", ap["subject"])
            if d:
                d["delivered_at"] = iso()
                store.upsert("deals", d)
        store.log_event(ap["action"] + "_done", ap["subject"], f"human:{human}", "R1",
                        {"approval": ap["id"]})
        return ap["subject"]
    return run


def board(q, b):
    aged = core.aged_board()
    leads_open = [l for l in store.load("leads") if not l.get("handled_at")]
    return {"config": store.load("config"),
            "board": {"aged": aged[:10],
                      "aged_interest": round(sum(r.get("interest_accrued", 0) for r in aged), 2),
                      "units_90plus": len([r for r in aged if r.get("bucket") == "90+"]),
                      "leads_open": len(leads_open),
                      "recovered": core.recovered_this_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/leads"): lambda q, b: {"rows": sorted(store.load("leads"),
        key=lambda m: m.get("at") or "", reverse=True)[:60]},
    ("POST", "/api/leads/<id>/handle"): lambda q, b: agents.handle_message(q["id"]),
    ("GET", "/api/units"): lambda q, b: {"rows": core.aged_board()[:40]},
    ("POST", "/api/deals/<id>/deliver"): lambda q, b: agents.mark_delivered(q["id"]),
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
    serve.run(ROOT / "app", ROUTES, PORT, "Lot OS")
