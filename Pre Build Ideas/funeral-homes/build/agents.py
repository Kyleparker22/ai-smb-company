#!/usr/bin/env python3
"""Arrangement OS — the agents. Everything routes through `core.gate`. Stdlib only."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import iso


def handle_call(call_id):
    m = store.by_id("calls", call_id)
    if not m:
        return {"error": "no such call"}
    c = core.read_call(m.get("text", ""))
    out = {"call": call_id, "classification": c, "steps": []}
    gate.act("read_call", "frontdesk", call_id, {"label": c["label"], "why": c["why"]})

    if c["label"] == "first_call":
        gate.act("page_director", "frontdesk", call_id,
                 {"summary": f"FIRST CALL: {m.get('text','')[:50]}",
                  "brief": first_call_brief(m)})
        ev = store.log_event("refused", call_id, "agent:frontdesk", "R0",
                             {"action": "automate_grief_support",
                              "why": "every human word comes from a human"})
        out["steps"].append({"action": "page_director",
                             "said": "We're so sorry. A director is being reached right now and "
                                     "will call you back within minutes. May I confirm where your "
                                     "loved one is, and the best number to reach you?",
                             "why": c["why"], "event": ev["id"]})
    elif c["label"] == "preneed":
        body = _preneed_copy(m)
        gate.act("draft_preneed_appointment", "frontdesk", call_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_preneed_appointment", "why": "a human sends"})
    elif c["label"] == "price_question":
        out["steps"].append({"action": "route_to_gpl_quote",
                             "why": "every number comes itemized from the recorded GPL — see the quote desk"})
    elif c["label"] == "document_status":
        gate.act("answer_document_status", "caredesk", call_id,
                 {"summary": "status answered from the case record"},
                 execute=lambda: True)
        out["steps"].append({"action": "answer_document_status",
                             "why": "a factual answer from the record, logged"})
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("calls", m)
    return out


def first_call_brief(m):
    """What the director gets with the page: the logistics the desk captured
    and nothing interpreted. Every human word comes from a human."""
    return {"verbatim": m.get("text"), "received_at": m.get("at"),
            "capture": ["where the loved one is (facility, room if given)",
                        "caller's name, relationship, callback number",
                        "whether transport has been requested by anyone else"],
            "rule": "the desk confirms logistics and promises the callback — it offers no words "
                    "of its own about the loss; every human word comes from a human"}


CHASE_PARTY = {"death_certificate": "the attending physician / vital records",
               "burial_permit": "the county registrar",
               "cremation_permit": "the medical examiner's office",
               "insurance_assignment": "the insurer's assignments desk"}


def _chase_copy(case, item, touch_n):
    """Institution-facing document chase — we chase so the family doesn't have
    to. Factual, case-numbered, never about the family's grief."""
    kind = item["kind"].replace("_", " ")
    party = CHASE_PARTY.get(item["kind"], "your office")
    needed = f" A service date depends on it ({str(item.get('needed_by'))[:10]})." if item.get("needed_by") else ""
    if touch_n >= core.CHASE_MAX_TOUCHES:
        return (f"Final written follow-up on the {kind} for case {case['id']} before our director "
                f"calls {party} directly.{needed} Reply with status or the direct line to whoever "
                f"holds it.")
    return (f"Following up on the {kind} for case {case['id']}, requested "
            f"{str(item.get('requested_at', ''))[:10]} from {party}.{needed} We handle this chase "
            f"so the family doesn't have to — status or an ETA is all we need.")


def _preneed_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — planning ahead is a kind thing to do for your family, and the "
            f"conversation is unhurried: about an hour, at the home or at your kitchen table, "
            f"no decisions required that day. You'll leave with the itemized price list either "
            f"way. What week works?")


def chase_sweep(limit=15):
    out = {"drafted": 0, "to_human": 0, "skipped": 0}
    for case in store.load("cases"):
        if case.get("demo_tag"):
            continue
        for item in case.get("documents") or []:
            if out["drafted"] >= limit:
                break
            plan = core.chase_plan(item)
            if plan["action"] == "draft_chase":
                touch_n = len(item.get("touches") or []) + 1
                body = _chase_copy(case, item, touch_n)
                gate.act("draft_document_chase", "caredesk", case["id"],
                         {"summary": f"chase {item['kind']} for case {case['id']}",
                          "kind": item["kind"], "preview": body[:110]})
                item.setdefault("touches", []).append({"at": iso(), "kind": "drafted",
                                                       "body": body})
                store.upsert("cases", case)
                out["drafted"] += 1
            elif plan["action"] == "human":
                out["to_human"] += 1
            else:
                out["skipped"] += 1
    return out


def run_all():
    handled = 0
    for m in store.load("calls"):
        if not m.get("handled_at"):
            handle_call(m["id"])
            handled += 1
    return {"calls": {"handled": handled}, "chase": chase_sweep()}
