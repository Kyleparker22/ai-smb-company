#!/usr/bin/env python3
"""Gate OS — the agents. Everything routes through `core.gate`. Stdlib only."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import iso, now


def handle_message(msg_id):
    m = store.by_id("messages", msg_id)
    if not m:
        return {"error": "no such message"}
    c = core.read_message(m.get("text", ""))
    out = {"message": msg_id, "classification": c, "steps": []}
    gate.act("read_message", "frontdesk", msg_id, {"label": c["label"], "why": c["why"]})

    if c["label"] == "military_signal":
        tenant = store.by_id("tenants", m.get("tenant_id")) if m.get("tenant_id") else None
        if tenant:
            tenant["military_flag"] = True
            tenant["scra_verified_at"] = None
            store.upsert("tenants", tenant)
        gate.act("freeze_lien_ladder", "frontdesk", m.get("tenant_id") or msg_id,
                 {"summary": f"military signal: {m.get('text','')[:50]}"})
        gate.act("verify_scra", "frontdesk", m.get("tenant_id") or msg_id,
                 {"summary": "verify SCRA status — human task with a record"})
        out["steps"].append({"action": "freeze_lien_ladder",
                             "why": "every lien step frozen for this tenant until a human "
                                    "verifies status — " + core.SCRA_RULE})
    elif c["label"] == "payment_promise":
        tenant = store.by_id("tenants", m.get("tenant_id")) if m.get("tenant_id") else None
        if tenant:
            tenant.setdefault("promises", []).append({"at": iso(), "text": m.get("text")})
            store.upsert("tenants", tenant)
        out["steps"].append({"action": "record_promise", "why": "recorded on the tenant"})
    elif c["label"] == "moveout":
        tenant = store.by_id("tenants", m.get("tenant_id")) if m.get("tenant_id") else None
        body = _moveout_copy(tenant or {})
        gate.act("draft_moveout_confirm", "frontdesk", m.get("tenant_id") or msg_id,
                 {"summary": "move-out confirmation draft", "preview": body[:110]})
        out["steps"].append({"action": "draft_moveout_confirm", "draft": body,
                             "why": "a human sends — the walkthrough date locks the final bill"})
    elif c["label"] == "gate_access":
        out["steps"].append({"action": "route_gate_access", "why": c["why"]})
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("messages", m)
    return out


def _moveout_copy(tenant):
    name = (tenant.get("name") or "there").split()[0]
    unit = tenant.get("unit", "your unit")
    return (f"Hi {name} — got your move-out notice for {unit}. To close it clean: unit empty and "
            f"swept, lock off, and tell us when you're done so we can do the walkthrough — that "
            f"date is what stops the billing, and anything prorated comes back to you. Thanks for "
            f"storing with us.")


def lien_step(tenant_id):
    """Any lien action for a tenant runs through the SCRA gate first."""
    t = store.by_id("tenants", tenant_id)
    if not t:
        return {"error": "no such tenant"}
    okl, why = core.can_lien_step(t)
    if not okl:
        ev = store.log_event("refused", tenant_id, "agent:ledger", "R0",
                             {"action": "lien_step_blocked", "why": why})
        return {"refused": why, "event": ev["id"]}
    cal = core.lien_calendar(t)
    for s in (cal.get("steps") or [])[:1]:
        gate.act("lien_date_alert", "ledger", tenant_id,
                 {"step": s["step"], "due": s["due"], "label": s["label"]})
    return {"calendar": cal}


def dunning_sweep(limit=25):
    out = {"drafted": 0, "to_human": 0, "skipped": 0}
    for t in store.load("tenants"):
        if out["drafted"] >= limit or t.get("demo_tag"):
            continue
        plan = core.dunning_plan(t)
        if plan["action"] == "draft":
            okt, why = core.dunning_text_ok(plan["text"])
            if not okt:
                store.log_event("refused", t["id"], "agent:ledger", "R0",
                                {"action": "threaten_tenant", "why": why})
                continue
            gate.act("draft_reminder", "ledger", t["id"],
                     {"summary": plan["text"][:70], "touch": plan.get("touch"),
                      "preview": plan["text"][:110]})
            t.setdefault("dunning_touches", []).append({"at": iso(), "kind": "drafted",
                                                        "body": plan["text"]})
            store.upsert("tenants", t)
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
    return {"messages": {"handled": handled}, "dunning": dunning_sweep()}
