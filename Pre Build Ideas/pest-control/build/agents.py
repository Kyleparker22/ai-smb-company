#!/usr/bin/env python3
"""Route OS — the agents. Everything routes through `core.gate`. Stdlib only."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import iso


def handle_message(msg_id):
    m = store.by_id("messages", msg_id)
    if not m:
        return {"error": "no such message"}
    c = core.read_message(m.get("text", ""))
    out = {"message": msg_id, "classification": c, "steps": []}
    gate.act("read_message", "frontdesk", msg_id, {"label": c["label"], "why": c["why"]})

    if c["label"] == "exposure":
        gate.act("route_exposure", "frontdesk", msg_id,
                 {"summary": m.get("text", "")[:60]})
        out["steps"].append({"action": "route_exposure", "said": core.POISON_INSTRUCTION,
                             "why": c["why"]})
    elif c["label"] == "safety_question":
        ev = store.log_event("refused", msg_id, "agent:frontdesk", "R0",
                             {"action": "answer_chemical_safety", "why": c["why"]})
        out["steps"].append({"action": "route_to_applicator", "refused": "routed unanswered",
                             "why": c["why"], "event": ev["id"]})
    elif c["label"] == "reservice":
        body = _reservice_copy(m)
        gate.act("draft_reservice_booking", "frontdesk", msg_id,
                 {"summary": f"reservice: {m.get('text','')[:60]}", "preview": body[:110]})
        m["draft_reply"] = body
        acct = store.by_id("accounts", m.get("account_id")) if m.get("account_id") else None
        if acct:
            store.log_event("churn_signal", acct["id"], "agent:frontdesk", "R3",
                            {"signal": "reservice", "message": msg_id})
        out["steps"].append({"action": "draft_reservice_booking",
                             "why": "scheduled AND recorded as the churn signal it is"})
    elif c["label"] == "cancellation":
        out["steps"].append({"action": "route_human", "why": c["why"]})
    elif c["label"] == "scheduling":
        gate.act("draft_scheduling_reply", "frontdesk", msg_id,
                 {"summary": f"draft: {m.get('text','')[:60]}"})
        out["steps"].append({"action": "draft_scheduling_reply", "why": "a human sends"})
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("messages", m)
    return out


def bill_service(service_id):
    """The billing path. A non-completed service is refused, logged, and never
    becomes an approvable row."""
    s = store.by_id("services", service_id)
    if not s:
        return {"error": "no such service"}
    okb, why = core.can_bill(s)
    if not okb:
        ev = store.log_event("refused", service_id, "agent:billing", "R0",
                             {"action": "bill_skipped_service", "why": why})
        return {"refused": why, "event": ev["id"]}
    return gate.act("bill_completed_service", "billing", service_id,
                    {"summary": f"bill {s.get('kind','service')} completed {s.get('completed_at')}"},
                    execute=lambda: store.upsert("services", dict(s, billed_at=iso())))


def draft_outreach(text, subject="campaign"):
    """Any outward marketing draft passes the guarantee-language check first."""
    okg, why = core.guarantee_ok(text)
    if not okg:
        ev = store.log_event("refused", subject, "agent:sales", "R0",
                             {"action": "promise_elimination", "why": why})
        return {"refused": why, "event": ev["id"]}
    return gate.act("draft_scheduling_reply", "sales", subject, {"summary": text[:70]})


def _reservice_copy(m):
    """Coverage language only — and the draft is run through the guarantee
    check anyway, so a copy edit can never smuggle in a promise."""
    body = (f"Sorry they're back — that's {core.COVERAGE_LANGUAGE}. We can be out Thursday or "
            f"Friday; reply with which works and the tech will hit the spots you're seeing plus "
            f"the entry points.")
    okg, why = core.guarantee_ok(body)
    assert okg, why  # structural: the shipped copy passes its own check
    return body


def _save_visit_copy(account):
    name = (account.get("name") or "there").split()[0]
    body = (f"Hi {name} — checking in, not upselling. Between the recent reservice and the missed "
            f"stop, your service hasn't been what it should be. The route manager would like to "
            f"walk the property with you this week, free, and reset the treatment plan. When "
            f"suits?")
    okg, why = core.guarantee_ok(body)
    assert okg, why
    return body


SAVE_VISIT_COOLDOWN_DAYS = 30


def save_visit_sweep(limit=10):
    """One drafted route-manager save visit per two-signal account per 30 days."""
    out = {"drafted": 0, "skipped": 0}
    from _kit.store import now, parse
    for row in core.churn_board()["rows"]:
        if out["drafted"] >= limit:
            break
        acct = store.by_id("accounts", row["account"])
        if not acct or acct.get("demo_tag"):
            continue
        last = acct.get("save_visit_at")
        if last and (now() - (parse(last) or now())).days < SAVE_VISIT_COOLDOWN_DAYS:
            out["skipped"] += 1
            continue
        body = _save_visit_copy(acct)
        gate.act("draft_save_visit", "routemanager", acct["id"],
                 {"summary": f"{row['count']} signals: " + ", ".join(s["signal"] for s in row["signals"]),
                  "preview": body[:110]})
        acct["save_visit_at"] = iso()
        store.upsert("accounts", acct)
        out["drafted"] += 1
    return out


def run_all():
    handled = 0
    for m in store.load("messages"):
        if not m.get("handled_at"):
            handle_message(m["id"])
            handled += 1
    return {"messages": {"handled": handled}, "saves": save_visit_sweep()}
