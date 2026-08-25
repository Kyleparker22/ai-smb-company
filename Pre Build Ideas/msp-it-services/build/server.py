#!/usr/bin/env python3
"""Queue OS — server. Stdlib only, 127.0.0.1:8834."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8834


def _executor(ap, human):
    def run():
        store.log_event(ap["action"].replace("draft_", "") + "_sent", ap["subject"],
                        f"human:{human}", "R1", {"approval": ap["id"]})
        return ap["subject"]
    return run


def board(q, b):
    sla = core.sla_board()
    sec_open = [t for t in store.load("tickets")
                if t.get("label") == "security" and not t.get("resolved_at") and not t.get("demo_tag")]
    oos = [f for f in store.load("scope_findings") if f.get("verdict") == "out_of_scope"]
    amb = [f for f in store.load("scope_findings") if f.get("verdict") == "ambiguous"]
    return {"config": store.load("config"),
            "board": {"sla_breached": sla["breached"], "sla_unknowable": len(sla["unknowable"]),
                      "security_open": len(sec_open), "oos": len(oos), "ambiguous": len(amb),
                      "sla_top": sla["rows"][:10], "recovered": core.recovered_this_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/tickets"): lambda q, b: {"rows": sorted(store.load("tickets"),
        key=lambda t: (t.get("label") != "security", t.get("opened_at") or ""), )[:80]},
    ("POST", "/api/tickets/<id>/triage"): lambda q, b: dict(
        core.triage((store.by_id("tickets", q["id"]) or {}).get("text", "")), ticket=q["id"]),
    ("POST", "/api/tickets/<id>/close"): lambda q, b: agents.close_ticket(q["id"], human=b.get("human")),
    ("POST", "/api/tickets/<id>/scope"): lambda q, b: dict(
        core.scope_check(store.by_id("tickets", q["id"]) or {}), ticket=q["id"]),
    ("GET", "/api/sla"): lambda q, b: core.sla_board(),
    ("GET", "/api/scope"): lambda q, b: {"rows": store.load("scope_findings")[-60:]},
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
    serve.run(ROOT / "app", ROUTES, PORT, "Queue OS")
