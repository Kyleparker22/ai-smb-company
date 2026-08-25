#!/usr/bin/env python3
"""Remit OS — server. Stdlib only, 127.0.0.1:8886."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8886


def _executor(ap, human):
    def run():
        if ap.get("action") == "draft_appeal":
            f = store.by_id("findings", ap.get("subject"))
            if f:
                f["state"] = "appeal_sent"
                f["appeal_sent_at"] = iso()
                store.upsert("findings", f)
        store.log_event(ap.get("action", "?") + "_done", ap.get("subject"),
                        f"human:{human}", "R1", {"approval": ap.get("id")})
        return ap.get("subject")
    return run


def board(q, b):
    lg = core.ledger()
    mb = core.margin_board()
    msgs = [m for m in store.load("messages") if not m.get("handled_at")]
    open_f = [f for f in store.load("findings")
              if f.get("state") in ("open", "appeal_drafted", "needs_human")]
    amb = [f for f in open_f if f.get("class") == "ambiguous"]
    return {"config": {k: v for k, v in store.load("config").items() if k != "acquisition"},
            "board": {"open_recoverable": lg["open_recoverable"],
                      "open_count": lg["open_count"],
                      "findings_open": len(open_f), "ambiguous_waiting": len(amb),
                      "unauditable": core.unauditable_pbms(),
                      "messages_open": len(msgs),
                      "loss": {"count": mb["loss_count"], "dollars": mb["loss_dollars"],
                               "unmeasured_lines": mb["unmeasured"]["lines"]},
                      "recovered": core.recovered(), "week": core.week_counts(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/remits"): lambda q, b: {"rows": [
        {"id": r["id"], "pbm": r["pbm"], "remit_date": r.get("remit_date"),
         "lines": len(r.get("lines") or []), "demo_tag": r.get("demo_tag"),
         "recorded": r["pbm"] in core.contracts()} for r in store.load("remits")]},
    ("GET", "/api/remits/<id>/autopsy"): lambda q, b: core.autopsy(q["id"]),
    ("GET", "/api/contracts"): lambda q, b: {"contracts": core.contracts(),
                                             "unauditable": core.unauditable_pbms()},
    ("GET", "/api/ledger"): lambda q, b: core.ledger(),
    ("GET", "/api/margin"): lambda q, b: core.margin_board(),
    ("GET", "/api/recovered"): lambda q, b: core.recovered(),
    ("GET", "/api/recovered/estimate"): lambda q, b: core.estimate_recovered(),
    ("POST", "/api/findings/<id>/appeal"): lambda q, b: agents.draft_appeal(q["id"]),
    ("POST", "/api/findings/<id>/resolve"): lambda q, b: agents.resolve_ambiguous(
        q["id"], b.get("reading"), b.get("human")),
    ("POST", "/api/findings/<id>/correction"): lambda q, b: agents.record_correction(
        q["id"], b.get("amount"), b.get("human")),
    ("GET", "/api/messages"): lambda q, b: {"rows": sorted(
        store.load("messages"), key=lambda m: m.get("at") or "", reverse=True)[:60]},
    ("POST", "/api/messages/<id>/handle"): lambda q, b: agents.handle_message(q["id"]),
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
    serve.run(ROOT / "app", ROUTES, PORT, "Remit OS")
