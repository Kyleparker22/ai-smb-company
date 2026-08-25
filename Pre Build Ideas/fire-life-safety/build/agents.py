#!/usr/bin/env python3
"""Code OS — the agents. Everything routes through `core.gate`. Stdlib only."""
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

    if c["label"] == "impairment":
        gate.act("escalate_impairment", "frontdesk", msg_id,
                 {"summary": m.get("text", "")[:60], "verbatim": m.get("text", "")})
        ev = store.log_event("refused", msg_id, "agent:frontdesk", "R0",
                             {"action": "downgrade_impairment",
                              "why": "software never decides an impairment was minor"})
        out["steps"].append({"action": "escalate_impairment", "said": core.FIRE_WATCH,
                             "why": c["why"], "event": ev["id"]})
    elif c["label"] == "marshal":
        ev = store.log_event("refused", msg_id, "agent:frontdesk", "R0",
                             {"action": "correspond_with_ahj",
                              "why": "the owner talks to the fire marshal"})
        out["steps"].append({"action": "route_to_owner",
                             "refused": "software never corresponds with the AHJ",
                             "why": c["why"], "event": ev["id"]})
    elif c["label"] == "due_ask":
        body = _booking_copy(m)
        gate.act("draft_inspection_booking", "frontdesk", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_inspection_booking", "why": "a human sends"})
    elif c["label"] == "quote_ask":
        out["steps"].append({"action": "route_to_deficiency_ladder",
                             "why": "the ladder answers with the finding and code reference cited"})
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("messages", m)
    return out


def _booking_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — pulling your device calendar now; anything due or overdue gets offered "
            f"first. Reply with two windows that work and the inspector will be there — the tag "
            f"gets a record behind it, which is what the tag is for.")


def _deficiency_copy(f, touch_n):
    """Deficiency chase — the finding and the code reference recorded with it,
    factual, no fear copy."""
    site = f.get("site_name", "your building")
    finding = f.get("finding", "the deficiency")
    code = f.get("code_ref", "the applicable standard")
    amt = f"${f.get('quote', 0):,.0f}"
    return {
        1: (f"From the last inspection at {site}: {finding} (ref {code}). The repair quote is "
            f"{amt}, and the finding stays open on your compliance record until it's fixed or "
            f"you tell us it was handled elsewhere. Want it scheduled?"),
        2: (f"Second note on the open finding at {site}: {finding}. Same {amt} quote. If another "
            f"contractor fixed it, send the record and we'll close it properly — that's a fine "
            f"outcome too."),
        3: (f"Last note on {finding} at {site}; we'll leave it with you. It remains on the open "
            f"list — not as pressure, but because a finding that quietly disappears helps nobody "
            f"at inspection time."),
    }.get(touch_n, f"Open finding at {site}: {finding} ({amt}).")


def mark_device(device_id, human=None, result=None):
    """The compliance path: a device is marked only WITH a recorded inspection
    result by a human; software marking without a record is refused."""
    d = store.by_id("devices", device_id)
    if not d:
        return {"error": "no such device"}
    if not human or not result:
        ev = store.log_event("refused", device_id, "agent:calendar", "R0",
                             {"action": "mark_compliant_without_record",
                              "why": "a green check without a record is the lie this system "
                                     "cannot tell — an inspector records a result, or the "
                                     "device stays as it is"})
        return {"refused": "no inspector result recorded — the device state does not change",
                "event": ev["id"]}
    d["last_inspected"] = iso()
    d["last_result"] = result
    store.upsert("devices", d)
    store.log_event("device_inspected", device_id, f"human:{human}", "R1", {"result": result})
    return {"marked": True, "by": human}


def deficiency_sweep(limit=15):
    out = {"drafted": 0, "skipped": 0}
    for f in store.load("deficiencies"):
        if out["drafted"] >= limit:
            break
        plan = core.deficiency_plan(f)
        if plan["action"] != "draft_chase":
            out["skipped"] += 1
            continue
        touch_n = len(f.get("touches") or []) + 1
        body = _deficiency_copy(f, touch_n)
        gate.act("draft_deficiency_chase", "sales", f["id"],
                 {"summary": f"{f.get('finding','finding')[:40]} ${f.get('quote',0):,.0f} touch {touch_n}",
                  "preview": body[:110]})
        f.setdefault("touches", []).append({"at": iso(), "kind": "drafted", "body": body})
        store.upsert("deficiencies", f)
        out["drafted"] += 1
    return out


def run_all():
    handled = 0
    for m in store.load("messages"):
        if not m.get("handled_at"):
            handle_message(m["id"])
            handled += 1
    return {"messages": {"handled": handled}, "deficiencies": deficiency_sweep()}
