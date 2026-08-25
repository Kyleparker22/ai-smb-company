#!/usr/bin/env python3
"""Key OS — domain core (locksmiths & access control).

Rules live here: emergency-first triage (a person locked in danger reads before
everything), the authorization gate (no dispatch path exists for an unverified
rekey/unlock — the draft names the missing authority), the key-code scrub
(codes are structurally unexpressable in outbound copy, like PHI), the
append-only master-key registry (a change is a new record, never an edit), the
rate-card clamp (no number off the recorded card exists in this system), the
access-control service clocks, and the matrix.

Stdlib only. Honesty rules come from `_kit`.
"""
import re, sys
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent))

from _kit.moat import Eval, Gate, Matrix, Roi                       # noqa: E402
from _kit.store import (Store, automation_rate, iso, median, now,   # noqa: E402
                        parse, unmeasured)

TABLES = ("config", "systems", "registry", "authorizations", "jobs", "messages",
          "clocks", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="KEYOS_DATA_ROOT")

# ---------------------------------------------------------------- the rate card

DEFAULT_RATE_CARD = {
    "_source": ("DEFAULT rate card, simplified — replace with the company's RECORDED card "
                "before go-live. The clamp is the point: no number off this card exists in "
                "this system, and the after-hours multiplier is on the card, not in a "
                "dispatcher's head at 2am."),
    "lockout_auto": 95, "lockout_residential": 110, "lockout_commercial": 160,
    "rekey_base": 75, "rekey_per_cylinder": 25, "master_system_change": 140,
    "access_control_service": 120,
    "after_hours_multiplier": 1.5, "holiday_multiplier": 2.0,
}

QUOTABLE = ("lockout_auto", "lockout_residential", "lockout_commercial", "rekey",
            "master_system_change", "access_control_service")


def rate_card():
    return store.load("config").get("rate_card") or DEFAULT_RATE_CARD


def quote_for(kind, cylinders=None, after_hours=False, holiday=False):
    """Every quote computes from the recorded card BY CONSTRUCTION — there is
    no argument to this function that can produce a number above it."""
    card = rate_card()
    if kind not in QUOTABLE:
        return unmeasured(f"no rate-card line for {kind!r} — a human quotes it or the card "
                          f"grows a line; software never invents a number", field="total")
    lines = []
    if kind == "rekey":
        lines.append({"item": "rekey service", "amount": card["rekey_base"]})
        if cylinders is None:
            return unmeasured("no cylinder count recorded — a rekey cannot be priced",
                              field="total")
        lines.append({"item": f"cylinders ({cylinders} × ${card['rekey_per_cylinder']})",
                      "amount": round(cylinders * card["rekey_per_cylinder"], 2)})
    else:
        lines.append({"item": kind.replace("_", " "), "amount": card[kind]})
    subtotal = round(sum(l["amount"] for l in lines), 2)
    mult = 1.0
    if holiday:
        mult = card["holiday_multiplier"]
        lines.append({"item": f"holiday multiplier ×{mult} (on the card)",
                      "amount": round(subtotal * (mult - 1), 2)})
    elif after_hours:
        mult = card["after_hours_multiplier"]
        lines.append({"item": f"after-hours multiplier ×{mult} (on the card)",
                      "amount": round(subtotal * (mult - 1), 2)})
    return {"lines": lines, "total": round(subtotal * mult, 2),
            "basis": "computed from the recorded rate card — no other number exists",
            "card_source": card["_source"]}


# ---------------------------------------------------------------- authorization

VERIFICATION_ACTS = ("id_seen", "deed_shown", "lease_shown", "work_order_on_letterhead")
AUTHORITY_ROLES = ("owner_of_record", "manager_of_record")


def authority_for(address):
    """The recorded owner/manager of record for an address, with at least one
    recorded verification act. A phone claim row can never come back from this
    function — that is the whole design."""
    for a in store.load("authorizations"):
        if a.get("address") == address and a.get("role") in AUTHORITY_ROLES \
           and a.get("verified_acts"):
            return a
    return None


def record_phone_claim(address, name, note=None):
    """A phone claim is RECORDED — as a claim. It never becomes authority; the
    row's role keeps it out of `authority_for` structurally."""
    row = {"id": store.nid("au"), "address": address, "name": name,
           "role": "phone_claim", "verified_acts": [],
           "note": note or "recorded as a claim, never as authority",
           "recorded_at": iso()}
    store.upsert("authorizations", row)
    store.log_event("phone_claim_recorded", address, "agent:dispatch", "R2",
                    {"name": name, "why": "a claim is a record, not a verification act"})
    return row


def can_dispatch(kind, address):
    """The authorization gate. A rekey/unlock with no recorded authority has NO
    dispatch path — the draft names what's missing and a human decides."""
    if kind not in ("rekey_request", "routine_lockout", "unlock"):
        return True, "not an authorization-gated job kind", None
    auth = authority_for(address)
    if not auth:
        return False, (f"no recorded owner/manager of record for {address or 'this address'} — "
                       f"a truck needs ID seen plus a deed or lease shown before a rekey or "
                       f"unlock. Opening a door for the wrong person is a break-in with an "
                       f"invoice."), None
    acts = ", ".join(auth.get("verified_acts") or [])
    return True, (f"{auth['name']} is the recorded {auth['role'].replace('_', ' ')} "
                  f"({acts})"), auth["id"]


def can_close(job):
    """Jobs close with the authorization reference and the rate-card citation —
    a closed job with neither is exactly the record that loses the lawsuit."""
    missing = []
    if job.get("kind") in ("rekey", "unlock", "lockout_residential", "lockout_commercial") \
       and not job.get("authorization_ref"):
        missing.append("authorization_ref")
    if not job.get("card_item"):
        missing.append("card_item (the rate-card line billed)")
    if missing:
        return False, (f"cannot close — missing: {', '.join(missing)}. The close record IS "
                       f"the defense file; an unreferenced close is a liability, not a job.")
    return True, (f"closes citing authorization {job.get('authorization_ref') or '(n/a)'} "
                  f"and card line {job['card_item']}")


# ---------------------------------------------------------------- the key-code scrub

# Regex half: keyway-coded and bitting-cut patterns as seeded and as used in the
# trade. Field half: every recorded code in the registry is checked verbatim —
# a code that leaks in any spelling the regex misses still fails the draft.
KEY_CODE_PATTERNS = (
    r"\b[A-Z]{2,3}\d?-\d{4,6}\b",     # keyway code, e.g. SC4-84921, KW1-2214
    r"\b\d(?:-\d){3,6}\b",            # bitting cut sequence, e.g. 3-5-2-4-6
    r"\bbitting\b\s*[:#]?\s*\d{4,6}\b",
)

# The only fields outbound copy may be built from. Codes, keyways and bittings
# are not on this list — the whitelist is the other half of the scrub.
OUTBOUND_FIELDS = ("name", "address", "site", "eta", "card lines", "authorization status")


def key_scrub_ok(text):
    """Outward drafts carry names, addresses and card lines — never key codes.
    Regex + the recorded codes themselves, like the PHI scrub."""
    t = text or ""
    for rx in KEY_CODE_PATTERNS:
        if re.search(rx, t):
            return False, "a key-code pattern never appears in an outward draft"
    for rec in store.load("registry"):
        code = rec.get("key_code")
        if code and code in t:
            return False, (f"a recorded key code never appears in an outward draft — the "
                           f"registry is the vault, not a mail merge")
    return True, "ok"


# ---------------------------------------------------------------- the master-key registry

def system_records(system_id):
    """Every record ever written for a system, oldest first. There is no edit
    function in this module — a change is a NEW record, and both stay."""
    rows = [r for r in store.load("registry") if r.get("system_id") == system_id]
    rows.sort(key=lambda r: r.get("at") or "")
    return rows


def registry_append(system_id, change, authorized_by, key_code=None, supersedes=None):
    """The ONLY write path into the registry. Append-only by construction:
    it never looks up an existing row to modify."""
    rec = {"id": store.nid("rg"), "system_id": system_id, "at": iso(),
           "change": change, "authorized_by": authorized_by,
           "key_code": key_code, "supersedes": supersedes}
    rows = store.load("registry")
    rows.append(rec)
    store.save("registry", rows)
    return rec


# ---------------------------------------------------------------- triage

EMERGENCY = (
    r"\b(toddlers?|childr?e?n?|kids?|bab(y|ies)|infants?|sons?|daughters?|dogs?|pupp(y|ies)|"
    r"pets?|cats?)\b.{0,60}\block(ed)? (in|inside)\b",
    r"\block(ed)? (in|inside)\b.{0,60}\b(toddlers?|childr?e?n?|kids?|bab(y|ies)|infants?)\b",
    r"\b(mom|mother|dad|father|grandma|grandmother|grandpa|grandfather|husband|wife|"
    r"neighbor|roommate)\b.{0,60}\block(ed)?\b.{0,60}\b(not answering|no answer|"
    r"unresponsive|not responding|won'?t answer)\b",
    r"\block(ed)? (in|inside)\b.{0,60}\b(hot|heat|heatstroke|not answering|unresponsive|"
    r"can'?t breathe|medical|hurry|danger)\b",
)
QUOTE = (
    r"\b(how much|price|prices|cost|costs|rate|rates|charge|charges|quote|estimate)\b.{0,60}"
    r"\b(rekey|lock|locks|lockout|unlock|key|keys|open|cylinder)\b",
    r"\b(rekey|lock|locks|lockout|unlock)\b.{0,60}\b(how much|price|cost|rate|charge|quote)\b",
)
MASTER = (
    r"\b(master[- ]?key|master system|grand master|sub[- ]?master)\b",
    r"\b(add|cut|issue|revoke|pull)\b.{0,40}\bkeys?\b.{0,40}\b(system|master)\b",
    r"\b(access[- ]?control|fob|fobs|badge|badges|key ?card)\b",
)
REKEY = (
    r"\bre-?key(ed|ing|s)?\b",
    r"\b(change|changed|changing|swap|swapped|replace|replaced)\b.{0,30}\b(the )?locks?\b",
    r"\blocks? (changed|swapped|replaced)\b",
)
LOCKOUT = (
    r"\block(ed)? (myself )?out\b",
    r"\bkeys? (are )?locked (in|inside)\b",
    r"\block(ed)? my keys? (in|inside)\b",
    r"\blost my keys?\b.{0,40}\b(get in|can'?t get in|house|apartment|car)\b",
    r"\bcan'?t get (in|into)\b.{0,40}\b(house|apartment|car|office|home)\b",
)


def read_message(text):
    """emergency_lockout | routine_lockout | rekey_request | master_system |
    quote | human. The emergency reads FIRST — a person locked in danger is a
    life-safety event, not a job ticket."""
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty message — a person reads it"}
    for rx in EMERGENCY:
        if re.search(rx, t):
            return {"label": "emergency_lockout",
                    "why": "a person or child locked in danger — the reply leads with 911 "
                           "and the truck rolls anyway; this label reads before everything"}
    for rx in QUOTE:
        if re.search(rx, t):
            return {"label": "quote",
                    "why": "price question — answered FROM the recorded card, never around it"}
    for rx in MASTER:
        if re.search(rx, t):
            return {"label": "master_system",
                    "why": "master-key / access-control system — the registry's named "
                           "authorizers decide; a change is a new record, never an edit"}
    for rx in REKEY:
        if re.search(rx, t):
            return {"label": "rekey_request",
                    "why": "a rekey — authorization-gated; no recorded authority means an "
                           "unverifiable draft, not a truck"}
    for rx in LOCKOUT:
        if re.search(rx, t):
            return {"label": "routine_lockout",
                    "why": "a lockout — authorization-gated before any door opens"}
    return {"label": "human", "why": "no clean signal — a person reads it"}


# ---------------------------------------------------------------- service clocks

SERVICE_MAX_TOUCHES = 3
SERVICE_COOLDOWN_DAYS = 14


def service_plan(clock, ref=None):
    """Access-control service reminders on a bounded ladder: 3 touches, a
    cooldown between them, and a silence exit — the ladder never nags forever."""
    ref = ref or now()
    if clock.get("demo_tag"):
        return {"action": "none", "why": "demo fixture — sweeps skip it"}
    last_done = parse(clock.get("last_done_at"))
    if not last_done:
        return {"action": "none", "why": "no recorded service date — the clock never started"}
    due = last_done + timedelta(days=clock.get("interval_days") or 365)
    if ref < due:
        return {"action": "none", "why": f"not due until {iso(due)}"}
    touches = clock.get("touches") or []
    if len(touches) >= SERVICE_MAX_TOUCHES:
        return {"action": "none",
                "why": f"ladder exhausted at {SERVICE_MAX_TOUCHES} — silence exit; the site "
                       f"goes to a human's call list, not an infinite drip"}
    last = parse(touches[-1]["at"]) if touches else None
    if last and (ref - last).days < SERVICE_COOLDOWN_DAYS:
        return {"action": "none", "why": f"inside the {SERVICE_COOLDOWN_DAYS}-day cooldown"}
    return {"action": "draft_service_reminder",
            "why": f"touch {len(touches) + 1} of {SERVICE_MAX_TOUCHES} — "
                   f"{clock.get('kind')} overdue since {iso(due)}"}


def recovered_this_week(ref=None):
    """Counted: jobs closed with their references, dispatches a human sent,
    emergencies recorded, service reminders a human sent. Inside 7 days."""
    ref = ref or now()
    closed = [j for j in store.load("jobs")
              if j.get("closed_at") and (ref - (parse(j["closed_at"]) or ref)).days <= 7]
    card = rate_card()
    closed_value = round(sum(card.get(j.get("card_item"), 0) for j in closed), 2)
    dispatches = sum(1 for e in store.events(kind="draft_dispatch")
                     if str(e.get("actor", "")).startswith("human:")
                     and (ref - (parse(e.get("at")) or ref)).days <= 7)
    emergencies = sum(1 for e in store.events(kind="record_emergency")
                      if (ref - (parse(e.get("at")) or ref)).days <= 7)
    reminders = sum(1 for e in store.events(kind="draft_service_reminder")
                    if str(e.get("actor", "")).startswith("human:")
                    and (ref - (parse(e.get("at")) or ref)).days <= 7)
    return {"jobs_closed": len(closed), "closed_value_on_card": closed_value,
            "dispatches_sent": dispatches, "emergencies_recorded": emergencies,
            "service_reminders_sent": reminders,
            "note": "counted from the job records and the event log — never asserted"}


# ---------------------------------------------------------------- eval

triage_eval = Eval("message triage",
                   costly_label="emergency_lockout",
                   costly_note=("A CHILD LOCKED IN A HOT CAR IS A LIFE-SAFETY EVENT, NOT A JOB "
                                "TICKET — the reply leads with the 911 script and the truck "
                                "rolls anyway. Over-routing a routine lockout costs a read."))

EVAL_CASES = [
    {"input": "my toddler is locked in the car and it's hot", "label": "emergency_lockout"},
    {"input": "my mom is locked in the bathroom and not answering", "label": "emergency_lockout"},
    {"input": "the baby is locked inside the car please hurry", "label": "emergency_lockout"},
    {"input": "my dog is locked in the truck and it's 95 out", "label": "emergency_lockout"},
    {"input": "I'm locked out of my house", "label": "routine_lockout"},
    {"input": "locked my keys in the car at the grocery store", "label": "routine_lockout"},
    {"input": "locked myself out of the apartment again", "label": "routine_lockout"},
    {"input": "I need the house rekeyed after my roommate moved out", "label": "rekey_request"},
    {"input": "just bought the place and want all the locks changed", "label": "rekey_request"},
    {"input": "we need to add a key to the master system at the office park", "label": "master_system"},
    {"input": "can you issue two more fobs for the loading dock badge reader", "label": "master_system"},
    {"input": "how much to rekey a 3 bedroom house with 5 locks", "label": "quote"},
    {"input": "what do you charge for a car lockout after hours", "label": "quote"},
    {"input": "", "label": "human"},
    {"input": "do you sell safes", "label": "human"},
    {"input": "what time do you open saturday", "label": "human"},
]


def run_eval():
    return triage_eval.run(EVAL_CASES, lambda t: read_message(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_message":       {"rung": "R3", "reason": "routing only; the emergency reads first"},
    "record_emergency":   {"rung": "R2", "reason": "the emergency record and the 911 script cannot wait for a click"},
    "perform_without_authorization": {"rung": "R0", "reason": "no dispatch path exists for an unverified rekey/unlock — the draft names the missing authority and a human decides", "never_promote": True},
    "disclose_key_code":  {"rung": "R0", "reason": "key codes are scrubbed from every outbound draft — the registry is the vault, not a mail merge", "never_promote": True},
    "authorize_by_phone_claim": {"rung": "R0", "reason": "a phone claim is recorded as a claim, never as authority — 'the guy on the phone said he owns it' is the industry's defining scandal", "never_promote": True},
    "quote_off_rate_card": {"rung": "R0", "reason": "no number off the recorded card exists in this system — after-hours pricing lives on the card, not in a 2am judgment call", "never_promote": True},
    "edit_registry_record": {"rung": "R0", "reason": "a change is a new record, never an edit — the chart's history is every tenant's security", "never_promote": True},
    "draft_emergency_reply": {"rung": "R1", "reason": "outward in a life-safety moment — a human sends, with the 911 script leading"},
    "draft_dispatch":     {"rung": "R1", "reason": "a truck roll against a recorded authority — a human dispatches"},
    "draft_quote":        {"rung": "R1", "reason": "outward money copy — a human sends, computed from the card"},
    "draft_rekey_reply":  {"rung": "R1", "reason": "outward reply — the authorization status named honestly"},
    "draft_service_reminder": {"rung": "R1", "reason": "outward reminder — a human sends; the ladder is bounded"},
    "registry_append":    {"rung": "R2", "reason": "an append against a named authorizer is safe internal record-keeping; the codes never leave"},
    "record_verification": {"rung": "R2", "reason": "an internal record of an act a human performed (ID seen, deed shown)"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Key OS — what it computes to")
        .line("After-hours capture", "revenue", "after-hours calls answered × the recorded card",
              ["after_hours_calls_mo", "after_hours_avg_ticket"],
              lambda g: float(g["after_hours_calls_mo"]) * 12 * float(g["after_hours_avg_ticket"]),
              note="the ticket comes from the card's own multiplier, not a 2am judgment call")
        .line("Master-system contracts renewed", "revenue", "systems renewed × annual contract",
              ["systems_renewed", "contract_value"],
              lambda g: float(g["systems_renewed"]) * float(g["contract_value"]),
              note="renewals are counted; the registry's clean history is the pitch")
        .line("Dispatch hours", "time_saved", "hrs/wk × 52 × rate",
              ["dispatch_hours_wk", "dispatch_rate"],
              lambda g: float(g["dispatch_hours_wk"]) * 52 * float(g["dispatch_rate"]))
        .line("The lawsuit file", "scenario", "you decide what the wrong-door job that never ran is worth",
              ["lawsuit_value"], lambda g: float(g["lawsuit_value"]),
              assumption="never a saving — a prevented break-in-with-an-invoice cannot be counted"))


def roi(given):
    rec = {}
    ref = now()
    ah = [j for j in store.load("jobs")
          if j.get("after_hours") and not j.get("demo_tag")
          and j.get("closed_at") and (ref - (parse(j["closed_at"]) or ref)).days <= 90]
    rec["after_hours_jobs_90d"] = len(ah)
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("read_message", "record_emergency", "draft_emergency_reply", "draft_dispatch",
          "draft_quote", "draft_rekey_reply", "draft_service_reminder", "registry_append")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("caller:",))
