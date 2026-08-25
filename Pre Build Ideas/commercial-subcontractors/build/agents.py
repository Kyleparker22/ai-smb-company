#!/usr/bin/env python3
"""Change OS — the agents. Every action goes through `core.gate`.

Agent names are internal only; external surfaces describe the OS by function.
Stdlib only.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import iso, now


# ---------------------------------------------------------------- 1 · change capture

def capture_sweep(limit=None):
    """Classify unreviewed field notes; a change event becomes a draft CO, an
    ambiguous note becomes a PM queue row. Nothing is submitted here."""
    out = {"classified": 0, "drafted": 0, "ambiguous": 0}
    notes = [n for n in store.load("notes") if not n.get("classified")]
    if limit:
        notes = notes[:limit]
    for n in notes:
        c = core.classify_note(n.get("text", ""))
        n.update(classified=True, label=c["label"], why=c["why"])
        store.upsert("notes", n)
        gate.act("classify_note", "capture", n["id"],
                 {"label": c["label"], "why": c["why"]})
        out["classified"] += 1
        if c["label"] == "change_event" and not n.get("demo_tag"):
            co = {"id": store.nid("co"), "project_id": n["project_id"],
                  "note_id": n["id"], "state": "draft", "value": n.get("est_value", 0),
                  "directive_ref": n.get("directive_ref"),
                  "summary": (n.get("text") or "")[:90], "created_at": iso()}
            store.upsert("cos", co)
            gate.act("draft_co", "capture", co["id"],
                     {"summary": co["summary"], "value": co["value"]})
            out["drafted"] += 1
        elif c["label"] == "ambiguous":
            out["ambiguous"] += 1
    return out


def submit_co(co_id):
    """Queue a CO submission for a human — unless it has no directive, in which
    case it is REFUSED, not queued: there is no approve button past that rule."""
    co = store.by_id("cos", co_id)
    if not co:
        return {"error": "no such CO"}
    ok, why = core.can_submit(co)
    if not ok:
        ev = store.log_event("refused", co_id, "agent:capture", "R1",
                             {"action": "submit_co", "why": why})
        return {"refused": why, "event": ev["id"]}
    packet = co_packet(co)
    res = gate.act("submit_co", "capture", co_id,
                   {"summary": co["summary"], "value": co.get("value"),
                    "directive_ref": co["directive_ref"],
                    "preview": packet["cover"][:110]})
    return dict(res, packet=packet)


def co_packet(co):
    """The submission packet a human reviews: the drafted cover, the directive
    reference, and the field note it traces back to. Assembled, never sent."""
    note = store.by_id("notes", co.get("note_id")) or {}
    p = store.by_id("projects", co.get("project_id")) or {}
    cover = (f"Attached is CO {co['id']} on {p.get('name', 'the project')} for "
             f"${co.get('value', 0):,.0f}, performed under {co.get('directive_ref')}. "
             f"The field record and directive are enclosed. Please advise on approval "
             f"so we can include it on the next pay application.")
    return {"cover": cover, "directive_ref": co.get("directive_ref"),
            "field_note": note.get("text"), "note_date": note.get("at"),
            "value": co.get("value"), "project": p.get("name"),
            "note": "a human reviews and sends — the packet only assembles what is on file"}


# ---------------------------------------------------------------- 2 · retainage chase

def retainage_sweep(ref=None):
    """The bounded ladder: at most one drafted chase per row per run, cooldown
    between steps, and past the last step the row leaves the message lane —
    silence is an answer, and the answer is a phone call."""
    ref = ref or now()
    out = {"drafted": 0, "escalated": 0, "waiting": 0}
    already = {e["subject"] for e in store.events(kind="queued_for_approval", since_days=7)
               if (e.get("detail") or {}).get("action") == "draft_retainage_chase"}
    for r in core.retainage_aging():
        p = store.by_id("projects", r["project_id"]) or {}
        touches = p.get("retainage_touches") or []
        r["terms_days"] = p.get("retainage_terms_days") or 60
        due = core.due_retainage_touch(r, touches, ref)
        if not due or r["project_id"] in already:
            out["waiting"] += 1
            continue
        if due.get("escalate"):
            if not p.get("retainage_escalated"):
                gate.act("escalate_to_call", "collections", r["project_id"],
                         {"summary": f"{r['project']}: ${r['held']:,.0f} — {due['why']}"})
                p["retainage_escalated"] = True
                store.upsert("projects", p)
                out["escalated"] += 1
            continue
        body = _chase_copy(r, due)
        gate.act("draft_retainage_chase", "collections", r["project_id"],
                 {"summary": f"step {due['step']} · ${r['held']:,.0f} held {r['days_since_completion']}d on {r['project']}",
                  "held": r["held"], "step": due["step"], "preview": body[:110]})
        touches.append({"step": due["step"], "at": iso(ref), "body": body})
        p["retainage_touches"] = touches
        store.upsert("projects", p)
        out["drafted"] += 1
    return out


def _chase_copy(r, step):
    """Drafted for a human to send. Factual, our own ledger's numbers, no legal
    language — entitlement assertions are R0 and never appear in copy."""
    gc = (store.by_id("gcs", r.get("gc_id")) or {}).get("name", "your office")
    held = f"${r['held']:,.0f}"
    days = r["days_since_completion"]
    return {
        "friendly": (f"Hi {gc} team — following up on {r['project']}: our records show {held} "
                     f"retainage held, with substantial completion {days} days back. Could you "
                     f"let us know where release stands in your queue?"),
        "specific": (f"Hi {gc} team — second note on {r['project']}. Retainage of {held} is now "
                     f"{days} days past substantial completion against {r.get('terms_days', 60)}-day "
                     f"terms. If anything is holding release on your side — punch, closeout docs — "
                     f"tell us and we'll clear it this week."),
        "final": (f"Hi {gc} team — third and final note on {r['project']} before we pick up the "
                  f"phone. {held} in retainage remains held {days} days after substantial "
                  f"completion. We'd rather resolve this in your AP queue than anywhere else — "
                  f"who should we call?"),
    }[step["kind"]]


# ---------------------------------------------------------------- 3 · deadline watch

def deadline_sweep(horizon_days=30):
    """Alert the PM on every deadline inside the horizon. The alert is a date,
    never advice; filing is R0 and does not appear here at all."""
    out = {"alerts": 0}
    board = core.deadline_board()
    already = {(e["subject"], (e.get("detail") or {}).get("step"))
               for e in store.events(kind="notice_alert", since_days=14)}
    for d in board["deadlines"]:
        if d["days_left"] > horizon_days or (d["project_id"], d["step"]) in already:
            continue
        gate.act("notice_alert", "calendar", d["project_id"],
                 {"step": d["step"], "due": d["due"], "days_left": d["days_left"],
                  "label": d["label"]})
        out["alerts"] += 1
    return out


# ---------------------------------------------------------------- 4 · invitations

def invitation_sweep():
    out = {"scored": 0}
    for inv in store.load("invitations"):
        if inv.get("score") is not None:
            continue
        s = core.invitation_score(inv)
        inv.update(score=s["score"], reasons=s["reasons"])
        store.upsert("invitations", inv)
        gate.act("score_invitation", "estimating", inv["id"],
                 {"score": s["score"], "gc": s["gc"]})
        out["scored"] += 1
    return out


def run_all():
    return {"capture": capture_sweep(), "retainage": retainage_sweep(),
            "deadlines": deadline_sweep(), "invitations": invitation_sweep()}
