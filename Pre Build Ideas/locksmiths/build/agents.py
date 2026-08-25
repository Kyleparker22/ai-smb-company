#!/usr/bin/env python3
"""Key OS — the agents. Everything routes through `core.gate`. Stdlib only."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import iso, now, parse

# The 911 script, verbatim — every emergency reply LEADS with this.
EMERGENCY_SCRIPT = ("If someone is in danger right now — a child or pet in a hot vehicle, a "
                    "person unresponsive behind a locked door — call 911 now; they are faster "
                    "than any locksmith and can authorize forced entry we cannot.")


def _outbound(body):
    """Every outward draft passes the key-code scrub structurally — a draft
    that fails it cannot be produced by this module."""
    okc, why = core.key_scrub_ok(body)
    assert okc, why
    return body


def handle_message(msg_id):
    m = store.by_id("messages", msg_id)
    if not m:
        return {"error": "no such message"}
    c = core.read_message(m.get("text", ""))
    out = {"message": msg_id, "classification": c, "steps": []}
    gate.act("read_message", "dispatch", msg_id, {"label": c["label"], "why": c["why"]})

    if c["label"] == "emergency_lockout":
        ev = store.log_event("record_emergency", msg_id, "agent:dispatch", "R2",
                             {"verbatim": m.get("text", ""), "from": m.get("from")})
        body = _outbound(_emergency_copy(m))
        gate.act("draft_emergency_reply", "dispatch", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_emergency_reply", "draft": body,
                             "why": "life-safety first: the 911 script leads verbatim and the "
                                    "nearest van rolls anyway", "event": ev["id"]})
    elif c["label"] in ("routine_lockout", "rekey_request"):
        address = m.get("address")
        okd, why, auth_ref = core.can_dispatch(c["label"], address)
        if not okd:
            ev = store.log_event("refused", msg_id, "agent:dispatch", "R0",
                                 {"action": "perform_without_authorization", "why": why})
            body = _outbound(_unverifiable_copy(m, why))
            gate.act("draft_rekey_reply", "dispatch", msg_id,
                     {"summary": m.get("text", "")[:60], "preview": body[:110],
                      "unverifiable": True, "gap": why})
            m["draft_reply"], m["unverifiable"] = body, True
            out["steps"].append({"action": "draft_rekey_reply", "unverifiable": True,
                                 "draft": body, "gap": why, "event": ev["id"],
                                 "why": "no recorded authority — there is no dispatch path; "
                                        "the draft names the gap and a human decides"})
        else:
            job = {"id": store.nid("jb"), "kind": "rekey" if c["label"] == "rekey_request"
                   else "unlock", "address": address, "customer": m.get("from"),
                   "authorization_ref": auth_ref,
                   "card_item": "rekey_base" if c["label"] == "rekey_request"
                   else "lockout_residential", "opened_at": iso()}
            store.upsert("jobs", job)
            body = _outbound(_dispatch_copy(m, why))
            gate.act("draft_dispatch", "dispatch", job["id"],
                     {"summary": f"{job['kind']} at {address}", "preview": body[:110],
                      "authorization_ref": auth_ref})
            m["draft_reply"] = body
            out["steps"].append({"action": "draft_dispatch", "job": job["id"],
                                 "authorization_ref": auth_ref, "draft": body,
                                 "why": f"authority on record — {why}"})
    elif c["label"] == "master_system":
        out["steps"].append(_handle_master(m))
    elif c["label"] == "quote":
        q = core.quote_for(_quote_kind(m.get("text", "")),
                           cylinders=m.get("cylinders"),
                           after_hours=bool(m.get("after_hours")))
        if q.get("total") is None:
            out["steps"].append({"action": "route_human", "refused": q.get("_missing"),
                                 "why": "the card cannot price it — a human quotes or the "
                                        "card grows a line; software never invents a number"})
        else:
            body = _outbound(_quote_copy(m, q))
            gate.act("draft_quote", "dispatch", msg_id,
                     {"summary": m.get("text", "")[:60], "preview": body[:110],
                      "total": q["total"]})
            m["draft_reply"] = body
            out["steps"].append({"action": "draft_quote", "quote": q, "draft": body,
                                 "why": "answered FROM the recorded card, never around it"})
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("messages", m)
    return out


def _handle_master(m):
    """A master-system change: the system's NAMED authorizers decide. A named
    authorizer's ask becomes a new registry record; anyone else drafts as
    unverifiable with the gap named."""
    sys_row = next((s for s in store.load("systems")
                    if s.get("site", "").lower() in (m.get("text") or "").lower()
                    or s["id"] == m.get("system_id")), None)
    if not sys_row:
        return {"action": "route_human",
                "why": "no master system matched to this message — a human reads it"}
    requester = m.get("from")
    if requester not in (sys_row.get("authorizers") or []):
        why = (f"{requester or 'the requester'} is not a named authorizer for "
               f"{sys_row['site']} — the recorded authorizers are the only people who can "
               f"change this system. A phone voice is not a name on the record.")
        ev = store.log_event("refused", sys_row["id"], "agent:registry", "R0",
                             {"action": "perform_without_authorization", "why": why})
        body = _outbound(_unverifiable_copy(m, why))
        gate.act("draft_rekey_reply", "registry", m["id"],
                 {"summary": (m.get("text") or "")[:60], "unverifiable": True, "gap": why})
        m["draft_reply"], m["unverifiable"] = body, True
        return {"action": "draft_rekey_reply", "unverifiable": True, "draft": body,
                "gap": why, "event": ev["id"],
                "why": "not a named authorizer — unverifiable, a human decides"}
    r = gate.act("registry_append", "registry", sys_row["id"],
                 {"change": (m.get("text") or "")[:80], "authorized_by": requester},
                 execute=lambda: core.registry_append(
                     sys_row["id"], (m.get("text") or "")[:80], requester))
    body = _outbound(_master_ack_copy(m, sys_row))
    m["draft_reply"] = body
    return {"action": "registry_append", "record": (r.get("result") or {}).get("id"),
            "draft": body,
            "why": f"{requester} is a named authorizer — the change lands as a NEW record; "
                   f"nothing is edited and no code appears in the reply"}


def _quote_kind(text):
    t = (text or "").lower()
    if "rekey" in t:
        return "rekey"
    if "car" in t or "auto" in t or "vehicle" in t:
        return "lockout_auto"
    if "office" in t or "commercial" in t or "store" in t:
        return "lockout_commercial"
    if "lockout" in t or "locked out" in t or "house" in t or "apartment" in t:
        return "lockout_residential"
    return "unpriceable"


# ---------------------------------------------------------------- copy

def _emergency_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"{EMERGENCY_SCRIPT}\n\n{who} — our nearest van is rolling to you right now "
            f"either way; stay by the vehicle or door, keep talking to whoever is inside, "
            f"and keep this line open. Nobody pays a dispatch fee to an emergency.")


def _unverifiable_copy(m, gap):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — we want to help, and here's the honest reason we can't roll a van "
            f"yet: {gap} It protects you too — it's the same rule that stops anyone else "
            f"from having YOUR locks opened. Meet our tech with a photo ID and the deed or "
            f"lease, and this becomes a same-day job.")


def _dispatch_copy(m, why):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — you're verified on our records ({why}), so a van is being assigned "
            f"now. The tech will confirm ID at the door — that step never gets skipped, for "
            f"anyone — and the invoice will cite the exact rate-card line, no surprises.")


def _quote_copy(m, q):
    who = (m.get("from") or "there").split()[0]
    lines = "; ".join(f"{l['item']} ${l['amount']:,.0f}" for l in q["lines"])
    return (f"Hi {who} — straight from our recorded rate card: {lines} — total "
            f"${q['total']:,.2f}. That card is the only price list this company has; nobody "
            f"here can quote around it, day or night.")


def _master_ack_copy(m, sys_row):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — logged. The change to the {sys_row['site']} system is recorded as a "
            f"new registry entry under your name; the full history stays intact and key "
            f"codes never travel by text or email — pickup is in person, ID confirmed.")


def _service_copy(clock, touch_n):
    site = clock.get("site") or "your site"
    return {
        1: (f"Hi — the {clock.get('kind', 'service')} interval for {site} has come due on our "
            f"records. Reply with a good window and we'll schedule it; twenty minutes now "
            f"beats a dead reader on a Friday night."),
        2: (f"Hi — second note on the overdue {clock.get('kind', 'service')} at {site}. If "
            f"another vendor covered it, tell us and we'll close the clock on our side."),
        3: (f"Hi — last reminder from us about the {clock.get('kind', 'service')} at {site}; "
            f"after this we go quiet and a person will check in instead. The clock and its "
            f"history stay on your file either way."),
    }.get(touch_n, f"Hi — the {clock.get('kind', 'service')} at {site} is due.")


# ---------------------------------------------------------------- jobs

def close_job(job_id, human=None):
    j = store.by_id("jobs", job_id)
    if not j:
        return {"error": "no such job"}
    okc, why = core.can_close(j)
    if not okc:
        ev = store.log_event("refused", job_id, "agent:dispatch", "R0",
                             {"action": "perform_without_authorization", "why": why})
        return {"refused": why, "event": ev["id"]}
    if not human:
        return {"refused": "the references are on file but closing is a human act — the tech "
                           "confirms the work happened", "why": why}
    j["closed_at"] = iso()
    store.upsert("jobs", j)
    store.log_event("job_closed", job_id, f"human:{human}", "R1", {"why": why})
    return {"closed": True, "why": why}


# ---------------------------------------------------------------- sweeps

def service_sweep(limit=20):
    out = {"drafted": 0, "skipped": 0}
    for clock in store.load("clocks"):
        if out["drafted"] >= limit:
            break
        plan = core.service_plan(clock)
        if plan["action"] != "draft_service_reminder":
            out["skipped"] += 1
            continue
        touch_n = len(clock.get("touches") or []) + 1
        body = _outbound(_service_copy(clock, touch_n))
        gate.act("draft_service_reminder", "service", clock["id"],
                 {"summary": f"{clock.get('site')} {clock.get('kind')} touch {touch_n}",
                  "preview": body[:110]})
        clock.setdefault("touches", []).append({"at": iso(), "kind": "drafted", "body": body})
        store.upsert("clocks", clock)
        out["drafted"] += 1
    return out


def run_all():
    handled = 0
    for m in store.load("messages"):
        if not m.get("handled_at"):
            handle_message(m["id"])
            handled += 1
    return {"messages": {"handled": handled}, "service": service_sweep()}
