#!/usr/bin/env python3
"""Ember OS — the agents. Everything routes through `core.gate`. Every word
bound for a family passes the tone check structurally — the assert is the
point. Stdlib only."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core
from core import gate, store
from _kit.store import iso


def _pet_for(m):
    if m.get("pet_id"):
        return store.by_id("pets", m["pet_id"])
    return None


def _first(name):
    return (name or "there").split()[0]


def _pn(pet):
    """Pronouns from the recorded sex — 'they' when unrecorded, never guessed."""
    return {"m": ("he", "him", "his"), "f": ("she", "her", "her")}.get(
        pet.get("sex"), ("they", "them", "their"))


def handle_message(msg_id):
    m = store.by_id("messages", msg_id)
    if not m:
        return {"error": "no such message"}
    c = core.read_message(m.get("text", ""))
    out = {"message": msg_id, "classification": c, "steps": []}
    gate.act("read_message", "caredesk", msg_id, {"label": c["label"], "why": c["why"]})
    pet = _pet_for(m)

    if c["label"] == "identity_worry":
        ev = store.log_event("refused", msg_id, "agent:caredesk", "R0",
                             {"action": "reassure_without_record",
                              "why": "comfort without the chain is a guess — the verbatim "
                                     "record answers, or a person calls"})
        if not pet:
            out["steps"].append({"action": "route_human",
                                 "why": "the worry outranks the queue and no pet record is "
                                        "attached — a person calls, with the record open",
                                 "event": ev["id"]})
        else:
            narrative = core.chain_narrative(pet)
            body = _identity_copy(m, pet, narrative)
            okt, why = core.tone_ok(body)
            assert okt, why  # structural: a family draft passes its own check
            gate.act("draft_identity_answer", "caredesk", msg_id,
                     {"pet": pet["id"], "chain_state": narrative["status"]["state"],
                      "preview": body[:110]})
            m["draft_reply"] = body
            out["steps"].append({"action": "draft_identity_answer", "draft": body,
                                 "chain": narrative, "why": c["why"], "event": ev["id"],
                                 "refused": "no reassurance without the record — the chain is "
                                            "cited verbatim, and a human sends it"})
    elif c["label"] == "clinic_pickup_request":
        clinic = store.by_id("clinics", m.get("clinic_id")) if m.get("clinic_id") else None
        body = _pickup_copy(m, clinic)
        gate.act("draft_pickup_confirmation", "clinicdesk", msg_id,
                 {"clinic": (clinic or {}).get("name"), "preview": body[:110]})
        m["draft_reply"] = body
        out["steps"].append({"action": "draft_pickup_confirmation", "draft": body,
                             "why": "routed from the recorded request; the clinic's recorded "
                                    "preferences cited — never memory"})
    elif c["label"] == "status_ask":
        if not pet:
            out["steps"].append({"action": "route_human",
                                 "why": "no pet record attached — a person answers"})
        else:
            body = _status_copy(m, pet)
            offered = False
            if not pet.get("addon_offered_at") and core.chain_status(pet).get("at") in \
               ("urn", "return"):
                body += " " + _offer_copy(pet)
                pet["addon_offered_at"] = iso()
                store.upsert("pets", pet)
                gate.act("draft_addon_offer", "caredesk", msg_id,
                         {"pet": pet["id"], "note": "offered once — never re-pitched"})
                offered = True
            okt, why = core.tone_ok(body)
            assert okt, why
            gate.act("draft_family_update", "caredesk", msg_id,
                     {"pet": pet["id"], "preview": body[:110]})
            m["draft_reply"] = body
            out["steps"].append({"action": "draft_family_update", "draft": body,
                                 "offered_addon": offered,
                                 "why": "answered from the chain, in family language"})
    elif c["label"] == "addon_order":
        if not pet:
            out["steps"].append({"action": "route_human",
                                 "why": "no pet record attached — a person takes the order"})
        else:
            body = _addon_copy(m, pet)
            okt, why = core.tone_ok(body)
            assert okt, why
            pet.setdefault("keepsakes", {}).setdefault(
                "orders", []).append({"text": m.get("text", "")[:80], "at": iso()})
            store.upsert("pets", pet)
            gate.act("draft_family_update", "caredesk", msg_id,
                     {"pet": pet["id"], "preview": body[:110]})
            m["draft_reply"] = body
            out["steps"].append({"action": "record_addon_order", "draft": body,
                                 "why": "recorded; any engraving waits on the family's "
                                        "approved proof — nothing is set without it"})
    elif c["label"] == "return_arrangement":
        if not pet:
            out["steps"].append({"action": "route_human",
                                 "why": "no pet record attached — a person arranges it"})
        else:
            body = _return_copy(m, pet)
            okt, why = core.tone_ok(body)
            assert okt, why
            pet["return_method_requested"] = {"text": m.get("text", "")[:80], "at": iso()}
            store.upsert("pets", pet)
            gate.act("draft_family_update", "caredesk", msg_id,
                     {"pet": pet["id"], "preview": body[:110]})
            m["draft_reply"] = body
            out["steps"].append({"action": "draft_family_update", "draft": body,
                                 "why": "method recorded; a person confirms before anything "
                                        "moves"})
    else:
        out["steps"].append({"action": "route_human", "why": c["why"]})
    m.update(handled_at=iso(), label=c["label"])
    store.upsert("messages", m)
    return out


# ---------------------------------------------------------------- family copy
# Every one of these passes core.tone_ok — asserted at the call site, tested
# in the suite. Grief tone: no logistics words, no hurry, nothing implied.

def _identity_copy(m, pet, narrative):
    who = _first(m.get("from"))
    name = pet.get("name", "your pet")
    _, _, poss = _pn(pet)
    st = narrative["status"]
    if st["state"] != "intact":
        return (f"Hi {who} — you deserve the record, not reassurance, and I want to be "
                f"straight with you: {name}'s record is on hold at one step while a person "
                f"verifies it physically. Nothing moves while it is. We will call you today "
                f"and walk you through exactly what we find, line by line.")
    lines = "\n".join(f"  · {l}" for l in narrative["lines"])
    return (f"Hi {who} — this is the one question we will never answer with comfort alone. "
            f"Here is {name}'s custody record, exactly as it was written:\n{lines}\n"
            f"{name}'s tag ({narrative['tag']}) was read and matched at every transfer by "
            f"the person named. If any step had been missing its check, {poss} record would "
            f"read HOLD and we would have called you before you ever had to ask. And if you "
            f"would like to sit down with us and walk the record in person, we will go "
            f"through it line by line, for as long as you need.")


STAGE_PHRASE = {
    "clinic": "still with {clinic}, and our driver will bring {obj} into our care on the "
              "next visit, tag checked at the door",
    "van": "with our driver, on the way into our care",
    "facility": "resting safely in our care — {poss} tag was read and matched on arrival",
    "chamber": "being cared for today, exactly as you chose",
    "urn": "ready to come home whenever you are — there is no hurry on anything from "
           "your side",
    "return": "home with you",
}


def _status_copy(m, pet):
    who = _first(m.get("from"))
    name = pet.get("name", "your pet")
    subj, obj, poss = _pn(pet)
    at = core.chain_status(pet).get("at", "facility")
    clinic = store.by_id("clinics", pet.get("clinic_id")) or {}
    phrase = STAGE_PHRASE.get(at, STAGE_PHRASE["facility"]).format(
        clinic=clinic.get("name", "the clinic"), subj=subj, obj=obj, poss=poss)
    return (f"Hi {who} — {name} is {phrase}. Every step of {poss} care is tag-checked and "
            f"written down, and we will reach out the moment there is anything to tell you.")


def _offer_copy(pet):
    return ("If you would ever like a clay paw print or an engraved urn for "
            f"{pet.get('name', 'them')}, we can include one — we mention it just this once, "
            "and only if it feels right to you.")


def _addon_copy(m, pet):
    who = _first(m.get("from"))
    name = pet.get("name", "your pet")
    return (f"Hi {who} — of course. We have noted it for {name}, and if any engraving is "
            f"involved you will see and approve the exact spelling before anything is set — "
            f"nothing is engraved without your written okay. A person will confirm the "
            f"details with you personally.")


def _return_copy(m, pet):
    who = _first(m.get("from"))
    name = pet.get("name", "your pet")
    subj, obj, poss = _pn(pet)
    return (f"Hi {who} — of course. We have noted how you would like {name} to come home, "
            f"and a person will confirm the day and time with you before anything moves. "
            f"{subj.capitalize()} stays safely in our care until then, tag checked at every "
            f"step.")


def _pickup_copy(m, clinic):
    if not clinic:
        return ("Good morning — confirming the pickup request; our driver will call ahead. "
                "Each pet is tag-verified at handoff and signed for on both sides.")
    prefs = clinic.get("preferences") or {}
    return (f"Good morning — confirming our driver's visit to {clinic.get('name')} "
            f"({', '.join(prefs.get('pickup_days') or [])}). Per your recorded preferences: "
            f"{prefs.get('paperwork', 'signed release with each pet')}; urn default "
            f"{prefs.get('urn_default', 'standard cedar')}. Each pet is tag-verified at "
            f"handoff and signed for on both sides.")


def _return_reminder_copy(pet, touch_n):
    who = _first(pet.get("family"))
    name = pet.get("name", "your pet")
    subj, obj, poss = _pn(pet)
    return {
        1: (f"Hi {who} — {name} is safe with us and ready to come home whenever you are. "
            f"There is no rush at all: come by any weekday, or reply and we will arrange a "
            f"quiet visit to your door."),
        2: (f"Hi {who} — we are still holding {name} for you, safely and with care. If "
            f"coming in feels hard, we understand completely — we can bring {obj} home to "
            f"you, or simply keep {obj} here a while longer."),
        3: (f"Hi {who} — we will keep {name} safe with us for as long as you need. Our "
            f"policy asks us to check in one last time, and this is that note — reply "
            f"whenever you are ready and we will hold {obj} well beyond it. There is no "
            f"charge, and no hurry."),
    }.get(touch_n, f"Hi {who} — {name} is ready to come home whenever you are.")


# ---------------------------------------------------------------- the tone probe

def try_family_draft(text, pet_id=None):
    """The only door a family draft leaves through. Logistics language is
    refused structurally and logged — never softened, never sent."""
    okt, why = core.tone_ok(text)
    if not okt:
        r = gate.act("logistics_language_to_family", "caredesk", pet_id or "draft",
                     {"why": why, "preview": (text or "")[:80]})
        return {"refused": why, "event": r.get("event")}
    return {"ok": True, "note": "passes the family tone check"}


# ---------------------------------------------------------------- sweeps

def return_sweep(limit=20):
    out = {"drafted": 0, "skipped": 0}
    for p in store.load("pets"):
        if out["drafted"] >= limit or not p.get("ashes_ready_at") or p.get("returned_at") \
           or p.get("final_disposition_at") or p.get("demo_tag"):
            continue
        plan = core.return_plan(p)
        if plan["action"] != "draft_reminder":
            out["skipped"] += 1
            continue
        touch_n = len(p.get("return_touches") or []) + 1
        body = _return_reminder_copy(p, touch_n)
        okt, why = core.tone_ok(body)
        assert okt, why
        gate.act("draft_return_reminder", "returns", p["id"],
                 {"summary": f"{p.get('name')} ({p.get('family')}) touch {touch_n}",
                  "preview": body[:110]})
        p.setdefault("return_touches", []).append({"at": iso(), "kind": "drafted",
                                                   "body": body})
        store.upsert("pets", p)
        out["drafted"] += 1
    return out


def run_all():
    handled = 0
    for m in store.load("messages"):
        if not m.get("handled_at"):
            handle_message(m["id"])
            handled += 1
    return {"messages": {"handled": handled}, "returns": return_sweep()}
