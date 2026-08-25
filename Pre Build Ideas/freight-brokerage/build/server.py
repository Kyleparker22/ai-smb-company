#!/usr/bin/env python3
"""Carrier OS — server. Stdlib only, 127.0.0.1 only."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8827


def _executor(ap, human="ops"):
    def run():
        if ap["action"] == "approve_carrier":
            # Approving vetting is NOT releasing the load. Two separate human
            # decisions, on purpose.
            store.log_event("carrier_approved", ap["subject"], f"human:{human}", "R1",
                            {"approval": ap["id"]})
        return ap["subject"]
    return run


def _num(v):
    try:
        float(v)
        return True
    except (TypeError, ValueError):
        return False


def release(q, b):
    """Load release is its own human act, gated separately from carrier approval."""
    load = store.by_id("loads", q["id"])
    if not load:
        return {"error": "no such load"}
    res = gate.act("release_load", "ops", q["id"],
                   {"summary": f"release {q['id']} to {b.get('carrier')}"})
    return {"queued": res, "note": "an agent cannot release a load. This created a decision row for "
                                   "a human — and that never changes with evidence"}


ROUTES = {
    ("GET", "/api/board"): lambda q, b: {"config": store.load("config"), "board": core.load_board(),
                                         "pending_approvals": len(gate.pending())},
    ("GET", "/api/triage/<id>"): lambda q, b: agents.triage(q["id"]),
    ("POST", "/api/vet"): lambda q, b: agents.vet(b.get("carrier"), b.get("load")),
    ("POST", "/api/loads/<id>/release"): release,
    ("GET", "/api/carriers"): lambda q, b: {
        "rows": [{**core.trust_file(c), "demo_tag": c.get("demo_tag"), "mc": c.get("mc")}
                 for c in store.load("carriers")]},
    ("GET", "/api/tripwires"): lambda q, b: {
        "definitions": {k: (v.__doc__ or k) for k, v in core.TRIPWIRES.items()},
        "hard_stops": sorted(core.HARD_STOPS),
        "log": store.load("tripwire_log")[-60:]},
    ("GET", "/api/tracking"): lambda q, b: agents.check_calls(),
    ("GET", "/api/approvals"): lambda q, b: {"pending": gate.pending()},
    ("POST", "/api/approvals/<id>/decide"): lambda q, b: (
        lambda ap, h: gate.decide(q["id"], h, approve=bool(b.get("approve", True)),
                                  execute=_executor(ap, h)) if ap else {"ok": False}
    )(store.by_id("approvals", q["id"]), b.get("human", "ops")),
    ("GET", "/api/roi"): lambda q, b: core.roi({k: float(v) for k, v in (q or {}).items() if _num(v)}),
    ("GET", "/api/eval"): lambda q, b: core.eval_tripwires(),
    ("GET", "/api/autonomy"): lambda q, b: {"matrix": core.MATRIX.actions,
                                            "never_promote": core.MATRIX.never_promote()},
    ("GET", "/api/events"): lambda q, b: {"events": store.load("events")[-300:]},
    ("POST", "/api/agents/run"): lambda q, b: agents.run_all(),
}

if __name__ == "__main__":
    if not store.load("config"):
        print("no data yet — run:  python3 seed.py")
    serve.run(ROOT / "app", ROUTES, PORT, "Carrier OS")
