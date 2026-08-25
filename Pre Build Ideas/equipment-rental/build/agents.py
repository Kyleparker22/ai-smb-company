#!/usr/bin/env python3
"""Yard OS — the agents. Everything routes through `core.gate`. Stdlib only."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import iso, now


def handle_call(call_id):
    """Triage one call. An off-rent request records the call at R2 immediately
    (delaying the record IS the harm) and queues the pickup at R1."""
    call = store.by_id("calls", call_id)
    if not call:
        return {"error": "no such call"}
    c = core.classify_call(call.get("transcript", ""))
    out = {"call": call_id, "classification": c, "steps": []}
    gate.act("classify_call", "frontdesk", call_id, {"label": c["label"], "why": c["why"]})

    if c["label"] == "off_rent":
        rental = store.by_id("rentals", call.get("rental_id")) if call.get("rental_id") else None
        if rental and not rental.get("off_rent_called_at"):
            rental["off_rent_called_at"] = call.get("at") or iso()
            store.upsert("rentals", rental)
            gate.act("record_off_rent", "frontdesk", rental["id"],
                     {"summary": f"billing stops at this call ({rental['off_rent_called_at']})"})
            gate.act("schedule_pickup", "dispatch", rental["id"],
                     {"summary": f"pickup for unit {rental.get('unit_id')} — the yard leak starts now"})
            out["steps"].append({"action": "record_off_rent",
                                 "why": "the clock stopped at this call — recorded before anything else"})
            out["steps"].append({"action": "schedule_pickup", "why": "queued for a human dispatcher"})
        else:
            out["steps"].append({"action": "route_human",
                                 "why": "no open rental matched — a person confirms which machine"})
    elif c["label"] == "breakdown":
        out["steps"].append({"action": "route_service",
                             "why": "machine down — service dispatch; the billing question is a human call"})
    elif c["label"] == "extension":
        if call.get("rental_id"):
            rental = store.by_id("rentals", call["rental_id"]) or {}
            body = _extension_copy(rental)
            gate.act("draft_extension_confirm", "frontdesk", call["rental_id"],
                     {"summary": "extension confirmation draft", "preview": body[:110]})
        out["steps"].append({"action": "draft_extension_confirm", "why": "a human sends"})
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    call.update(handled_at=iso(), label=c["label"])
    store.upsert("calls", call)
    return out


def _extension_copy(rental):
    """Drafted for a human to send — restates the rate and that the clock keeps
    running to the NEW off-rent call, so there is no billing surprise later."""
    unit = rental.get("unit_id", "the machine")
    rate = rental.get("day_rate")
    rate_txt = f"${rate:,.0f}/day" if rate else "the agreed rate"
    return (f"Confirming your extension on {unit} at {rate_txt}. Billing continues until you call "
            f"it off rent — same number, any time, and the clock stops at that call. Thanks for "
            f"the heads-up.")


def _claim_copy(v, rental):
    """The damage conversation, drafted with the evidence pair named. Factual,
    photo counts cited, no accusation language."""
    unit = rental.get("unit_id", "the unit")
    dmg = ", ".join(v["new_damage"])
    ev = v["evidence"]
    return (f"On return of {unit} our check-in found: {dmg}. This wasn't on the checkout record "
            f"({ev['checkout_photos']} photos at handoff; {ev['checkin_photos']} at return — both "
            f"sets attached). The repair estimate follows; happy to walk through the photos "
            f"together first.")


def try_damage_claim(rental_id):
    """Draft a damage claim — or be refused for missing evidence."""
    v = core.damage_claim(rental_id)
    if not v["assertable"]:
        ev = store.log_event("refused", rental_id, "agent:yard", "R0",
                             {"action": "assert_damage_without_evidence", "why": v["refused"]})
        return {**v, "event": ev["id"]}
    rental = store.by_id("rentals", rental_id) or {}
    body = _claim_copy(v, rental)
    r = gate.act("draft_damage_claim", "yard", rental_id,
                 {"summary": f"damage claim: {', '.join(v['new_damage'])}",
                  "evidence": v["evidence"], "preview": body[:110]})
    return {**v, "gate": r, "draft": body}


def pickup_sweep(ref=None):
    """The yard-leak chaser: any off-rent unit waiting 2+ days for pickup gets
    one internal dispatch alert per 3 days — the queue is money idling."""
    ref = ref or now()
    out = {"alerts": 0}
    already = {e["subject"] for e in store.events(kind="pickup_overdue", since_days=3)}
    for row in core.pickup_queue(ref):
        if row["days_waiting"] < 2 or row["rental"] in already:
            continue
        gate.act("pickup_overdue", "dispatch", row["rental"],
                 {"summary": f"unit {row['unit']} waiting {row['days_waiting']}d — not billing, not re-rentable"})
        out["alerts"] += 1
    return out


def waiver(rental_id, amount):
    """Goodwill credit — the standing-limit demo. Small executes at R2; above
    the limit the same action demotes to the gate."""
    return gate.act("issue_waiver", "frontdesk", rental_id,
                    {"summary": f"goodwill credit ${amount:,.0f}"}, amount=amount,
                    execute=lambda: store.log_event("waiver_issued", rental_id,
                                                    "agent:frontdesk", "R2", {"amount": amount}))


def run_all():
    handled = 0
    for c in store.load("calls"):
        if not c.get("handled_at"):
            handle_call(c["id"])
            handled += 1
    return {"calls": {"handled": handled}, "pickups": pickup_sweep(),
            "pickup_queue": len(core.pickup_queue())}
