#!/usr/bin/env python3
"""Queue OS — the agents. Everything routes through `core.gate`. Stdlib only."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import iso, now


def triage_sweep():
    """Triage every untriaged ticket. Security escalates at R2 immediately."""
    out = {"triaged": 0, "escalated": 0, "drafted": 0}
    for t in store.load("tickets"):
        if t.get("label"):
            continue
        c = core.triage(t.get("text", ""))
        t.update(label=c["label"], why=c["why"])
        if c["label"] == "security":
            t["security_kind"] = c["kind"]
        store.upsert("tickets", t)
        gate.act("triage_ticket", "dispatcher", t["id"], {"label": c["label"], "why": c["why"]})
        out["triaged"] += 1
        if c["label"] == "security" and not t.get("demo_tag"):
            brief = security_brief(t, c["kind"])
            gate.act("escalate_security", "dispatcher", t["id"],
                     {"summary": f"{c['kind']}: {t.get('text','')[:60]}", "kind": c["kind"],
                      "brief": brief})
            out["escalated"] += 1
        elif c["label"] == "routine" and not t.get("demo_tag"):
            body = _routine_reply_copy(t)
            gate.act("draft_routine_reply", "dispatcher", t["id"],
                     {"summary": f"draft reply: {t.get('text','')[:60]}",
                      "preview": body[:110]})
            t["draft_reply"] = body
            store.upsert("tickets", t)
            out["drafted"] += 1
    return out


def security_brief(t, kind):
    """The internal escalation brief: what the engineer needs in the first
    thirty seconds, and the two rules that hold no matter what."""
    client = store.by_id("clients", t.get("client_id")) or {}
    return {"kind": kind, "client": client.get("name"), "tier": client.get("tier"),
            "reported_at": t.get("opened_at"), "verbatim": t.get("text"),
            "rules": ["software never closes or downgrades this ticket",
                      "credentials never travel in a reply"],
            "first_moves": {"phishing": "isolate the mailbox rule surface; pull the message trace",
                            "ransomware": "isolate the host from the network before anything else",
                            "account_compromise": "revoke sessions, then reset — order matters",
                            "mfa_bombing": "block push, switch to number matching, call the user",
                            "data_exfil": "snapshot audit logs before they age out",
                            }.get(kind, "engineer's judgment"),
            "note": "a head start, not a runbook — hands touch production, software does not"}


def _routine_reply_copy(t):
    """Drafted first replies for the four routine shapes. No credential ever
    appears in copy — the reset flow sends a link through the portal."""
    text = (t.get("text") or "").lower()
    who = (t.get("from") or "there").split()[0]
    if "password" in text:
        return (f"Hi {who} — sent a secure reset link to your enrolled phone via the portal. "
                f"It expires in 15 minutes. (We never send passwords in email — if you ever get "
                f"one that way, it isn't us.)")
    if "printer" in text or "toner" in text or "scan" in text:
        return (f"Hi {who} — on it. Quick check while we connect: is it one printer or the whole "
                f"floor, and does it show an error code? Reply with either and we'll be faster.")
    if "new " in text or "onboard" in text:
        return (f"Hi {who} — new-hire setup started. We'll have accounts, laptop image, and access "
                f"groups staged; your manager approves the access list before anything activates.")
    return (f"Hi {who} — got it, ticket open. First availability is today; reply with a good time "
            f"if you need a specific window.")


def close_ticket(ticket_id, human=None):
    """Close path. Software closing a security ticket is refused, logged, and
    never becomes an approvable row."""
    t = store.by_id("tickets", ticket_id)
    if not t:
        return {"error": "no such ticket"}
    okc, why = core.can_close(t, actor_is_human=bool(human))
    if not okc:
        ev = store.log_event("refused", ticket_id, "agent:dispatcher", "R0",
                             {"action": "close_security_ticket", "why": why})
        return {"refused": why, "event": ev["id"]}
    t["resolved_at"] = iso()
    store.upsert("tickets", t)
    actor = f"human:{human}" if human else "agent:dispatcher"
    store.log_event("ticket_closed", ticket_id, actor, "R1" if human else "R2", {})
    return {"closed": True, "by": actor}


def scope_sweep():
    """Scope-check every open non-routine ticket once; out-of-scope drafts a
    billable (R1), ambiguous queues for a human, nothing is billed."""
    out = {"checked": 0, "out_of_scope": 0, "ambiguous": 0}
    done = {f["ticket_id"] for f in store.load("scope_findings")}
    for t in store.load("tickets"):
        if t["id"] in done or t.get("demo_tag") or t.get("label") in (None, "routine", "security"):
            continue
        v = core.scope_check(t)
        f = {"id": store.nid("sf"), "ticket_id": t["id"], "client_id": t.get("client_id"),
             "at": iso(), **v}
        store.upsert("scope_findings", f)
        out["checked"] += 1
        if v["verdict"] == "out_of_scope":
            body = _billable_copy(v, t)
            gate.act("draft_billable", "scopekeeper", t["id"],
                     {"summary": f"{v['category']} excluded by {v['clause']}: {t.get('text','')[:50]}",
                      "clause": v["clause"], "preview": body[:110]})
            f["conversation_draft"] = body
            store.upsert("scope_findings", f)
            out["out_of_scope"] += 1
        elif v["verdict"] == "ambiguous":
            store.log_event("scope_ambiguous", t["id"], "agent:scopekeeper", "R1",
                            {"why": v["why"]})
            out["ambiguous"] += 1
    return out


def _billable_copy(v, t):
    """The scope conversation, drafted — a quote path, never an invoice, and
    always the clause verbatim so the client reads the same words we did."""
    client = store.by_id("clients", t.get("client_id")) or {}
    who = client.get("name", "your team")
    return (f"Hi {who} — the request \"{(t.get('text') or '')[:60]}\" falls outside the agreement: "
            f"clause {v['clause']} reads \"{v.get('clause_text', '')}\". Happy to do the work — "
            f"we'll send a small quote first so there are no surprise line items. Want it?")


def run_all():
    return {"triage": triage_sweep(), "scope": scope_sweep()}
