#!/usr/bin/env python3
"""Plat OS — the agents. Everything routes through `core.gate`. Stdlib only."""
import re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import iso, now, parse


def handle_message(msg_id):
    m = store.by_id("messages", msg_id)
    if not m:
        return {"error": "no such message"}
    c = core.read_message(m.get("text", ""))
    out = {"message": msg_id, "classification": c, "steps": []}
    gate.act("read_message", "desk", msg_id, {"label": c["label"], "why": c["why"]})

    if c["label"] == "boundary_question":
        row = core.record_boundary_question(m.get("text", ""), m.get("from"), m.get("job_id"))
        ev = store.log_event("refused", row["id"], "agent:desk", "R0",
                             {"action": "state_boundary_conclusion",
                              "verbatim": m.get("text", ""), "from": m.get("from"),
                              "why": "software never states where a line falls"})
        body = _boundary_copy(m)
        okb, why = core.boundary_reply_ok(body)
        assert okb, why  # structural: the shipped copy passes its own check
        gate.act("draft_boundary_reply", "desk", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110],
                  "routed_to": core.recorded_pls()["name"]})
        m["draft_reply"] = body
        out["steps"].append({"action": "route_to_pls", "recorded": row["id"], "draft": body,
                             "refused": "no boundary conclusion from this message — the "
                                        "question is recorded verbatim and the recorded PLS "
                                        "answers on the sealed record",
                             "why": c["why"], "event": ev["id"]})
    elif c["label"] == "deadline_risk":
        job = store.by_id("jobs", m.get("job_id")) if m.get("job_id") else None
        if not job:
            out["steps"].append({"action": "route_human",
                                 "why": "deadline risk with no job on the record — a person "
                                        "matches it before anything is promised"})
        else:
            p = core.promise_closing_reply(job)
            if "refused" in p:
                ev = store.log_event("refused", job["id"], "agent:desk", "R1",
                                     {"action": "promise_closing_date", "why": p["refused"]})
                out["steps"].append({"action": "promise_closing_date",
                                     "refused": p["refused"], "event": ev["id"]})
            else:
                body = _deadline_copy(m, p["projection"])
                gate.act("draft_deadline_reply", "desk", job["id"],
                         {"summary": m.get("text", "")[:60], "preview": body[:110],
                          "projection": p["projection"]})
                m["draft_reply"] = body
                out["steps"].append({"action": "draft_deadline_reply", "draft": body,
                                     "projection": p["projection"],
                                     "why": "flagged to a human BEFORE closing week — the "
                                            "projection is the recorded clocks' arithmetic"})
    elif c["label"] == "status":
        job = store.by_id("jobs", m.get("job_id")) if m.get("job_id") else None
        body = _status_copy(m, job)
        gate.act("draft_status_reply", "desk", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_status_reply", "draft": body,
                             "why": "answered from the pipeline record"})
    elif c["label"] == "quote":
        parsed = _parse_quote(m.get("text", ""))
        math = core.quote_math(parsed["job_type"], parsed.get("acreage"))
        if "refused" in math:
            ev = store.log_event("refused", msg_id, "agent:desk", "R0",
                                 {"action": "quote_without_comparables", "why": math["refused"],
                                  "asked": m.get("text", "")[:80]})
            out["steps"].append({"action": "quote_without_comparables",
                                 "refused": math["refused"], "event": ev["id"]})
        else:
            body = _quote_copy(m, parsed, math)
            gate.act("draft_quote", "desk", msg_id,
                     {"summary": f"${math['amount']:,.0f} — {math['basis'][:60]}",
                      "preview": body[:110]})
            m["draft_reply"] = body
            out["steps"].append({"action": "draft_quote", "draft": body, "math": math,
                                 "why": "the comparables' median drafts; a human sends"})
    elif c["label"] == "records":
        body = _records_copy(m)
        gate.act("draft_records_reply", "desk", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_records_reply", "draft": body,
                             "why": "the cited chain does the talking"})
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("messages", m)
    return out


def _parse_quote(text):
    t = (text or "").lower()
    acre = re.search(r"(\d+(?:\.\d+)?)[\s-]*acres?", t)
    for kind in ("alta", "topo", "subdivision", "mortgage"):
        if kind in t:
            jt = {"mortgage": "mortgage_loc"}.get(kind, kind)
            break
    else:
        jt = "boundary"
    return {"job_type": jt, "acreage": float(acre.group(1)) if acre else None}


def _boundary_copy(m):
    who = (m.get("from") or "there").split()[0]
    pls = core.recorded_pls()
    return (f"Hi {who} — that is exactly the question a survey exists to answer, and it can "
            f"only be answered one way: by our licensed surveyor, {pls['name']} ({pls['license']}), "
            f"on the sealed record. Nothing in this message says where the line falls — software "
            f"can't, and anyone unlicensed who does is guessing with your property. Your question "
            f"is recorded verbatim and is in front of {pls['name']} now; you'll get a sealed "
            f"answer, not an opinion.")


def _deadline_copy(m, p):
    who = (m.get("from") or "there").split()[0]
    verdict = ("on the recorded clocks it seals in time" if p.get("makes_it")
               else "on the recorded clocks it is TIGHT — a person is on it today")
    return (f"Hi {who} — from our own stage clocks ({p['basis']}): this job is in "
            f"{p['stage']} with a projected {p['projected_days_to_seal']} days to seal against "
            f"{p['days_to_closing']} days to your closing — {verdict}. A person confirms before "
            f"we promise anything against a closing; you'll hear from us today.")


def _status_copy(m, job):
    who = (m.get("from") or "there").split()[0]
    if job:
        chain = core.chain_check(job)
        cited = f"{chain.get('cited', 0)} instrument(s) cited" if "ok" in chain else "chain pending"
        return (f"Hi {who} — from the pipeline record: job {job['id']} is in {job['stage']}, "
                f"{cited}"
                + (f", closing on file {job['closing_date'][:10]}" if job.get("closing_date") else "")
                + ". That's the record, not a recollection — a person follows up with anything it doesn't show.")
    return (f"Hi {who} — pulling the pipeline record for your job now; you'll get the exact "
            f"stage and what's ahead of it in a moment, from the record rather than memory.")


def _quote_copy(m, parsed, math):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — for a {parsed['job_type']} survey at {math['bucket']}: "
            f"${math['amount']:,.0f}, the {math['basis']}. Recorded range "
            f"${math['range'][0]:,.0f}–${math['range'][1]:,.0f}. A person confirms scope before "
            f"this becomes a commitment.")


def _records_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — the research chain is on the record for every job we draft: deed book "
            f"and page, prior plats, and points of beginning, cited instrument by instrument. "
            f"Pulling the references you asked about now; you'll get the citations themselves, "
            f"not a summary of them.")


# ---------------------------------------------------------------- the seal gate

def seal_plat(job_id, seal_number=None, seal_date=None, pls=None):
    """A plat is 'sealed' only with its recorded seal reference — number AND
    date — and only by the PLS. There is no code path to sealed without them."""
    j = store.by_id("jobs", job_id)
    if not j:
        return {"error": "no such job"}
    if not seal_number or not seal_date:
        ev = store.log_event("refused", job_id, "agent:pipeline", "R0",
                             {"action": "seal_without_reference",
                              "why": "no seal reference — a plat is sealed by its recorded "
                                     "number and date, and there is no path without them"})
        return {"refused": "a plat is sealed by its recorded seal reference — number and date. "
                           "There is no path to 'sealed' without them.", "event": ev["id"]}
    if not pls:
        return {"refused": "the seal is the PLS's act — a licensed human records it, "
                           "software never seals on its own"}
    j["seal"] = {"number": seal_number, "date": seal_date}
    j["stage"] = "sealed"
    j.setdefault("stage_log", []).append({"stage": "sealed", "at": iso()})
    store.upsert("jobs", j)
    ev = store.log_event("mark_plat_sealed", job_id, f"human:{pls}", "R1",
                         {"seal": j["seal"]})
    return {"sealed": True, "seal": j["seal"], "event": ev["id"]}


# ---------------------------------------------------------------- the chain gate

def begin_draft(job_id):
    """Move a job to the draft stage — refused without its research chain."""
    j = store.by_id("jobs", job_id)
    if not j:
        return {"error": "no such job"}
    chain = core.chain_check(j)
    if "refused" in chain:
        ev = store.log_event("refused", job_id, "agent:pipeline", "R0",
                             {"action": "draft_without_research_chain", "why": chain["refused"]})
        return {"refused": chain["refused"], "event": ev["id"]}
    j["stage"] = "draft"
    j.setdefault("stage_log", []).append({"stage": "draft", "at": iso()})
    store.upsert("jobs", j)
    gate.act("advance_stage", "pipeline", job_id,
             {"to": "draft", "cited": chain["cited"]})
    return {"stage": "draft", "chain": chain}


# ---------------------------------------------------------------- the deadline sweep

def deadline_sweep(limit=10):
    """Draft a deadline alert for every open job inside the closing week —
    BEFORE the closing, capped, demo fixtures skipped."""
    out = {"drafted": 0, "skipped": 0}
    for j in store.load("jobs"):
        if out["drafted"] >= limit:
            break
        if j.get("stage") == "sealed" or j.get("demo_tag") or not j.get("closing_date"):
            continue
        dtc = (parse(j["closing_date"]) - now()).days if parse(j["closing_date"]) else None
        if dtc is None or dtc > core.CLOSING_WEEK_DAYS or j.get("deadline_alerted_at"):
            out["skipped"] += 1
            continue
        p = core.closing_projection(j)
        gate.act("draft_deadline_reply", "desk", j["id"],
                 {"summary": f"{j.get('client')} closes in {dtc}d, job in {j['stage']}",
                  "projection": None if "_missing" in p else p})
        j["deadline_alerted_at"] = iso()
        store.upsert("jobs", j)
        out["drafted"] += 1
    return out


def run_all():
    handled = 0
    for m in store.load("messages"):
        if not m.get("handled_at"):
            handle_message(m["id"])
            handled += 1
    return {"messages": {"handled": handled}, "deadlines": deadline_sweep()}
