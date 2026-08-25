#!/usr/bin/env python3
"""Quote Desk OS — server. Stdlib only, 127.0.0.1 only."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8828


def _executor(ap, human="desk"):
    def run():
        if ap["action"] == "send_quote":
            q = store.by_id("quotes", ap["subject"])
            if q:
                q["state"] = "sent"
                q["sent_at"] = iso()
                store.upsert("quotes", q)
                store.log_event("quote_sent", q["id"], f"human:{human}", "R1",
                                {"approval": ap["id"]})
        return ap["subject"]
    return run


def _num(v):
    try:
        float(v)
        return True
    except (TypeError, ValueError):
        return False


def desk(q, b):
    quotes = sorted(store.load("quotes"), key=lambda x: x.get("created_at") or "", reverse=True)
    live = [x for x in quotes if x.get("state") in ("draft", "queued_for_human", "awaiting_approval")]
    return {"board": core.desk_board(), "config": store.load("config"),
            "live": live[:40], "pending_approvals": len(gate.pending())}


ROUTES = {
    ("GET", "/api/desk"): desk,
    ("GET", "/api/rfqs"): lambda q, b: {
        "live": [r for r in store.load("rfqs") if not r.get("quoted_at")][:20]},
    ("POST", "/api/rfqs/<id>/quote"): lambda q, b: agents.build_quote(q["id"]),
    ("GET", "/api/pos"): lambda q, b: {
        "rows": [p for p in store.load("pos") if p.get("processed_at") or p.get("demo_tag")][:40],
        "exceptions": [p for p in store.load("pos") if p.get("verdict") == "exception"][:30]},
    ("POST", "/api/pos/<id>/ingest"): lambda q, b: agents.ingest_po(q["id"]),
    ("GET", "/api/ledger"): lambda q, b: core.margin_ledger(),
    ("GET", "/api/approvals"): lambda q, b: {"pending": gate.pending()},
    ("POST", "/api/approvals/<id>/decide"): lambda q, b: (
        lambda ap, h: gate.decide(q["id"], h, approve=bool(b.get("approve", True)),
                                  execute=_executor(ap, h)) if ap else {"ok": False}
    )(store.by_id("approvals", q["id"]), b.get("human", "desk")),
    ("GET", "/api/roi"): lambda q, b: core.roi({k: float(v) for k, v in (q or {}).items() if _num(v)}),
    ("GET", "/api/eval"): lambda q, b: core.eval_matching(),
    ("GET", "/api/autonomy"): lambda q, b: {"matrix": core.MATRIX.actions,
                                            "never_promote": core.MATRIX.never_promote()},
    ("GET", "/api/events"): lambda q, b: {"events": store.load("events")[-300:]},
    ("POST", "/api/agents/run"): lambda q, b: agents.run_all(),
}

if __name__ == "__main__":
    if not store.load("config"):
        print("no data yet — run:  python3 seed.py")
    serve.run(ROOT / "app", ROUTES, PORT, "Quote Desk OS")
