#!/usr/bin/env python3
"""Field OS — the agents. Everything routes through `core.gate`. Stdlib only."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import iso


def handle_message(msg_id):
    m = store.by_id("messages", msg_id)
    if not m:
        return {"error": "no such message"}
    c = core.read_message(m.get("text", ""))
    out = {"message": msg_id, "classification": c, "steps": []}
    gate.act("read_message", "frontdesk", msg_id, {"label": c["label"], "why": c["why"]})

    if c["label"] == "drift_exposure":
        gate.act("log_complaint", "frontdesk", msg_id,
                 {"verbatim": m.get("text", ""), "at": m.get("at"),
                  "caller": m.get("from") or "unknown",
                  "summary": f"DRIFT/EXPOSURE: {m.get('text','')[:50]}"})
        ev = store.log_event("refused", msg_id, "agent:frontdesk", "R0",
                             {"action": "assert_drift_cause",
                              "why": "the system asserts nothing about cause"})
        out["steps"].append({"action": "log_complaint", "said": core.COMPLAINT_PROTOCOL,
                             "why": c["why"], "event": ev["id"]})
    elif c["label"] == "chemical_question":
        ev = store.log_event("refused", msg_id, "agent:frontdesk", "R0",
                             {"action": "recommend_chemical_or_rate", "why": c["why"]})
        out["steps"].append({"action": "route_to_agronomist", "refused": "routed unanswered",
                             "why": c["why"], "event": ev["id"]})
    elif c["label"] == "work_request":
        body = _job_ack_copy(m)
        gate.act("draft_job", "frontdesk", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_job", "why": "a human books the window"})
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("messages", m)
    return out


def _job_ack_copy(m):
    """The work-request ack a human sends — honest about the weather's veto."""
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — got it, you're on the board. We'll slot you into the first window the "
            f"weather gives us and text the morning we're coming; if wind or rain moves it, "
            f"you'll hear from us, not from silence.")


def _invoice_copy(j, why):
    """The invoice cover — the as-applied record does the talking."""
    return (f"Invoice attached for {j.get('desc', 'the application')}: {why}. The as-applied "
            f"record rides with it — acres, product, rate, date, and the applicator's license, "
            f"so your file matches ours.")


def bill_job(job_id):
    j = store.by_id("jobs", job_id)
    if not j:
        return {"error": "no such job"}
    okb, why = core.can_bill(j)
    if not okb:
        ev = store.log_event("refused", job_id, "agent:office", "R0",
                             {"action": "bill_without_as_applied", "why": why})
        return {"refused": why, "event": ev["id"]}
    body = _invoice_copy(j, why)
    r = gate.act("draft_invoice", "office", job_id, {"summary": why, "preview": body[:110]})
    return dict(r, draft=body)


def dispatch_job(job_id):
    j = store.by_id("jobs", job_id)
    if not j:
        return {"error": "no such job"}
    okd, why = core.can_dispatch(j)
    if not okd:
        ev = store.log_event("refused", job_id, "agent:dispatch", "R0",
                             {"action": "dispatch_rup_unlicensed", "why": why})
        return {"refused": why, "event": ev["id"]}
    return gate.act("dispatch_job", "dispatch", job_id, {"summary": why})


def run_all():
    handled = 0
    for m in store.load("messages"):
        if not m.get("handled_at"):
            handle_message(m["id"])
            handled += 1
    return {"messages": {"handled": handled}}
