#!/usr/bin/env python3
"""Claim OS — the agents. Everything routes through `core.gate`. Stdlib only."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import iso, now, parse


def triage_sweep():
    out = {"triaged": 0}
    for d in store.load("denials"):
        if d.get("kind"):
            continue
        t = core.triage_denial(d)
        d.update(kind=t["kind"], why=t["why"])
        store.upsert("denials", d)
        gate.act("triage_denial", "denials", d["id"], {"kind": t["kind"], "why": t["why"]})
        out["triaged"] += 1
    return out


def recode(claim_id, new_code):
    c = store.by_id("claims", claim_id)
    if not c:
        return {"error": "no such claim"}
    okr, why = core.can_recode(c, new_code)
    if not okr:
        ev = store.log_event("refused", claim_id, "agent:coding", "R0",
                             {"action": "upcode_without_documentation", "why": why})
        return {"refused": why, "event": ev["id"]}
    if "downcode" in why:
        return gate.act("downcode_claim", "coding", claim_id, {"summary": why},
                        execute=lambda: store.upsert("claims", dict(c, cpt=new_code)))
    return gate.act("submit_claim", "coding", claim_id, {"summary": why})


def submit(claim_id):
    c = store.by_id("claims", claim_id)
    if not c:
        return {"error": "no such claim"}
    oks, why = core.can_submit(c)
    if not oks:
        ev = store.log_event("refused", claim_id, "agent:billing", "R0",
                             {"action": "submit_incomplete_claim", "why": why})
        return {"refused": why, "event": ev["id"]}
    return gate.act("submit_claim", "billing", claim_id, {"summary": why})


def _appeal_copy(d, claim, touch_n):
    """The appeal draft — reason code cited, documentation referenced, claim
    reference only (PHI-scrubbed by the check, structurally)."""
    body = (f"Re: claim {claim.get('id')} (DOS {str(claim.get('date_of_service', ''))[:10]}), "
            f"denied under {d.get('carc')}. Enclosed: the rendering provider's documentation "
            f"({claim.get('provider_doc_ref') or 'to be attached by the provider'}) supporting "
            f"medical necessity as billed. We request reconsideration within your appeal window. "
            f"— {'Second and final written appeal before a call.' if touch_n >= 2 else 'First appeal.'}")
    okp, why = core.phi_scrub_ok(body)
    assert okp, why  # structural: appeal drafts carry no identifiers
    return body


def appeal_sweep(limit=15):
    out = {"drafted": 0, "to_human": 0, "skipped": 0}
    for d in store.load("denials"):
        if out["drafted"] >= limit:
            break
        plan = core.appeal_plan(d)
        if plan["action"] == "draft_appeal":
            claim = store.by_id("claims", d.get("claim_id")) or {}
            touch_n = len(d.get("touches") or []) + 1
            body = _appeal_copy(d, claim, touch_n)
            gate.act("draft_appeal", "denials", d["id"],
                     {"summary": f"{d.get('carc')} appeal touch {touch_n}", "preview": body[:110]})
            d.setdefault("touches", []).append({"at": iso(), "kind": "drafted", "body": body})
            store.upsert("denials", d)
            out["drafted"] += 1
        elif plan["action"] == "human":
            out["to_human"] += 1
        else:
            out["skipped"] += 1
    return out


def filing_sweep(limit=25):
    out = {"alerts": 0}
    already = {e["subject"] for e in store.events(kind="filing_alert", since_days=7)}
    for row in core.at_risk_board()["rows"]:
        if out["alerts"] >= limit or row["claim"] in already or row["expired"]:
            continue
        gate.act("filing_alert", "denials", row["claim"],
                 {"summary": f"${row['amount']:,.0f} at {row['payer']} — {row['days_left']}d to the window",
                  "days_left": row["days_left"]})
        out["alerts"] += 1
    return out


def run_all():
    return {"triage": triage_sweep(), "appeals": appeal_sweep(), "filing": filing_sweep()}
