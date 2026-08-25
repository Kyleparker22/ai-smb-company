#!/usr/bin/env python3
"""Post OS — the agents. Everything routes through `core.gate`. Stdlib only."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import iso, now, parse


def handle_message(msg_id):
    m = store.by_id("reports", msg_id)
    if not m:
        return {"error": "no such message"}
    c = core.read_message(m.get("text", ""))
    out = {"message": msg_id, "classification": c, "steps": []}
    gate.act("read_message", "desk", msg_id, {"label": c["label"], "why": c["why"]})

    if c["label"] == "incident":
        inc = core.record_incident(m.get("post_id"), m.get("guard_id") or m.get("from", "unknown"),
                                   m.get("text", ""))
        gate.act("brief_supervisor", "desk", inc["id"],
                 {"summary": m.get("text", "")[:60],
                  "brief": {"verbatim": m.get("text"), "post": m.get("post_id"),
                            "rules": ["software never edits a narrative",
                                      "use-of-force questions go to a human supervisor"],
                            "first_move": "call the guard, then the client contact — in that order"}})
        out["steps"].append({"action": "record_incident", "incident": inc["id"],
                             "why": "verbatim, append-only; the supervisor brief is logistics only"})
    elif c["label"] == "callout":
        post = store.by_id("posts", m.get("post_id")) if m.get("post_id") else None
        if post:
            post["filled_by"] = None
            store.upsert("posts", post)
        out["steps"].append({"action": "open_post",
                             "why": "the post is open NOW — the coverage board proposes "
                                    "credential-matched fills only"})
    elif c["label"] == "coverage_request":
        body = _coverage_copy(m)
        gate.act("draft_coverage_reply", "desk", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_coverage_reply", "why": "a human sends"})
    elif c["label"] == "credential":
        guard = store.by_id("guards", m.get("guard_id")) if m.get("guard_id") else None
        body = _credential_copy(m, guard)
        out["steps"].append({"action": "answer_from_calendar", "draft": body,
                             "why": "answered from the recorded calendar"})
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("reports", m)
    return out


def _coverage_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — we can cover it. You'll get named, credential-verified officers (we "
            f"never send anyone whose card doesn't match the post), and the schedule confirms "
            f"today. Reply with the site, dates, and whether the post is armed.")


def _credential_copy(m, guard):
    who = (m.get("from") or "there").split()[0]
    if guard:
        creds = guard.get("credentials") or {}
        lines = ", ".join(f"{k} expires {str(v)[:10]}" for k, v in creds.items())
        return (f"Hi {who} — from the recorded calendar: {lines or 'no credentials on file'}. "
                f"Renewals inside 45 days get flagged automatically; an expired card drops you "
                f"from fill lists the same day, so renew early.")
    return f"Hi {who} — reply with your guard ID and the calendar answer comes right back."


def fill_post(post_id, guard_id):
    p = store.by_id("posts", post_id)
    g = store.by_id("guards", guard_id)
    if not p or not g:
        return {"error": "no such post or guard"}
    okf, why = core.can_fill(p, g)
    if not okf:
        ev = store.log_event("refused", post_id, "agent:scheduler", "R0",
                             {"action": "fill_post_unqualified", "guard": guard_id, "why": why})
        return {"refused": why, "event": ev["id"]}
    return gate.act("fill_post", "scheduler", post_id,
                    {"summary": f"{g.get('name')} → {p.get('site')} ({why})", "guard": guard_id})


def credential_sweep(limit=20):
    out = {"alerts": 0}
    already = {(e["subject"], (e.get("detail") or {}).get("cred"))
               for e in store.events(kind="credential_alert", since_days=14)}
    for row in core.credential_calendar():
        if out["alerts"] >= limit or (row["guard_id"], row["cred"]) in already:
            continue
        gate.act("credential_alert", "scheduler", row["guard_id"],
                 {"summary": f"{row['guard']}: {row['cred']} expires in {row['days']}d",
                  "cred": row["cred"], "days": row["days"]})
        out["alerts"] += 1
    return out


def run_all():
    handled = 0
    for m in store.load("reports"):
        if not m.get("handled_at"):
            handle_message(m["id"])
            handled += 1
    return {"messages": {"handled": handled}, "credentials": credential_sweep()}
