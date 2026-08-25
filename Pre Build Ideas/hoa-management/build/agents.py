#!/usr/bin/env python3
"""Reserve OS — the agents. Everything routes through `core.gate`. Stdlib only."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import iso, now, parse


def handle_message(msg_id):
    m = store.by_id("messages", msg_id)
    if not m:
        return {"error": "no such message"}
    c = core.read_message(m.get("text", ""))
    out = {"message": msg_id, "classification": c, "steps": []}
    gate.act("read_message", "concierge", msg_id, {"label": c["label"], "why": c["why"]})

    if c["label"] == "safety":
        # The costly path: routed NOW at R2 — the escalation executes before
        # any draft exists, verbatim, and dismissal has no code path.
        r = gate.act("escalate_safety_report", "concierge", msg_id,
                     {"verbatim": m.get("text", ""), "from": m.get("from"),
                      "association": m.get("association_id"),
                      "routed": "NOW — ahead of everything else in the queue"})
        ev = store.log_event("refused", msg_id, "agent:concierge", "R0",
                             {"action": "dismiss_safety_report",
                              "why": "a safety report cannot be triaged away — escalation "
                                     "already ran; a human takes it from here"})
        body = _safety_ack(m)
        gate.act("draft_safety_ack", "concierge", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "escalate_safety_report", "escalated": True,
                             "verbatim": m.get("text", ""), "draft": body,
                             "refused": "dismissal has no code path — the report routed NOW, "
                                        "verbatim, ahead of the queue",
                             "why": c["why"], "gate": r, "event": ev["id"]})
    elif c["label"] == "dues_dispute":
        assoc = store.by_id("associations", m.get("association_id")) or {}
        body = core.dues_answer(assoc, m.get("from"))
        gate.act("draft_dues_reply", "concierge", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_dues_reply", "draft": body,
                             "why": "answered by citation — the recorded line items "
                                    "verbatim plus the band math"})
    elif c["label"] == "appeal":
        body = _appeal_ack(m)
        gate.act("draft_appeal_ack", "concierge", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_appeal_ack", "draft": body,
                             "why": "a recorded right — the hearing process cited, and the "
                                    "hearing decision stays a human's"})
    elif c["label"] == "amenity":
        body = _amenity_copy(m)
        gate.act("draft_amenity_reply", "concierge", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_amenity_reply", "draft": body,
                             "why": "answered from the record"})
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("messages", m)
    return out


def _safety_ack(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — your report is already moving: it was routed to the community "
            f"manager the moment it arrived, in your exact words, ahead of everything else "
            f"in the queue. Common-area safety never waits behind paperwork here. A person "
            f"will confirm what's being done and when — and if the hazard gets worse before "
            f"then, call the manager's line directly.")


def _appeal_ack(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — appealing is your recorded right, and here is exactly how it runs: "
            f"the ladder is courtesy → notice → hearing → fine, per your association's "
            f"recorded enforcement policy, and nothing skips a rung. Your file goes to the "
            f"hearing with the cited rule and any photos attached, and the decision there "
            f"is made by a person, on the record — never by this system. You'll get the "
            f"hearing date from the manager.")


def _amenity_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — checking the association's record for that now; you'll get the "
            f"exact answer (availability, code, or replacement steps) in one message, not "
            f"a phone tree. If it needs a board decision, we'll say so plainly.")


def draft_violation_notice(violation_id):
    """Advance one rung on the recorded ladder (courtesy → notice → hearing) and
    draft the outward notice, rule cited verbatim, at R1."""
    v = store.by_id("violations", violation_id)
    if not v:
        return {"error": "no such violation"}
    nxt, why = core.can_advance(v)
    if not nxt:
        return {"refused": why}
    gate.act("advance_violation", "compliance", violation_id,
             {"from": v["stage"], "to": nxt, "why": why})
    v["stage"] = nxt
    v.setdefault("history", []).append({"at": iso(), "stage": nxt})
    store.upsert("violations", v)
    body = _notice_copy(v, nxt)
    r = gate.act("draft_violation_notice", "compliance", violation_id,
                 {"summary": f"{v.get('unit')} · {v['rule_section']} → {nxt}",
                  "preview": body[:110]})
    return {"advanced_to": nxt, "draft": body, "gate": r,
            "cited": f"{v['rule_section']} — {v['rule_title']}"}


def _notice_copy(v, stage):
    lead = {"notice": "This is a formal notice", "hearing": "A hearing has been scheduled"}
    return (f"{lead.get(stage, 'Notice')} regarding unit {v.get('unit')}: "
            f"{v['rule_section']} — {v['rule_title']}. Recorded observation: "
            f"\"{v.get('description', '')}\""
            + (f" (photo on file: {v['photo_ref']})." if v.get("photo_ref") else ".")
            + f" The enforcement ladder is courtesy → notice → hearing → fine, per the "
              f"association's recorded policy; this matter is now at the {stage} rung. "
              f"You may appeal at any rung — the hearing decision is made by a person, "
              f"on the record.")


def assess_fine(violation_id, amount):
    """The fine path a UI can try: the clamp refuses anything off the recorded
    schedule; an on-schedule amount still queues R1 — money waits for a human."""
    chk = core.check_fine(violation_id, amount)
    if "refused" in chk or "error" in chk:
        return chk
    v = store.by_id("violations", violation_id)
    r = gate.act("assess_fine", "compliance", violation_id,
                 {"summary": f"{v.get('unit')} · {chk['scheduled']['basis']}"},
                 amount=float(amount))
    return {**chk, "gate": r}


def draft_board_packet(assoc_id):
    """The monthly board packet: funding bands, horizon, violation ledger
    summary, the counted week — drafted R1 for the manager, never auto-sent."""
    bv = core.board_view(assoc_id)
    if "error" in bv:
        return bv
    fb = bv["funding"]
    if fb.get("unknowable"):
        funding_line = "Reserves: UNKNOWABLE — no study on record; no adequacy claim appears."
    else:
        def hz(b):
            y = fb["bands"][b]["horizon"]["year"]
            return str(y) if y else "beyond window"
        funding_line = (f"Reserves: horizon {hz('bear')} (bear) / {hz('base')} (base) / "
                        f"{hz('bull')} (bull); end balances "
                        f"${fb['bands']['bear']['end_balance']:,.0f} / "
                        f"${fb['bands']['base']['end_balance']:,.0f} / "
                        f"${fb['bands']['bull']['end_balance']:,.0f}"
                        + (" — STUDY STALE, every number flagged" if fb.get("stale") else ""))
    week = core.counted_this_week()
    summary = (f"{bv['association']['name']} — {funding_line} · Violations: "
               f"{bv['violations']['open']} open of {bv['violations']['total']} "
               f"({', '.join(f'{k} {n}' for k, n in sorted(bv['violations']['by_stage'].items()))}) "
               f"· Week counted: {week['safety_reports_escalated']} safety escalation(s), "
               f"{week['notices_sent']} notice(s) sent, {week['disputes_answered']} "
               f"dispute(s) answered")
    r = gate.act("draft_board_packet", "packets", assoc_id,
                 {"summary": summary[:200], "month": iso()[:7]})
    return {"packet": summary, "gate": r,
            "note": "drafted for the manager at R1 — the numbers are the board_view's own; "
                    "nothing in the packet is written that the doors don't already show"}


def run_all():
    handled = 0
    for m in store.load("messages"):
        if not m.get("handled_at"):
            handle_message(m["id"])
            handled += 1
    return {"messages": {"handled": handled}}
