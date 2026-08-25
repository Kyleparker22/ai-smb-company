#!/usr/bin/env python3
"""Renewal OS — the agents: watchtower, remarket, COI desk, cross-sell, claims.

No agent here quotes, binds, or gives a coverage opinion. Material client
communication is drafted for a licensed producer, and the drafts say so.

Stdlib only.
"""
import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import days_until, iso, now, parse


# ---------------------------------------------------------------- 1 · renewal watchtower

def watchtower(ref=None, horizon=90):
    ref = ref or now()
    pols = store.index("policies")
    quiet, material = 0, []
    for r in store.load("renewals"):
        if r.get("triaged_at"):
            continue
        pol = pols.get(r["policy_id"])
        if not pol:
            continue
        d = int(days_until(r["effective"], ref) or 999)
        if d > horizon or d < -30:
            continue
        c = core.classify_renewal(pol, r)
        r.update(triaged_at=iso(ref), material=c["material"], cause=c["cause"],
                 delta_pct=c["premium_delta_pct"])
        store.upsert("renewals", r)
        gate.act("classify_renewal", "watchtower", r["id"],
                 {"summary": f"{pol['line']} · {c['why']}", "cause": c["cause"]})
        if not c["material"]:
            gate.act("quiet_renewal_touch", "watchtower", r["id"],
                     {"summary": f"quiet renewal — {c['why']}",
                      "preview": _quiet_copy(pol, c)})
            quiet += 1
        else:
            body = _material_copy(pol, r, c)
            res = gate.act("draft_renewal_call", "watchtower", r["id"],
                           {"summary": f"{pol['line']} {c['why']} · {core.CAUSES[c['cause']]}",
                            "preview": body[:130], "cause": c["cause"]})
            material.append({"renewal": r["id"], "policy": pol["id"], "line": pol["line"],
                             "delta_pct": c["premium_delta_pct"], "cause": c["cause"],
                             "cause_note": c["cause_note"], "coverage_changes": c["coverage_changes"],
                             "body": body, "approval": res.get("approval"),
                             "days_out": d})
    material.sort(key=lambda m: (m["days_out"], -(abs(m["delta_pct"] or 0))))
    return {"quiet": quiet, "material": material,
            "note": "quiet renewals get a light touch automatically; a material change is a "
                    "conversation a licensed producer owns"}


def material_queue(ref=None, horizon=90):
    """READS the queue. Distinct from `watchtower()`, which is the sweep that
    triages new renewals — a screen that silently re-runs a sweep shows an empty
    list the second time somebody opens it."""
    ref = ref or now()
    pols = store.index("policies")
    out = []
    for r in store.load("renewals"):
        if not r.get("material") or r.get("outcome"):
            continue
        pol = pols.get(r["policy_id"])
        if not pol:
            continue
        d = int(days_until(r["effective"], ref) or 999)
        if d > horizon or d < -30:
            continue
        c = core.classify_renewal(pol, r)
        out.append({"renewal": r["id"], "policy": pol["id"], "line": pol["line"],
                    "household": (store.by_id("households", pol["household_id"]) or {}).get("name"),
                    "producer": pol.get("producer"), "carrier": pol.get("carrier"),
                    "delta_pct": c["premium_delta_pct"], "cause": c["cause"],
                    "cause_note": c["cause_note"], "coverage_changes": c["coverage_changes"],
                    "body": _material_copy(pol, r, c), "days_out": d})
    out.sort(key=lambda m: (m["days_out"], -(abs(m["delta_pct"] or 0))))
    shown = out[:80]
    return {"material": shown, "total": len(out),
            # No silent truncation: if the screen is showing a subset, it says so.
            "truncated": (f"showing the {len(shown)} closest to their effective date of {len(out)}"
                          if len(shown) < len(out) else None),
            "quiet_handled": sum(1 for e in store.load("events")
                                 if e["kind"] == "quiet_renewal_touch"),
            "note": "quiet renewals get a light touch automatically; a material change is a "
                    "conversation a licensed producer owns"}


def coi_state():
    """READS the certificate desk, same reason."""
    issued, escalated, waiting = [], [], []
    for c in store.load("certificates"):
        k = core.classify_certificate(c)
        row = {"id": c["id"], "holder": c.get("holder"), "why": k["why"],
               "reasons": k["reasons"], "language": c.get("requested_language"),
               "requested_at": c.get("requested_at")}
        if c.get("escalated_at"):
            escalated.append(row)
        elif c.get("issued_by") == "agent":
            issued.append({**row, "executed": True})
        elif not c.get("issued_at"):
            waiting.append(row)
    issued.sort(key=lambda r: r.get("requested_at") or "", reverse=True)
    escalated.sort(key=lambda r: r.get("requested_at") or "", reverse=True)
    return {"issued": issued[:40], "escalated": escalated[:40], "waiting": len(waiting),
            "note": "non-standard language is a hard stop, not a lower confidence score — "
                    "nobody auto-issues an additional insured"}


def _quiet_copy(pol, c):
    return (f"Your {core.LINES[pol['line']]['label'].lower()} renewal is on its way and nothing "
            f"material changed this term. Nothing for you to do — we've checked it.")


def _material_copy(pol, r, c):
    d = c["premium_delta_pct"]
    move = f"up {d:.0%}" if d and d > 0 else f"down {abs(d):.0%}" if d else "changed"
    lines = [f"[FOR PRODUCER REVIEW — {pol.get('producer','unassigned')}]",
             f"Your {core.LINES[pol['line']]['label'].lower()} renews {r['effective'][:10]} and the "
             f"premium is {move}.",
             f"What we can see caused it: {core.CAUSES[c['cause']]}."]
    if c["coverage_changes"]:
        lines.append("The coverage also changed: " + "; ".join(
            f"{x['field']} was {x['was']}, now {x['now']}" for x in c["coverage_changes"]) + ".")
    if c["cause"] == "unknown":
        lines.append("The carrier did not state a reason — we are asking them before we call you.")
    lines.append("I'd like ten minutes before it takes effect so you hear it from me first.")
    return " ".join(lines)


# ---------------------------------------------------------------- 2 · remarket packet

def remarket(policy_id, quote=None, ref=None):
    """Assembles the submission from our own data, then produces the comparison —
    which refuses to render on price alone."""
    ref = ref or now()
    pol = store.by_id("policies", policy_id)
    if not pol:
        return {"error": "no such policy"}
    hh = store.by_id("households", pol["household_id"]) or {}
    claims = [c for c in store.load("claims") if c.get("policy_id") == policy_id]
    submission = {"named_insured": hh.get("name"), "line": pol["line"],
                  "expiring_premium": pol["premium"], "coverage": pol.get("coverage", {}),
                  "loss_history": [{"date": c["date"], "paid": c["paid"], "type": c["type"]}
                                   for c in claims],
                  "years_with_agency": hh.get("years_with_agency"),
                  "assembled_at": iso(ref)}
    gate.act("assemble_remarket", "remarket", policy_id,
             {"summary": f"submission for {hh.get('name')} · {pol['line']}"})
    comp = core.comparison_sheet(pol, quote) if quote else None
    if comp:
        res = gate.act("present_comparison", "remarket", policy_id,
                       {"summary": ("comparison ready" if comp.get("renderable")
                                    else "comparison REFUSED — no coverage schedule"),
                        "renderable": comp.get("renderable")})
        comp["gate"] = res
    return {"submission": submission, "comparison": comp}


# ---------------------------------------------------------------- 3 · COI desk

def coi_desk(ref=None):
    ref = ref or now()
    issued, escalated = [], []
    for c in store.load("certificates"):
        if c.get("issued_at") or c.get("escalated_at"):
            continue
        k = core.classify_certificate(c)
        if k["kind"] == "standard":
            def _issue(c=c):
                c["issued_at"] = iso(ref)
                c["issued_by"] = "agent"
                store.upsert("certificates", c)
                return c["id"]
            res = gate.act("issue_standard_coi", "coi", c["id"],
                           {"summary": f"{c.get('holder')} · matches {c.get('prior_certificate')}",
                            "why": k["why"]}, execute=_issue)
            issued.append({"id": c["id"], "holder": c.get("holder"), "why": k["why"],
                           "executed": res.get("executed")})
        else:
            gate.act("issue_nonstandard_coi", "coi", c["id"],
                     {"summary": f"{c.get('holder')} — {', '.join(k['reasons'])}", "why": k["why"]})
            c["escalated_at"] = iso(ref)
            c["escalation_reasons"] = k["reasons"]
            store.upsert("certificates", c)
            escalated.append({"id": c["id"], "holder": c.get("holder"),
                              "reasons": k["reasons"], "why": k["why"],
                              "language": c.get("requested_language")})
    return {"issued": issued, "escalated": escalated,
            "note": "non-standard language is a hard stop, not a lower confidence score — "
                    "nobody auto-issues an additional insured"}


# ---------------------------------------------------------------- 4 · cross-sell

def cross_sell(ref=None, limit=40):
    pol = store.load("policies")
    rows = []
    for h in store.load("households"):
        s = core.cross_sell_score(h, pol)
        if s["score"] > 0:
            rows.append({"household": h["name"], "household_id": h["id"], **s})
    rows.sort(key=lambda r: -r["score"])
    if rows:
        gate.act("cross_sell_list", "crosssell", f"xs_{iso(ref or now())[:10]}",
                 {"summary": f"{len(rows)} mono-line households ranked for the producers"})
    return {"rows": rows[:limit], "n": len(rows),
            "permitted_factors": list(core.PERMITTED_FACTORS),
            "note": "scored on agency data only — policies held, tenure, prior quotes, recorded "
                    "life events, claim-free years, premium. No purchased data, and no inference "
                    "about anyone's protected characteristics"}


# ---------------------------------------------------------------- 5 · claims touch

def claims_touch(ref=None):
    ref = ref or now()
    out = []
    for c in store.load("claims"):
        if c.get("state") != "open" or c.get("touched_at"):
            continue
        hh = store.by_id("households", c.get("household_id")) or {}
        body = (f"[FOR PRODUCER — {c.get('producer','unassigned')}] {hh.get('name')} has an open "
                f"{c['type']} claim from {c['date'][:10]}. Nothing to decide — this is the check-in "
                f"call, and it is the one that keeps the account at renewal.")
        res = gate.act("claims_touch", "claims", c["id"],
                       {"summary": f"{hh.get('name')} · open {c['type']} claim", "preview": body[:120]})
        c["touched_at"] = iso(ref)
        store.upsert("claims", c)
        out.append({"claim": c["id"], "approval": res.get("approval"), "body": body})
    return {"drafted": len(out), "detail": out[:10]}


def run_all():
    return {"watchtower": {"quiet": watchtower()["quiet"]}, "coi": coi_desk(),
            "cross_sell": {"n": cross_sell()["n"]}, "claims": claims_touch()}
