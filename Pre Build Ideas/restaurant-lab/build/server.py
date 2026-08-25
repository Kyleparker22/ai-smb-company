#!/usr/bin/env python3
"""Lab OS — server. Stdlib only, 127.0.0.1:8889."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8889


def _executor(ap, human):
    def run():
        if ap.get("action") == "draft_rollout_recommendation":
            e = store.by_id("experiments", ap.get("subject"))
            if e:
                e["rollout_approved_at"] = iso()
                store.upsert("experiments", e)
        store.log_event(str(ap.get("action")) + "_done", ap.get("subject"),
                        f"human:{human}", "R1", {"approval": ap.get("id")})
        return ap.get("subject")
    return run


def board(q, b):
    exps = store.load("experiments")
    live = [e for e in exps if e.get("status") == "live"]
    too_early = [e for e in live
                 if str(core.verdict(e).get("verdict", "")).startswith("TOO EARLY")]
    msgs = [m for m in store.load("messages") if not m.get("handled_at")]
    return {"config": store.load("config"),
            "board": {"experiments_live": len(live), "too_early": len(too_early),
                      "experiments_concluded": len([e for e in exps
                                                    if e.get("status") == "concluded"]),
                      "eightysix_week": core.eightysix_counted(7),
                      "messages_open": len(msgs),
                      "week": core.week_counted(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


def experiments_view(q, b):
    units = {u["id"]: u["name"] for u in store.load("units")}
    rows = []
    for e in sorted(store.load("experiments"),
                    key=lambda x: x.get("started_at") or "", reverse=True):
        cur = e.get("verdict") if e.get("status") == "concluded" else core.verdict(e)
        arms = (" + ".join(units.get(u, u) for u in e.get("treatment_units") or [])
                + "  vs  "
                + " + ".join(units.get(u, u) for u in e.get("control_units") or []))
        rows.append({**e, "arms": arms, "current": cur})
    return {"rows": rows, "floors_source": core.sample_floors()["_source"]}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/messages"): lambda q, b: {"rows": sorted(store.load("messages"),
        key=lambda m: m.get("at") or "", reverse=True)[:60]},
    ("POST", "/api/messages/<id>/handle"): lambda q, b: agents.handle_message(q["id"]),
    ("GET", "/api/experiments"): experiments_view,
    ("POST", "/api/experiments/create"): lambda q, b: core.create_experiment(
        b.get("hypothesis", ""), b.get("metric", ""),
        b.get("treatment_units") or [], b.get("control_units") or [],
        item=b.get("item")),
    ("GET", "/api/experiments/<id>/verdict"): lambda q, b: core.verdict(q["id"]),
    ("POST", "/api/experiments/<id>/conclude"): lambda q, b: core.conclude(
        q["id"], b.get("human", "owner")),
    ("POST", "/api/experiments/<id>/rollout"): lambda q, b: core.rollout(q["id"]),
    ("GET", "/api/ledger"): lambda q, b: core.ledger_board(),
    ("GET", "/api/stockouts/<id>/price"): lambda q, b: (
        lambda s: {"error": "no such stockout"} if not s
        else {**s, "unit": core._unit_name(s.get("unit_id")), **core.price_stockout(s)}
    )(store.by_id("stockouts", q["id"])),
    ("GET", "/api/graveyard"): lambda q, b: {"rows": store.load("graveyard")},
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
    serve.run(ROOT / "app", ROUTES, PORT, "Lab OS")
