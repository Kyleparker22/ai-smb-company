#!/usr/bin/env python3
"""Code OS — server. Stdlib only, 127.0.0.1:8855."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8855


def _executor(ap, human):
    def run():
        store.log_event(ap["action"] + "_done", ap["subject"], f"human:{human}", "R1",
                        {"approval": ap["id"]})
        return ap["subject"]
    return run


def board(q, b):
    sb = core.site_board()
    msgs = [m for m in store.load("messages") if not m.get("handled_at")]
    impairments = [m for m in store.load("messages") if m.get("label") == "impairment"]
    open_d = [f for f in store.load("deficiencies")
              if not f.get("repaired_at") and not f.get("declined_at") and not f.get("demo_tag")]
    return {"config": store.load("config"),
            "board": {"sites": len(sb), "sites_top": sb[:10],
                      "overdue": sum(r["overdue"] for r in sb),
                      "unknown": sum(r["unknown"] for r in sb),
                      "impairments": len(impairments),
                      "open_deficiencies": len(open_d),
                      "open_deficiency_value": round(sum(f.get("quote", 0) for f in open_d), 2),
                      "messages_open": len(msgs),
                      "recovered": core.recovered_this_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/messages"): lambda q, b: {"rows": sorted(store.load("messages"),
        key=lambda m: m.get("at") or "", reverse=True)[:60]},
    ("POST", "/api/messages/<id>/handle"): lambda q, b: agents.handle_message(q["id"]),
    ("GET", "/api/sites"): lambda q, b: {"rows": core.site_board()[:40]},
    ("POST", "/api/devices/<id>/mark"): lambda q, b: agents.mark_device(
        q["id"], human=b.get("human"), result=b.get("result")),
    ("GET", "/api/deficiencies"): lambda q, b: {"rows": store.load("deficiencies")[:50]},
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
    serve.run(ROOT / "app", ROUTES, PORT, "Code OS")
