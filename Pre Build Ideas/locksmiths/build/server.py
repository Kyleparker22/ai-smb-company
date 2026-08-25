#!/usr/bin/env python3
"""Key OS — server. Stdlib only, 127.0.0.1:8874."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8874


def _executor(ap, human):
    def run():
        store.log_event(ap["action"] + "_done", ap["subject"], f"human:{human}", "R1",
                        {"approval": ap["id"]})
        return ap["subject"]
    return run


def board(q, b):
    msgs = [m for m in store.load("messages") if not m.get("handled_at")]
    open_jobs = [j for j in store.load("jobs") if not j.get("closed_at")]
    unverifiable = [m for m in store.load("messages") if m.get("unverifiable")]
    due = [c for c in store.load("clocks")
           if core.service_plan(c)["action"] == "draft_service_reminder"]
    return {"config": store.load("config"),
            "board": {"messages_open": len(msgs), "jobs_open": len(open_jobs),
                      "unverifiable": len(unverifiable),
                      "systems": len(store.load("systems")),
                      "registry_records": len(store.load("registry")),
                      "clocks_due": len(due),
                      "recovered": core.recovered_this_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


def systems_view(q, b):
    out = []
    for s in store.load("systems")[:40]:
        recs = core.system_records(s["id"])
        out.append({**s, "records": len(recs),
                    "last_change": recs[-1]["change"] if recs else None,
                    "note": "key codes live in the registry and never appear in outbound copy"})
    return {"rows": out, "append_only": "a change is a new record — there is no edit path"}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/messages"): lambda q, b: {"rows": sorted(store.load("messages"),
        key=lambda m: m.get("at") or "", reverse=True)[:60]},
    ("POST", "/api/messages/<id>/handle"): lambda q, b: agents.handle_message(q["id"]),
    ("GET", "/api/systems"): systems_view,
    ("GET", "/api/systems/<id>/registry"): lambda q, b: {"rows": core.system_records(q["id"])},
    ("GET", "/api/jobs"): lambda q, b: {"rows": sorted(store.load("jobs"),
        key=lambda j: j.get("opened_at") or "", reverse=True)[:60]},
    ("POST", "/api/jobs/<id>/close"): lambda q, b: agents.close_job(q["id"], human=b.get("human")),
    ("GET", "/api/quote"): lambda q, b: core.quote_for(q.get("kind", ""),
        cylinders=int(q["cylinders"]) if q.get("cylinders") else None,
        after_hours=q.get("after_hours") in ("1", "true")),
    ("POST", "/api/scrub/check"): lambda q, b: dict(zip(("ok", "why"),
        core.key_scrub_ok(b.get("text", "")))),
    ("GET", "/api/clocks"): lambda q, b: {"rows": [
        {**c, "plan": core.service_plan(c)} for c in store.load("clocks")]},
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
    serve.run(ROOT / "app", ROUTES, PORT, "Key OS")
