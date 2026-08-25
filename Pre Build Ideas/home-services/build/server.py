#!/usr/bin/env python3
"""Dispatch OS — server. Stdlib only, 127.0.0.1 only.

  GET  /api/board                    the owner's screen
  GET  /api/calls                    today's live board
  POST /api/calls/<id>/handle        run the front desk on one call
  GET  /api/estimates                aging + the recovery ladder
  GET  /api/deferred                 the seasonal re-offer campaign
  GET  /api/dispatch                 proposed board (proposals only)
  GET  /api/approvals                the R1 floor
  POST /api/approvals/<id>/decide    a human decides
  GET  /api/roi[?k=v]                the model, computed from your numbers
  GET  /api/eval                     the intake eval, emergency recall alone
  GET  /api/autonomy                 the matrix
  GET  /api/events                   the audit log
  POST /api/agents/run               run every sweep now
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso, now

PORT = 8821


def _executor(ap, human="owner"):
    """What an approved action actually does. Nothing here can run without a
    human decision row — that is the point of the gate."""
    action = ap["action"]

    def run():
        if action == "draft_estimate_touch":
            est = store.by_id("estimates", ap["subject"])
            if not est:
                return None
            for t in est.get("touches", []):
                if t.get("approval") == ap["id"]:
                    t["sent_at"] = iso()
            store.upsert("estimates", est)
            store.log_event("estimate_touch_sent", est["id"], f"human:{human}",
                            "R1", {"approval": ap["id"]})
            return est["id"]
        if action == "book_after_hours":
            call = store.by_id("calls", ap["subject"])
            if call:
                call["outcome"] = "answered"
                call["after_hours_approved"] = True
                call["handled_at"] = iso()
                store.upsert("calls", call)
            return ap["subject"]
        return ap["subject"]
    return run


def board(q, b):
    cfg = store.load("config")
    return {"config": {k: cfg.get(k) for k in ("company", "owner", "trucks", "employees",
                                               "diagnostic_fee", "after_hours_fee")},
            "at_risk": core.revenue_at_risk(),
            "recovered": core.recovered_this_week(),
            "avg_ticket": core.avg_ticket(),
            "pending_approvals": len(gate.pending())}


def calls(q, b):
    rows = [c for c in store.load("calls") if not c.get("handled_at")]
    rows.sort(key=lambda c: c["at"], reverse=True)
    custs = store.index("customers")
    out = []
    for c in rows[:40]:
        out.append(dict(c, customer=custs.get(c.get("customer_id"), {}).get("name"),
                        zone=custs.get(c.get("customer_id"), {}).get("zone"),
                        preview=core.classify(c.get("transcript", ""))))
    missed_today = [c for c in store.load("calls")
                    if c.get("outcome") == "missed"
                    and (c["at"][:10] == iso()[:10])]
    return {"live": out, "missed_today": len(missed_today)}


def handle_call(q, b):
    return agents.front_desk(q["id"])


def estimates(q, b):
    ests = store.load("estimates")
    buckets = core.aging_buckets(ests)
    live = [e for e in ests if core.estimate_state(e) == "presented"]
    live.sort(key=lambda e: e["presented_at"])
    return {"undecided": core.undecided_value(ests),
            "aging": {k: {"n": len(v), "amount": round(sum(x["amount"] for x in v), 2)}
                      for k, v in buckets.items()},
            "loss_reasons": {r: sum(1 for e in ests if e.get("loss_reason") == r)
                             for r in core.LOSS_REASONS},
            "rows": [{"id": e["id"], "customer": e["customer_name"], "scope": e["scope"],
                      "amount": e["amount"], "presented_at": e["presented_at"],
                      "tech": e.get("tech_name"), "touches": e.get("touches", []),
                      "due": [t["kind"] for t in core.due_touches(e)]} for e in live[:60]],
            "ladder": core.LADDER}


def deferred(q, b):
    c = agents.seasonal_campaign()
    parsed = agents.read_tech_notes()
    return {"campaign": c, "parsing": parsed,
            "components": core.COMPONENTS, "cooldown_days": core.REOFFER_COOLDOWN_DAYS}


def dispatch(q, b):
    return agents.propose_board()


def approvals(q, b):
    return {"pending": gate.pending(), "rung_floor": "R1"}


def decide(q, b):
    ap = store.by_id("approvals", q["id"])
    if not ap:
        return {"ok": False, "why": "no such approval"}
    human = b.get("human", "owner")
    return gate.decide(q["id"], human, approve=bool(b.get("approve", True)),
                       note=b.get("note"), execute=_executor(ap, human))


def roi(q, b):
    given = {}
    for k, v in (q or {}).items():
        try:
            given[k] = float(v)
        except (TypeError, ValueError):
            pass
    return core.roi(given)


def save_roi(q, b):
    cfg = store.load("config")
    cfg.setdefault("roi_inputs", {}).update({k: v for k, v in (b or {}).items() if v not in (None, "")})
    store.save("config", cfg)
    return core.roi()


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/calls"): calls,
    ("POST", "/api/calls/<id>/handle"): handle_call,
    ("GET", "/api/estimates"): estimates,
    ("GET", "/api/deferred"): deferred,
    ("GET", "/api/dispatch"): dispatch,
    ("GET", "/api/approvals"): approvals,
    ("POST", "/api/approvals/<id>/decide"): decide,
    ("GET", "/api/roi"): roi,
    ("POST", "/api/roi"): save_roi,
    ("GET", "/api/eval"): lambda q, b: core.eval_intake(),
    ("GET", "/api/autonomy"): lambda q, b: {"matrix": core.MATRIX.actions,
                                            "never_promote": core.MATRIX.never_promote()},
    ("GET", "/api/events"): lambda q, b: {"events": store.load("events")[-300:]},
    ("POST", "/api/agents/run"): lambda q, b: agents.run_all(),
}

if __name__ == "__main__":
    if not store.load("config"):
        print("no data yet — run:  python3 seed.py")
    serve.run(ROOT / "app", ROUTES, PORT, "Dispatch OS")
