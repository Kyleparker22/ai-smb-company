#!/usr/bin/env python3
"""Proof OS — the agents. Everything routes through `core.gate`. Stdlib only."""
import sys
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
    gate.act("read_message", "frontdesk", msg_id, {"label": c["label"], "why": c["why"]})

    if c["label"] == "approval":
        job = store.by_id("jobs", m.get("job_id")) if m.get("job_id") else None
        if job and job.get("proof_sent_at"):
            job["proof_approval"] = {"approved_by": m.get("from", "customer"),
                                     "at": m.get("at") or iso(),
                                     "revision": job.get("current_revision", 1),
                                     "message_id": msg_id}
            store.upsert("jobs", job)
            gate.act("record_approval", "frontdesk", job["id"],
                     {"summary": f"rev {job['proof_approval']['revision']} approved by "
                                 f"{job['proof_approval']['approved_by']}"})
            out["steps"].append({"action": "record_approval",
                                 "why": "the click is now a record — who, when, which revision"})
        else:
            out["steps"].append({"action": "route_human",
                                 "why": "approval language with no matched job/proof — a person "
                                        "confirms which job before anything is recorded"})
    elif c["label"] == "complaint":
        job = store.by_id("jobs", m.get("job_id")) if m.get("job_id") else None
        body = _complaint_copy(m, job)
        gate.act("draft_complaint_reply", "frontdesk", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_complaint_reply", "draft": body,
                             "why": "cites the approved revision, or admits none exists"})
    elif c["label"] == "art_inbound":
        job = store.by_id("jobs", m.get("job_id")) if m.get("job_id") else None
        if job:
            ip = core.ip_check(job)
            if ip["flagged"]:
                ev = store.log_event("refused", job["id"], "agent:preflight", "R0",
                                     {"action": "approve_trademarked_art", "why": ip["why"]})
                out["steps"].append({"action": "queue_ip_check", "refused": ip["why"],
                                     "event": ev["id"]})
            else:
                out["steps"].append({"action": "preflight", "why": "no IP flags — preflight queues"})
        else:
            out["steps"].append({"action": "route_human", "why": "no job matched"})
    elif c["label"] == "rush":
        disp = core.rush_displacement(4)
        body = _rush_copy(m, disp)
        gate.act("draft_rush_quote", "frontdesk", msg_id,
                 {"summary": m.get("text", "")[:60], "displaced": len(disp["displaced"]),
                  "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_rush_quote", "displacement": disp,
                             "why": "a rush is a trade — the displacement is named"})
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("messages", m)
    return out


def _complaint_copy(m, job):
    who = (m.get("from") or "there").split()[0]
    ap = (job or {}).get("proof_approval")
    if ap:
        return (f"Hi {who} — pulling the approved proof now: revision {ap['revision']}, approved "
                f"by {ap['approved_by']} on {str(ap['at'])[:10]}. If the print doesn't match that "
                f"revision, the reprint is on us, fast and free. If it matches and reads "
                f"differently in person, come see it side-by-side with the proof and we'll make "
                f"it right together.")
    return (f"Hi {who} — straight answer: we don't have a recorded proof approval on this job, "
            f"so we won't argue about what was agreed. Come in, we'll put the print next to the "
            f"file, and we'll fix what's ours to fix.")


def _chase_copy(job, touch_n):
    who = (job.get("customer_name") or "there").split()[0]
    desc = job.get("desc", "your job")
    return {
        1: (f"Hi {who} — your proof for {desc} is waiting on your click. Nothing prints until "
            f"you approve it (that protects both of us), and your slot on the press starts at "
            f"the click, not before. One minute now saves days later."),
        2: (f"Hi {who} — second nudge on the {desc} proof. If something in it needs changing, "
            f"reply with the change — a revision is quick; a stalled proof isn't."),
        3: (f"Hi {who} — last note on the {desc} proof; a person will call next. The press slot "
            f"we're holding releases to other work if we don't hear back this week."),
    }.get(touch_n, f"Hi {who} — the {desc} proof is waiting on your approval.")


def _rush_copy(m, disp):
    who = (m.get("from") or "there").split()[0]
    n = len(disp["displaced"])
    return (f"Hi {who} — we can do the rush, and here's the honest trade: it moves {n} promised "
            f"job(s), whose customers we'll tell before they notice. Rush pricing covers the "
            f"overtime, not a penalty. Confirm and we'll re-run the schedule with your date in it.")


def release_job(job_id):
    j = store.by_id("jobs", job_id)
    if not j:
        return {"error": "no such job"}
    okp, why = core.can_produce(j)
    if not okp:
        ev = store.log_event("refused", job_id, "agent:press", "R0",
                             {"action": "produce_without_proof_approval", "why": why})
        return {"refused": why, "event": ev["id"]}
    return gate.act("release_to_press", "press", job_id, {"summary": why})


def chase_sweep(limit=15):
    out = {"drafted": 0, "to_human": 0, "skipped": 0}
    for j in store.load("jobs"):
        if out["drafted"] >= limit:
            break
        plan = core.chase_plan(j)
        if plan["action"] == "draft_chase":
            touch_n = len(j.get("chase_touches") or []) + 1
            body = _chase_copy(j, touch_n)
            gate.act("draft_proof_chase", "frontdesk", j["id"],
                     {"summary": f"{j.get('desc','job')} waiting, touch {touch_n}",
                      "preview": body[:110]})
            j.setdefault("chase_touches", []).append({"at": iso(), "kind": "drafted", "body": body})
            store.upsert("jobs", j)
            out["drafted"] += 1
        elif plan["action"] == "human":
            out["to_human"] += 1
        else:
            out["skipped"] += 1
    return out


def run_all():
    handled = 0
    for m in store.load("messages"):
        if not m.get("handled_at"):
            handle_message(m["id"])
            handled += 1
    return {"messages": {"handled": handled}, "chases": chase_sweep()}
