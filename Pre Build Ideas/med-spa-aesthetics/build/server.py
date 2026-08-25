#!/usr/bin/env python3
"""Consult OS — server. Stdlib only, 127.0.0.1 only."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8822


def _executor(ap, human="frontdesk"):
    def run():
        if ap["action"] == "draft_decision_touch":
            p = store.by_id("plans", ap["subject"])
            if p:
                for t in p.get("touches", []):
                    if t.get("approval") == ap["id"]:
                        t["sent_at"] = iso()
                store.upsert("plans", p)
                store.log_event("decision_touch_sent", p["id"], f"human:{human}", "R1",
                                {"approval": ap["id"]})
            return ap["subject"]
        return ap["subject"]
    return run


ROUTES = {
    ("GET", "/api/board"): lambda q, b: {
        "config": {k: store.load("config").get(k) for k in ("practice", "locations", "owner", "consult_fee")},
        "board": core.board(), "pending_approvals": len(gate.pending())},
    ("GET", "/api/inquiries"): lambda q, b: {
        "live": [dict(i, read=core.qualify(i.get("text", "")))
                 for i in sorted([x for x in store.load("inquiries") if not x.get("first_response_at")],
                                 key=lambda x: x["at"], reverse=True)[:40]],
        "latency": core.latency_read(store.load("inquiries"))},
    ("POST", "/api/inquiries/<id>/answer"): lambda q, b: agents.concierge(q["id"]),
    ("GET", "/api/consults"): lambda q, b: {
        "upcoming": [c for c in store.load("consults") if c.get("state") == "booked"][:40],
        "no_show_rate": core.no_show_rate(store.load("consults")),
        "ladder": core.SHOWUP_LADDER},
    ("POST", "/api/consults/<id>/cancel"): lambda q, b: agents.refill_cancellation(q["id"]),
    ("GET", "/api/plans"): lambda q, b: {
        "undecided": core.undecided_value(store.load("plans")),
        "ladder": core.DECISION_LADDER,
        "rows": [{"id": p["id"], "patient": p["patient_name"], "amount": p["amount"],
                  "summary": p["summary"], "provider": p.get("provider"),
                  "objection": p.get("objection"), "presented_at": p["presented_at"],
                  "touches": p.get("touches", []), "due": [t["kind"] for t in core.due_decision(p)]}
                 for p in store.load("plans") if core.plan_state(p) == "presented"][:60],
        "decline_reasons": {r: sum(1 for p in store.load("plans") if p.get("decline_reason") == r)
                            for r in core.DECLINE_REASONS}},
    ("GET", "/api/cadence"): lambda q, b: agents.cadence_engine(),
    ("GET", "/api/funnel"): lambda q, b: core.funnel(),
    ("GET", "/api/approvals"): lambda q, b: {"pending": gate.pending()},
    ("POST", "/api/approvals/<id>/decide"): lambda q, b: (
        lambda ap, human: gate.decide(q["id"], human, approve=bool(b.get("approve", True)),
                                      execute=_executor(ap, human)) if ap else {"ok": False}
    )(store.by_id("approvals", q["id"]), b.get("human", "frontdesk")),
    ("GET", "/api/roi"): lambda q, b: core.roi({k: float(v) for k, v in (q or {}).items()
                                                if _num(v)}),
    ("GET", "/api/eval"): lambda q, b: {"clinical": core.eval_clinical(),
                                        "urgent": core.urgent_recall_check()},
    ("GET", "/api/autonomy"): lambda q, b: {"matrix": core.MATRIX.actions,
                                            "never_promote": core.MATRIX.never_promote()},
    ("GET", "/api/events"): lambda q, b: {"events": store.load("events")[-300:]},
    ("POST", "/api/agents/run"): lambda q, b: agents.run_all(),
}


def _num(v):
    try:
        float(v)
        return True
    except (TypeError, ValueError):
        return False


if __name__ == "__main__":
    if not store.load("config"):
        print("no data yet — run:  python3 seed.py")
    serve.run(ROOT / "app", ROUTES, PORT, "Consult OS")
