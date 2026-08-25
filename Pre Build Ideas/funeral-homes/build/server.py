#!/usr/bin/env python3
"""Arrangement OS — server. Stdlib only, 127.0.0.1:8845."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8845


def _executor(ap, human):
    def run():
        store.log_event(ap["action"].replace("draft_", "") + "_done", ap["subject"],
                        f"human:{human}", "R1", {"approval": ap["id"]})
        return ap["subject"]
    return run


def board(q, b):
    calls_open = [c for c in store.load("calls") if not c.get("handled_at")]
    open_docs, dated = 0, []
    for case in store.load("cases"):
        for d in core.case_documents(case):
            if d["state"] == "open":
                open_docs += 1
                if d.get("needed_by"):
                    dated.append({"case": case["id"], **d})
    dated.sort(key=lambda x: x.get("days_left") or 0)
    return {"config": store.load("config"),
            "board": {"calls_open": len(calls_open), "open_documents": open_docs,
                      "dated_documents": dated[:10],
                      "preneed": core.preneed_ledger(),
                      "recovered": core.recovered_this_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/calls"): lambda q, b: {"rows": sorted(store.load("calls"),
        key=lambda m: m.get("at") or "", reverse=True)[:60]},
    ("POST", "/api/calls/<id>/handle"): lambda q, b: agents.handle_call(q["id"]),
    ("GET", "/api/gpl"): lambda q, b: {"rows": store.load("gpl")},
    ("POST", "/api/quote"): lambda q, b: core.quote(b.get("items") or []),
    ("GET", "/api/cases"): lambda q, b: {"rows": [
        {"case": c["id"], "family": c.get("family"), "documents": core.case_documents(c)}
        for c in store.load("cases")][:40]},
    ("GET", "/api/roi"): lambda q, b: core.roi(q),
    ("GET", "/api/eval"): lambda q, b: {"triage": core.run_eval()},
    ("GET", "/api/autonomy"): lambda q, b: {"matrix": core.matrix.actions,
                                            "never_promote": core.matrix.never_promote(),
                                            "automation": core.automation()},
    ("GET", "/api/approvals"): lambda q, b: {"pending": gate.pending()},
    ("POST", "/api/approvals/<id>/decide"): lambda q, b: gate.decide(
        q["id"], b.get("human", "director"), b.get("approve", True),
        execute=_executor(store.by_id("approvals", q["id"]) or {}, b.get("human", "director"))),
    ("GET", "/api/events"): lambda q, b: {"events": store.events()[-120:]},
    ("POST", "/api/agents/run"): lambda q, b: agents.run_all(),
}

if __name__ == "__main__":
    serve.run(ROOT / "app", ROUTES, PORT, "Arrangement OS")
