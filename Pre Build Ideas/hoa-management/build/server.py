#!/usr/bin/env python3
"""Reserve OS — server. Stdlib only, 127.0.0.1:8887."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8887


def _executor(ap, human):
    def run():
        store.log_event(ap["action"] + "_done", ap["subject"], f"human:{human}", "R1",
                        {"approval": ap["id"]})
        return ap["subject"]
    return run


def _assoc_summary(a):
    fb = core.funding_bands(a)
    if fb.get("unknowable"):
        state = {"state": "unknowable", "note": "no study on record — no adequacy claim"}
    else:
        hz = fb["bands"]["base"]["horizon"]
        state = {"state": "stale" if fb.get("stale") else "ok",
                 "base_horizon": hz["year"],
                 "base_horizon_note": hz["note"],
                 "bear_horizon": fb["bands"]["bear"]["horizon"]["year"],
                 "bull_horizon": fb["bands"]["bull"]["horizon"]["year"],
                 "window_years": fb["window_years"]}
    vios = [v for v in store.load("violations")
            if v.get("association_id") == a["id"] and not v.get("demo_tag")]
    return {"id": a["id"], "name": a.get("name"), "doors": a.get("doors"),
            "reserve_balance": a.get("reserve_balance"),
            "monthly_contribution": a.get("monthly_contribution"),
            "funding": state,
            "violations_open": sum(1 for v in vios if v.get("stage") != "closed")}


def board(q, b):
    assocs = store.load("associations")
    rows = [_assoc_summary(a) for a in assocs]
    states = {}
    for r in rows:
        states[r["funding"]["state"]] = states.get(r["funding"]["state"], 0) + 1
    msgs = [m for m in store.load("messages") if not m.get("handled_at")]
    vios = [v for v in store.load("violations") if not v.get("demo_tag")]
    return {"config": store.load("config"),
            "board": {"associations": rows, "funding_states": states,
                      "doors": sum(a.get("doors") or 0 for a in assocs),
                      "violations_open": sum(1 for v in vios if v.get("stage") != "closed"),
                      "messages_open": len(msgs),
                      "week": core.counted_this_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


def homeowners_for(q, b):
    return {"rows": [h for h in store.load("homeowners")
                     if h.get("association_id") == q["id"]]}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/associations"): lambda q, b: {"rows": [
        _assoc_summary(a) for a in store.load("associations")]},
    ("GET", "/api/association/<id>"): lambda q, b: core.board_view(q["id"]),
    ("GET", "/api/association/<id>/bands"): lambda q, b: core.adequacy(q["id"]),
    ("GET", "/api/association/<id>/homeowners"): homeowners_for,
    ("GET", "/api/association/<id>/homeowner/<hid>"): lambda q, b:
        core.homeowner_view(q["id"], q["hid"]),
    ("GET", "/api/association/<id>/dues-answer"): lambda q, b: {
        "draft": core.dues_answer(store.by_id("associations", q["id"]) or {},
                                  q.get("who"))},
    ("POST", "/api/association/<id>/packet"): lambda q, b: agents.draft_board_packet(q["id"]),
    ("GET", "/api/messages"): lambda q, b: {"rows": sorted(store.load("messages"),
        key=lambda m: m.get("at") or "", reverse=True)[:60]},
    ("POST", "/api/messages/<id>/handle"): lambda q, b: agents.handle_message(q["id"]),
    ("GET", "/api/violations"): lambda q, b: {"rows": sorted(
        [v for v in store.load("violations")
         if not q.get("association") or v.get("association_id") == q["association"]],
        key=lambda v: v.get("opened_at") or "", reverse=True)[:80]},
    ("POST", "/api/violations/create"): lambda q, b: core.create_violation(
        b.get("association"), b.get("unit"), b.get("section"), b.get("description", ""),
        photo_ref=b.get("photo_ref"), offense_n=b.get("offense_n", 1),
        demo_tag=b.get("demo_tag")),
    ("POST", "/api/violations/<id>/advance"): lambda q, b:
        agents.draft_violation_notice(q["id"]),
    ("POST", "/api/violations/<id>/hearing"): lambda q, b: core.hearing_decide(
        q["id"], human=b.get("human"), outcome=b.get("outcome", "upheld"),
        note=b.get("note")),
    ("POST", "/api/violations/<id>/fine"): lambda q, b:
        agents.assess_fine(q["id"], b.get("amount", 0)),
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
    serve.run(ROOT / "app", ROUTES, PORT, "Reserve OS")
