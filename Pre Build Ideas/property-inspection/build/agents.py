#!/usr/bin/env python3
"""Inspect OS — the agents. Everything routes through `core.gate`. Stdlib only."""
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

    if c["label"] == "soften_request":
        ev = store.log_event("refused", msg_id, "agent:frontdesk", "R0",
                             {"action": "soften_or_remove_finding",
                              "verbatim": m.get("text", ""), "from": m.get("from"),
                              "why": "findings are append-only; the request is preserved verbatim"})
        body = _soften_reply(m)
        out["steps"].append({"action": "refuse_and_log_verbatim", "draft": body,
                             "refused": "the finding stands — the request itself is now part of "
                                        "the record", "why": c["why"], "event": ev["id"]})
    elif c["label"] == "early_copy_request":
        insp = store.by_id("inspections", m.get("inspection_id")) if m.get("inspection_id") else None
        okr, why = core.can_release(insp or {}, m.get("from", "requester"))
        if not okr:
            ev = store.log_event("refused", msg_id, "agent:frontdesk", "R0",
                                 {"action": "release_to_non_client", "why": why})
            out["steps"].append({"action": "refuse_release", "refused": why,
                                 "draft": _release_reply(m), "event": ev["id"]})
        else:
            out["steps"].append({"action": "release_ok", "why": why})
    elif c["label"] == "cost_ask":
        ev = store.log_event("refused", msg_id, "agent:frontdesk", "R0",
                             {"action": "estimate_repair_cost", "why": c["why"]})
        out["steps"].append({"action": "refer_to_trades",
                             "draft": _cost_reply(m),
                             "refused": "no repair number from us — not our license",
                             "why": c["why"], "event": ev["id"]})
    elif c["label"] == "status":
        insp = store.by_id("inspections", m.get("inspection_id")) if m.get("inspection_id") else None
        clock = core.report_clock(insp) if insp else {}
        body = _status_reply(m, clock)
        gate.act("draft_status_reply", "frontdesk", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_status_reply", "clock": clock,
                             "why": "answered from the clock"})
    elif c["label"] == "booking":
        body = _booking_reply(m)
        gate.act("draft_booking", "frontdesk", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_booking", "why": "a human sends"})
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("messages", m)
    return out


def _soften_reply(m):
    """The refusal a human sends. Polite, immovable, and explicit that the
    request is now on the record."""
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — we can't change, soften, or omit a finding, for anyone, on any deal. "
            f"That's not stubbornness; it's the entire value of the report, and it protects "
            f"every party including you. The finding stands as written, and our records note "
            f"the request. If the condition itself is corrected, we're glad to re-inspect and "
            f"record that — that's the honest path to a cleaner report.")


def _release_reply(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — the report goes to our client first; it's their document. Once they "
            f"authorize sharing it with you, it's on its way the same hour. Ask them to reply "
            f"'share with {who}' to any of our emails and that authorization gets recorded.")


def _cost_reply(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — we don't price repairs; an inspector quoting repair numbers is guessing "
            f"outside their license, and a guess in writing helps nobody. The report describes "
            f"the condition precisely so licensed trades can quote it exactly. Two or three "
            f"trade quotes on that finding will beat any number we could invent.")


def _status_reply(m, clock):
    who = (m.get("from") or "there").split()[0]
    if clock.get("hours_left") is not None:
        return (f"Hi {who} — the report is in write-up and lands inside our 24-hour window "
                f"({max(0, round(clock['hours_left']))}h remaining). You'll get it by email the "
                f"moment it's finished.")
    return f"Hi {who} — checking the file now; a human will confirm status shortly."


def _booking_reply(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — happy to help. Reply with the address, square footage if you know it, "
            f"and two windows that work; we'll confirm one today. Reports deliver within 24 "
            f"hours of the walk, to you first.")


def _referral_thanks(r):
    return (f"Thanks for trusting us with your client's inspection — the report went out inside "
            f"the 24-hour window as always. We never soften a finding and never release to "
            f"anyone but the client, which we suspect is why you keep sending people. It's "
            f"noticed and appreciated.")


def referral_sweep(limit=10):
    out = {"drafted": 0}
    recent = {e["subject"] for e in store.events(kind="queued_for_approval", since_days=30)
              if (e.get("detail") or {}).get("action") == "draft_referral_thanks"}
    counts = {}
    for r in store.load("referrals"):
        src = r.get("source")
        if src and src != "direct":
            counts.setdefault(src, 0)
            counts[src] += 1
    for src, n in sorted(counts.items(), key=lambda x: -x[1]):
        if out["drafted"] >= limit or src in recent:
            continue
        body = _referral_thanks({"source": src})
        gate.act("draft_referral_thanks", "frontdesk", src,
                 {"summary": f"{src}: {n} referral(s)", "preview": body[:110]})
        out["drafted"] += 1
    return out


def run_all():
    handled = 0
    for m in store.load("messages"):
        if not m.get("handled_at"):
            handle_message(m["id"])
            handled += 1
    return {"messages": {"handled": handled}, "referrals": referral_sweep()}
