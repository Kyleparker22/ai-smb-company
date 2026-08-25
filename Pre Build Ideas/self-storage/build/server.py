#!/usr/bin/env python3
"""Gate OS — server. Stdlib only, 127.0.0.1:8843."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8843


def _executor(ap, human):
    def run():
        store.log_event(ap["action"].replace("draft_", "") + "_done", ap["subject"],
                        f"human:{human}", "R1", {"approval": ap["id"]})
        if ap["action"] == "verify_scra":
            t = store.by_id("tenants", ap["subject"])
            if t:
                t["scra_verified_at"] = iso()
                store.upsert("tenants", t)
        return ap["subject"]
    return run


def board(q, b):
    tenants = store.load("tenants")
    delinquent = [t for t in tenants if t.get("delinquent_since") and not t.get("demo_tag")]
    frozen = [t for t in delinquent if not core.can_lien_step(t)[0]]
    msgs = [m for m in store.load("messages") if not m.get("handled_at")]
    return {"config": store.load("config"),
            "board": {"delinquent": len(delinquent),
                      "delinquent_total": round(sum(t.get("balance", 0) for t in delinquent), 2),
                      "lien_frozen": len(frozen),
                      "occupancy": core.occupancy(), "messages_open": len(msgs),
                      "recovered": core.recovered_this_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/messages"): lambda q, b: {"rows": sorted(store.load("messages"),
        key=lambda m: m.get("at") or "", reverse=True)[:60]},
    ("POST", "/api/messages/<id>/handle"): lambda q, b: agents.handle_message(q["id"]),
    ("GET", "/api/delinquent"): lambda q, b: {"rows": [
        {"tenant": t["id"], "name": t.get("name"), "unit": t.get("unit"),
         "balance": t.get("balance"), "since": t.get("delinquent_since"),
         "military": bool(t.get("military_flag")),
         "scra_verified": bool(t.get("scra_verified_at")),
         "touches": len(t.get("dunning_touches") or []),
         "lien_ok": core.can_lien_step(t)[0]}
        for t in store.load("tenants") if t.get("delinquent_since")][:60]},
    ("POST", "/api/tenants/<id>/lien"): lambda q, b: agents.lien_step(q["id"]),
    ("GET", "/api/occupancy"): lambda q, b: {"rows": core.occupancy()},
    ("GET", "/api/roi"): lambda q, b: core.roi(q),
    ("GET", "/api/eval"): lambda q, b: {"triage": core.run_eval()},
    ("GET", "/api/autonomy"): lambda q, b: {"matrix": core.matrix.actions,
                                            "never_promote": core.matrix.never_promote(),
                                            "automation": core.automation()},
    ("GET", "/api/approvals"): lambda q, b: {"pending": gate.pending()},
    ("POST", "/api/approvals/<id>/decide"): lambda q, b: gate.decide(
        q["id"], b.get("human", "manager"), b.get("approve", True),
        execute=_executor(store.by_id("approvals", q["id"]) or {}, b.get("human", "manager"))),
    ("GET", "/api/events"): lambda q, b: {"events": store.events()[-120:]},
    ("POST", "/api/agents/run"): lambda q, b: agents.run_all(),
}

if __name__ == "__main__":
    serve.run(ROOT / "app", ROUTES, PORT, "Gate OS")
