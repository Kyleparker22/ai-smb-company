#!/usr/bin/env python3
"""Traveler OS — the agents. Everything routes through `core.gate`. Stdlib only."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import iso


def handle_rfq(rfq_id):
    """Scan an RFQ for cert flags, then attempt the quote arithmetic."""
    r = store.by_id("rfqs", rfq_id)
    if not r:
        return {"error": "no such RFQ"}
    flags = core.rfq_flags(r.get("text", ""))
    r.update(cert_required=flags["cert_required"], flags=flags["flags"], scanned_at=iso())
    store.upsert("rfqs", r)
    gate.act("scan_rfq", "estimator", rfq_id, {"flags": flags["flags"], "why": flags["why"]})
    out = {"rfq": rfq_id, "flags": flags, "steps": []}

    q = core.quote_rfq(r)
    if q.get("refused"):
        ev = store.log_event("refused", rfq_id, "agent:estimator", "R0",
                             {"action": "quote_stale_material", "why": q["refused"]})
        out["steps"].append({"action": "refuse_quote", "refused": q["refused"], "event": ev["id"]})
    else:
        body = _quote_copy(r, q, flags)
        gate.act("draft_quote", "estimator", rfq_id,
                 {"summary": f"${q['total']:,.0f} — {q['note'][:50]}", "preview": body[:110]})
        out["steps"].append({"action": "draft_quote", "quote": q, "draft": body,
                             "why": "a human sends, with the arithmetic shown"})
    return out


def _quote_copy(r, q, flags):
    """The quote cover a human sends — the number, its basis, and the cert
    regime named back to the customer so scope is agreed before chips fly."""
    cert_line = ""
    if flags["cert_required"]:
        cert_line = (f" We read this as {', '.join(f.upper() for f in flags['flags'])} work — "
                     f"cert paperwork is priced in and ships with the parts; tell us if we've "
                     f"read that wrong.")
    return (f"Quote attached: ${q['total']:,.0f}, priced on material bought this month "
            f"({q.get('note', '')[:60]}).{cert_line} Valid 14 days — metal moves, and we'd rather "
            f"requote than surprise you.")


def ship_job(job_id):
    """The shipping path — through the cert gate, always."""
    j = store.by_id("jobs", job_id)
    if not j:
        return {"error": "no such job"}
    oks, why = core.can_ship(j)
    if not oks:
        ev = store.log_event("refused", job_id, "agent:shipping", "R0",
                             {"action": "ship_without_certs", "why": why})
        return {"refused": why, "event": ev["id"]}
    return gate.act("release_to_ship", "shipping", job_id, {"summary": why})


def promise(job_id):
    j = store.by_id("jobs", job_id)
    if not j:
        return {"error": "no such job"}
    p = core.promise_date(j.get("hours_remaining") or j.get("est_hours") or 0)
    if p.get("_missing"):
        ev = store.log_event("refused", job_id, "agent:scheduler", "R0",
                             {"action": "promise_without_capacity", "why": p["_missing"]})
        return {"refused": p["_missing"], "event": ev["id"]}
    gate.act("draft_promise_date", "scheduler", job_id,
             {"summary": f"promise {p['date'][:10]} — {p['basis'][:60]}"})
    return {"promise": p, "note": "a human commits — the arithmetic is shown"}


def run_all():
    scanned = 0
    for r in store.load("rfqs"):
        if not r.get("scanned_at"):
            handle_rfq(r["id"])
            scanned += 1
    return {"rfqs": {"scanned": scanned}}
