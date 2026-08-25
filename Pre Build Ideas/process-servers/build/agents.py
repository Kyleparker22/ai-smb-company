#!/usr/bin/env python3
"""Serve OS — the agents. Everything routes through `core.gate`. Stdlib only."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import days_until, iso, now


def handle_message(msg_id):
    m = store.by_id("messages", msg_id)
    if not m:
        return {"error": "no such message"}
    c = core.read_message(m.get("text", ""))
    out = {"message": msg_id, "classification": c, "steps": []}
    gate.act("read_message", "desk", msg_id, {"label": c["label"], "why": c["why"]})
    s = store.by_id("serves", m["serve_id"]) if m.get("serve_id") else None
    atts = core.attempts_for(s["id"]) if s else []

    if c["label"] == "deadline_risk":
        if not s:
            out["steps"].append({"action": "route_human",
                                 "why": "deadline risk with no matched serve — a person matches "
                                        "it to the file NOW; the flag does not wait for the match"})
            gate.act("flag_deadline_risk", "desk", msg_id,
                     {"summary": m.get("text", "")[:80], "unmatched": True})
        else:
            gate.act("flag_deadline_risk", "desk", s["id"],
                     {"summary": f"{s.get('defendant')} — {m.get('text', '')[:80]}"})
            s["deadline_flagged_at"] = iso()
            store.upsert("serves", s)
            dd = core.due_diligence(s, atts)
            body = _deadline_copy(m, s, atts, dd)
            gate.act("draft_deadline_reply", "desk", s["id"],
                     {"summary": m.get("text", "")[:60], "preview": body[:110]})
            m["draft_reply"] = body
            out["steps"].append({"action": "flag_deadline_risk", "draft": body,
                                 "why": "flagged to a human at R2 the moment it arrived; the "
                                        "reply reads from the attempt log and the recorded rule"})
    elif c["label"] == "status_ask":
        if not s:
            out["steps"].append({"action": "route_human",
                                 "why": "status ask with no matched serve — a person matches it"})
        else:
            body = _status_copy(m, s, atts)
            gate.act("draft_status_reply", "desk", s["id"],
                     {"summary": m.get("text", "")[:60], "preview": body[:110]})
            m["draft_reply"] = body
            out["steps"].append({"action": "draft_status_reply", "draft": body,
                                 "why": "answered from the record: attempts and the next window"})
    elif c["label"] == "new_serve":
        sid = store.nid("sv")
        serve = {"id": sid, "case_number": m.get("case_number"), "court": m.get("court"),
                 "county": m.get("county"), "defendant": m.get("defendant") or "(from the papers)",
                 "address": m.get("address"), "firm": m.get("firm"), "papers": m.get("papers"),
                 "fee": m.get("fee"), "received_at": iso(), "deadline": m.get("deadline"),
                 "status": "papers_in"}
        store.upsert("serves", serve)
        gate.act("log_serve", "intake", sid,
                 {"summary": f"{serve['defendant']} — {serve.get('county') or 'county not stated'}"})
        note = ("" if serve.get("deadline") else
                " No court deadline came with the papers — the file says so and ranks last, "
                "unranked and named, until one is recorded.")
        out["steps"].append({"action": "log_serve", "serve": sid,
                             "why": f"papers in — the file is open and the clock starts.{note}"})
    elif c["label"] == "affidavit_request":
        if s and s.get("status") in ("served", "substituted"):
            r = draft_affidavit(s["id"])
            out["steps"].append({"action": "draft_affidavit", **r,
                                 "why": "assembled verbatim from the attempt log; a human "
                                        "reviews and signs"})
        elif s:
            body = _not_yet_copy(m, s, atts)
            gate.act("draft_status_reply", "desk", s["id"],
                     {"summary": m.get("text", "")[:60], "preview": body[:110]})
            m["draft_reply"] = body
            out["steps"].append({"action": "draft_status_reply", "draft": body,
                                 "why": "no affidavit before the record — the honest state, "
                                        "with the record attached"})
        else:
            out["steps"].append({"action": "route_human",
                                 "why": "affidavit ask with no matched serve — a person matches it"})
    elif c["label"] == "rush_request":
        if s:
            s["rush"] = True
            store.upsert("serves", s)
            gate.act("log_rush", "desk", s["id"], {"summary": m.get("text", "")[:60]})
            out["steps"].append({"action": "log_rush",
                                 "why": "rush noted — the board re-ranks by the court clock; "
                                        "the fee conversation is a human's"})
        else:
            out["steps"].append({"action": "route_human",
                                 "why": "rush ask with no matched serve — a person matches it"})
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("messages", m)
    return out


def _deadline_copy(m, s, atts, dd):
    who = (m.get("from") or "there").split()[0]
    d = days_until(s.get("deadline"))
    last = atts[-1] if atts else None
    lastline = (f"latest {str(last['attempted_at'])[:10]} at {last['address']} — {last['outcome']}"
                if last else "no attempts recorded yet")
    ddline = (dd["why"] if not dd.get("met") else
              f"the due-diligence rule is satisfied by the log ({dd['rule']})")
    return (f"Hi {who} — this was flagged to a person the moment it arrived. The record on "
            f"{s.get('defendant')}: {len(atts)} attempt(s) so far; {lastline}. Next attempt "
            f"window: {core.next_window(s, atts)}. Court deadline "
            f"{str(s.get('deadline'))[:10] if s.get('deadline') else 'not recorded'}"
            f"{f' ({d} day(s) out)' if d is not None else ''}. On substituted service: {ddline} "
            f"Everything above reads straight from the attempt log — nothing here is a guess, "
            f"and a person owns this serve today.")


def _status_copy(m, s, atts):
    who = (m.get("from") or "there").split()[0]
    last = atts[-1] if atts else None
    lastline = (f"latest {str(last['attempted_at'])[:10]} at {last['address']} — {last['outcome']}"
                if last else "no attempts recorded yet")
    return (f"Hi {who} — from the record on {s.get('defendant')}: {len(atts)} attempt(s); "
            f"{lastline}. Next attempt window: {core.next_window(s, atts)}. Court deadline "
            f"{str(s.get('deadline'))[:10] if s.get('deadline') else 'not recorded'}. "
            f"This is read straight from the attempt log — nothing speculative.")


def _not_yet_copy(m, s, atts):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — straight answer: {s.get('defendant')} has not been served yet, so there "
            f"is no affidavit to send — we don't draft court paper ahead of the record. Where it "
            f"stands: {len(atts)} attempt(s), next window {core.next_window(s, atts)}. The "
            f"affidavit assembles verbatim from the attempt log the day service lands.")


def draft_affidavit(serve_id, extra_fact=None):
    r = core.affidavit_draft(serve_id, extra_fact=extra_fact)
    if "refused" in r or "error" in r:
        return r
    g = gate.act("draft_affidavit", "desk", serve_id,
                 {"summary": r["draft"].splitlines()[0][:70],
                  "assembled_from": r["assembled_from"]})
    return {**r, "gate": g}


def attest(serve_id):
    """The probe that must always refuse: software never signs, never attests."""
    return gate.act("sign_or_attest", "desk", serve_id,
                    {"summary": "request to sign/attest an affidavit"})


def substitute(serve_id):
    """Substituted service clears ONLY when the recorded jurisdiction rule is
    satisfied by the log itself; otherwise refused with the gap named."""
    s = store.by_id("serves", serve_id)
    if not s:
        return {"error": "no such serve"}
    dd = core.due_diligence(s)
    if not dd["met"]:
        ev = store.log_event("refused", serve_id, "agent:desk", "R0",
                             {"action": "declare_due_diligence_met", "why": dd["why"],
                              "rule": dd.get("rule")})
        return {"refused": dd["why"], "rule": dd.get("rule"), "event": ev["id"]}
    store.log_event("due_diligence_met", serve_id, "agent:desk", "R2",
                    {"basis": dd["why"], "rule": dd["rule"]})
    return {"allowed": True, "basis": dd["why"], "rule": dd["rule"],
            "note": "the log satisfies the recorded rule — substituted service may proceed in "
                    "the field; the affidavit of due diligence drafts from these same entries, "
                    "and a human signs it"}


def assignment_sweep(limit=40):
    """Open, unassigned serves get a proposed server by territory and open
    load — proposals queue at R1; a human confirms the day list."""
    servers = [x for x in store.load("servers") if x.get("status", "active") == "active"]
    open_load = {}
    for s in store.load("serves"):
        if s.get("status") in ("papers_in", "attempting") and s.get("assigned_to"):
            open_load[s["assigned_to"]] = open_load.get(s["assigned_to"], 0) + 1
    out = {"proposed": 0, "skipped": 0}
    for s in store.load("serves"):
        if out["proposed"] >= limit:
            break
        if s.get("status") not in ("papers_in", "attempting") or s.get("assigned_to") \
           or s.get("demo_tag") or s.get("assignment_proposed_at"):
            continue
        cands = [x for x in servers if s.get("county") in (x.get("territory") or [])]
        if not cands:
            out["skipped"] += 1
            continue
        pick = min(cands, key=lambda x: open_load.get(x["id"], 0))
        gate.act("propose_assignment", "router", s["id"],
                 {"server": pick["id"],
                  "summary": f"{s.get('defendant')} ({s.get('county')}) → {pick.get('name')} — "
                             f"territory match, lightest open load"})
        s["assignment_proposed_at"] = iso()
        store.upsert("serves", s)
        open_load[pick["id"]] = open_load.get(pick["id"], 0) + 1
        out["proposed"] += 1
    return out


def run_all():
    handled = 0
    for m in store.load("messages"):
        if not m.get("handled_at"):
            handle_message(m["id"])
            handled += 1
    return {"messages": {"handled": handled}, "assignments": assignment_sweep()}
