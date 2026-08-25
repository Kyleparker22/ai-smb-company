#!/usr/bin/env python3
"""Consult OS — the agents.

Four: the concierge, the show-up ladder, the decision chaser, the cadence
engine. Every action goes through `core.gate`. The concierge's first move on
every message is the clinical read, and there is no code path in this file that
answers a clinical question — the refusal is structural, not a prompt.

Stdlib only.
"""
import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import iso, now, parse


# ---------------------------------------------------------------- 1 · concierge

def concierge(inquiry_id, ref=None):
    ref = ref or now()
    inq = store.by_id("inquiries", inquiry_id)
    if not inq:
        return {"error": "no such inquiry"}
    q = core.qualify(inq.get("text", ""))
    out = {"inquiry": inquiry_id, "read": q, "steps": []}
    gate.act("classify_inquiry", "concierge", inquiry_id,
             {"summary": inq.get("text", "")[:70], "read": q})

    inq["first_response_at"] = iso(ref)
    inq["read_tier"] = q["tier"]

    if q["tier"] == "urgent_clinical":
        gate.act("route_clinical", "concierge", inquiry_id,
                 {"summary": "possible complication — injector paged", "why": q["why"], "urgent": True})
        inq["routed"] = "urgent_clinical"
        store.upsert("inquiries", inq)
        out["steps"].append({"action": "route_clinical", "urgent": True, "why": q["why"],
                             "said": "I'm getting a nurse injector to you right now — please call the "
                                     "clinic line, and if you have vision changes, severe pain or "
                                     "trouble breathing, go to urgent care or call 911 first.",
                             "refused": "The system did not answer the medical question and did not "
                                        "reassure the patient. Both would be practising medicine."})
        return out

    if q["tier"] == "clinical":
        gate.act("route_clinical", "concierge", inquiry_id,
                 {"summary": "medical question — routed unanswered", "why": q["why"]})
        inq["routed"] = "clinical"
        store.upsert("inquiries", inq)
        out["steps"].append({"action": "route_clinical", "why": q["why"],
                             "said": "That one's for a licensed injector rather than me — I've sent it "
                                     "straight to them and they'll come back to you today. I can get "
                                     "you on the book in the meantime if you'd like.",
                             "refused": "no dosing, no units, no candidacy, no contraindication ruling"})
        return out

    # commercial: the agent may answer, book, and state a BAND
    svc = q["service"]
    if not svc:
        inq["routed"] = "clarifying"
        store.upsert("inquiries", inq)
        gate.act("answer_logistics", "concierge", inquiry_id,
                 {"summary": "no treatment named — asking rather than assuming"})
        out["steps"].append({"action": "ask_clarifying",
                             "said": "Happy to help — which treatment are you thinking about, so I "
                                     "book you with the right provider?"})
        return out

    spec = core.SERVICES[svc]
    gate.act("state_price_band", "concierge", inquiry_id,
             {"summary": f"{spec['label']} band ${spec['band'][0]}–${spec['band'][1]}", "service": svc})

    def _book():
        c = {"id": store.nid("con"), "patient_id": inq.get("patient_id"),
             "patient_name": inq.get("patient_name"), "service": svc,
             "starts_at": iso(ref + timedelta(days=3, hours=2)), "state": "booked",
             "created_at": iso(ref), "source_inquiry": inquiry_id, "touches": [],
             "consult_fee": core.CONSULT_FEE}
        store.upsert("consults", c)
        inq["consult_id"] = c["id"]
        store.upsert("inquiries", inq)
        return c["id"]

    res = gate.act("book_consult", "concierge", inquiry_id,
                   {"summary": f"{spec['label']} consult", "service": svc}, execute=_book)
    out["steps"].append({
        "action": "book_consult", "result": res,
        "said": f"{spec['label']} runs ${spec['band'][0]}–${spec['band'][1]} depending on what the "
                f"injector maps out with you. The consult is ${core.CONSULT_FEE} and it's credited "
                f"toward whatever you decide to do. I can hold Thursday at 2."})

    dep = gate.act("request_deposit", "concierge", inq.get("consult_id") or inquiry_id,
                   {"summary": f"${core.DEPOSIT} deposit to hold the chair"}, amount=core.DEPOSIT)
    out["steps"].append({"action": "request_deposit", "result": dep,
                         "said": "I'll send a link to hold it once the front desk okays the deposit.",
                         "refused": "the agent never touches card data — it sends a link, and only "
                                    "after a human approves the ask"})
    store.upsert("inquiries", inq)
    return out


def sweep_inquiries(limit=300):
    """Works the backlog. Deliberately steps over anything tagged for the
    walkthrough — a demo whose examples were already consumed by a batch job is
    a demo you cannot give."""
    done = []
    for i in sorted(store.load("inquiries"), key=lambda x: x["at"]):
        if i.get("first_response_at") or i.get("demo_tag"):
            continue
        done.append(concierge(i["id"]))
        if len(done) >= limit:
            break
    return {"answered": len(done), "recent": done[-3:]}


# ---------------------------------------------------------------- 2 · show-up ladder

def showup_ladder(ref=None):
    ref = ref or now()
    sent = 0
    for c in store.load("consults"):
        for t in core.due_showup(c, ref):
            body = _showup_copy(c, t)
            action = "request_deposit" if t["kind"] == "deposit" else "send_showup_touch"
            res = gate.act(action, "frontdesk", c["id"],
                           {"summary": f"{t['kind']} · {c.get('patient_name')}", "preview": body[:110]},
                           amount=core.DEPOSIT if t["kind"] == "deposit" else None)
            c.setdefault("touches", []).append({"kind": t["kind"], "at": iso(ref),
                                                "sent": bool(res.get("executed")), "body": body})
            store.upsert("consults", c)
            sent += 1
    return {"touches": sent}


def _showup_copy(c, t):
    name = (c.get("patient_name") or "there").split()[0]
    svc = core.SERVICES.get(c.get("service"), {}).get("label", "your consult")
    return {
        "deposit": f"Hi {name} — holding your {svc} consult. A ${core.DEPOSIT} deposit keeps the chair, "
                   f"and it comes straight off whatever you decide to do.",
        "expect": f"Hi {name} — quick note on Thursday: it's a mapping conversation, not a hard sell. "
                  f"You'll leave with a written plan whether or not you treat that day.",
        "confirm": f"Hi {name} — confirming Thursday 2:00 for your {svc} consult. Reply C to confirm "
                   f"or M to move it.",
        "morning": f"Hi {name} — see you at 2. We're in Suite 210, park in the deck on Ellery. "
                   f"You're with Dr. Vance.",
    }[t["kind"]]


def refill_cancellation(consult_id, ref=None):
    """A cancellation is a slot, and a slot goes cold in twenty minutes."""
    ref = ref or now()
    c = store.by_id("consults", consult_id)
    if not c:
        return {"error": "no such consult"}
    c["state"] = "cancelled"
    store.upsert("consults", c)
    plans = {p["patient_id"]: p for p in store.load("plans") if core.plan_state(p) == "presented"}
    waitlist = []
    for p in store.load("patients"):
        if not p.get("flexible"):
            continue
        plan = plans.get(p["id"])
        waitlist.append({"patient": p["name"], "patient_id": p["id"],
                         "value": plan["amount"] if plan else None,
                         "why": ("has an undecided plan worth "
                                 f"${plan['amount']:,.0f}" if plan else "on the flexible list"),
                         "distance_min": p.get("distance_min")})
    waitlist.sort(key=lambda r: (-(r["value"] or 0), r["distance_min"] or 99))
    res = gate.act("refill_cancellation", "frontdesk", consult_id,
                   {"summary": f"{len(waitlist)} on the ranked list — wave one is the top 3"})
    return {"cancelled": consult_id, "ranked": waitlist[:10], "wave_one": waitlist[:3],
            "gate": res,
            "note": "waves, not a blast — the list stops the moment the chair is filled"}


# ---------------------------------------------------------------- 3 · decision chaser

def decision_chaser(ref=None):
    ref = ref or now()
    drafted, closed = 0, 0
    for p in store.load("plans"):
        if core.plan_state(p, ref) == "expired" and p.get("state") == "presented":
            def _close(p=p):
                p.update(state="declined", decline_reason="unreachable", decided_at=iso(ref))
                store.upsert("plans", p)
                return p["id"]
            gate.act("close_plan_declined", "chaser", p["id"],
                     {"summary": f"${p['amount']:,.0f} plan, {core.PLAN_TTL_DAYS}d with no decision",
                      "decline_reason": "unreachable"}, execute=_close)
            closed += 1
            continue
        for t in core.due_decision(p, ref):
            body = _decision_copy(p, t)
            res = gate.act("draft_decision_touch", "chaser", p["id"],
                           {"summary": f"{t['kind']} · ${p['amount']:,.0f} · {p['patient_name']}",
                            "preview": body[:110]})
            p.setdefault("touches", []).append({"day": t["day"], "kind": t["kind"],
                                                "drafted_at": iso(ref), "approval": res.get("approval"),
                                                "body": body})
            store.upsert("plans", p)
            drafted += 1
    return {"drafted": drafted, "closed": closed}


def _decision_copy(plan, t):
    name = plan["patient_name"].split()[0]
    who = plan.get("provider", "your injector")
    obj = plan.get("objection")
    if t["kind"] == "recap":
        return (f"Hi {name} — {who} here. Writing up what we mapped out: {plan['summary']}. "
                f"Nothing expires on you; I just want it in writing so you can sit with it.")
    if t["kind"] == "options":
        base = f"Hi {name} — thinking about what you said"
        if obj == "price":
            return base + " on the number. We can stage it — do the area that bothers you most first, and revisit in the fall."
        if obj == "nervous":
            return base + " about it looking overdone. My approach is under-treat and reassess at two weeks; that visit is included."
        if obj == "spouse_partner":
            return base + " about talking it over. Happy to have you both in for ten minutes, no charge and no pressure."
        if obj == "timing":
            return base + " on timing. If the event is the driver, here is the last date that still leaves settling time."
        return base + " — here are the options we discussed, written out."
    if t["kind"] == "check":
        return (f"Hi {name} — still thinking on the plan? Either way is fine, I just don't want to "
                f"leave it hanging on your chart.")
    return (f"Hi {name} — last note from me on this. I'll close it out, and it's easy to pick back "
            f"up whenever you want.")


# ---------------------------------------------------------------- 4 · cadence engine

def cadence_engine(ref=None):
    ref = ref or now()
    rows = core.drift_list(ref)
    if rows:
        gate.act("flag_cadence_drift", "cadence", f"drift_{iso(ref)[:10]}",
                 {"summary": f"{len(rows)} patients past their own interval, ranked by their value"})
    unknown = []
    tx = store.load("treatments")
    for p in store.load("patients"):
        c = core.cadence_state(p, tx, ref)
        if c.get("_missing"):
            unknown.append({"patient": p["name"], "why": c["_missing"]})
    return {"drifting": rows[:40], "n": len(rows),
            "not_flagged": unknown[:12],
            "note": "a patient with no recorded treatment history is never flagged — "
                    "we would be guessing at a clock that does not exist"}


def run_all():
    return {"inquiries": sweep_inquiries(), "showup": showup_ladder(),
            "decisions": decision_chaser(), "cadence": {"n": cadence_engine()["n"]}}
