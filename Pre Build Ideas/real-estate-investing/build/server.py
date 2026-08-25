#!/usr/bin/env python3
"""Deal OS — server. Stdlib only, 127.0.0.1:8881."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8881


def _executor(ap, human):
    def run():
        store.log_event(ap["action"] + "_done", ap["subject"], f"human:{human}", "R1",
                        {"approval": ap["id"]})
        return ap["subject"]
    return run


def board(q, b):
    scr = core.deal_screen()
    msgs = [m for m in store.load("messages") if not m.get("handled_at")]
    return {"config": store.load("config"),
            "board": {"screen": ({"matches": len(scr["rows"]), "criteria": scr["criteria"],
                                  "skipped": scr["skipped"]}
                                 if "refused" not in scr else {"refused": scr["refused"]}),
                      "messages_open": len(msgs),
                      "screened": core.screened_this_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


def _num(v):
    try:
        float(v)
        return True
    except (TypeError, ValueError):
        return False


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/screen"): lambda q, b: core.deal_screen(),
    ("GET", "/api/messages"): lambda q, b: {"rows": sorted(store.load("messages"),
        key=lambda m: m.get("at") or "", reverse=True)[:60]},
    ("POST", "/api/messages/<id>/handle"): lambda q, b: agents.handle_message(q["id"]),
    ("POST", "/api/listings/<id>/analyze"): lambda q, b: agents.analyze(
        q["id"], {k: float(v) for k, v in (b or {}).items() if _num(v)}),
    ("GET", "/api/listings/<id>/bands"): lambda q, b: core.exit_bands(
        store.by_id("listings", q["id"]) or {}, q.get("strategy", "ltr"),
        int(q.get("years", 10))),
    ("GET", "/api/listings/<id>/point"): lambda q, b: core.point_estimate(
        store.by_id("listings", q["id"]) or {}, q.get("strategy", "ltr"),
        int(q.get("years", 10))),
    ("GET", "/api/listings/<id>/sensitivity"): lambda q, b: core.sensitivity(
        store.by_id("listings", q["id"]) or {}, q.get("strategy", "ltr")),
    ("POST", "/api/listings/<id>/payoff"): lambda q, b: (
        lambda l: core.underwrite(l, b.get("strategy", "ltr"),
                                  extra_monthly=float(b.get("extra_monthly", 0)))
        if l else {"error": "no such listing"})(store.by_id("listings", q["id"])),
    ("GET", "/api/markets"): lambda q, b: {"rows": [
        {**m, "rate_view": core.market_rate(m),
         "appreciation": core.appreciation_base(m)} for m in store.load("markets")]},
    ("GET", "/api/roi"): lambda q, b: core.roi({k: float(v) for k, v in (q or {}).items()
                                                if _num(v)}),
    ("GET", "/api/eval"): lambda q, b: {"triage": core.run_eval()},
    ("GET", "/api/autonomy"): lambda q, b: {"matrix": core.matrix.actions,
                                            "never_promote": core.matrix.never_promote(),
                                            "automation": core.automation()},
    ("GET", "/api/approvals"): lambda q, b: {"pending": gate.pending()},
    ("POST", "/api/approvals/<id>/decide"): lambda q, b: gate.decide(
        q["id"], b.get("human", "operator"), b.get("approve", True),
        execute=_executor(store.by_id("approvals", q["id"]) or {}, b.get("human", "operator"))),
    ("GET", "/api/events"): lambda q, b: {"events": store.events()[-120:]},
    ("POST", "/api/agents/run"): lambda q, b: agents.run_all(),
}

if __name__ == "__main__":
    serve.run(ROOT / "app", ROUTES, PORT, "Deal OS")
