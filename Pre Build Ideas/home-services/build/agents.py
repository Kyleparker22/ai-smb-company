#!/usr/bin/env python3
"""Dispatch OS — the agents.

Four of them, and every action they take goes through `core.gate`, which either
executes it (R2/R3) or turns it into a row a human decides (R0/R1). No agent
here decides its own rung, states a price, or sends anything outward on its own.

Agent names are internal. Nothing in this file surfaces a name to a homeowner —
external surfaces describe the OS by function (`CLAUDE.md` §External-surface).

Stdlib only.
"""
import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import days_until, iso, now, parse


# ---------------------------------------------------------------- 1 · front desk

def front_desk(call_id, actor_note=None):
    """Answer one inbound. Emergency stop first, then qualify, then offer only
    slots the board can actually honour."""
    call = store.by_id("calls", call_id)
    if not call:
        return {"error": "no such call"}
    out = {"call": call_id, "steps": []}

    c = core.classify(call.get("transcript", ""))
    gate.act("classify_call", "frontdesk", call_id,
             {"summary": f"{call.get('transcript','')[:60]}…", "classification": c})
    out["classification"] = c

    if c["emergency"]:
        gate.act("route_emergency", "frontdesk", call_id,
                 {"summary": "emergency signal — human on the line now", "why": c["why"]})
        call.update(outcome="answered", routed="human_emergency", handled_at=iso())
        store.upsert("calls", call)
        out["steps"].append({"action": "route_emergency", "why": c["why"],
                             "said": "I'm getting a person on the line with you right now. "
                                     "If you smell gas or see fire, leave the house and call 911 first."})
        return out

    if not c["job_class"]:
        gate.act("ask_clarifying", "frontdesk", call_id,
                 {"summary": "no symptom matched — asking rather than guessing", "why": c["why"]})
        call.update(outcome="answered", routed="clarifying", handled_at=iso())
        store.upsert("calls", call)
        out["steps"].append({"action": "ask_clarifying", "why": c["why"],
                             "said": "So I send the right technician — is it heating and cooling, "
                                     "plumbing, or electrical?"})
        return out

    cust = store.by_id("customers", call.get("customer_id")) or {}
    zone = cust.get("zone", "central")
    if not core.in_service_area(zone):
        call.update(outcome="answered", routed="out_of_area", handled_at=iso())
        store.upsert("calls", call)
        out["steps"].append({"action": "decline_out_of_area",
                             "said": "That address is outside the service area — referring out."})
        return out

    slots = core.open_slots(store.load("slots"), c["job_class"], zone)
    if not slots:
        out["steps"].append({"action": "no_capacity",
                             "why": "no slot on the board has the skill, the minutes and the drive time",
                             "said": "I don't have an honest opening today — putting you first on "
                                     "tomorrow's board and a dispatcher will confirm."})
        call.update(outcome="answered", routed="waitlist", handled_at=iso())
        store.upsert("calls", call)
        return out

    slot = slots[0]
    after_hours = slot["slot_class"] == core.AFTER_HOURS
    action = "book_after_hours" if after_hours else "book_standard_slot"
    fee = core.AFTER_HOURS_FEE if after_hours else core.DIAGNOSTIC_FEE

    def _book():
        job = {"id": store.nid("job"), "customer_id": call.get("customer_id"),
               "job_class": c["job_class"], "trade": c["trade"], "urgency": c["urgency"],
               "slot_id": slot["id"], "scheduled_for": slot["starts_at"], "zone": zone,
               "created_at": iso(), "source_call": call_id, "status": "scheduled",
               "diagnostic_fee": fee}
        store.upsert("jobs", job)
        slot_row = store.by_id("slots", slot["id"])
        slot_row["booked_job"] = job["id"]
        store.upsert("slots", slot_row)
        call.update(outcome="answered", booked_job=job["id"], handled_at=iso())
        store.upsert("calls", call)
        return job["id"]

    res = gate.act(action, "frontdesk", call_id, amount=fee if after_hours else None,
                   detail={"summary": f"{core.JOB_CLASSES[c['job_class']]['label']} → "
                                      f"{slot['starts_at'][:16]} ({slot['tech_name']})",
                           "fee_quoted": fee, "drive_minutes": slot["drive_minutes"]},
                   execute=_book)
    out["steps"].append({"action": action, "result": res, "slot": slot,
                         "said": (f"I can get {slot['tech_name']} out {slot['starts_at'][11:16]} "
                                  f"— the diagnostic is ${fee}.")
                         if res.get("executed") else
                         "That window carries the after-hours rate, so I'm putting it in front of "
                         "a dispatcher to confirm before I commit to it."})
    return out


def sweep_calls(limit=200):
    """Every unhandled call, oldest first. Steps over anything tagged for the
    walkthrough — a demo whose examples a batch job already ate is not a demo."""
    handled = []
    for c in sorted(store.load("calls"), key=lambda x: x["at"]):
        if c.get("handled_at") or c.get("outcome") == "missed" or c.get("demo_tag"):
            continue
        handled.append(front_desk(c["id"]))
        if len(handled) >= limit:
            break
    return {"handled": len(handled), "results": handled[-5:]}


# ---------------------------------------------------------------- 2 · estimate recovery

def estimate_recovery(ref=None):
    """No estimate rests in 'presented'. Due ladder steps become drafts; past
    TTL becomes a recorded expiry with a reason."""
    ref = ref or now()
    drafted, expired = [], []
    for e in store.load("estimates"):
        state = core.estimate_state(e, ref)
        if state == "expired" and e.get("state") == "presented":
            def _close(e=e):
                e.update(state="lost", loss_reason="unreachable", decided_at=iso(ref),
                         closed_by="expiry_rule")
                store.upsert("estimates", e)
                return e["id"]
            gate.act("close_estimate_lost", "recovery", e["id"],
                     {"summary": f"${e['amount']:,.0f} {e['scope']} — {core.ESTIMATE_TTL_DAYS}d with no decision",
                      "loss_reason": "unreachable"}, execute=_close)
            expired.append(e["id"])
            continue
        for t in core.due_touches(e, ref):
            body = _touch_copy(e, t)
            res = gate.act("draft_estimate_touch", "recovery", e["id"],
                           {"summary": f"{t['kind']} touch · ${e['amount']:,.0f} · {e['customer_name']}",
                            "preview": body[:120], "channel": t["channel"], "day": t["day"]})
            e.setdefault("touches", []).append(
                {"day": t["day"], "channel": t["channel"], "kind": t["kind"],
                 "drafted_at": iso(ref), "approval": res.get("approval"), "body": body})
            store.upsert("estimates", e)
            drafted.append({"estimate": e["id"], "touch": t["kind"], "approval": res.get("approval")})
    return {"drafted": len(drafted), "expired": len(expired), "detail": drafted[:8]}


def _touch_copy(est, touch):
    """Copy in the technician's voice, referencing the actual scope. Never a
    price the tech did not already put in writing."""
    who, scope, amt = est.get("tech_name", "our technician"), est["scope"], est["amount"]
    name = est["customer_name"].split()[0]
    if touch["kind"] == "recap":
        return (f"Hi {name} — {who} here. Recapping what I found: {scope}. The quote I left you is "
                f"${amt:,.0f}, good for {core.ESTIMATE_TTL_DAYS} days. Happy to walk through the photo "
                f"I took if it helps you talk it over.")
    if touch["kind"] == "options":
        return (f"Hi {name} — sending the options for the {scope} we talked about, plus the financing "
                f"link if spreading it out is easier. No pressure either way; I'd rather you decide "
                f"with the numbers in front of you.")
    if touch["kind"] == "call":
        return (f"[call task for {who}] {name} — {scope}, ${amt:,.0f}, quoted "
                f"{est['presented_at'][:10]}. The tech who quoted it makes this call, not the office.")
    if touch["kind"] == "check":
        return (f"Hi {name} — still thinking on the {scope}? Totally fine either way, I just don't want "
                f"to keep it open on your account if you've moved on.")
    return (f"Hi {name} — last note from me on the {scope}. I'll close it out on our side, and if "
            f"anything changes the quote's easy to refresh.")


# ---------------------------------------------------------------- 3 · deferred-work ledger

def read_tech_notes():
    """Turn job notes into structured recommendations. A note that parses to
    nothing is surfaced, never dropped."""
    made, unparsed = [], []
    for j in store.load("jobs"):
        if not j.get("tech_note") or j.get("note_parsed"):
            continue
        p = core.parse_note(j["tech_note"])
        for r in p["recommendations"]:
            rec = {"id": store.nid("rec"), "job_id": j["id"], "customer_id": j.get("customer_id"),
                   "component": r["component"], "trade": r["trade"], "matched": r["matched"],
                   "typical": r["typical"], "urgency": r["urgency"],
                   "state": "declined" if j.get("note_declined", True) else "sold",
                   "declined_at": j.get("completed_at"), "source_note": j["tech_note"]}
            store.upsert("recommendations", rec)
            gate.act("log_deferred_work", "ledger", rec["id"],
                     {"summary": f"{r['component']} from job {j['id']}", "matched": r["matched"]})
            made.append(rec["id"])
        if p["unparsed"]:
            unparsed.append({"job": j["id"], "note": p["unparsed"]})
        j["note_parsed"] = iso()
        store.upsert("jobs", j)
    return {"recommendations": len(made), "unparsed_for_a_human": unparsed[:10],
            "note": "an unparsed note is listed here, never discarded"}


def seasonal_campaign(ref=None):
    """Build this month's re-offer list. Staged for the owner — never sent."""
    ref = ref or now()
    due, held = [], []
    custs = store.index("customers")
    for r in store.load("recommendations"):
        ok, why = core.reoffer_due(r, ref)
        (due if ok else held).append({"rec": r["id"], "component": r.get("component"),
                                      "customer": custs.get(r.get("customer_id"), {}).get("name"),
                                      "value": core.COMPONENTS.get(r.get("component"), {}).get("typical"),
                                      "why": why})
    if due:
        gate.act("stage_seasonal_campaign", "ledger", f"campaign_{ref.strftime('%Y_%m')}",
                 {"summary": f"{len(due)} re-offers worth "
                             f"${sum(d['value'] or 0 for d in due):,.0f} — staged for the owner",
                  "month": ref.month})
    return {"month": ref.month, "due": due, "held": held[:12],
            "value": round(sum(d["value"] or 0 for d in due), 2)}


# ---------------------------------------------------------------- 4 · dispatch assist

def propose_board(day=None):
    """Proposes the board and nothing else. This action never climbs a rung —
    who goes where is a judgement about people, and it stays a human's."""
    slots = [s for s in store.load("slots") if not s.get("booked_job")]
    jobs = [j for j in store.load("jobs") if j.get("status") == "scheduled" and not j.get("assigned_tech")]
    proposals = []
    for j in jobs:
        spec = core.JOB_CLASSES.get(j["job_class"], {})
        fits = [s for s in slots if spec.get("trade") in s.get("skills", [])]
        ranked = sorted(
            fits, key=lambda s: (core.drive_minutes(s.get("from_zone", "central"), j.get("zone", "central")),
                                 -s.get("minutes_free", 0)))[:3]
        proposals.append({
            "job": j["id"], "class": spec.get("label"), "zone": j.get("zone"),
            "options": [{"tech": s["tech_name"], "starts": s["starts_at"],
                         "drive": core.drive_minutes(s.get("from_zone", "central"), j.get("zone", "central")),
                         "free": s.get("minutes_free"),
                         "why": f"{s['tech_name']} carries {spec.get('trade')}, "
                                f"{core.drive_minutes(s.get('from_zone','central'), j.get('zone','central'))}m drive"}
                        for s in ranked]})
    gate.act("propose_board", "dispatch", f"board_{iso()[:10]}",
             {"summary": f"{len(proposals)} unassigned jobs, ranked options for the dispatcher"})
    return {"proposals": proposals,
            "note": "proposals only — the dispatcher moves the board; this action never promotes"}


# ---------------------------------------------------------------- run everything

def run_all():
    return {"calls": sweep_calls(), "estimates": estimate_recovery(),
            "notes": read_tech_notes(), "campaign": seasonal_campaign(),
            "board": {"proposals": len(propose_board()["proposals"])}}
