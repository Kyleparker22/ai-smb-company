#!/usr/bin/env python3
"""Case OS — the agents: intake, the records engine, demand assembly, client status.

No agent here answers a legal question. `intake()` runs the conflict check
BEFORE any substantive conversation, and a hit stops everything.

Stdlib only.
"""
import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import days_until, iso, now, parse


# ---------------------------------------------------------------- 1 · intake

def intake(lead_id, ref=None):
    ref = ref or now()
    lead = store.by_id("leads", lead_id)
    if not lead:
        return {"error": "no such lead"}
    cfg = store.load("config")
    out = {"lead": lead_id, "steps": []}

    # -- conflict FIRST, before anything substantive is said
    conf = core.conflict_check(lead.get("name"), lead.get("opposing"),
                               store.load("matters"), store.load("clients"))
    gate.act("conflict_check", "intake", lead_id,
             {"summary": "clear" if conf["clear"] else "CONFLICT", "hits": conf["hits"]})
    out["conflict"] = conf
    if not conf["clear"]:
        lead.update(handled_at=iso(ref), outcome="conflict_stop")
        store.upsert("leads", lead)
        out["steps"].append({"action": "conflict_stop", "why": conf["why"],
                             "said": "Before we go any further I need a lawyer here to check "
                                     "something on our side. Someone will call you straight back.",
                             "refused": "no facts were taken and no advice was given — a conflict "
                                        "hit stops the conversation, it does not slow it down"})
        return out

    # -- a legal question is routed, whatever else is in the message
    lq = core.legal_question(lead.get("message", ""))
    if lq["is_legal"]:
        gate.act("legal_advice", "intake", lead_id,
                 {"summary": "legal question — routed unanswered", "matched": lq["matched"]})
        out["steps"].append({"action": "route_to_attorney", "matched": lq["matched"],
                             "said": "That's a question for one of our attorneys rather than me — "
                                     "I can take the details now and have them call you today.",
                             "refused": "no case value, no liability opinion, no chances, no advice "
                                        "on whether to sign or settle"})

    s = core.screen(lead.get("facts", {}), cfg["criteria"])
    gate.act("screen_intake", "intake", lead_id,
             {"summary": s["verdict"], "why": s["why"]})
    out["screen"] = s
    lead["screen"] = s

    if s["verdict"] == "human_review":
        lead.update(handled_at=iso(ref), outcome="human_review")
        store.upsert("leads", lead)
        out["steps"].append({"action": "human_review", "why": s["why"],
                             "unknown": s["unknown"]})
        return out

    if s["verdict"] == "declined":
        lead.update(handled_at=iso(ref), outcome="declined", decline_reason=s["why"])
        store.upsert("leads", lead)
        out["steps"].append({
            "action": "decline_and_refer", "why": s["why"],
            "said": "This one isn't a fit for our firm, and I don't want to sit on it — here are "
                    "two firms that handle this kind of matter.",
            "note": "the reason is recorded so the firm can audit its own screening later"})
        return out

    def _send():
        lead.update(handled_at=iso(ref), outcome="retainer_sent")
        store.upsert("leads", lead)
        return lead_id

    res = gate.act("send_retainer", "intake", lead_id,
                   {"summary": f"{lead.get('name')} · {lead['facts'].get('case_type')} · "
                               f"meets every criterion", "preview": "retainer for e-signature"},
                   execute=_send)
    out["steps"].append({"action": "send_retainer", "result": res,
                         "said": "You meet everything we look for. I'm sending the agreement for "
                                 "signature now and an attorney will call you today.",
                         "refused": "the fee agreement itself waits for a human — a firm entering a "
                                    "relationship is not an automated act"})
    return out


def sweep_leads(limit=200):
    done = []
    for l in sorted(store.load("leads"), key=lambda x: x["at"]):
        if l.get("handled_at") or l.get("demo_tag"):
            continue
        done.append(intake(l["id"]))
        if len(done) >= limit:
            break
    return {"handled": len(done)}


# ---------------------------------------------------------------- 2 · records engine

def records_engine(ref=None):
    ref = ref or now()
    providers = store.index("providers")
    sent, followed, prepay, verified = 0, 0, 0, 0
    for r in store.load("records"):
        prov = providers.get(r.get("provider_id"), {})
        state = r.get("state", "drafted")

        if state == "drafted":
            matter = store.by_id("matters", r["matter_id"]) or {}
            packet = core.request_packet(prov, matter)
            if packet["prepay"]:
                res = gate.act("records_prepay", "records", r["id"],
                               {"summary": f"{prov.get('name')} requires prepayment "
                                           f"(${prov.get('prepay_amount', 25)})",
                                "packet": packet}, amount=prov.get("prepay_amount", 25))
                if not res.get("executed"):
                    r["state"] = "drafted"
                    r["blocked_on"] = "prepayment approval"
                    store.upsert("records", r)
                    prepay += 1
                    continue
            gate.act("send_records_request", "records", r["id"],
                     {"summary": f"{prov.get('name')} · {packet['format']}", "packet": packet})
            r.update(state="sent", sent_at=iso(ref), packet=packet, blocked_on=None)
            store.upsert("records", r)
            sent += 1
            continue

        if state == "sent":
            age = -(days_until(r.get("sent_at"), ref) or 0)
            expected = prov.get("turnaround_days", 21)
            if age > expected:
                gate.act("records_followup", "records", r["id"],
                         {"summary": f"{prov.get('name')} · {age}d, expected {expected}d",
                          "escalation": prov.get("escalation_contact")})
                r.setdefault("followups", []).append(iso(ref))
                store.upsert("records", r)
                followed += 1
            continue

        if state == "produced" and not r.get("verification"):
            prod = next((p for p in store.load("productions") if p.get("request_id") == r["id"]), None)
            if not prod:
                continue
            v = core.verify_production(
                {"date_from": r.get("date_from"), "date_to": r.get("date_to"),
                 "requested": ["records", "billing"], "patient_name": r.get("patient_name")},
                prod)
            r["verification"] = v
            if v["complete"]:
                gate.act("mark_production_complete", "records", r["id"],
                         {"summary": f"{prov.get('name')} verified complete"})
                r["state"] = "complete"
                prod["verified"] = True
                store.upsert("productions", prod)
                verified += 1
            else:
                r["state"] = "produced"
                r["blocked_on"] = f"{len(v['gaps'])} gap(s) — a supplemental request is needed"
            store.upsert("records", r)
    return {"sent": sent, "followed_up": followed, "waiting_on_prepay_approval": prepay,
            "verified_complete": verified,
            "note": "a production is complete only when verification finds zero gaps. An agent "
                    "cannot override that, and a PDF arriving is not the same as a file being whole"}


# ---------------------------------------------------------------- 3 · demand assembly

def demand_draft(matter_id, ref=None):
    ref = ref or now()
    m = store.by_id("matters", matter_id)
    if not m:
        return {"error": "no such matter"}
    comp = core.completeness(matter_id, ref)
    chron = core.build_chronology(matter_id)
    blocked = comp.get("_missing") or (comp.get("pct", 0) < 1.0)
    res = gate.act("draft_demand_facts", "demand", matter_id,
                   {"summary": f"{m.get('client_name')} · {len(chron['entries'])} cited entries",
                    "completeness": comp})
    return {"matter": matter_id, "completeness": comp, "chronology": chron, "gate": res,
            "blocked": blocked,
            "warning": ("THE FILE IS NOT COMPLETE. This draft covers only what has been verified; "
                        "an attorney decides whether to demand on a partial file."
                        if blocked else None),
            "header": f"[FOR ATTORNEY REVIEW — {m.get('attorney')}] Factual sections only. "
                      f"No demand figure is stated by this system."}


# ---------------------------------------------------------------- 4 · client status

def client_status(ref=None):
    ref = ref or now()
    board = core.case_board(ref)
    drafted = []
    for r in board["rows"]:
        if not (r["contact_overdue"] or r["no_contact_recorded"]):
            continue
        m = store.by_id("matters", r["matter"])
        if m and m.get("demo_tag"):
            continue                      # held out so the demo has live examples
        body = _status_copy(m, r)
        res = gate.act("client_status_update", "status", r["matter"],
                       {"summary": f"{r['client']} · "
                                   f"{'never contacted' if r['no_contact_recorded'] else str(r['days_since_contact']) + 'd silent'}",
                        "preview": body[:120]})
        store.upsert("contacts", {"id": store.nid("ct"), "matter_id": r["matter"],
                                  "at": iso(ref), "kind": "status_update",
                                  "approval": res.get("approval")})
        drafted.append({"matter": r["matter"], "client": r["client"], "body": body,
                        "executed": res.get("executed")})
    return {"drafted": len(drafted), "detail": drafted[:12],
            "note": "including the honest 'nothing changed this month, and here is why that is "
                    "normal at this stage' update — silence is the #1 bar complaint, not delay"}


def _status_copy(m, r):
    name = (r.get("client") or "there").split()[0]
    stage = m.get("stage")
    if stage == "treating":
        return (f"Hi {name} — nothing has changed on your case this month, and at this stage that "
                f"is normal: we don't request records until you're finished treating, because a "
                f"partial file weakens the demand. Keep going to your appointments and tell us "
                f"when you're released.")
    if stage == "records":
        return (f"Hi {name} — we're collecting your medical records and bills. "
                f"{r['completeness'].get('complete', 0)} of "
                f"{r['completeness'].get('of', '?')} providers are back so far. Providers move at "
                f"their own speed; we chase every one on a schedule.")
    if stage == "demand":
        return (f"Hi {name} — your demand package is being assembled from the records we've "
                f"verified. Your attorney reviews it before anything goes out.")
    return (f"Hi {name} — quick check-in on where things stand: your case is at the {stage} stage. "
            f"Nothing is needed from you right now.")


def run_all():
    return {"leads": sweep_leads(), "records": records_engine(),
            "status": {"drafted": client_status()["drafted"]}}
