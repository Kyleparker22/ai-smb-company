#!/usr/bin/env python3
"""Haul OS — the agents. Everything routes through `core.gate`. Stdlib only."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import iso, now


def answer_item(msg_id):
    """Answer one 'can I throw X away' question. Allowed answers at R2 with the
    weight caveat; hazardous is a refusal with human routing; unknown routes."""
    m = store.by_id("messages", msg_id)
    if not m:
        return {"error": "no such message"}
    c = core.classify_item(m.get("text", ""))
    out = {"message": msg_id, "classification": c, "steps": []}
    gate.act("classify_item", "frontdesk", msg_id, {"label": c["label"], "why": c["why"]})

    if c["label"] == "hazardous":
        ev = store.log_event("refused", msg_id, "agent:frontdesk", "R0",
                             {"action": "approve_hazardous_item", "kind": c.get("kind"),
                              "why": c["why"]})
        out["steps"].append({"action": "refuse_and_route", "kind": c.get("kind"),
                             "said": f"That can't go in the container ({c.get('kind','prohibited').replace('_',' ')}). "
                                     f"Someone will call you shortly with disposal options.",
                             "why": c["why"], "event": ev["id"]})
    elif c["label"] == "allowed":
        gate.act("answer_allowed_item", "frontdesk", msg_id,
                 {"summary": m.get("text", "")[:60]},
                 execute=lambda: True)
        out["steps"].append({"action": "answer_allowed_item",
                             "said": f"Yes, that's fine. Note: {c['note']}.",
                             "why": c["why"]})
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("messages", m)
    return out


def try_charge(charge_id):
    c = store.by_id("charges", charge_id)
    if not c:
        return {"error": "no such charge"}
    v = core.charge_check(c)
    if not v["assertable"]:
        ev = store.log_event("refused", charge_id, "agent:billing", "R0",
                             {"action": "assert_charge_without_ticket", "why": v["refused"]})
        return {**v, "event": ev["id"]}
    body = _charge_copy(c, v)
    r = gate.act("draft_charge", "billing", charge_id,
                 {"summary": f"{c['kind']} ${c.get('amount',0):,.0f}", "evidence": v["evidence"],
                  "preview": body[:110]})
    return {**v, "gate": r, "draft": body}


def _charge_copy(c, v):
    """The charge conversation, drafted with the evidence named up front —
    the ticket or photo does the arguing, not the tone."""
    amt = f"${c.get('amount', 0):,.0f}"
    if c["kind"] == "overweight":
        return (f"Your container came in over the included weight — scale ticket "
                f"{v['evidence']} is attached with the exact numbers. The overage is {amt} at "
                f"the posted per-ton rate. Question about the ticket? Call and we'll walk it.")
    return (f"Our crew found prohibited material in the load — photo record {v['evidence']} "
            f"attached. The handling charge is {amt}. If the photos don't match what you loaded, "
            f"call us before this bills — we'd rather sort it than argue it.")


def missed_pickup_sweep(ref=None):
    """Every late pull gets one drafted make-right per 3 days: apology, new
    date, and the site's own facts. Late is late — the copy never disputes it."""
    ref = ref or now()
    out = {"drafted": 0}
    already = {e["subject"] for e in store.events(kind="queued_for_approval", since_days=3)
               if (e.get("detail") or {}).get("action") == "draft_pickup_makeright"}
    for row in core.missed_pickups(ref):
        if row["order"] in already:
            continue
        body = (f"We missed the pickup we promised on {str(row['promised_at'])[:10]} — that's on "
                f"us, no excuses. The pull is first on tomorrow's route, and today's rental days "
                f"since the promise are off the bill. Reply if tomorrow doesn't work.")
        gate.act("draft_pickup_makeright", "dispatch", row["order"],
                 {"summary": f"{row['days_late']}d late on {row['container']}",
                  "preview": body[:110]})
        out["drafted"] += 1
    return out


def idle_sweep():
    out = {"flagged": 0}
    already = {e["subject"] for e in store.events(kind="flag_idle_container", since_days=3)}
    for r in core.idle_containers():
        if not r.get("flagged") or r["container"] in already:
            continue
        gate.act("flag_idle_container", "dispatch", r["container"],
                 {"summary": f"{r['days']}d on site at {r.get('site','?')} with no pull ordered"})
        out["flagged"] += 1
    return out


def run_all():
    handled = 0
    for m in store.load("messages"):
        if not m.get("handled_at"):
            answer_item(m["id"])
            handled += 1
    return {"messages": {"handled": handled}, "idle": idle_sweep(),
            "makerights": missed_pickup_sweep()}
