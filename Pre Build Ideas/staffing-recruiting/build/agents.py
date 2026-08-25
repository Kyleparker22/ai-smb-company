#!/usr/bin/env python3
"""Redeploy OS — the agents: shortlist, screen & schedule, packet, redeploy, credentials.

There is no code path in this file that sets a candidate to rejected. The
shortlist is a proposal; blockers are named; a recruiter decides.

Stdlib only.
"""
import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import days_until, iso, now, parse


# ---------------------------------------------------------------- 1 · database-first shortlist

def shortlist(req_id, ref=None):
    """The database BEFORE anything external. And the gap statement, which is
    the more valuable half when the database genuinely does not have it."""
    ref = ref or now()
    req = store.by_id("reqs", req_id)
    if not req:
        return {"error": "no such req"}
    res = core.rank_candidates(req, ref=ref)
    cands = store.index("candidates")
    rows = [{**r, "candidate": cands.get(r["candidate_id"], {}).get("display_name")}
            for r in res["ranked"]]
    blocked = [{**b, "candidate": cands.get(b["candidate_id"], {}).get("display_name")}
               for b in res["blocked"]]
    gap = core.gap_statement(req, res)
    g = gate.act("shortlist", "sourcing", req_id,
                 {"summary": f"{len(rows)} ranked of {res['considered']} on file"
                             + (" — GAP" if gap else ""),
                  "gap": gap})
    req["shortlisted_at"] = iso(ref)
    store.upsert("reqs", req)
    return {"req": req, "ranked": rows, "blocked": blocked, "gap": gap, "gate": g,
            "considered": res["considered"], "note": res["note"]}


def sweep_reqs(limit=15, ref=None):
    """Shortlists open reqs. Capped per run so the button stays responsive over
    an 11,000-row database — and the cap is REPORTED, never silent."""
    n, remaining = 0, 0
    for r in store.load("reqs"):
        if r.get("state") != "open" or r.get("shortlisted_at") or r.get("demo_tag"):
            continue
        if n >= limit:
            remaining += 1
            continue
        shortlist(r["id"], ref)
        n += 1
    return {"shortlisted": n, "left_for_the_next_run": remaining,
            "note": (f"capped at {limit} per run; {remaining} still waiting"
                     if remaining else "everything open was shortlisted")}


# ---------------------------------------------------------------- 2 · screen & schedule

def screen(candidate_id, req_id, answers=None, ref=None):
    """Logistics only. Availability, rate expectation, interest — captured, not
    judged. Anything evaluative is a recruiter's."""
    ref = ref or now()
    c = store.by_id("candidates", candidate_id)
    req = store.by_id("reqs", req_id)
    if not c or not req:
        return {"error": "unknown candidate or req"}
    a = answers or {"available_from": iso(ref + timedelta(days=2)),
                    "rate_expectation": req.get("pay_rate", 0) + 0.5,
                    "interested": True, "shift_ok": True}
    gate.act("screen_logistics", "screener", candidate_id,
             {"summary": f"{c.get('display_name')} · available {a['available_from'][:10]} · "
                         f"wants ${a['rate_expectation']}/hr", "req": req_id})
    sub = {"id": store.nid("sb"), "req_id": req_id, "candidate_id": candidate_id,
           "state": "screened", "screened_at": iso(ref), "answers": a}
    store.upsert("submissions", sub)

    sched = gate.act("schedule_interview", "screener", sub["id"],
                     {"summary": f"interview slot for {c.get('display_name')} with {req.get('client')}"})
    return {"submission": sub, "schedule": sched,
            "refused": "no evaluative judgement was made here — availability and rate are facts "
                       "the candidate stated, not a verdict on them"}


# ---------------------------------------------------------------- 3 · submission packet

def packet(submission_id, ref=None):
    ref = ref or now()
    sub = store.by_id("submissions", submission_id)
    if not sub:
        return {"error": "no such submission"}
    c = store.by_id("candidates", sub["candidate_id"]) or {}
    req = store.by_id("reqs", sub["req_id"]) or {}
    creds = [{"type": x["type"], **core.credential_state(x, ref)}
             for x in store.load("credentials") if x["candidate_id"] == c.get("id")]
    body = {
        "candidate": c.get("display_name"),
        "skills": c.get("skills"), "experience_months": c.get("verified_experience_months"),
        "availability": (sub.get("answers") or {}).get("available_from"),
        "rate": (sub.get("answers") or {}).get("rate_expectation"),
        "credentials": creds,
        "screening_notes": "availability and rate as stated by the candidate; no evaluative "
                           "judgement was made by the system",
        "format": req.get("client_format", "standard"),
    }
    gate.act("assemble_packet", "packets", submission_id,
             {"summary": f"packet for {c.get('display_name')} → {req.get('client')}"})
    res = gate.act("submit_to_client", "packets", submission_id,
                   {"summary": f"submit {c.get('display_name')} to {req.get('client')}",
                    "preview": f"{c.get('display_name')} · {', '.join(c.get('skills') or [])}"})
    sub["packet"] = body
    sub["state"] = "submitted" if res.get("executed") else "screened"
    if res.get("executed"):
        sub["submitted_at"] = iso(ref)
    store.upsert("submissions", sub)
    return {"packet": body, "gate": res,
            "time_to_submit_hours": core.time_to_submit(req, store.load("submissions"))}


# ---------------------------------------------------------------- 3b · Present — the branded render

def present(submission_id, ref=None):
    """The branded submittal: the recorded source résumé re-rendered into the
    agency's template. A reformat, never an enhancement — wording suggestions
    queue R1 with the original beside each one, and a render with no source
    behind it is refused."""
    ref = ref or now()
    sub = store.by_id("submissions", submission_id)
    if not sub:
        return {"error": "no such submission"}
    c = store.by_id("candidates", sub["candidate_id"]) or {}
    source = c.get("resume_source")
    if not source:
        store.log_event("refused", submission_id, "agent:present", "R0",
                        {"action": "render_without_source",
                         "why": "no source résumé on file — nothing to reformat, and inventing "
                                "one is the module's one forbidden act"})
        return {"refused": "no source résumé on file for this candidate. Ask for the résumé — "
                           "this module reformats a recorded document, it does not write one"}
    rendered = core.render_submittal(c, source)
    prov = core.provenance_check(rendered, source)
    g = gate.act("render_submittal", "present", submission_id,
                 {"summary": f"branded submittal for {c.get('display_name')} · "
                             f"{len(rendered['scrubbed_fields'])} contact field(s) withheld",
                  "provenance": "clean" if prov["clean"] else "UNSOURCED CLAIM FOUND"})
    polish = core.polish_suggestions(source)
    pg = None
    if polish:
        pg = gate.act("polish_wording", "present", submission_id,
                      {"summary": f"{len(polish)} wording suggestion(s) for "
                                  f"{c.get('display_name')} — original kept beside each",
                       "suggestions": polish})
    sub["submittal"] = {"rendered_at": iso(ref), "brand": rendered["brand"],
                        "scrubbed_fields": rendered["scrubbed_fields"],
                        "provenance_clean": prov["clean"]}
    store.upsert("submissions", sub)
    return {"rendered": rendered, "provenance": prov, "gate": g,
            "polish": {"suggestions": polish, "gate": pg,
                       "note": "drafted only — nothing is applied until a recruiter approves "
                               "the line"} if polish else
                      {"suggestions": [], "note": "no wording suggestions — the source reads fine"}}


# ---------------------------------------------------------------- 4 · redeploy watchtower

def redeploy(ref=None):
    ref = ref or now()
    due = core.redeploy_due(ref)
    cands = store.index("candidates")
    reqs = [r for r in store.load("reqs") if r.get("state") == "open"]
    out = []
    for d in due:
        a = store.by_id("assignments", d["assignment"])
        c = cands.get(d["candidate_id"], {})
        matches = []
        for r in reqs:
            res = core.rank_candidates(r, [c], ref)
            if res["ranked"]:
                matches.append({"req": r["id"], "client": r.get("client"),
                                "score": res["ranked"][0]["score"],
                                "reasons": res["ranked"][0]["reasons"]})
        matches.sort(key=lambda m: -m["score"])
        gate.act("open_redeploy", "redeploy", d["assignment"],
                 {"summary": f"{c.get('display_name')} ends in {d['days_to_end']} days · "
                             f"{len(matches)} open req(s) fit"})
        body = (f"[FOR THE RECRUITER] {c.get('display_name')}'s assignment at {d['client']} ends in "
                f"{d['days_to_end']} days. "
                + (f"{len(matches)} open req(s) fit — top is {matches[0]['client']}."
                   if matches else
                   "Nothing open fits them right now, which is worth knowing three weeks early "
                   "rather than on their last Friday."))
        res = gate.act("redeploy_outreach", "redeploy", d["assignment"],
                       {"summary": f"redeploy conversation with {c.get('display_name')}",
                        "preview": body[:120]})
        a["redeploy_opened"] = iso(ref)
        store.upsert("assignments", a)
        out.append({**d, "candidate": c.get("display_name"), "matches": matches[:3],
                    "body": body, "approval": res.get("approval")})
    return {"opened": len(out), "rows": out[:30],
            "note": "opened at T-21 days. The system never messages the worker itself — the "
                    "conversation about somebody's next assignment is a recruiter's"}


# ---------------------------------------------------------------- 5 · credentials

def credentials(ref=None):
    ref = ref or now()
    cands = store.index("candidates")
    active_ids = {a["candidate_id"] for a in store.load("assignments")
                  if a.get("state") == "active"}
    warned, unknown = [], []
    for c in store.load("credentials"):
        st = core.credential_state(c, ref)
        if st.get("_missing"):
            unknown.append({"candidate": cands.get(c["candidate_id"], {}).get("display_name"),
                            "type": c["type"], "why": st["_missing"]})
            continue
        if st["state"] not in ("expiring", "expired"):
            continue
        on_assignment = c["candidate_id"] in active_ids
        # Only the ACTIONABLE ones get their own event. A compliance sweep that
        # writes four thousand rows a day makes the audit log unreadable — and
        # the log is only useful if a human can still find the row that mattered.
        if on_assignment:
            gate.act("credential_warn", "compliance", c["candidate_id"],
                     {"summary": f"{st['label']} {st['state']} ({st['days_left']}d)",
                      "billing_impact": "ON ASSIGNMENT — they come off site the day it lapses "
                                        "and the billing stops"})
            gate.act("notify_client_credential", "compliance", c["candidate_id"],
                     {"summary": f"client notice: {st['label']} lapses in {st['days_left']} days"})
        warned.append({"candidate": cands.get(c["candidate_id"], {}).get("display_name"),
                       "type": c["type"], **st, "on_assignment": on_assignment})
    warned.sort(key=lambda w: w["days_left"])
    placed = sum(1 for w in warned if w["on_assignment"])
    gate.act("credential_warn", "compliance", f"sweep_{iso(ref)[:10]}",
             {"summary": f"{len(warned)} expiring or expired · {placed} of them on assignment · "
                         f"{len(unknown)} with no issue date on file"})
    return {"warned": warned[:40], "n": len(warned), "on_assignment": placed,
            "unknown": unknown[:12],
            "note": "a credential with no issue date on file is reported as unknowable, never "
                    "assumed current"}


def run_all():
    return {"reqs": sweep_reqs(), "redeploy": {"opened": redeploy()["opened"]},
            "credentials": {"warned": credentials()["n"]}}
