#!/usr/bin/env python3
"""Fix OS — the agents. Everything routes through `core.gate`. Stdlib only."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import iso, now, parse


def _unit_for(m):
    if m.get("unit_id"):
        return store.by_id("units", m["unit_id"])
    who = m.get("from")
    if not who:
        return None
    return next((u for u in store.load("units") if u.get("customer") == who), None)


def handle_message(msg_id):
    m = store.by_id("messages", msg_id)
    if not m:
        return {"error": "no such message"}
    c = core.read_message(m.get("text", ""))
    out = {"message": msg_id, "classification": c, "steps": []}
    gate.act("read_message", "intake", msg_id, {"label": c["label"], "why": c["why"]})
    unit = _unit_for(m)

    if c["label"] == "safety_symptom":
        script = core.SAFETY_SCRIPT_GAS if c.get("gas") else core.SAFETY_SCRIPT_GENERAL
        body = _safety_copy(m, script)
        # Structural: the customer's own words survive verbatim in the draft.
        assert m.get("text", "") in body and script in body
        ev = store.log_event("refused", msg_id, "agent:intake", "R0",
                             {"action": "dismiss_safety_symptom",
                              "why": "the symptom rides verbatim — software never downgrades it"})
        gate.act("draft_safety_reply", "intake", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_safety_reply", "draft": body,
                             "refused": "nothing here softens the symptom — the script leads and "
                                        "a technician calls next, ahead of everything routine",
                             "why": c["why"], "event": ev["id"]})
    elif c["label"] in ("warranty_repair", "cod_repair"):
        if unit:
            covered, cov_why = core.warranty_active(unit)
        else:
            covered, cov_why = False, ("no unit on file for this customer — COD until a serial "
                                       "and proof of purchase are recorded")
        route = "warranty" if covered else "cod"
        appliance = c.get("appliance") or (unit or {}).get("appliance")
        ptb = core.parts_to_bring(appliance, c.get("symptom"), unit)
        job = {"id": store.nid("jb"), "message_id": msg_id, "customer": m.get("from"),
               "unit_id": (unit or {}).get("id"), "appliance": appliance,
               "symptom": c.get("symptom"), "kind": route, "coverage_basis": cov_why,
               "parts_to_bring": ptb.get("parts"), "parts_basis": ptb.get("basis"),
               "opened_at": iso(), "visits": 0, "work": []}
        rc = core.recall_check(unit) if unit else {"flagged": False}
        if rc.get("flagged"):
            job["recall_notice"] = rc["notice"]  # verbatim — never summarized, never dropped
        store.upsert("jobs", job)
        if rc.get("flagged"):
            gate.act("flag_recall", "dispatch", job["id"], {"notice": rc["notice"]})
        gate.act("log_ticket", "dispatch", job["id"],
                 {"route": route, "parts": ptb.get("parts"), "coverage": cov_why})
        body = _repair_copy(m, route, cov_why, ptb)
        gate.act("draft_repair_reply", "intake", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "log_ticket", "job": job["id"], "route": route,
                             "parts_to_bring": ptb.get("parts"), "parts_basis": ptb.get("basis"),
                             "recall_notice": job.get("recall_notice"), "draft": body,
                             "why": f"routed {route} from the recorded coverage — {cov_why}"})
    elif c["label"] == "status":
        job = next((j for j in store.load("jobs")
                    if j.get("customer") == m.get("from") and not j.get("closed_at")), None)
        body = _status_copy(m, job)
        gate.act("draft_status_reply", "intake", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_status_reply", "draft": body,
                             "why": "answered from the job record, never from memory"})
    elif c["label"] == "parts_ask":
        body = _parts_copy(m)
        gate.act("draft_parts_reply", "intake", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_parts_reply", "draft": body,
                             "why": "the recorded parts order does the talking"})
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("messages", m)
    return out


def _safety_copy(m, script):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — you told us: \"{m.get('text', '')}\". {script} A technician is being "
            f"called about this right now, ahead of everything routine — you'll hear a human "
            f"voice shortly. Please don't run the appliance again until they've seen it.")


def _repair_copy(m, route, cov_why, ptb):
    who = (m.get("from") or "there").split()[0]
    parts = ", ".join(ptb.get("parts") or [])
    if route == "warranty":
        return (f"Hi {who} — good news: our records show this unit is covered ({cov_why}), so "
                f"the repair goes through the manufacturer at no charge to you. The ticket is "
                f"open and the tech comes with the likely parts already on the truck"
                + (f" ({parts})" if parts else "")
                + " — one visit is the goal. We'll confirm a window shortly.")
    return (f"Hi {who} — the ticket is open. Our records show this repair is out of warranty "
            f"({cov_why}), so we quote before any work: you authorize an amount, and nothing "
            f"past it happens without your OK — that's a rule in our system, not a promise. "
            f"The tech comes with the likely parts"
            + (f" ({parts})" if parts else "") + " so one visit can finish it.")


def _status_copy(m, job):
    who = (m.get("from") or "there").split()[0]
    if not job:
        return (f"Hi {who} — I don't show an open ticket under your name, so rather than guess, "
                f"a person is pulling the record now and will answer from it — not from memory.")
    parts = ", ".join(job.get("parts_to_bring") or [])
    return (f"Hi {who} — from the ticket record: your {job.get('appliance') or 'appliance'} "
            f"job is open and scheduled"
            + (f", parts staged: {parts}" if parts else "")
            + ". Everything in this answer comes from the record — nothing is estimated.")


def _parts_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — checking the recorded parts orders against your ticket now; the answer "
            f"comes from the order record, not from memory. If the part is in, we book the "
            f"visit in the same reply.")


# ---------------------------------------------------------------- claims

def submit_claim(claim_id):
    """The claim gate. Incomplete → refused with every missing field named;
    complete → drafts at R1 for a human to release. There is no third path."""
    c = store.by_id("claims", claim_id)
    if not c:
        return {"error": "no such claim"}
    okc, why = core.can_submit(c)
    if not okc:
        missing, _ = core.claim_completeness(c)
        ev = store.log_event("refused", claim_id, "agent:claims", "R0",
                             {"action": "submit_incomplete_claim", "why": why,
                              "missing": missing})
        return {"refused": why, "missing": missing, "event": ev["id"]}
    r = gate.act("submit_claim", "claims", claim_id,
                 {"summary": f"${c.get('amount', 0):,.2f} to {c.get('make')} — "
                             f"{c.get('failure_code')}",
                  "fields": {f: bool(c.get(f)) for f in core.REQUIRED_CLAIM_FIELDS}})
    return {"ok": True, "why": why, "gate": r}


def draft_narrative(claim_id, fields=None):
    c = store.by_id("claims", claim_id)
    if not c:
        return {"error": "no such claim"}
    n = core.assemble_narrative(c, fields)
    if "refused" in n:
        ev = store.log_event("refused", claim_id, "agent:claims", "R0",
                             {"action": "invent_failure_narrative", "why": n["refused"]})
        return {"refused": n["refused"], "event": ev["id"]}
    c["narrative"] = n["narrative"]
    store.upsert("claims", c)
    return dict(n, claim=claim_id)


# ---------------------------------------------------------------- the COD clamp

def add_work(job_id, desc, amount):
    """Inside the recorded authorization: executes at R2. Past it: no path —
    a refused event plus an overage draft the CUSTOMER approves."""
    j = store.by_id("jobs", job_id)
    if not j:
        return {"error": "no such job"}
    amount = float(amount or 0)
    okw, why = core.can_add_work(j, amount)
    if not okw:
        ev = store.log_event("refused", job_id, "agent:bench", "R0",
                             {"action": "exceed_authorized_amount", "why": why,
                              "amount": amount})
        out = {"refused": why, "event": ev["id"]}
        if core.authorization(j) is not None:
            out["overage"] = gate.act("draft_overage_request", "bench", job_id,
                                      {"summary": f"+${amount:,.2f} {desc}"[:80], "work": desc},
                                      amount=amount)
        return out
    j.setdefault("work", []).append({"desc": desc, "amount": amount, "at": iso()})
    store.upsert("jobs", j)
    gate.act("add_work", "bench", job_id, {"desc": desc, "amount": amount, "why": why})
    return {"ok": True, "why": why, "total": core.job_total(j)}


# ---------------------------------------------------------------- sweeps (skip demo rows)

def message_sweep(limit=40):
    out = {"handled": 0}
    for m in store.load("messages"):
        if out["handled"] >= limit or m.get("handled_at") or m.get("demo_tag"):
            continue
        handle_message(m["id"])
        out["handled"] += 1
    return out


def claims_sweep(limit=40):
    """Every open claim goes through the gate: complete ones draft for release,
    incomplete ones are refused with the fields named. Demo rows are skipped —
    they belong to the demo buttons."""
    out = {"drafted": 0, "refused": 0}
    for c in store.load("claims"):
        if out["drafted"] + out["refused"] >= limit or c.get("submitted_at") \
           or c.get("demo_tag"):
            continue
        r = submit_claim(c["id"])
        out["refused" if "refused" in r else "drafted"] += 1
    return out


def run_all():
    return {"messages": message_sweep(), "claims": claims_sweep()}
