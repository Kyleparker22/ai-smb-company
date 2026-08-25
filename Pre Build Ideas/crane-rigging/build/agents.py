#!/usr/bin/env python3
"""Rig OS — the agents. Everything routes through `core.gate`. Stdlib only."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import iso, now, parse


def handle_rfq(rfq_id):
    r = store.by_id("rfqs", rfq_id)
    if not r:
        return {"error": "no such RFQ"}
    flags = core.rfq_flags(r.get("text", ""))
    r.update(critical=flags["critical"], flags=flags["flags"], scanned_at=iso())
    store.upsert("rfqs", r)
    gate.act("scan_rfq", "estimator", rfq_id, {"flags": flags["flags"], "why": flags["why"]})
    out = {"rfq": rfq_id, "flags": flags, "steps": []}

    if flags["critical"]:
        ev = store.log_event("refused", rfq_id, "agent:estimator", "R0",
                             {"action": "quote_critical_as_taxi", "why": flags["why"]})
        body = _critical_copy(r, flags)
        out["steps"].append({"action": "route_to_engineering", "draft": body,
                             "refused": "flagged critical — the engineering path is the only path",
                             "why": flags["why"], "event": ev["id"]})
        return out

    okq, why = core.can_quote_firm(r)
    if not okq:
        ev = store.log_event("refused", rfq_id, "agent:estimator", "R0",
                             {"action": "quote_firm_without_site_data", "why": why})
        body = _site_visit_copy(r)
        out["steps"].append({"action": "estimate_pending_site_visit", "draft": body,
                             "refused": why, "event": ev["id"]})
    else:
        body = _quote_copy(r, why)
        gate.act("draft_quote", "estimator", rfq_id,
                 {"summary": why[:60], "preview": body[:110]})
        out["steps"].append({"action": "draft_quote", "draft": body, "why": why})
    return out


def _critical_copy(r, flags):
    who = (r.get("from") or "there").split()[0]
    return (f"Hi {who} — this one reads as a critical lift ({', '.join(flags['flags'])}), which "
            f"is a compliment to the job, not an obstacle: it gets an engineered plan, a named "
            f"lift director, and a crane picked by the chart instead of by habit. That takes a "
            f"few days and it's why nothing we set ends up in the news. Site walk this week?")


def _site_visit_copy(r):
    who = (r.get("from") or "there").split()[0]
    return (f"Hi {who} — we can give you a real number after a site look: exact radius, actual "
            f"weight, and what's between the crane and the set. A guessed radius becomes a "
            f"change-order fight on the day, and nobody enjoys those. The walk takes an hour — "
            f"when works?")


def _quote_copy(r, why):
    who = (r.get("from") or "there").split()[0]
    return (f"Hi {who} — quote attached, priced off the recorded site data ({why[:60]}). The "
            f"crane and configuration are named on the quote; if the weight or radius changes, "
            f"tell us before the morning of, not on it.")


def assign_operator(lift_id, operator_id):
    l = store.by_id("lifts", lift_id)
    o = store.by_id("operators", operator_id)
    if not l or not o:
        return {"error": "no such lift or operator"}
    crane = store.by_id("cranes", l.get("crane_id")) or {}
    oka, why = core.can_assign_operator(o, crane)
    if not oka:
        ev = store.log_event("refused", lift_id, "agent:scheduler", "R0",
                             {"action": "assign_uncertified_operator", "operator": operator_id,
                              "why": why})
        return {"refused": why, "event": ev["id"]}
    return gate.act("schedule_lift", "scheduler", lift_id,
                    {"summary": f"{o.get('name')} on {crane.get('desc')} ({why})"})


def schedule_lift(lift_id):
    l = store.by_id("lifts", lift_id)
    if not l:
        return {"error": "no such lift"}
    oks, why = core.can_schedule_lift(l)
    if not oks:
        ev = store.log_event("refused", lift_id, "agent:scheduler", "R0",
                             {"action": "approve_lift_plan", "why": why})
        return {"refused": why, "event": ev["id"]}
    return gate.act("schedule_lift", "scheduler", lift_id, {"summary": why[:80]})


def dispatch_today(lift_id, forecast_mph=None):
    l = store.by_id("lifts", lift_id)
    if not l:
        return {"error": "no such lift"}
    okd, why = core.can_dispatch_today(l, forecast_mph)
    if not okd:
        ev = store.log_event("refused", lift_id, "agent:dispatch", "R0",
                             {"action": "dispatch_over_wind_limit", "why": why})
        return {"refused": why, "event": ev["id"]}
    return {"dispatchable": True, "why": why}


def cert_sweep(limit=20, ref=None):
    ref = ref or now()
    out = {"alerts": 0}
    already = {(e["subject"], (e.get("detail") or {}).get("cert"))
               for e in store.events(kind="cert_alert", since_days=14)}
    for o in store.load("operators"):
        for cert, exp in (o.get("certs") or {}).items():
            d = parse(exp)
            if d and (d - ref).days <= 45 and (o["id"], cert) not in already:
                gate.act("cert_alert", "scheduler", o["id"],
                         {"summary": f"{o.get('name')}: {cert} expires in {(d - ref).days}d",
                          "cert": cert})
                out["alerts"] += 1
                if out["alerts"] >= limit:
                    return out
    return out


def run_all():
    scanned = 0
    for r in store.load("rfqs"):
        if not r.get("scanned_at"):
            handle_rfq(r["id"])
            scanned += 1
    return {"rfqs": {"scanned": scanned}, "certs": cert_sweep()}
