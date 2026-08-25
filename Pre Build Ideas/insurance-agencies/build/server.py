#!/usr/bin/env python3
"""Renewal OS — server. Stdlib only, 127.0.0.1 only."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8824


def _executor(ap, human="producer"):
    def run():
        if ap["action"] == "draft_renewal_call":
            store.log_event("renewal_call_sent", ap["subject"], f"human:{human}", "R1",
                            {"approval": ap["id"]})
        return ap["subject"]
    return run


def _num(v):
    try:
        float(v)
        return True
    except (TypeError, ValueError):
        return False


def remarket(q, b):
    """The demo quote deliberately comes back WITHOUT a coverage schedule when
    `bare=1`, so the comparison refusal is demonstrable."""
    pol = store.by_id("policies", q["id"])
    if not pol:
        return {"error": "no such policy"}
    if q.get("bare"):
        quote = {"premium": round(pol["premium"] * 0.86, 2)}
    else:
        # A realistic competing quote: cheaper because the deductible doubled and
        # the roof settlement dropped to actual cash value. That is exactly the
        # trade a price-only comparison hides.
        cov = dict(pol.get("coverage", {}))
        if "deductible" in cov and isinstance(cov["deductible"], int):
            cov["deductible"] = cov["deductible"] * 2
        if cov.get("roof_settlement") == "replacement":
            cov["roof_settlement"] = "acv"
        if cov.get("water_backup") is True:
            cov["water_backup"] = False
        quote = {"premium": round(pol["premium"] * 0.86, 2), "coverage": cov}
    return agents.remarket(q["id"], quote)


ROUTES = {
    ("GET", "/api/board"): lambda q, b: {"config": store.load("config"), "board": core.book_board(),
                                         "pending_approvals": len(gate.pending())},
    ("GET", "/api/renewals"): lambda q, b: agents.material_queue(),
    ("POST", "/api/renewals/sweep"): lambda q, b: {"quiet": agents.watchtower()["quiet"]},
    ("GET", "/api/remarket/<id>"): remarket,
    ("GET", "/api/coi"): lambda q, b: agents.coi_state(),
    ("POST", "/api/coi/sweep"): lambda q, b: agents.coi_desk(),
    ("GET", "/api/crosssell"): lambda q, b: agents.cross_sell(),
    ("GET", "/api/claims"): lambda q, b: agents.claims_touch(),
    ("GET", "/api/policies"): lambda q, b: {"rows": [p for p in store.load("policies")
                                                     if p.get("active")][:60]},
    ("GET", "/api/approvals"): lambda q, b: {"pending": gate.pending()},
    ("POST", "/api/approvals/<id>/decide"): lambda q, b: (
        lambda ap, h: gate.decide(q["id"], h, approve=bool(b.get("approve", True)),
                                  execute=_executor(ap, h)) if ap else {"ok": False}
    )(store.by_id("approvals", q["id"]), b.get("human", "producer")),
    ("GET", "/api/roi"): lambda q, b: core.roi({k: float(v) for k, v in (q or {}).items() if _num(v)}),
    ("GET", "/api/eval"): lambda q, b: core.eval_coi(),
    ("GET", "/api/autonomy"): lambda q, b: {"matrix": core.MATRIX.actions,
                                            "never_promote": core.MATRIX.never_promote()},
    ("GET", "/api/events"): lambda q, b: {"events": store.load("events")[-300:]},
    ("POST", "/api/agents/run"): lambda q, b: agents.run_all(),
}

if __name__ == "__main__":
    if not store.load("config"):
        print("no data yet — run:  python3 seed.py")
    serve.run(ROOT / "app", ROUTES, PORT, "Renewal OS")
