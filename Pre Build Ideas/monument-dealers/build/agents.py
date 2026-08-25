#!/usr/bin/env python3
"""Stone OS — the agents. Everything routes through `core.gate`. Stdlib only."""
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
    order = store.by_id("orders", m.get("order_id")) if m.get("order_id") else None

    if c["label"] == "proof_change":
        corr = {"id": store.nid("cx"), "message_id": msg_id, "order_id": m.get("order_id"),
                "verbatim": m.get("text"), "family": m.get("from"), "at": m.get("at") or iso()}
        store.upsert("corrections", corr)
        if order:
            order["engraving_hold"] = {"at": iso(), "why": "family correction on the record"}
            store.upsert("orders", order)
        gate.act("record_proof_change", "proofdesk", corr["id"],
                 {"verbatim": m.get("text", ""), "from": m.get("from"),
                  "hold": bool(order)})
        r0 = gate.act("approve_proof", "proofdesk", corr["order_id"] or msg_id,
                      {"why": "the corrected proof goes back to the family — software never "
                              "approves a proof, corrected or otherwise"})
        body = _proof_ack(m)
        okt, why = core.tone_ok(body)
        assert okt, why  # structural: the shipped copy passes its own tone check
        gate.act("draft_proof_reply", "proofdesk", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "record_proof_change", "correction": corr["id"],
                             "draft": body,
                             "refused": "nothing approved by this message — the corrected "
                                        "proof goes back to the family, and only the family "
                                        "approves it",
                             "why": c["why"], "event": r0["event"]})
    elif c["label"] == "timeline":
        if not order:
            out["steps"].append({"action": "route_human",
                                 "why": "no order linked to this message — a person matches "
                                        "the family to their order first; a guessed status "
                                        "is worse than a short wait"})
        else:
            body = _update_copy(m, order)
            okt, why = core.tone_ok(body)
            assert okt, why
            gate.act("draft_family_update", "frontdesk", order["id"],
                     {"summary": f"{order.get('family_name')} — {order.get('stage')}",
                      "preview": body[:110]})
            m["draft_reply"] = body
            out["steps"].append({"action": "draft_family_update", "draft": body,
                                 "why": "the recorded stage does the talking — never a "
                                        "guessed date"})
    elif c["label"] == "balance":
        if not order:
            out["steps"].append({"action": "route_human",
                                 "why": "no order linked — a person pulls the ledger row "
                                        "before any number is said out loud"})
        else:
            body = _balance_reply(m, order)
            okt, why = core.tone_ok(body)
            assert okt, why
            gate.act("draft_balance_reply", "ledger", order["id"],
                     {"summary": f"balance ${order.get('balance_due') or 0:,.0f}",
                      "preview": body[:110]})
            m["draft_reply"] = body
            out["steps"].append({"action": "draft_balance_reply", "draft": body,
                                 "why": "answered from the ledger, gently — no urgency "
                                        "language exists in this lane"})
    elif c["label"] == "new_inquiry":
        body = _inquiry_copy(m)
        okt, why = core.tone_ok(body)
        assert okt, why
        gate.act("draft_inquiry_reply", "frontdesk", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_inquiry_reply", "draft": body,
                             "why": "a new family's first impression — no hurry, every "
                                    "number in writing"})
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("messages", m)
    return out


def _proof_ack(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — thank you for catching this, truly. Your correction is on the record "
            f"exactly as you wrote it: \"{m.get('text', '')}\". Engraving is on hold, and "
            f"nothing is carved until you have seen and approved the corrected proof yourself — "
            f"that approval is yours alone to give, in writing, whenever you are ready. A "
            f"corrected proof is on its way to you; take all the time you need with it.")


def _update_copy(m, o):
    who = (m.get("from") or "there").split()[0]
    stage = o.get("stage", "contract")
    note = core.STAGE_NOTE.get(stage, stage)
    blocker = o.get("blocker")
    bline = (f" Right now it waits on the {blocker}, and we are on it." if blocker else "")
    return (f"Hi {who} — here is the honest, current state of "
            f"{o.get('deceased_name', 'your family member')}'s memorial: it is at the "
            f"{stage.replace('_', ' ')} stage — {note}.{bline} We would rather tell you the "
            f"real stage than a guessed date, and we will tell you the moment it moves. If a "
            f"date matters to your family — an anniversary, a gathering — tell us and we will "
            f"plan around it.")


def _balance_reply(m, o):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — from the signed contract, the remaining balance on "
            f"{o.get('deceased_name', 'the')}'s memorial is ${o.get('balance_due') or 0:,.0f}. "
            f"Whenever it suits you — phone, mail, or next time you are in. There is no clock "
            f"on this from our side, and the memorial stands either way.")


def _inquiry_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — we are so sorry for your loss. There is no hurry on any of this: "
            f"memorials are decided in months, not days, and nothing good comes from deciding "
            f"before the heart is ready. When it feels right, the showroom is open — come as "
            f"you are, and every option and every number goes in writing before you decide "
            f"anything.")


def _balance_copy(o, touch_n):
    who = (o.get("family_name") or "there").split()[0]
    amt = o.get("balance_due") or 0
    name = o.get("deceased_name", "your family member")
    return {
        1: (f"Hi {who} — a quiet note so it never becomes a surprise: the remaining balance on "
            f"{name}'s memorial is ${amt:,.0f}. Whenever it suits you — phone, mail, or in "
            f"person. There is no clock on this from our side."),
        2: (f"Hi {who} — a gentle second note about the ${amt:,.0f} balance on {name}'s "
            f"memorial. If the timing is hard, tell us and we will work something out — "
            f"families come before ledgers here, always."),
        3: (f"Hi {who} — this is our last note about the balance, and we mean that kindly: we "
            f"will not write about it again. Whenever you are ready, we are here — and the "
            f"memorial stands either way."),
    }.get(touch_n, f"Hi {who} — a note about {name}'s memorial.")


def record_family_approval(proof_id, family_member=None, signature_ref=None, staff=None):
    """The recorded HUMAN act: staff records the family's signed approval —
    a named person and a signature reference, or it is not a record."""
    p = store.by_id("proofs", proof_id)
    if not p:
        return {"error": "no such proof"}
    if not family_member or not signature_ref:
        ev = store.log_event("refused", proof_id, f"human:{staff or 'staff'}", "R1",
                             {"action": "record_family_approval",
                              "why": "an approval without a named family member and a "
                                     "signature reference is not a record — it is the phone "
                                     "note this system exists to replace"})
        return {"refused": "an approval needs a named family member and a signature "
                           "reference — a record, not a phone note", "event": ev["id"]}
    p["approval"] = {"by": family_member, "signature_ref": signature_ref, "at": iso(),
                     "recorded_by": staff or "staff"}
    store.upsert("proofs", p)
    store.log_event("proof_approved", proof_id, f"human:{staff or 'staff'}", "R1",
                    {"family_member": family_member, "signature_ref": signature_ref,
                     "party": "family"})
    return {"approved": True, "approval": p["approval"],
            "note": "recorded as the family's act — software recorded it and did not make it"}


def start_engraving(order_id):
    o = store.by_id("orders", order_id)
    if not o:
        return {"error": "no such order"}
    oke, why = core.can_engrave(o)
    if not oke:
        r = gate.act("start_engraving_without_proof_approval", "shop", order_id, {"why": why})
        return {"refused": why, "event": r["event"]}
    if o.get("engraving_hold"):
        return {"refused": (f"engraving hold on record since {o['engraving_hold']['at']} — "
                            f"{o['engraving_hold']['why']}. The hold lifts when the family "
                            f"approves the corrected proof, not before.")}

    def execute():
        o["stage"] = "engraving"
        o["stage_entered_at"] = iso()
        store.upsert("orders", o)
        return o["stage"]

    r = gate.act("start_engraving", "shop", order_id, {"approval": why}, execute=execute)
    return {"started": True, "why": why, "gate": r}


def schedule_setting(order_id):
    o = store.by_id("orders", order_id)
    if not o:
        return {"error": "no such order"}
    okd, why = core.can_set(o)
    if not okd:
        r = gate.act("set_before_cure", "scheduler", order_id, {"why": why})
        return {"refused": why, "event": r["event"]}
    body = _setting_copy(o, why)
    okt, twhy = core.tone_ok(body)
    assert okt, twhy
    r = gate.act("schedule_setting", "scheduler", order_id,
                 {"summary": f"{o.get('family_name')} — setting request", "preview": body[:110],
                  "date_checks": why})
    return {"clear": True, "why": why, "draft": body, "gate": r}


def _setting_copy(o, why):
    cem = store.by_id("cemeteries", o.get("cemetery_id")) or {}
    return (f"To the {cem.get('name', 'cemetery')} office — requesting a setting date for the "
            f"{o.get('family_name', '')} family memorial. Your approval is on our record and "
            f"the foundation has cured ({why}). We will follow your grounds schedule and your "
            f"paperwork; proposed windows attached.")


def balance_sweep(limit=20):
    out = {"drafted": 0, "skipped": 0}
    for o in store.load("orders"):
        if out["drafted"] >= limit or not o.get("balance_due") or o.get("demo_tag") \
           or o.get("balance_paid_at") or not o.get("set_at"):
            continue  # the ladder only runs after the monument is set — never before
        plan = core.balance_plan(o)
        if plan["action"] != "draft_reminder":
            out["skipped"] += 1
            continue
        touch_n = len(o.get("balance_touches") or []) + 1
        body = _balance_copy(o, touch_n)
        okt, why = core.tone_ok(body)
        assert okt, why
        gate.act("draft_balance_reminder", "ledger", o["id"],
                 {"summary": f"{o.get('family_name')} ${o.get('balance_due') or 0:,.0f} "
                             f"touch {touch_n}",
                  "preview": body[:110]})
        o.setdefault("balance_touches", []).append({"at": iso(), "kind": "drafted",
                                                    "body": body})
        store.upsert("orders", o)
        out["drafted"] += 1
    return out


def run_all():
    handled = 0
    for m in store.load("messages"):
        if not m.get("handled_at"):
            handle_message(m["id"])
            handled += 1
    return {"messages": {"handled": handled}, "balances": balance_sweep()}
