#!/usr/bin/env python3
"""Rehearsal OS — server. Stdlib only, 127.0.0.1:8885."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve

PORT = 8885


def _executor(ap, human):
    def run():
        if ap.get("action") == "record_endorsement":
            d = ap.get("detail") or {}
            agents.apply_endorsement(ap["subject"], d.get("kind"), d.get("key"), human)
        return ap.get("subject")
    return run


def board(q, b):
    cfg = store.load("config")
    radar = core.renewal_radar()
    accounts = store.load("accounts")
    unread = sum(1 for a in accounts if not a.get("policy_recorded"))
    msgs = [m for m in store.load("messages") if not m.get("handled_at")]
    return {"config": {"agency": cfg.get("agency"), "producers": cfg.get("producers"),
                       "csrs": cfg.get("csrs")},
            "board": {"accounts": len(accounts), "unread_policies": unread,
                      "renewals_60": len(radar["rows"]),
                      "renewals_not_rehearsed": radar["not_rehearsed"],
                      "renewals_unreadable": radar["unreadable"],
                      "gaps": core.gap_ledger(),
                      "week": core.counted_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


def rehearse(q, b):
    if q.get("severity") or (b or {}).get("severity"):
        return agents.refuse_single_number(q["id"], q.get("severity") or b.get("severity"))
    return agents.rehearse_account(q["id"])


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/renewals"): lambda q, b: core.renewal_radar(),
    ("GET", "/api/accounts/<id>"): lambda q, b: store.by_id("accounts", q["id"])
    or {"error": "no such account"},
    ("POST", "/api/accounts/<id>/rehearse"): rehearse,
    ("POST", "/api/accounts/<id>/fixsheet"): lambda q, b: agents.draft_fix_sheet(q["id"]),
    ("POST", "/api/accounts/<id>/packet"): lambda q, b: agents.draft_renewal_packet(q["id"]),
    ("POST", "/api/accounts/<id>/endorse"): lambda q, b: agents.record_endorsement(
        q["id"], (b or {}).get("kind", "exclusion"), (b or {}).get("key")),
    ("GET", "/api/messages"): lambda q, b: {"rows": sorted(store.load("messages"),
        key=lambda m: m.get("at") or "", reverse=True)[:60]},
    ("POST", "/api/messages/<id>/handle"): lambda q, b: agents.handle_message(q["id"]),
    ("POST", "/api/probe/<kind>"): lambda q, b: agents.check_client_draft(
        (store.load("config").get("demo_probes") or {}).get(q["kind"], ""),
        subject=f"probe:{q['kind']}"),
    ("GET", "/api/roi"): lambda q, b: core.roi(q),
    ("GET", "/api/eval"): lambda q, b: {"triage": core.run_eval()},
    ("GET", "/api/autonomy"): lambda q, b: {"matrix": core.matrix.actions,
                                            "never_promote": core.matrix.never_promote(),
                                            "automation": core.automation()},
    ("GET", "/api/approvals"): lambda q, b: {"pending": gate.pending()},
    ("POST", "/api/approvals/<id>/decide"): lambda q, b: gate.decide(
        q["id"], b.get("human", "principal"), b.get("approve", True),
        execute=_executor(store.by_id("approvals", q["id"]) or {},
                          b.get("human", "principal"))),
    ("GET", "/api/events"): lambda q, b: {"events": store.events()[-120:]},
    ("POST", "/api/agents/run"): lambda q, b: agents.run_all(),
}

if __name__ == "__main__":
    serve.run(ROOT / "app", ROUTES, PORT, "Rehearsal OS")
