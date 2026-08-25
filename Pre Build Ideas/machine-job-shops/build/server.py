#!/usr/bin/env python3
"""Traveler OS — server. Stdlib only, 127.0.0.1:8849."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8849


def _executor(ap, human):
    def run():
        store.log_event(ap["action"].replace("draft_", "") + "_done", ap["subject"],
                        f"human:{human}", "R1", {"approval": ap["id"]})
        if ap["action"] == "release_to_ship":
            j = store.by_id("jobs", ap["subject"])
            if j:
                j["shipped_at"] = iso()
                store.upsert("jobs", j)
        return ap["subject"]
    return run


def board(q, b):
    o = core.otd()
    cert_blocked = [j for j in store.load("jobs")
                    if j.get("cert_required") and not j.get("shipped_at")
                    and not core.can_ship(j)[0] and not j.get("demo_tag")]
    rfqs_open = [r for r in store.load("rfqs") if not r.get("scanned_at")]
    p = core.promise_date(0)
    return {"config": store.load("config"),
            "board": {"otd": o, "cert_blocked": len(cert_blocked),
                      "rfqs_open": len(rfqs_open),
                      "backlog_weeks": p.get("weeks_out"),
                      "recovered": core.recovered_this_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/rfqs"): lambda q, b: {"rows": sorted(store.load("rfqs"),
        key=lambda r: r.get("at") or "", reverse=True)[:40]},
    ("POST", "/api/rfqs/<id>/handle"): lambda q, b: agents.handle_rfq(q["id"]),
    ("GET", "/api/jobs"): lambda q, b: {"rows": [
        dict(j, ship_check=core.can_ship(j)[1], can_ship=core.can_ship(j)[0])
        for j in store.load("jobs") if not j.get("shipped_at")][:40]},
    ("POST", "/api/jobs/<id>/ship"): lambda q, b: agents.ship_job(q["id"]),
    ("POST", "/api/jobs/<id>/promise"): lambda q, b: agents.promise(q["id"]),
    ("GET", "/api/materials"): lambda q, b: {"rows": [
        dict(m, check=core.material_check(m["id"])) for m in store.load("materials")]},
    ("GET", "/api/roi"): lambda q, b: core.roi(q),
    ("GET", "/api/eval"): lambda q, b: {"flags": core.run_eval()},
    ("GET", "/api/autonomy"): lambda q, b: {"matrix": core.matrix.actions,
                                            "never_promote": core.matrix.never_promote(),
                                            "automation": core.automation()},
    ("GET", "/api/approvals"): lambda q, b: {"pending": gate.pending()},
    ("POST", "/api/approvals/<id>/decide"): lambda q, b: gate.decide(
        q["id"], b.get("human", "gm"), b.get("approve", True),
        execute=_executor(store.by_id("approvals", q["id"]) or {}, b.get("human", "gm"))),
    ("GET", "/api/events"): lambda q, b: {"events": store.events()[-120:]},
    ("POST", "/api/agents/run"): lambda q, b: agents.run_all(),
}

if __name__ == "__main__":
    serve.run(ROOT / "app", ROUTES, PORT, "Traveler OS")
