#!/usr/bin/env python3
"""Halflife OS — the agents. Everything routes through `core.gate`. Stdlib only.

Three human acts the agents can only stage, never perform: sending a
preservation letter (sets on_notice — the clock keeps running), recording a
possession receipt (the only thing that makes an item secured), and contacting
a witness (the only thing that refreshes memory). There is deliberately no
resurrect path — LOST is permanent.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import iso, now, parse


def _firm():
    return store.load("config").get("firm", "the firm")


# ---------------------------------------------------------------- intake

def intake(facts):
    """A new matter spawns its evidence inventory from typed facts, and every
    non-witness item gets a preservation letter DRAFTED in the same call (R1 —
    queued for an attorney, not sent). The incident date starts every clock."""
    missing = [f for f in ("client", "case_type", "incident_date") if not facts.get(f)]
    if missing:
        return {"refused": f"cannot open the matter — missing: {', '.join(missing)}. "
                           f"A clock with no start date cannot be computed"}
    m = {"id": store.nid("mat"), "client": facts["client"],
         "case_type": facts["case_type"], "opposing": facts.get("opposing"),
         "incident_date": facts["incident_date"], "stage": "intake",
         "opened_at": iso()}
    store.upsert("matters", m)
    gate.act("open_matter", "intake", m["id"],
             {"client": m["client"], "incident_date": m["incident_date"],
              "why": "the inventory starts NOW — every day of delay is evidence gone"})
    items, letters = [], []
    for e in (facts.get("evidence") or []):
        item = _spawn_item(m, e.get("type", "footage"), e.get("source"),
                           e.get("custodian"), e.get("custodian_type"))
        items.append({"item": item, "clock": core.clock(item)})
        letters.append(_draft_for(item, m))
    return {"matter": m, "items": items, "letters": letters,
            "note": "letters DRAFTED and queued at R1 for an attorney — NOT sent. "
                    "Every clock runs from the incident date, already burning"}


def _spawn_item(matter, typ, source, custodian, custodian_type):
    item = {"id": store.nid("ev"), "matter_id": matter["id"], "type": typ,
            "source": source or "unnamed", "custodian": custodian or "unnamed",
            "custodian_type": custodian_type or "unstated",
            "created_at": matter.get("incident_date") or iso(), "state": "at_large"}
    store.upsert("evidence", item)
    c = core.clock(item)
    gate.act("inventory_evidence", "preservation", item["id"],
             {"matter": matter["id"], "custodian_type": item["custodian_type"],
              "clock": c["basis"],
              "days_left": c["days_left"] if not c["unknown"] else "UNKNOWN"})
    return item


def _draft_for(item, matter):
    """The right R1 draft for the item: a preservation letter to a custodian,
    or witness outreach for a memory clock. Queued, never sent."""
    if item.get("type") == "witness":
        body = _witness_copy(item, matter)
        r = gate.act("draft_witness_outreach", "preservation", item["id"],
                     {"summary": f"witness outreach — {item.get('source')}",
                      "preview": body[:110]})
    else:
        body = _letter_copy(item, matter)
        r = gate.act("draft_preservation_letter", "preservation", item["id"],
                     {"summary": f"preserve: {item.get('source')} @ {item.get('custodian')}",
                      "preview": body[:110]})
    item["draft"] = body
    item["letter_drafted"] = True
    store.upsert("evidence", item)
    return {"item": item["id"], "gate": r, "draft": body}


def _letter_copy(item, matter):
    c = core.clock(item)
    if c["unknown"]:
        clock_line = (f"We have no recorded retention policy for this material. Please "
                      f"state your retention schedule in writing; until then we treat "
                      f"its expiry as UNKNOWN and this request as immediate.")
    else:
        clock_line = (f"Our records indicate material of this class is retained "
                      f"approximately {c['basis']} — an estimated expiry of "
                      f"{(c['expiry'] or '')[:10]}. This request is time-critical.")
    return (f"PRESERVATION OF EVIDENCE — {item.get('source')}\n"
            f"To: {item.get('custodian')}\n"
            f"Re: {matter.get('client')} — incident of {(matter.get('incident_date') or '')[:10]}\n\n"
            f"You are hereby requested to preserve, and to suspend any routine "
            f"destruction or overwriting of, the material identified above, including "
            f"all native files, metadata and logs. {clock_line}\n\n"
            f"This letter places you on notice of anticipated litigation; failure to "
            f"preserve may constitute spoliation. Please confirm preservation in "
            f"writing and advise how a copy may be obtained — notice is not "
            f"possession, and we intend to take possession.\n\n"
            f"DRAFT FOR ATTORNEY REVIEW — {_firm()}")


def _witness_copy(item, matter):
    c = core.clock(item)
    left = "UNKNOWN" if c["unknown"] else f"{c['days_left']} day(s)"
    return (f"WITNESS OUTREACH — {item.get('source')}\n"
            f"Re: {matter.get('client')} — incident of {(matter.get('incident_date') or '')[:10]}\n\n"
            f"Purpose: schedule a recorded statement while the account is fresh. The "
            f"recorded memory-freshness window on this witness reads {left}; a "
            f"statement not yet taken decays like any other evidence. A recorded "
            f"contact resets the freshness clock — nothing else does.\n\n"
            f"DRAFT FOR ATTORNEY REVIEW — {_firm()}")


# ---------------------------------------------------------------- messages

def handle_message(msg_id):
    m = store.by_id("messages", msg_id)
    if not m:
        return {"error": "no such message"}
    c = core.read_message(m.get("text", ""))
    out = {"message": msg_id, "classification": c, "steps": []}
    gate.act("read_message", "intake", msg_id, {"label": c["label"], "why": c["why"]})

    if c["label"] == "evidence_tip":
        out["steps"].append(_handle_tip(m))
    elif c["label"] == "deadline_ask":
        ev = gate.act("legal_advice_to_nonclient", "intake", msg_id,
                      {"why": "a deadline is legal advice — software states no dates"})
        body = _deadline_copy(m)
        gate.act("draft_status_reply", "intake", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "route_attorney", "draft": body,
                             "refused": "no date, no opinion — a deadline answer is "
                                        "legal advice and this system never gives it",
                             "why": c["why"], "event": ev.get("event")})
    elif c["label"] == "new_matter":
        shell = {"id": store.nid("mat"), "client": m.get("from"),
                 "case_type": "unclassified", "incident_date": None,
                 "stage": "intake", "opened_at": iso()}
        store.upsert("matters", shell)
        gate.act("open_matter", "intake", shell["id"],
                 {"client": shell["client"], "from_message": msg_id,
                  "why": "the inventory starts NOW; typed intake facts complete it"})
        out["steps"].append({"action": "open_matter", "matter": shell["id"],
                             "why": "matter shell opened the moment the message landed "
                                    "— every day of delay is evidence gone. Typed "
                                    "intake facts (incident date, evidence list) spawn "
                                    "the inventory and its clocks"})
    elif c["label"] == "status":
        body = _status_copy(m)
        gate.act("draft_status_reply", "intake", msg_id,
                 {"summary": m.get("text", "")[:60], "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_status_reply", "draft": body,
                             "why": "facts from the ledger, no advice"})
    else:
        lq = core.legal_question(m.get("text", ""))
        if lq["is_legal"]:
            ev = gate.act("legal_advice_to_nonclient", "intake", msg_id,
                          {"matched": lq["matched"]})
            out["steps"].append({"action": "route_attorney",
                                 "refused": f"'{lq['matched']}' is a legal question — "
                                            f"routed to a licensed attorney unanswered",
                                 "event": ev.get("event")})
        else:
            out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("messages", m)
    return out


def _handle_tip(m):
    """The costly path. The tip spawns an inventory item and a preservation
    letter draft NOW — the clock started at the incident and is already
    running. An unrecognizable custodian reads UNKNOWN and tops the queue."""
    matter = store.by_id("matters", m.get("matter_id") or "")
    if not matter:
        matter = {"id": store.nid("mat"), "client": m.get("from"),
                  "case_type": "unclassified", "incident_date": None,
                  "stage": "intake", "opened_at": iso()}
        store.upsert("matters", matter)
        gate.act("open_matter", "intake", matter["id"],
                 {"client": matter["client"], "from_message": m["id"],
                  "why": "a tip with no matter still starts an inventory"})
    ct = core.tip_custodian(m.get("text", ""))
    item = _spawn_item(matter, ct["type"], m.get("text", "")[:90],
                       "unnamed — identified from the tip", ct["custodian_type"])
    letter = _draft_for(item, matter)
    c = core.clock(item)
    return {"action": "inventory_evidence", "item": item["id"],
            "clock": ("expiry UNKNOWN — tops the dies-first queue" if c["unknown"]
                      else f"{c['days_left']} day(s) left — {c['basis']}"),
            "draft": letter["draft"], "letter_gate": letter["gate"],
            "why": "the evidence-exists tip is NEVER routed casually: the item is on "
                   "the ledger and the preservation letter is drafted in this same "
                   "pass, queued at R1 for an attorney"}


def _deadline_copy(m):
    who = (m.get("from") or "there").split()[0]
    return (f"Hi {who} — deadline questions are exactly the kind of thing a licensed "
            f"attorney answers, and nothing else should. One of our attorneys will "
            f"call you today to talk through it properly. Nothing in this message is "
            f"a date, an opinion, or advice.\n\n{_firm()}")


def _status_copy(m):
    who = (m.get("from") or "there").split()[0]
    matter = store.by_id("matters", m.get("matter_id") or "")
    if matter:
        items = [i for i in store.load("evidence") if i.get("matter_id") == matter["id"]]
        secured = sum(1 for i in items if i.get("state") == "secured")
        notice = sum(1 for i in items if i.get("state") == "on_notice")
        facts = (f"{len(items)} evidence item(s) on your ledger: {secured} secured in "
                 f"our possession, {notice} under preservation notice.")
    else:
        facts = "your file is being assembled; the evidence ledger will show every item."
    return (f"Hi {who} — factual status from the ledger: {facts} A person reviews "
            f"every step; this note contains no legal opinion.\n\n{_firm()}")


# ---------------------------------------------------------------- the human acts

def secure(item_id, receipt_ref=None, human=None):
    """Only a recorded possession receipt makes an item 'secured' — and a human
    records it. No receipt → assert_evidence_secured refuses at R0."""
    item = store.by_id("evidence", item_id)
    if not item:
        return {"error": "no such item"}
    okc, why = core.can_secure(item, receipt_ref)
    if not okc:
        r = gate.act("assert_evidence_secured", "preservation", item_id, {"why": why})
        return {"refused": why, "event": r.get("event"), "rung": r.get("rung")}
    if not human:
        return {"refused": "a possession receipt is a recorded HUMAN act — name the "
                           "person who logged it", "why": why}
    if item.get("state") == "secured":
        return {"secured": True, "why": "already secured — receipt on file",
                "receipt": item.get("receipt")}
    item.update(state="secured", secured_at=iso(), receipt=receipt_ref)
    store.upsert("evidence", item)
    ev = store.log_event("evidence_secured", item_id, f"human:{human}", "R1",
                         {"receipt": receipt_ref})
    return {"secured": True, "receipt": receipt_ref, "event": ev["id"],
            "why": "possession recorded — the race for this item is over"}


def letter_sent(item_id, human):
    """A HUMAN sending an approved preservation letter sets on_notice. The
    clock KEEPS RUNNING — a letter is notice, not possession."""
    item = store.by_id("evidence", item_id)
    if not item:
        return {"error": "no such item"}
    if item.get("state") == "LOST":
        return {"refused": "this item is LOST and LOST is permanent — a letter now is "
                           "a record for the file, not a state change"}
    if item.get("state") == "at_large":
        item["state"] = "on_notice"
    item["notice"] = {"sent_at": iso(), "by": human}
    store.upsert("evidence", item)
    ev = store.log_event("preservation_letter_sent", item_id, f"human:{human}", "R1",
                         {"note": "notice, not possession — the clock keeps running"})
    return {"state": item["state"], "event": ev["id"],
            "note": "on notice — the clock keeps running until a possession receipt "
                    "is recorded"}


def witness_contact(item_id, human, note=None):
    """A recorded human contact is the only thing that refreshes a witness's
    memory clock."""
    item = store.by_id("evidence", item_id)
    if not item:
        return {"error": "no such item"}
    if item.get("type") != "witness":
        return {"refused": "only a witness item carries a freshness clock"}
    if item.get("state") == "LOST":
        return {"refused": "this witness clock already expired — LOST is permanent; a "
                           "late statement is inventoried as a NEW item"}
    item["last_contact"] = iso()
    store.upsert("evidence", item)
    ev = store.log_event("witness_contact", item_id, f"human:{human}", "R1",
                         {"note": note or "recorded contact — freshness window resets"})
    return {"last_contact": item["last_contact"], "event": ev["id"],
            "clock": core.clock(item)}


# ---------------------------------------------------------------- sweeps

def sweep_expiry(ref=None):
    """Expiry passed → LOST, with died_at and whether we were on notice. The
    ledger does not forgive; there is no resurrect path anywhere in this
    codebase."""
    ref = ref or now()
    marked = 0
    for i in store.load("evidence"):
        if i.get("demo_tag") or i.get("state") not in ("at_large", "on_notice"):
            continue
        c = core.clock(i, ref)
        if c["unknown"] or c["days_left"] is None or c["days_left"] >= 0:
            continue
        i.update(state="LOST", died_at=c["expiry"],
                 was_on_notice=(i.get("state") == "on_notice"))
        store.upsert("evidence", i)
        gate.act("mark_lost", "operations", i["id"],
                 {"died_at": c["expiry"], "was_on_notice": i["was_on_notice"],
                  "basis": c["basis"]})
        marked += 1
    return {"marked_lost": marked}


def letters_sweep(limit=15):
    """Draft preservation letters for at-large items that don't have one yet.
    R1 every time — drafted, never sent."""
    out = {"drafted": 0, "skipped": 0}
    matters = store.index("matters")
    for i in store.load("evidence"):
        if out["drafted"] >= limit:
            break
        if i.get("demo_tag") or i.get("state") != "at_large" or i.get("letter_drafted"):
            out["skipped"] += 1
            continue
        m = matters.get(i.get("matter_id")) or {}
        _draft_for(i, m)
        out["drafted"] += 1
    return out


def run_all():
    handled = 0
    for m in store.load("messages"):
        if not m.get("handled_at"):
            handle_message(m["id"])
            handled += 1
    q = core.dies_first_queue()
    gate.act("rank_queue", "operations", "dies_first_queue",
             {"rows": len(q["rows"]), "unknown_first": q["unknown_count"]})
    return {"messages": {"handled": handled}, "letters": letters_sweep(),
            "expiry": sweep_expiry(),
            "queue": {"rows": len(q["rows"]), "unknown": q["unknown_count"]}}
