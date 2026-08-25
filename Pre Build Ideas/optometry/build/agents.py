#!/usr/bin/env python3
"""Exam OS — the agents. Everything routes through `core.gate`. Stdlib only."""
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
    patient = store.by_id("patients", m.get("patient_id")) if m.get("patient_id") else None

    if c["label"] == "emergency":
        gate.act("route_emergency", "frontdesk", msg_id,
                 {"summary": f"{c['kind']}: {m.get('text','')[:50]}", "kind": c["kind"]})
        out["steps"].append({"action": "route_emergency", "kind": c["kind"],
                             "said": c["instruction"], "why": c["why"]})
    elif c["label"] == "clinical":
        ev = store.log_event("refused", msg_id, "agent:frontdesk", "R0",
                             {"action": "clinical_answer", "why": c["why"]})
        out["steps"].append({"action": "route_to_doctor", "refused": "routed unanswered",
                             "why": c["why"], "event": ev["id"]})
    elif c["label"] == "reorder":
        chk = core.reorder_check(patient or {})
        if chk["ok"]:
            gate.act("draft_reorder", "frontdesk", m.get("patient_id") or msg_id,
                     {"summary": f"reorder against Rx expiring {chk['expires']}"})
            out["steps"].append({"action": "draft_reorder", "why": chk["note"]})
        else:
            ev = store.log_event("refused", msg_id, "agent:frontdesk", "R0",
                                 {"action": "refill_expired_rx", "why": chk["refused"]})
            gate.act("draft_booking", "frontdesk", m.get("patient_id") or msg_id,
                     {"summary": "exam draft — the Rx is expired or unknown"})
            out["steps"].append({"action": "refuse_and_offer_exam", "refused": chk["refused"],
                                 "event": ev["id"]})
    elif c["label"] == "rx_request":
        gate.act("draft_rx_release", "frontdesk", m.get("patient_id") or msg_id,
                 {"summary": "Rx release — the patient's prescription is the patient's"})
        out["steps"].append({"action": "draft_rx_release",
                             "why": "drafted promptly — the system never withholds"})
    elif c["label"] == "booking":
        gate.act("draft_booking", "frontdesk", msg_id, {"summary": m.get("text", "")[:60]})
        out["steps"].append({"action": "draft_booking", "why": "a human sends"})
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("messages", m)
    return out


def recall_sweep(limit=20):
    out = {"drafted": 0, "skipped": 0}
    for row in core.lapsed():
        if out["drafted"] >= limit:
            break
        p = store.by_id("patients", row["patient"])
        if p.get("demo_tag"):
            continue
        plan = core.recall_plan(p)
        if plan["action"] != "draft_recall":
            out["skipped"] += 1
            continue
        touch_n = len(p.get("recalls") or []) + 1
        body = _recall_copy(p, row, touch_n)
        gate.act("draft_recall", "recall", p["id"],
                 {"summary": f"{p.get('name')} — {row['overdue_days']}d overdue",
                  "touch": touch_n, "preview": body[:110]})
        p.setdefault("recalls", []).append({"at": iso(), "kind": "drafted", "body": body})
        store.upsert("patients", p)
        out["drafted"] += 1
    return out


def _recall_copy(p, row, touch_n):
    """Recall copy that names the chart fact — never a scare line about eye
    disease, and the third touch closes gently."""
    name = (p.get("name") or "there").split()[0]
    return {
        1: (f"Hi {name} — your eye exam came due on our books ({row.get('overdue_days', 0)} days "
            f"ago). An exam also renews your prescription, so ordering stays easy. Want a "
            f"morning or an afternoon?"),
        2: (f"Hi {name} — second nudge on that overdue exam. If you've switched practices, tell "
            f"us and we'll send your records wherever they need to go — no hard feelings."),
        3: (f"Hi {name} — last reminder from us; we'll leave it here. Your chart stays ready "
            f"whenever you are."),
    }.get(touch_n, f"Hi {name} — your exam is due.")


def run_all():
    handled = 0
    for m in store.load("messages"):
        if not m.get("handled_at"):
            handle_message(m["id"])
            handled += 1
    return {"messages": {"handled": handled}, "recall": recall_sweep()}
