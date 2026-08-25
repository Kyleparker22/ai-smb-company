#!/usr/bin/env python3
"""Fix OS — server. Stdlib only, 127.0.0.1:8878."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import agents, core
from core import gate, store
from _kit import serve
from _kit.store import iso

PORT = 8878


def _executor(ap, human):
    def run():
        if ap.get("action") == "submit_claim":
            c = store.by_id("claims", ap["subject"])
            if c:
                c["submitted_at"] = iso()
                store.upsert("claims", c)
        if ap.get("action") == "draft_overage_request":
            j = store.by_id("jobs", ap["subject"])
            if j:
                amt = float(ap.get("amount") or 0)
                j["authorized_amount"] = round(core.job_total(j) + amt, 2)
                j.setdefault("work", []).append(
                    {"desc": (ap.get("detail") or {}).get("work") or "approved overage",
                     "amount": amt, "at": iso(),
                     "note": "added only after the customer's approval"})
                store.upsert("jobs", j)
        store.log_event(ap["action"] + "_done", ap["subject"], f"human:{human}", "R1",
                        {"approval": ap["id"]})
        return ap["subject"]
    return run


def board(q, b):
    cb = core.claims_board()
    msgs = [m for m in store.load("messages") if not m.get("handled_at")]
    rf = core.recall_flagged()
    return {"config": store.load("config"),
            "board": {"claims": {"blocked": cb["blocked"], "blocked_value": cb["blocked_value"],
                                 "ready": cb["ready"], "ready_value": cb["ready_value"]},
                      "claims_top": cb["rows"][:10],
                      "messages_open": len(msgs),
                      "recall_flagged": len(rf["rows"]),
                      "recovered": core.recovered_this_week(),
                      "automation": core.automation()},
            "pending_approvals": len(gate.pending())}


def claims_list(q, b):
    rows = []
    for c in store.load("claims"):
        missing, _ = core.claim_completeness(c)
        rows.append({"id": c["id"], "make": c.get("make"), "amount": c.get("amount", 0),
                     "failure_code": c.get("failure_code"), "missing": missing,
                     "submitted_at": c.get("submitted_at"), "paid_at": c.get("paid_at"),
                     "demo_tag": c.get("demo_tag")})
    rows.sort(key=lambda r: (bool(r["submitted_at"]), -len(r["missing"])))
    return {"rows": rows[:40], "note": core.claims_board()["note"]}


def jobs_list(q, b):
    rows = []
    for j in store.load("jobs"):
        if j.get("closed_at"):
            continue
        rows.append({"id": j["id"], "customer": j.get("customer"),
                     "appliance": j.get("appliance"), "symptom": j.get("symptom"),
                     "kind": j.get("kind"), "authorized": j.get("authorized_amount"),
                     "total": core.job_total(j), "parts_to_bring": j.get("parts_to_bring"),
                     "recall_notice": j.get("recall_notice"), "demo_tag": j.get("demo_tag")})
    rows.sort(key=lambda r: (not r["demo_tag"], r["id"]))
    return {"rows": rows[:40]}


ROUTES = {
    ("GET", "/api/board"): board,
    ("GET", "/api/messages"): lambda q, b: {"rows": sorted(store.load("messages"),
        key=lambda m: m.get("at") or "", reverse=True)[:60]},
    ("POST", "/api/messages/<id>/handle"): lambda q, b: agents.handle_message(q["id"]),
    ("GET", "/api/claims"): claims_list,
    ("POST", "/api/claims/<id>/submit"): lambda q, b: agents.submit_claim(q["id"]),
    ("POST", "/api/claims/<id>/narrative"): lambda q, b: agents.draft_narrative(
        q["id"], b.get("fields")),
    ("GET", "/api/jobs"): jobs_list,
    ("POST", "/api/jobs/<id>/work"): lambda q, b: agents.add_work(
        q["id"], b.get("desc") or "work", b.get("amount") or 0),
    ("GET", "/api/recalls"): lambda q, b: core.recall_flagged(),
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
    serve.run(ROOT / "app", ROUTES, PORT, "Fix OS")
