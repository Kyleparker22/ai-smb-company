#!/usr/bin/env python3
"""Change OS — server. Stdlib only, 127.0.0.1:8831."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8831


def _executor(ap, human):
    action = ap["action"]

    def run():
        if action == "submit_co":
            co = store.by_id("cos", ap["subject"])
            if co:
                co["state"] = "submitted"
                co["submitted_at"] = iso()
                store.upsert("cos", co)
                store.log_event("submit_co_done", ap["subject"], f"human:{human}", "R1",
                                {"approval": ap["id"], "value": co.get("value")})
            return ap["subject"]
        if action == "draft_retainage_chase":
            store.log_event("retainage_chase_sent", ap["subject"], f"human:{human}", "R1",
                            {"approval": ap["id"]})
            return ap["subject"]
        return None
    return run


def board(q, b):
    ub = core.unbilled_change_value()
    ret = core.retainage_aging()
    dl = core.deadline_board()
    pending = [n for n in store.load("notes") if n.get("label") == "ambiguous"]
    return {"config": store.load("config"),
            "board": {"unbilled": ub,
                      "retainage_overdue": round(sum(r["held"] for r in ret if r["overdue"]), 2),
                      "retainage_rows": ret[:12],
                      "next_deadlines": dl["deadlines"][:8],
                      "uncomputable": dl["uncomputable"],
                      "rules_source": dl["rules_source"],
                      "ambiguous_notes": len(pending),
                      "recovered": core.recovered_this_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


def _retainage():
    rows, last_draft, last_at = [], None, ""
    for r in core.retainage_aging():
        p = store.by_id("projects", r["project_id"]) or {}
        touches = p.get("retainage_touches") or []
        r["touches"] = len(touches)
        r["escalated"] = bool(p.get("retainage_escalated"))
        if touches and touches[-1]["at"] > last_at:
            last_at, last_draft = touches[-1]["at"], touches[-1].get("body")
        rows.append(r)
    return {"rows": rows, "last_draft": last_draft}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/notes"): lambda q, b: {"rows": sorted(store.load("notes"), key=lambda n: n.get("at") or "", reverse=True)[:80]},
    ("POST", "/api/notes/<id>/classify"): lambda q, b: dict(core.classify_note((store.by_id("notes", q["id"]) or {}).get("text", "")), note=q["id"]),
    ("GET", "/api/cos"): lambda q, b: {"rows": store.load("cos"), "unbilled": core.unbilled_change_value()},
    ("POST", "/api/cos/<id>/submit"): lambda q, b: agents.submit_co(q["id"]),
    ("GET", "/api/retainage"): lambda q, b: _retainage(),
    ("GET", "/api/deadlines"): lambda q, b: core.deadline_board(),
    ("GET", "/api/invitations"): lambda q, b: {"rows": sorted(store.load("invitations"), key=lambda i: -(i.get("score") or 0))},
    ("GET", "/api/roi"): lambda q, b: core.roi(q),
    ("GET", "/api/eval"): lambda q, b: {"capture": core.run_eval()},
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
    serve.run(ROOT / "app", ROUTES, PORT, "Change OS")
