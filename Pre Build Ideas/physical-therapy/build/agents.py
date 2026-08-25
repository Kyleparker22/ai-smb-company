#!/usr/bin/env python3
"""Rehab OS — the agents. Everything routes through `core.gate`. Stdlib only."""
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

    if c["label"] == "red_flag":
        gate.act("route_red_flag", "frontdesk", msg_id,
                 {"summary": f"{c['kind']}: {m.get('text','')[:50]}", "kind": c["kind"]})
        out["steps"].append({"action": "route_red_flag", "kind": c["kind"],
                             "said": core.ER_INSTRUCTION, "why": c["why"]})
    elif c["label"] == "clinical":
        ev = store.log_event("refused", msg_id, "agent:frontdesk", "R0",
                             {"action": "clinical_answer", "why": c["why"]})
        out["steps"].append({"action": "route_to_therapist", "refused": "routed unanswered",
                             "why": c["why"], "event": ev["id"]})
    elif c["label"] == "cancellation":
        gate.act("draft_rebooking", "frontdesk", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": _rebook_copy(m)[:110]})
        if m.get("patient_id"):
            store.log_event("dropout_signal", m["patient_id"], "agent:frontdesk", "R3",
                            {"signal": "cancellation", "message": msg_id})
        out["steps"].append({"action": "draft_rebooking",
                             "why": "rebooking drafts AND the dropout signal records"})
    elif c["label"] == "scheduling":
        gate.act("draft_rebooking", "frontdesk", msg_id, {"summary": m.get("text", "")[:60]})
        out["steps"].append({"action": "draft_scheduling_reply", "why": "a human sends"})
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("messages", m)
    return out


def book_visit(patient_id):
    """The booking path — refused past authorization, drafts inside it."""
    p = store.by_id("patients", patient_id)
    if not p:
        return {"error": "no such patient"}
    okb, why = core.can_book_billable(p)
    if not okb:
        ev = store.log_event("refused", patient_id, "agent:scheduler", "R0",
                             {"action": "bill_beyond_authorization", "why": why})
        gate.act("book_within_auth", "scheduler", patient_id,
                 {"summary": f"NEEDS PAYER: {why[:70]}"})
        return {"refused": why, "event": ev["id"],
                "note": "queued for a human to take to the payer — never silently booked"}
    return gate.act("book_within_auth", "scheduler", patient_id,
                    {"summary": f"book next visit — {why}"})


def dropout_sweep(limit=15):
    out = {"drafted": 0}
    recent = {e["subject"] for e in store.events(kind="queued_for_approval", since_days=7)
              if (e.get("detail") or {}).get("action") == "draft_dropout_outreach"}
    for r in core.dropout_board()["rows"]:
        if out["drafted"] >= limit or r["patient"] in recent:
            continue
        p = store.by_id("patients", r["patient"]) or {}
        body = _outreach_copy(p, r)
        gate.act("draft_dropout_outreach", "carecoach", r["patient"],
                 {"summary": f"{r['name']}: " + "; ".join(s["detail"] for s in r["signals"][:2]),
                  "preview": body[:110]})
        out["drafted"] += 1
    return out


def _outreach_copy(p, row):
    """The dropout check-in a human sends. Practical, no guilt, no outcome
    promise — 'plans work when you're in them' is as far as it goes."""
    name = (p.get("name") or row.get("name") or "there").split()[0]
    return (f"Hi {name} — we noticed the last couple of visits didn't happen and wanted to check "
            f"in, not chase you. If the schedule, the cost, or the exercises themselves are the "
            f"problem, tell us — all three are fixable. Your plan works when you're in it, and "
            f"we'd rather adjust it than lose you to it.")


def _rebook_copy(m):
    return ("No problem — thanks for telling us. Reply with two windows that work this week and "
            "we'll hold one; keeping the rhythm matters more than which day it lands on.")


def run_all():
    handled = 0
    for m in store.load("messages"):
        if not m.get("handled_at"):
            handle_message(m["id"])
            handled += 1
    return {"messages": {"handled": handled}, "dropout": dropout_sweep()}
