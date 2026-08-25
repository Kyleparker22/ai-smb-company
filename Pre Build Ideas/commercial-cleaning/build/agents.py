#!/usr/bin/env python3
"""Crew OS — the agents. Everything routes through `core.gate`. Stdlib only."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import iso


def handle_report(report_id):
    m = store.by_id("reports", report_id)
    if not m:
        return {"error": "no such report"}
    c = core.classify_report(m.get("text", ""))
    out = {"report": report_id, "classification": c, "steps": []}
    gate.act("classify_report", "nightdesk", report_id, {"label": c["label"], "why": c["why"]})

    if c["label"] == "security":
        brief = security_brief(m)
        gate.act("escalate_security", "nightdesk", report_id,
                 {"summary": m.get("text", "")[:60], "brief": brief})
        out["steps"].append({"action": "escalate_security", "brief": brief,
                             "why": c["why"] + " — software cannot close this; a human follows up "
                                              "with the client and closes it"})
    elif c["label"] == "access_request":
        ev = store.log_event("refused", report_id, "agent:nightdesk", "R0",
                             {"action": "share_access_info", "why": c["why"]})
        out["steps"].append({"action": "refuse_access_info",
                             "refused": "no code, key or combo ever moves through this system",
                             "why": c["why"], "event": ev["id"]})
    elif c["label"] == "complaint":
        claim = core.clean_claim(m.get("contract_id"))
        body = _complaint_reply_copy(m, claim)
        if claim["assertable"]:
            gate.act("draft_complaint_reply", "nightdesk", report_id,
                     {"summary": f"reply citing inspection {claim['inspection']} "
                                 f"(score {claim.get('score')})", "preview": body[:110]})
            out["steps"].append({"action": "draft_complaint_reply", "evidence": claim,
                                 "draft": body, "why": claim["note"]})
        else:
            ev = store.log_event("refused", report_id, "agent:nightdesk", "R0",
                                 {"action": "assert_cleaned_without_inspection",
                                  "why": claim["refused"]})
            gate.act("draft_complaint_reply", "nightdesk", report_id,
                     {"summary": "honest reply: no recent inspection on file — booking one",
                      "preview": body[:110]})
            out["steps"].append({"action": "draft_honest_reply", "refused": claim["refused"],
                                 "draft": body,
                                 "why": "the reply admits the gap and books an inspection",
                                 "event": ev["id"]})
    elif c["label"] == "supply":
        gate.act("draft_supply_order", "nightdesk", report_id,
                 {"summary": m.get("text", "")[:60]})
        out["steps"].append({"action": "draft_supply_order", "why": "a human orders"})
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("reports", m)
    return out


def security_brief(m):
    """The supervisor's first thirty seconds, plus the two standing rules."""
    contract = store.by_id("contracts", m.get("contract_id")) or {}
    return {"site": contract.get("name") or contract.get("client"),
            "reported_at": m.get("at"), "verbatim": m.get("text"),
            "rules": ["software never closes a security incident",
                      "no code, key or combo ever moves through this system"],
            "first_move": ("call the client's after-hours contact from the contract sheet, then "
                           "the crew lead on site — in that order; the client hears it from us "
                           "before they find it themselves"),
            "note": "a head start for the supervisor — the follow-up and the close are human"}


def _complaint_reply_copy(m, claim):
    """Two shapes: cite the inspection, or admit the gap. Both end with the
    same make-right — a re-do tonight, not a debate."""
    contract = store.by_id("contracts", m.get("contract_id")) or {}
    site = contract.get("name") or "your building"
    if claim["assertable"]:
        return (f"Thanks for flagging this at {site}. Our last walk-through was "
                f"{str(claim['at'])[:10]} (scored {claim.get('score', '—')}/100, record "
                f"{claim['inspection']}), so something slipped since — tonight's crew will re-do "
                f"the area first, and the supervisor will photo-confirm before they leave.")
    return (f"Thanks for flagging this at {site}. Straight answer: we don't have a walk-through "
            f"on file recent enough to argue with you, so we won't. Tonight's crew re-does the "
            f"area first, and we're booking an inspection this week so next time we both have "
            f"the record.")


def close_incident(report_id, human=None):
    m = store.by_id("reports", report_id)
    if not m:
        return {"error": "no such report"}
    if m.get("label") == "security" and not human:
        ev = store.log_event("refused", report_id, "agent:nightdesk", "R0",
                             {"action": "close_security_incident",
                              "why": "a human closes a security incident after follow-up"})
        return {"refused": "a human closes a security incident after follow-up", "event": ev["id"]}
    m["closed_at"] = iso()
    store.upsert("reports", m)
    store.log_event("incident_closed", report_id,
                    f"human:{human}" if human else "agent:nightdesk", "R1" if human else "R2", {})
    return {"closed": True}


def coverage_sweep():
    out = {"proposed": 0}
    cb = core.coverage_board()
    for u in cb["uncovered"]:
        if not u["candidates"]:
            continue
        gate.act("propose_coverage", "scheduler", u["contract_id"],
                 {"summary": f"{u['contract']} uncovered tonight — {len(u['candidates'])} "
                             f"keyed candidate(s)"})
        out["proposed"] += 1
    return out


def run_all():
    handled = 0
    for m in store.load("reports"):
        if not m.get("handled_at"):
            handle_report(m["id"])
            handled += 1
    return {"reports": {"handled": handled}, "coverage": coverage_sweep()}
