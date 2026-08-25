#!/usr/bin/env python3
"""Close OS — server. Stdlib only, 127.0.0.1 only."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8825


def _executor(ap, human="partner"):
    def run():
        if ap["action"] in ("chase_escalate", "request_items", "chase_nudge"):
            store.log_event("chase_sent", ap["subject"], f"human:{human}", ap["rung"],
                            {"approval": ap["id"]})
        return ap["subject"]
    return run


def _num(v):
    try:
        float(v)
        return True
    except (TypeError, ValueError):
        return False


def documents(q, b):
    docs = [d for d in store.load("documents") if d.get("processed_at")]
    docs.sort(key=lambda d: d.get("processed_at") or "", reverse=True)
    counts = {"file": 0, "flag": 0, "human_queue": 0}
    for d in docs:
        counts[d.get("outcome", "human_queue")] = counts.get(d.get("outcome", "human_queue"), 0) + 1
    return {"counts": counts, "rows": docs[:60], "unprocessed": len(
        [d for d in store.load("documents") if not d.get("processed_at")]),
        "note": "a mismatch is flagged with its reason and never filed. Nothing is ever deleted — "
                "a correction is a new event and both states stay in the log"}


ROUTES = {
    ("GET", "/api/board"): lambda q, b: {"config": store.load("config"),
                                         "board": core.partner_board(),
                                         "blocker_ages": core.blocker_ages(),
                                         "pending_approvals": len(gate.pending())},
    ("GET", "/api/chase"): lambda q, b: agents.chase_state(),
    ("POST", "/api/chase/sweep"): lambda q, b: {k: v for k, v in agents.chaser().items()
                                                if k in ("touches", "bundles", "escalated")},
    ("GET", "/api/documents"): documents,
    ("POST", "/api/documents/sweep"): lambda q, b: agents.intake(),
    ("GET", "/api/scope"): lambda q, b: core.scope_ledger(),
    ("POST", "/api/message"): lambda q, b: agents.client_message(
        b.get("engagement", "en_demo"), b.get("text", "")),
    ("GET", "/api/engagements/<id>"): lambda q, b: {
        "engagement": store.by_id("engagements", q["id"]),
        "items": [i for i in store.load("open_items") if i["engagement_id"] == q["id"]]},
    ("GET", "/api/approvals"): lambda q, b: {"pending": gate.pending()},
    ("POST", "/api/approvals/<id>/decide"): lambda q, b: (
        lambda ap, h: gate.decide(q["id"], h, approve=bool(b.get("approve", True)),
                                  execute=_executor(ap, h)) if ap else {"ok": False}
    )(store.by_id("approvals", q["id"]), b.get("human", "partner")),
    ("GET", "/api/roi"): lambda q, b: core.roi({k: float(v) for k, v in (q or {}).items() if _num(v)}),
    ("GET", "/api/eval"): lambda q, b: core.eval_documents(),
    ("GET", "/api/autonomy"): lambda q, b: {"matrix": core.MATRIX.actions,
                                            "never_promote": core.MATRIX.never_promote()},
    ("GET", "/api/events"): lambda q, b: {"events": store.load("events")[-300:]},
    ("POST", "/api/agents/run"): lambda q, b: agents.run_all(),
}

if __name__ == "__main__":
    if not store.load("config"):
        print("no data yet — run:  python3 seed.py")
    serve.run(ROOT / "app", ROUTES, PORT, "Close OS")
