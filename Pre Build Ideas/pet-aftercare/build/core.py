#!/usr/bin/env python3
"""Ember OS — domain core (pet aftercare & cremation).

Rules live here: identity-first triage (the wrong-ashes worry outranks
everything), the chain of custody (every transfer requires the recorded tag
verification — a transfer without it has no code path, and a gap reads HOLD,
never assumed), the service-level wall, the family tone check, the keepsake
proof rule, the aged-remains policy clock, and the matrix.

Written with restraint: this vertical's product is a family's trust at the
loss of a pet they loved. The system runs the logistics and refuses
everything that must stay human — and it never lets the logistics leak into
a family's inbox.

Stdlib only. Honesty rules come from `_kit`.
"""
import re, sys
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent))

from _kit.moat import Eval, Gate, Matrix, Roi                       # noqa: E402
from _kit.store import (Store, automation_rate, iso, now,           # noqa: E402
                        parse, unmeasured)

TABLES = ("config", "pets", "clinics", "loads", "messages", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="EMBEROS_DATA_ROOT")

SERVICE_LEVELS = ("private", "individual", "communal")


# ---------------------------------------------------------------- the chain of custody

CHAIN_STEPS = ("clinic", "van", "facility", "chamber", "urn", "return")


def chain_status(pet):
    """Walk the recorded chain. Every link needs its tag verification and its
    steps in order; anything else reads HOLD — a gap is never assumed away."""
    custody = pet.get("custody") or []
    if not custody:
        return {"state": "HOLD", "at": "clinic",
                "why": "no custody record yet — nothing is assumed; the chain starts at the "
                       "first tag-checked transfer"}
    pos = 0
    for t in custody:
        tc = t.get("tag_check") or {}
        if not tc.get("tag") or not tc.get("by"):
            return {"state": "HOLD", "at": CHAIN_STEPS[pos],
                    "why": "a transfer in this record is missing its tag verification — the "
                           "chain reads HOLD, never assumed; a person walks it back physically"}
        if tc["tag"] != pet.get("tag"):
            return {"state": "HOLD", "at": CHAIN_STEPS[pos],
                    "why": f"tag mismatch in the record ({tc['tag']} vs {pet.get('tag')}) — "
                           f"HOLD, never assumed; a person resolves it before anything moves"}
        want_from, want_to = CHAIN_STEPS[pos], CHAIN_STEPS[pos + 1]
        if t.get("from") != want_from or t.get("to") != want_to:
            return {"state": "HOLD", "at": want_from,
                    "why": f"gap in the chain — the record jumps {t.get('from')} → {t.get('to')} "
                           f"where {want_from} → {want_to} was expected. A gap reads HOLD, "
                           f"never assumed; the pet does not move again until a person closes it"}
        pos += 1
    return {"state": "intact", "at": CHAIN_STEPS[pos], "steps": pos,
            "complete": pos == len(CHAIN_STEPS) - 1}


def chain_narrative(pet):
    """The verbatim record — every transfer, quoted as written. This is the
    only honest answer to the identity worry; nothing here is paraphrased."""
    st = chain_status(pet)
    lines = []
    for t in pet.get("custody") or []:
        tc = t.get("tag_check") or {}
        lines.append(f"{str(t.get('at', ''))[:16].replace('T', ' ')} — {t.get('from')} → "
                     f"{t.get('to')}: tag {tc.get('tag', '(none)')} read and matched by "
                     f"{tc.get('by', '(no one recorded)')}")
    return {"status": st, "lines": lines, "tag": pet.get("tag")}


def record_transfer(pet_id, to=None, tag_read=None, by=None, actor="custody"):
    """THE ONLY WAY a custody transfer is recorded. The tag verification is a
    required input, checked against the pet's record, before anything is
    written — a transfer without it has no code path anywhere in this build."""
    pet = store.by_id("pets", pet_id)
    if not pet:
        return {"error": "no such pet"}
    if not tag_read or not by:
        r = gate.act("transfer_without_tag_check", actor, pet_id,
                     {"attempted_to": to, "why": "no tag verification presented"})
        return {"refused": "no transfer without the recorded tag verification — the check is "
                           "the chain, and the chain is the business", "event": r.get("event")}
    if tag_read != pet.get("tag"):
        r = gate.act("transfer_without_tag_check", actor, pet_id,
                     {"attempted_to": to, "why": f"tag read {tag_read} does not match the "
                                                 f"record {pet.get('tag')}"})
        return {"refused": f"the tag read ({tag_read}) does not match the record "
                           f"({pet.get('tag')}) — the transfer HOLDs and a person walks it "
                           f"back physically", "event": r.get("event")}
    st = chain_status(pet)
    if st["state"] == "HOLD":
        return {"refused": f"this chain is on HOLD — {st['why']}. Nothing moves over a hold."}
    if st.get("complete"):
        return {"refused": "the chain is complete — this pet is home"}
    expected = CHAIN_STEPS[CHAIN_STEPS.index(st["at"]) + 1]
    if to and to != expected:
        return {"refused": f"custody steps cannot be skipped — at {st['at']}, the next step "
                           f"is {expected}, not {to}"}
    to = to or expected

    def _write():
        p = store.by_id("pets", pet_id)
        p.setdefault("custody", []).append(
            {"at": iso(), "from": st["at"], "to": to,
             "tag_check": {"tag": tag_read, "by": by, "at": iso()}})
        if to == "urn" and not p.get("ashes_ready_at"):
            p["ashes_ready_at"] = iso()
        if to == "return":
            p["returned_at"] = iso()
        store.upsert("pets", p)
        return {"to": to}

    r = gate.act("record_transfer", actor, pet_id,
                 {"from": st["at"], "to": to, "tag": tag_read, "by": by}, execute=_write)
    return {"recorded": True, "from": st["at"], "to": to, "tag_checked_by": by,
            "gate": r, "chain": chain_status(store.by_id("pets", pet_id))}


# ---------------------------------------------------------------- the service-level wall

def change_service_level(pet_id, new_level, human=None, consent_ref=None):
    """Human-only, with the family's recorded consent ref. Software drafts the
    conversation; it never flips the level — a communal cremation performed on
    a paid-private pet is irreversible."""
    pet = store.by_id("pets", pet_id)
    if not pet:
        return {"error": "no such pet"}
    if new_level not in SERVICE_LEVELS:
        return {"error": f"service level must be one of {SERVICE_LEVELS}"}
    if not human or not consent_ref:
        r = gate.act("change_service_level", "caredesk", pet_id,
                     {"attempted": new_level, "recorded": pet.get("service_level"),
                      "election_ref": pet.get("election_ref")})
        return {"refused": f"{pet['name']} is recorded {pet.get('service_level')} under signed "
                           f"election {pet.get('election_ref')} — a change is a human act with "
                           f"the family's recorded consent ref, never a software write",
                "event": r.get("event")}
    old = pet.get("service_level")
    pet["service_level"] = new_level
    pet.setdefault("consent_refs", []).append(
        {"ref": consent_ref, "from": old, "to": new_level, "by": human, "at": iso()})
    store.upsert("pets", pet)
    store.log_event("service_level_changed", pet_id, f"human:{human}", "R1",
                    {"from": old, "to": new_level, "consent_ref": consent_ref})
    return {"changed": True, "from": old, "to": new_level, "consent_ref": consent_ref}


def add_to_load(load_id, pet_id, actor="chamber"):
    """The chamber board. A private pet shares a chamber with no one, and no
    pet enters a load that doesn't match its recorded election — structural."""
    load = store.by_id("loads", load_id)
    pet = store.by_id("pets", pet_id)
    if not load or not pet:
        return {"error": "no such load or pet"}
    level = pet.get("service_level")
    if level != load.get("kind"):
        r = gate.act("mix_private_chamber_load", actor, pet_id,
                     {"load": load_id, "load_kind": load.get("kind"), "pet_level": level,
                      "election_ref": pet.get("election_ref")})
        return {"refused": f"{pet['name']} is recorded {level} (signed election "
                           f"{pet.get('election_ref')}); this load is {load.get('kind')} — "
                           f"service levels do not mix, structurally", "event": r.get("event")}
    if load.get("kind") == "private" and load.get("pets"):
        r = gate.act("mix_private_chamber_load", actor, pet_id,
                     {"load": load_id, "why": "a private load already holds its one pet"})
        return {"refused": "a private chamber load holds exactly one pet — private means "
                           "alone, and that is not a setting", "event": r.get("event")}

    def _write():
        l = store.by_id("loads", load_id)
        l.setdefault("pets", []).append(pet_id)
        store.upsert("loads", l)
        return True

    r = gate.act("add_to_chamber_load", actor, pet_id,
                 {"load": load_id, "kind": load.get("kind")}, execute=_write)
    return {"added": True, "load": load_id, "gate": r}


# ---------------------------------------------------------------- the family tone check

FORBIDDEN_TO_FAMILY = ("shipment", "unit", "processed", "disposal", "inventory")


def tone_ok(text):
    t = (text or "").lower()
    hits = [w for w in FORBIDDEN_TO_FAMILY if re.search(rf"\b{w}s?\b", t)]
    if hits:
        return False, (f"logistics language never reaches a family — forbidden here: "
                       f"{', '.join(hits)}. This is a goodbye, not a delivery.")
    return True, "ok"


# ---------------------------------------------------------------- keepsakes: the proof rule

def approve_proof(pet_id, family=None, ref=None):
    """Urn engraving proof approval is the FAMILY's recorded act. Software
    drafts the proof and never signs off a name spelling — the name on the
    urn is forever."""
    pet = store.by_id("pets", pet_id)
    if not pet:
        return {"error": "no such pet"}
    proof = (pet.get("keepsakes") or {}).get("engraving")
    if not proof:
        return {"error": "no engraving proof on file for this pet"}
    if not family or not ref:
        r = gate.act("approve_engraving_proof", "keepsakes", pet_id,
                     {"proof": proof.get("text")})
        return {"refused": "the proof is approved by the family's recorded act — software "
                           "never approves a spelling that will be engraved forever",
                "event": r.get("event")}
    proof["approved"] = {"by": family, "ref": ref, "at": iso()}
    pet.setdefault("keepsakes", {})["engraving"] = proof
    store.upsert("pets", pet)
    store.log_event("proof_approved", pet_id, f"family:{family}", None,
                    {"ref": ref, "text": proof.get("text")})
    return {"approved": True, "by": family, "ref": ref, "text": proof.get("text")}


# ---------------------------------------------------------------- the aged-remains clock

RETURN_MAX_TOUCHES = 3
RETURN_COOLDOWN_DAYS = 21

DEFAULT_RETURN_POLICY = {
    "_source": ("DEFAULT aged-remains policy clock, simplified — replace with the operator's "
                "adopted policy and any local rule before go-live. Every date is a DATE ALERT, "
                "not legal advice."),
    "days_before_final_disposition": 180,
}


def return_policy():
    return store.load("config").get("return_policy") or DEFAULT_RETURN_POLICY


def return_board(ref=None):
    """Ashes ready, not yet home — with each case's gentle ladder and clock."""
    ref = ref or now()
    policy = return_policy()
    rows = []
    for p in store.load("pets"):
        if not p.get("ashes_ready_at") or p.get("returned_at") or p.get("final_disposition_at") \
           or p.get("demo_tag"):
            continue
        ready = parse(p["ashes_ready_at"])
        days = (ref - ready).days if ready else None
        row = {"pet": p["id"], "name": p.get("name"), "family": p.get("family"),
               "days_waiting": days, "touches": len(p.get("return_touches") or [])}
        if days is not None:
            row["clock_days_left"] = policy["days_before_final_disposition"] - days
            row["label"] = ("DATE ALERT — what happens after the clock is a human decision, "
                            "never before and never by software")
        rows.append(row)
    rows.sort(key=lambda r: -(r.get("days_waiting") or 0))
    return {"rows": rows, "policy_source": policy["_source"]}


def return_plan(pet, ref=None):
    ref = ref or now()
    touches = pet.get("return_touches") or []
    if len(touches) >= RETURN_MAX_TOUCHES:
        return {"action": "none", "why": f"ladder exhausted at {RETURN_MAX_TOUCHES} — the clock "
                                         f"runs quietly; the final decision stays a human act"}
    last = parse(touches[-1]["at"]) if touches else parse(pet.get("ashes_ready_at"))
    if last and (ref - last).days < RETURN_COOLDOWN_DAYS:
        return {"action": "none", "why": f"inside the {RETURN_COOLDOWN_DAYS}-day cooldown — "
                                         f"grief is not chased"}
    return {"action": "draft_reminder", "why": f"touch {len(touches)+1} of {RETURN_MAX_TOUCHES}"}


def can_final_disposition(pet, ref=None):
    ref = ref or now()
    policy = return_policy()
    if pet.get("returned_at"):
        return False, "this pet is home — there is nothing to decide"
    ready = parse(pet.get("ashes_ready_at"))
    if not ready:
        return False, "no ready date recorded — the clock never started"
    days = (ref - ready).days
    need = policy["days_before_final_disposition"]
    if days < need:
        return False, (f"the recorded policy clock runs {need} days; this case is at {days}. "
                       f"Before the clock the answer is the gentle ladder — we keep "
                       f"{pet.get('name')} safe and we wait.")
    return True, (f"clock complete ({days}d ≥ {need}d) — what happens next is a human "
                  f"decision, made once and recorded, and only now")


def final_disposition(pet_id, human=None):
    pet = store.by_id("pets", pet_id)
    if not pet:
        return {"error": "no such pet"}
    okd, why = can_final_disposition(pet)
    if not okd:
        r = gate.act("final_disposition_before_clock", "returns", pet_id, {"why": why})
        return {"refused": why, "event": r.get("event")}
    if not human:
        return {"refused": "the clock is complete but the final decision is a human act — "
                           "a person decides, once, and it is recorded", "why": why}
    pet["final_disposition_at"] = iso()
    store.upsert("pets", pet)
    store.log_event("final_disposition", pet_id, f"human:{human}", "R1", {"why": why})
    return {"done": True, "why": why}


# ---------------------------------------------------------------- counted, this week

def recovered_this_week(ref=None):
    """Counted, never asserted: pets home, tag checks recorded, proofs the
    family approved, and reminders a human actually sent — inside 7 days."""
    ref = ref or now()
    pets = store.load("pets")
    home = [p for p in pets if p.get("returned_at")
            and (ref - (parse(p["returned_at"]) or ref)).days <= 7]
    checks = 0
    for p in pets:
        for t in p.get("custody") or []:
            at = parse((t.get("tag_check") or {}).get("at"))
            if at and (ref - at).days <= 7:
                checks += 1
    proofs = sum(1 for e in store.events(kind="proof_approved")
                 if (ref - (parse(e.get("at")) or ref)).days <= 7)
    reminders = sum(1 for e in store.events(kind="draft_return_reminder")
                    if str(e.get("actor", "")).startswith("human:")
                    and (ref - (parse(e.get("at")) or ref)).days <= 7)
    return {"pets_home": len(home), "tag_checks_recorded": checks,
            "proofs_approved": proofs, "reminders_sent": reminders,
            "note": "counted from the custody records and the event log — never asserted"}


# ---------------------------------------------------------------- triage

IDENTITY = (
    r"\b(really|actually|truly)\b.*\b(ashes|remains)\b",
    r"\b(ashes|remains)\b.*\b(really|actually|truly)\b",
    r"\b(right|wrong|someone else'?s?|another (pet|dog|cat|family)'?s?)\b.*\b(ashes|remains)\b",
    r"\b(ashes|remains)\b.*\b(someone else'?s?|another (pet|dog|cat|family)|wrong|mixed)\b",
    r"\b(mix(ed)?[- ]?up|mixing up|swap(ped)?|switch(ed)?)\b.*\b(pets?|ashes|remains|cremat\w*)\b",
    r"\b(cremat\w+)\b.*\b(mix(ed|ing)?[- ]?up|swap)\w*",
    r"\bhow (do|can|would) (i|we) know\b.*\b(ashes|remains|his|hers?|him|her|didn'?t)\b",
)
CLINIC_PICKUP = (
    r"\b(clinic|hospital|veterinary|vet)\b.*\b(pick ?up|collect|ready|waiting)\b",
    r"\b(pick ?up|collect|route|driver)\b.*\b(clinic|hospital|patients?)\b",
)
ADDON = (
    r"\b(add|order|upgrade|purchase|buy|include)\w*\b.*\b(paw ?print|nose ?print|keepsake|"
    r"engrav\w+|urn|fur clipping)\b",
    r"\b(paw ?print|nose ?print|keepsake|engrav\w+|fur clipping)\b",
    r"\burn\b.*\b(instead|upgrade|order|engraved?|cedar|brass)\b",
)
STATUS = (
    r"\b(when|how long|status|update|any word|hear)\b.*\b(ashes|urn|ready|back|home|him|her)\b",
    r"\b(is|are)\b.*\b(ready|done)\b",
    r"\b(ashes|urn)\b.*\b(ready|when|status)\b",
)
RETURN_ARR = (
    r"\b(deliver\w*|drop (them |it |him |her )?off|mail|courier)\b.*\b(ashes|urn|home|house)\b",
    r"\b(come (by|in|to you)|stop by|swing by)\b.*\b(ashes|urn|home|hours|bring)\b",
    r"\bbring (him|her|them|\w+) home\b",
)


def read_message(text):
    """identity_worry | clinic_pickup_request | status_ask | addon_order |
    return_arrangement | human. The identity worry reads first — always."""
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty message — a person reads it"}
    for rx in IDENTITY:
        if re.search(rx, t):
            return {"label": "identity_worry",
                    "why": "the wrong-ashes worry — never answered with comfort alone; the "
                           "verbatim chain of custody is the answer, and a human sends it"}
    for rx in CLINIC_PICKUP:
        if re.search(rx, t):
            return {"label": "clinic_pickup_request",
                    "why": "a clinic pickup — routed from the recorded request, the clinic's "
                           "recorded preferences cited"}
    for rx in ADDON:
        if re.search(rx, t):
            return {"label": "addon_order",
                    "why": "a keepsake order — recorded; any engraving waits on the family's "
                           "approved proof"}
    for rx in STATUS:
        if re.search(rx, t):
            return {"label": "status_ask",
                    "why": "a status ask — answered from the chain, in family language"}
    for rx in RETURN_ARR:
        if re.search(rx, t):
            return {"label": "return_arrangement",
                    "why": "bringing them home — method recorded, confirmed by a person"}
    return {"label": "human", "why": "no clean signal — a person reads it"}


# ---------------------------------------------------------------- eval

triage_eval = Eval("message triage",
                   costly_label="identity_worry",
                   costly_note=("THE WRONG ASHES END THE BUSINESS. A family's identity worry "
                                "answered with reassurance instead of the record is the doubt "
                                "that never heals and the story that closes the doors. "
                                "Over-routing a status ask costs a read."))

EVAL_CASES = [
    {"input": "how do I know these are really Max's ashes", "label": "identity_worry"},
    {"input": "are you sure these are actually Bella's remains and not another dog's",
     "label": "identity_worry"},
    {"input": "I read about crematories mixing up pets, how do I know you didn't",
     "label": "identity_worry"},
    {"input": "did we get the right ashes back? the bag seems small", "label": "identity_worry"},
    {"input": "riverbend animal hospital has three patients ready for pickup",
     "label": "clinic_pickup_request"},
    {"input": "can your driver collect two pets from our clinic tomorrow",
     "label": "clinic_pickup_request"},
    {"input": "when will Luna's ashes be ready to come home", "label": "status_ask"},
    {"input": "any update on Cooper? we miss him", "label": "status_ask"},
    {"input": "we'd like to add a paw print keepsake for Daisy", "label": "addon_order"},
    {"input": "can we order the engraved cedar urn instead of the standard one",
     "label": "addon_order"},
    {"input": "can you deliver Milo's ashes to our house on saturday",
     "label": "return_arrangement"},
    {"input": "we'd rather come to you to bring Rosie home, what are your hours",
     "label": "return_arrangement"},
    {"input": "", "label": "human"},
    {"input": "thank you for taking such good care of our girl", "label": "human"},
    {"input": "do you also do horses", "label": "human"},
]


def run_eval():
    return triage_eval.run(EVAL_CASES, lambda t: read_message(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_message":        {"rung": "R3", "reason": "routing only; the identity worry reads first"},
    "record_transfer":     {"rung": "R2", "reason": "the recording happens the moment the tag check passes — the check itself is structural and required"},
    "add_to_chamber_load": {"rung": "R2", "reason": "the load record mirrors the physical board; the mix refusal is structural"},
    "transfer_without_tag_check": {"rung": "R0", "reason": "every custody transfer — clinic, van, facility, chamber, urn, return — requires the recorded tag verification; without it there is no path, and a chain gap reads HOLD, never assumed", "never_promote": True},
    "reassure_without_record": {"rung": "R0", "reason": "comfort without the chain is a guess — the identity answer cites the verbatim record or a person calls", "never_promote": True},
    "change_service_level": {"rung": "R0", "reason": "software drafts; the change is a human act with the family's recorded consent ref — a communal cremation on a paid-private pet is irreversible", "never_promote": True},
    "mix_private_chamber_load": {"rung": "R0", "reason": "a private pet shares a chamber with no one — structural, not a setting", "never_promote": True},
    "logistics_language_to_family": {"rung": "R0", "reason": "grief comms never read like shipping updates — the tone check runs on every family draft", "never_promote": True},
    "final_disposition_before_clock": {"rung": "R0", "reason": "unreturned remains wait out the recorded policy clock, and then a human decides — never software, never early", "never_promote": True},
    "approve_engraving_proof": {"rung": "R0", "reason": "the name on the urn is approved by the family's recorded act — software never signs off a spelling", "never_promote": True},
    "draft_identity_answer": {"rung": "R1", "reason": "outward, to a grieving family — a human sends, with the verbatim chain attached"},
    "draft_family_update":  {"rung": "R1", "reason": "outward to a family — a human sends; tone-checked structurally"},
    "draft_pickup_confirmation": {"rung": "R1", "reason": "outward to a clinic — the recorded preferences cited; a human sends"},
    "draft_addon_offer":    {"rung": "R1", "reason": "outward, gentle, offered once — never re-pitched"},
    "draft_return_reminder": {"rung": "R1", "reason": "outward — the gentle ladder; a human sends"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Ember OS — what it computes to")
        .line("Clinic relationships kept", "revenue",
              "active clinics × avg revenue/clinic/mo × 12 × retention lift",
              ["active_clinics", "clinic_avg_monthly", "retention_lift"],
              lambda g: float(g["active_clinics"]) * float(g["clinic_avg_monthly"]) * 12
                        * float(g["retention_lift"]),
              note="active clinics are counted; the lift is your call — trust is the product")
        .line("Keepsakes, offered once", "revenue", "pets/mo × keepsake price × attach lift",
              ["pets_mo", "addon_price", "attach_lift"],
              lambda g: float(g["pets_mo"]) * float(g["addon_price"]) * float(g["attach_lift"])
                        * 12,
              note="the current attach rate is counted; the lift from one gentle offer is yours")
        .line("Route & office hours", "time_saved", "hrs/wk × 52 × rate",
              ["office_hours_wk", "office_rate"],
              lambda g: float(g["office_hours_wk"]) * 52 * float(g["office_rate"]))
        .line("The wrong-ashes file", "scenario",
              "you decide what the unbroken chain is worth",
              ["wrong_ashes_value"], lambda g: float(g["wrong_ashes_value"]),
              assumption="never a number of ours — one mistake ends the business; the intact "
                         "chain is the whole point"))


def roi(given):
    pets = store.load("pets")
    active = set()
    for p in pets:
        d = parse(p.get("intake_at"))
        if d and (now() - d).days <= 90 and p.get("clinic_id"):
            active.add(p["clinic_id"])
    rec = {"active_clinics": len(active)}
    returned = [p for p in pets if p.get("returned_at")]
    with_keepsake = [p for p in returned if p.get("keepsakes")]
    if returned:
        rec["addon_attach_rate"] = round(len(with_keepsake) / len(returned), 3)
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("read_message", "record_transfer", "draft_identity_answer", "draft_family_update",
          "draft_pickup_confirmation", "draft_addon_offer", "draft_return_reminder")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("family:", "clinic:"))
