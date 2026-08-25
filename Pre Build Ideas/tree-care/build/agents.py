#!/usr/bin/env python3
"""Canopy OS — the agents. Everything routes through `core.gate`. Stdlib only."""
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
    gate.act("read_message", "frontdesk", msg_id, {"label": c["label"], "why": c["why"]})

    if c["label"] == "emergency":
        gate.act("route_emergency", "frontdesk", msg_id,
                 {"summary": m.get("text", "")[:60], "verbatim": m.get("text", "")})
        out["steps"].append({"action": "route_emergency", "said": core.EMERGENCY_ACK,
                             "why": c["why"]})
    elif c["label"] == "hazard_ask":
        ev = store.log_event("refused", msg_id, "agent:frontdesk", "R0",
                             {"action": "assert_tree_safety", "why": c["why"]})
        body = _assessment_copy(m)
        gate.act("draft_assessment_visit", "frontdesk", msg_id,
                 {"summary": f"arborist visit: {m.get('text','')[:50]}", "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_assessment_visit", "draft": body,
                             "refused": "no safety verdict from software — the visit is the answer",
                             "why": c["why"], "event": ev["id"]})
    elif c["label"] == "quote":
        body = _quote_copy(m)
        gate.act("draft_schedule_reply", "frontdesk", msg_id,
                 {"summary": f"site-look reply: {m.get('text','')[:50]}", "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "route_to_site_look", "draft": body,
                             "why": "a real number needs eyes on the tree and the access"})
    elif c["label"] == "schedule":
        gate.act("draft_schedule_reply", "frontdesk", msg_id,
                 {"summary": m.get("text", "")[:60]})
        out["steps"].append({"action": "draft_schedule_reply", "why": "a human sends"})
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("messages", m)
    return out


def _assessment_copy(m):
    """The hazard-ask reply: books the arborist, judges nothing. Tested to
    contain neither verdict word."""
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — good question to ask, and the honest answer is that nobody should "
            f"answer it from a text, including us. Our certified arborist can look this week: "
            f"they'll check root flare, lean change, deadwood and cavities on site, and give you "
            f"a written assessment. Want morning or afternoon?")


def _quote_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — happy to price it. Tree work quotes off the actual tree and the access "
            f"(what's under it, what the equipment can reach), so we do a quick site look first — "
            f"free, usually inside 2 days. Reply with the address and any gate details.")


def _estimate_chase_copy(e, touch_n):
    who = (e.get("customer_name") or "there").split()[0]
    amt = f"${e.get('amount', 0):,.0f}"
    desc = e.get("desc", "the tree work")
    return {
        1: (f"Hi {who} — following up on the estimate for {desc} ({amt}). It holds 30 days from "
            f"the site visit; if the scope changed, tell us and we'll re-walk it."),
        2: (f"Hi {who} — second note on {desc} ({amt}). Crews are booking about two weeks out; "
            f"a yes this week gets you on the board before storm season fills it."),
        3: (f"Hi {who} — last note on {desc} ({amt}); we'll leave it with you. If the tree "
            f"changes — new lean, new deadwood — call us and we'll look again either way."),
    }.get(touch_n, f"Hi {who} — following up on {desc} ({amt}).")


def _phc_copy(p):
    who = (p.get("customer_name") or "there").split()[0]
    return (f"Hi {who} — your {p.get('program', 'plant health care')} program comes due on "
            f"{str(p.get('next_due', ''))[:10]}. Same trees, same schedule as last season; reply Y "
            f"to renew or tell us what changed in the yard.")


def schedule_job(job_id):
    j = store.by_id("jobs", job_id)
    if not j:
        return {"error": "no such job"}
    oks, why = core.can_schedule(j)
    if not oks:
        ev = store.log_event("refused", job_id, "agent:scheduler", "R0",
                             {"action": "schedule_powerline_unclear", "why": why})
        return {"refused": why, "event": ev["id"]}
    return gate.act("schedule_job", "scheduler", job_id, {"summary": why})


def estimate_sweep(limit=15):
    out = {"drafted": 0, "skipped": 0}
    for e in store.load("estimates"):
        if out["drafted"] >= limit:
            break
        plan = core.estimate_plan(e)
        if plan["action"] != "draft_chase":
            out["skipped"] += 1
            continue
        touch_n = len(e.get("touches") or []) + 1
        body = _estimate_chase_copy(e, touch_n)
        gate.act("draft_estimate_chase", "sales", e["id"],
                 {"summary": f"{e.get('desc','estimate')} ${e.get('amount',0):,.0f} touch {touch_n}",
                  "preview": body[:110]})
        e.setdefault("touches", []).append({"at": iso(), "kind": "drafted", "body": body})
        store.upsert("estimates", e)
        out["drafted"] += 1
    return out


def phc_sweep(limit=15):
    out = {"drafted": 0}
    recent = {ev["subject"] for ev in store.events(kind="queued_for_approval", since_days=14)
              if (ev.get("detail") or {}).get("action") == "draft_phc_renewal"}
    for row in core.phc_due():
        if out["drafted"] >= limit or row["renewed"] or row["phc"] in recent:
            continue
        p = store.by_id("phc", row["phc"])
        body = _phc_copy(p)
        gate.act("draft_phc_renewal", "sales", p["id"],
                 {"summary": f"{p.get('program')} due {row['next_due'][:10]}", "preview": body[:110]})
        out["drafted"] += 1
    return out


def run_all():
    handled = 0
    for m in store.load("messages"):
        if not m.get("handled_at"):
            handle_message(m["id"])
            handled += 1
    return {"messages": {"handled": handled}, "estimates": estimate_sweep(),
            "phc": phc_sweep()}
