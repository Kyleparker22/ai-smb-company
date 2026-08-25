#!/usr/bin/env python3
"""Visit OS — the agents. Everything routes through `core.gate`. Stdlib only."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import iso, now


def handle_message(msg_id):
    """Triage one message. Emergencies act at R2 — routed now, human told now —
    with the ER instruction verbatim. Clinical and QoL route unanswered."""
    m = store.by_id("messages", msg_id)
    if not m:
        return {"error": "no such message"}
    c = core.read_message(m.get("text", ""))
    out = {"message": msg_id, "classification": c, "steps": []}
    gate.act("read_message", "triage", msg_id, {"label": c["label"], "why": c["why"]})

    if c["label"] == "emergency":
        gate.act("route_emergency", "triage", msg_id,
                 {"summary": f"{c['kind']}: {m.get('text','')[:60]}", "kind": c["kind"]})
        out["steps"].append({"action": "route_emergency", "kind": c["kind"],
                             "said": core.EMERGENCY_INSTRUCTION,
                             "why": "routed to a human immediately; nothing was assessed"})
    elif c["label"] == "qol":
        ev = store.log_event("refused", msg_id, "agent:triage", "R0",
                             {"action": "qol_conversation", "why": c["why"]})
        out["steps"].append({"action": "route_to_human", "kind": "quality_of_life",
                             "refused": "no automated reply of any kind — a person calls",
                             "why": c["why"], "event": ev["id"]})
    elif c["label"] == "clinical":
        ev = store.log_event("refused", msg_id, "agent:triage", "R0",
                             {"action": "clinical_answer", "why": c["why"]})
        out["steps"].append({"action": "route_to_dvm", "refused": "routed unanswered",
                             "why": c["why"], "event": ev["id"]})
    else:
        out["steps"].append({"action": "route_routine" if c["label"] == "routine" else "route_human",
                             "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("messages", m)
    return out


def reactivation_sweep(limit=20):
    """Draft reminders for lapsed ACTIVE patients only. The query cannot see a
    deceased patient; reminder_plan re-checks anyway."""
    out = {"drafted": 0, "skipped": 0}
    for row in core.lapsed():
        if out["drafted"] >= limit:
            break
        p = store.by_id("patients", row["patient"])
        plan = core.reminder_plan(p)
        if plan["action"] != "draft_reminder":
            out["skipped"] += 1
            continue
        due = ", ".join(d["item"] for d in row["due"])
        touch_n = len(p.get("reminders") or []) + 1
        body = _reminder_copy(p, row, touch_n)
        gate.act("draft_reminder", "reactivation", p["id"],
                 {"summary": f"{p['name']} ({p['species']}) overdue: {due}",
                  "touch": touch_n, "preview": body[:110]})
        p.setdefault("reminders", []).append({"at": iso(), "kind": "drafted", "body": body})
        store.upsert("patients", p)
        out["drafted"] += 1
    return out


def _reminder_copy(p, row, touch_n):
    """Drafted for a human to send. Names the patient and exactly what is due
    from the chart — never a symptom claim, never urgency theater. The status
    check has already run twice before copy is ever drafted."""
    client = store.by_id("clients", p.get("client_id")) or {}
    who = (client.get("name") or "there").split()[0]
    due = " and ".join(d["item"] for d in row["due"])
    name = p.get("name", "your pet")
    return {
        1: (f"Hi {who} — {name}'s {due} came due on our books. Happy to find a time that "
            f"works; reply here or call and we'll get {name} on the schedule."),
        2: (f"Hi {who} — a second gentle nudge that {name} is overdue for {due}. If you've "
            f"moved or switched clinics, tell us and we'll close the file properly."),
        3: (f"Hi {who} — last reminder from us about {name}'s {due}; we'll leave it here. "
            f"The records stay ready whenever you need them."),
    }.get(touch_n, f"Hi {who} — {name} is due for {due}.")


def _offer_copy(w, slot):
    who = (w.get("name") or "there").split()[0] if isinstance(w.get("name"), str) else "there"
    return (f"Hi — a {slot.get('minutes', 30)}-minute slot just opened {slot.get('when', 'soon')} "
            f"with {slot.get('doctor', 'the doctor')}. It's first-come: reply YES and it's yours, "
            f"otherwise we'll offer it to the next family on the list.")


def cancel_and_rank(appt_id):
    """Demo path: cancel a slot and rank the waitlist for it."""
    a = store.by_id("appointments", appt_id)
    if not a:
        return {"error": "no such appointment"}
    if not a.get("cancelled_at"):
        a["cancelled_at"] = iso()
        store.upsert("appointments", a)
        store.log_event("cancelled", appt_id, "client:demo", None, {})
    ranked = core.rank_waitlist(a)
    for c in ranked["candidates"][:3]:
        w = store.by_id("waitlist", c["waitlist_id"]) or {}
        body = _offer_copy(w, a)
        gate.act("draft_backfill_offer", "scheduler", c["waitlist_id"],
                 {"summary": f"offer {a.get('when','slot')} to {c['who']} (score {c['score']})",
                  "appointment": appt_id, "preview": body[:110]})
    return {"appointment": a, **ranked,
            "note": "waves, not a blast — three offers, then the next three if the slot is still open"}


def run_all():
    handled = 0
    for m in store.load("messages"):
        if not m.get("handled_at"):
            handle_message(m["id"])
            handled += 1
    return {"messages": {"handled": handled}, "reactivation": reactivation_sweep()}
