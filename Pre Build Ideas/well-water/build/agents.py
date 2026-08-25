#!/usr/bin/env python3
"""Well OS — the agents. Everything routes through `core.gate`. Stdlib only."""
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
    gate.act("read_message", "intake", msg_id, {"label": c["label"], "why": c["why"]})

    if c["label"] == "contamination":
        gate.act("log_contamination", "intake", msg_id,
                 {"verbatim": m.get("text", ""), "from": m.get("from"), "at": m.get("at")})
        ev = store.log_event("refused", msg_id, "agent:intake", "R0",
                             {"action": "downgrade_contamination_worry",
                              "why": "a water-quality worry is never softened by software — "
                                     "record, escalate, human"})
        body = _contamination_ack(m)
        oks, why = core.soothe_ok(body)
        assert oks, why  # structural: the shipped copy passes its own check
        gate.act("draft_contamination_ack", "intake", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "log_contamination", "draft": body,
                             "said": core.CONTAMINATION_PROTOCOL,
                             "refused": "nothing about the water is judged by this message — "
                                        "the lab answers potability, by report, or nobody does",
                             "why": c["why"], "event": ev["id"]})
    elif c["label"] == "no_water":
        gate.act("log_no_water", "intake", msg_id,
                 {"verbatim": m.get("text", ""), "from": m.get("from")})
        body = _dispatch_copy(m)
        gate.act("draft_dispatch_reply", "intake", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "log_no_water", "draft": body,
                             "why": "a dry house is a P1 — logged now, a human dispatches today"})
    elif c["label"] == "service_due":
        body = _service_reply_copy(m)
        gate.act("draft_service_reply", "service", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_service_reply", "draft": body,
                             "why": "answered from the recorded clocks — never from memory"})
    elif c["label"] == "quote":
        body = _quote_reply_copy(m)
        gate.act("draft_quote", "sales", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_quote", "draft": body,
                             "why": "we measure, then we price — the visit comes before the number"})
    elif c["label"] == "status":
        body = _status_copy(m)
        gate.act("draft_status_reply", "office", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_status_reply", "draft": body,
                             "why": "the pipeline record does the talking"})
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("messages", m)
    return out


def _contamination_ack(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — taken seriously and recorded word-for-word. Here is exactly what "
            f"happens: a sampling visit goes to the top of today's route, the sample goes to "
            f"an accredited lab, and the answer comes back as a report — an id, a date, a "
            f"result. Until that report exists nobody here will tell you the water is fine, "
            f"and we'd hold off drinking it in the meantime. A person calls you back today.")


def _dispatch_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — a house with no water is a today problem, full stop. This is at the "
            f"top of the dispatch board right now; a person confirms the truck and calls you "
            f"with an arrival window. If anything changes at the tap before then, reply here "
            f"and it rides along to the tech.")


def _service_reply_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — checking your system's recorded clocks now: every filter, lamp, and "
            f"media bed on your account carries its own service interval and last-service "
            f"date, and the answer comes from those records, not memory. You'll get the exact "
            f"dates and, if anything is due, a scheduling link in the follow-up.")


def _quote_reply_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — happy to price it, and here's how we do that honestly: we measure, "
            f"then we price. A site visit records the well log — depth, casing, yield, static "
            f"level — and the quote cites those numbers line by line. Anyone who quotes a "
            f"well without them is guessing in writing. Want us to book the measuring visit?")


def _status_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — pulling your job from the pipeline record: permit, drill, pump test, "
            f"water test, state report — each stage carries its date, and the county's own "
            f"clock is tracked as a date alert. You'll get the current stage and the next "
            f"date in the follow-up, straight from the record.")


def _reminder_copy(s, comp_kind, touch_n):
    who = (s.get("customer_name") or "there").split()[0]
    return {
        1: (f"Hi {who} — the {comp_kind} on your treatment system has reached its recorded "
            f"service clock. Past the clock it isn't doing what it's there for — a UV lamp "
            f"still glows, it just stops sterilizing. Reply and we'll put the swap on a route "
            f"day, no extra trip charge."),
        2: (f"Hi {who} — second note on the {comp_kind}: still past its recorded clock on our "
            f"board. The visit takes minutes on a regular route day; reply with a week that "
            f"works and it's done."),
        3: (f"Hi {who} — last note from us on the {comp_kind}; we won't keep asking. It stays "
            f"flagged on your file, and if you'd rather handle it yourself or elsewhere, no "
            f"hard feelings — the clock is yours either way."),
    }.get(touch_n, f"Hi {who} — the {comp_kind} on your system is past its recorded clock.")


def answer_water_safe(well_id):
    """The lab rule, executed: cite the recorded report or refuse."""
    w = core.water_safety(well_id)
    if "refused" in w:
        ev = store.log_event("refused", well_id, "agent:water", "R0",
                             {"action": "declare_water_safe", "why": w["refused"]})
        return {"refused": w["refused"], "event": ev["id"],
                "pending": w.get("pending")}
    store.log_event("lab_report_cited", well_id, "agent:water", "R2",
                    {"report_no": w["report"]["report_no"],
                     "sampled_at": w["report"].get("sampled_at")})
    return {"answer": w["answer"], "report": w["report"]}


def claim_protected(system_id):
    """The clock rule, executed: 'protected' cites in-clock dates or refuses."""
    s = store.by_id("systems", system_id)
    if not s:
        return {"error": "no such system"}
    okp, why = core.can_claim_protected(s)
    if not okp:
        ev = store.log_event("refused", system_id, "agent:service", "R0",
                             {"action": "claim_protection_past_clock", "why": why})
        return {"refused": why, "event": ev["id"],
                "status": core.protection_status(s)}
    return {"protected": True, "why": why, "status": core.protection_status(s)}


def draft_quote(well_id):
    """The quote gate, executed: the recorded log cited at R1, or refused."""
    w = store.by_id("wells", well_id)
    basis = core.quote_basis(w)
    if "refused" in basis:
        ev = store.log_event("refused", well_id, "agent:sales", "R0",
                             {"action": "quote_without_well_log", "why": basis["refused"]})
        return {"refused": basis["refused"], "event": ev["id"]}
    r = gate.act("draft_quote", "sales", well_id,
                 {"summary": basis["basis"][:80], "log": basis["log"]})
    return {"basis": basis["basis"], "log": basis["log"], "gate": r}


def service_sweep(limit=20):
    """The bounded reminder ladder over the service book. Capped per run;
    demo fixtures skipped; three touches, then silence is an answer."""
    out = {"drafted": 0, "skipped": 0}
    for s in store.load("systems"):
        if out["drafted"] >= limit:
            break
        if s.get("demo_tag"):
            continue
        plan = core.service_plan(s)
        if plan["action"] != "draft_reminder":
            out["skipped"] += 1
            continue
        touch_n = len(s.get("reminder_touches") or []) + 1
        body = _reminder_copy(s, plan.get("component", "system"), touch_n)
        gate.act("draft_service_reminder", "service", s["id"],
                 {"summary": f"{s.get('customer_name')} {plan.get('component')} touch {touch_n}",
                  "preview": body[:110]})
        s.setdefault("reminder_touches", []).append({"at": iso(), "kind": "drafted",
                                                     "body": body})
        store.upsert("systems", s)
        out["drafted"] += 1
    return out


def run_all():
    handled = 0
    for m in store.load("messages"):
        if not m.get("handled_at"):
            handle_message(m["id"])
            handled += 1
    return {"messages": {"handled": handled}, "service": service_sweep()}
