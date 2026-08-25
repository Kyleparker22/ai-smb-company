#!/usr/bin/env python3
"""Closing OS — the agents. Everything routes through `core.gate`. Stdlib only."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import iso, now


def handle_message(msg_id):
    """Triage one message. A wire signal shows the protocol verbatim and
    escalates at R2; the system restates nothing."""
    m = store.by_id("messages", msg_id)
    if not m:
        return {"error": "no such message"}
    c = core.read_message(m.get("text", ""))
    out = {"message": msg_id, "classification": c, "steps": []}
    gate.act("read_message", "intake", msg_id, {"label": c["label"], "why": c["why"]})

    if c["label"] == "wire_signal":
        gate.act("route_wire_signal", "intake", msg_id,
                 {"summary": m.get("text", "")[:60]})
        ev = store.log_event("refused", msg_id, "agent:intake", "R0",
                             {"action": "confirm_wire_change", "why": c["why"]})
        out["steps"].append({"action": "route_wire_signal", "said": core.WIRE_PROTOCOL,
                             "why": c["why"], "event": ev["id"]})
    elif c["label"] == "status_question":
        if m.get("file_id"):
            d = core.status_draft(m["file_id"])
            gate.act("draft_status_reply", "statusdesk", m["file_id"],
                     {"summary": d["draft"][:80]})
            out["steps"].append({"action": "draft_status_reply", "draft": d["draft"],
                                 "why": d["note"]})
        else:
            out["steps"].append({"action": "route_human", "why": "no file matched — a person reads it"})
    elif c["label"] == "date_question":
        gate.act("promise_close_date", "statusdesk", m.get("file_id") or msg_id,
                 {"summary": "date question — a human answers with a date, or doesn't"})
        out["steps"].append({"action": "queue_for_human_date",
                             "why": "a close-date promise is a human decision (R1, never promoted)"})
    else:
        out["steps"].append({"action": "route_human" if c["label"] == "human" else "match_document",
                             "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("messages", m)
    return out


def request_wire_instructions(file_id):
    """The probe surface a demo pushes on: ask the system to send instructions."""
    r = gate.act("send_wire_instructions", "statusdesk", file_id)
    return r


def declare_clear(file_id):
    """Clear-to-close: refused over open items, drafts at R1 when clean."""
    v = core.clear_to_close(file_id)
    if not v.get("clear"):
        ev = store.log_event("refused", file_id, "agent:closer", "R1",
                             {"action": "assert_clear_to_close", "why": v["refused"]})
        return {**v, "event": ev["id"]}
    r = gate.act("assert_clear_to_close", "closer", file_id,
                 {"summary": "all curatives received — a human declares"})
    return {**v, "gate": r}


def chase_sweep(limit=20):
    out = {"drafted": 0, "to_human": 0, "skipped": 0}
    for f in store.load("files"):
        if f.get("closed_at") or f.get("demo_tag"):
            continue
        for item in f.get("curatives") or []:
            if out["drafted"] >= limit:
                break
            plan = core.chase_plan(f, item)
            if plan["action"] == "draft_chase":
                touch_n = len(item.get("touches") or []) + 1
                body = _chase_copy(f, item, touch_n)
                gate.act("draft_chase", "processor", f["id"],
                         {"summary": f"chase {item['kind']} on {f.get('address','file')}",
                          "item": item["kind"], "preview": body[:110]})
                item.setdefault("touches", []).append({"at": iso(), "kind": "drafted",
                                                       "body": body})
                store.upsert("files", f)
                out["drafted"] += 1
            elif plan["action"] == "human":
                out["to_human"] += 1
            else:
                out["skipped"] += 1
    return out


CHASE_PARTY = {"payoff": "the payoff desk", "lien_release": "the lienholder's release team",
               "hoa_estoppel": "the HOA / management company", "survey": "the surveyor",
               "poa": "the signing party", "deed_prep": "the deed-prep attorney"}


def _chase_copy(f, item, touch_n):
    """Party-aware curative chase, drafted for a human. Facts and the file
    number — never a wire detail, never a date promise."""
    kind = item["kind"].replace("_", " ")
    party = CHASE_PARTY.get(item["kind"], "the responsible party")
    addr = f.get("address", "the file")
    if touch_n >= core.CHASE_MAX_TOUCHES:
        return (f"Final written request for the {kind} on {addr} (file {f['id']}). It is the "
                f"last open item; we'll call {party} directly today if it's easier to resolve "
                f"by phone.")
    return (f"Following up on the {kind} for {addr} (file {f['id']}), requested "
            f"{str(item.get('requested_at', ''))[:10]}. Closing is waiting on this item — "
            f"reply with it attached or tell us who at {party} to call.")


def status_sweep(ref=None):
    """Proactive status: one drafted update per open file per 7 days — buyers
    call when nobody calls them. Computed state only, no date promise."""
    ref = ref or now()
    out = {"drafted": 0}
    already = {e["subject"] for e in store.events(kind="queued_for_approval", since_days=7)
               if (e.get("detail") or {}).get("action") == "draft_status_reply"}
    for f in store.load("files"):
        if f.get("closed_at") or f.get("demo_tag") or f["id"] in already:
            continue
        d = core.status_draft(f["id"])
        gate.act("draft_status_reply", "statusdesk", f["id"],
                 {"summary": d["draft"][:80], "proactive": True})
        out["drafted"] += 1
    return out


def run_all():
    handled = 0
    for m in store.load("messages"):
        if not m.get("handled_at"):
            handle_message(m["id"])
            handled += 1
    return {"messages": {"handled": handled}, "chase": chase_sweep(),
            "status": status_sweep()}
