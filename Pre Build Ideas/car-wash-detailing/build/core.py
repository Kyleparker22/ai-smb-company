#!/usr/bin/env python3
"""Shine OS — domain core (car wash & detailing).

Rules live here: damage-claim-first triage (software never denies one), the
cancellation clock (Member OS pattern), the non-threatening dunning ladder,
weather reschedules, and the matrix.

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

TABLES = ("config", "members", "messages", "claims", "details", "payments",
          "cancellations", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="SHINEOS_DATA_ROOT")

CLAIM_PROTOCOL = ("Logged verbatim with a timestamp. The tunnel camera footage for your visit is "
                  "being pulled now, and a manager calls you within 24 hours with the footage in "
                  "front of them. Nothing is denied by this message — and nothing is argued.")

# ---------------------------------------------------------------- triage

DAMAGE = (
    r"\b(wash|brush|tunnel|dryer|machine)\b.*\b(broke|scratch|crack|snapp?ed|bent|damag|ripped|tore)\w*",
    r"\b(antenna|mirror|wiper|trim|emblem|spoiler)\b.*\b(broke|gone|missing|snapp?ed|bent|damag)\w*",
    r"\b(scratch|swirl)\w*\b.*\b(after|since|from)\b.*\b(wash|tunnel)\b",
)
CANCEL = (
    r"\bcancel\b.*\b(membership|plan|subscription|monthly)\b|\bcancel my\b",
    r"\bstop (charging|billing|the payments?)\b",
)
BILLING = (
    r"\b(charged twice|double charge|wrong (charge|amount)|refund|card (was )?declined|update (my )?card)\b",
)
DETAIL = (
    r"\b(book|schedule|reschedule|move)\b.*\b(detail|ceramic|interior|full)\b",
    r"\b(detail|ceramic coat)\w*\b.*\b(book|schedule|price|appointment|saturday|available)\b",
)


def read_message(text):
    """damage_claim | cancellation | billing | detail | human. Damage first."""
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty message — a person reads it"}
    for rx in DAMAGE:
        if re.search(rx, t):
            return {"label": "damage_claim", "protocol": CLAIM_PROTOCOL,
                    "why": "a damage claim — logged verbatim, footage pulled, a manager calls; "
                           "software never argues physics and never denies"}
    for rx in CANCEL:
        if re.search(rx, t):
            return {"label": "cancellation",
                    "why": "cancellation — the processing clock starts NOW; any save offer is a "
                           "separate row that never delays it"}
    for rx in BILLING:
        if re.search(rx, t):
            return {"label": "billing", "why": "billing question — draft at R1"}
    for rx in DETAIL:
        if re.search(rx, t):
            return {"label": "detail", "why": "detail booking — draft at R1"}
    return {"label": "human", "why": "no clean signal — a person reads it"}


# ---------------------------------------------------------------- cancellation clock

DEFAULT_CANCEL_RULES = {
    "_source": ("DEFAULT rule set, simplified — replace with counsel-reviewed per-state rules "
                "before go-live; auto-renew law is moving."),
    "_default": {"must_process_days": 3},
}


def cancel_rules():
    return store.load("config").get("cancel_rules") or DEFAULT_CANCEL_RULES


def cancellation_clock(requested_at):
    rule = cancel_rules()["_default"]
    req = parse(requested_at) or now()
    return {"requested_at": iso(req),
            "process_by": iso(req + timedelta(days=rule["must_process_days"])),
            "days": rule["must_process_days"],
            "rule_label": "the clock starts at the request, not after a save attempt"}


def can_charge(member, ref=None):
    """A membership with a recorded cancellation request cannot be charged
    after it — by construction."""
    ref = ref or now()
    cx = member.get("cancel_requested_at")
    if cx and parse(cx) and parse(cx) <= ref:
        return False, (f"cancellation requested {str(cx)[:10]} — a charge after the recorded "
                       f"request is the chargeback and the AG complaint; it cannot be expressed")
    return True, "active membership"


# ---------------------------------------------------------------- dunning

DUNNING_MAX_TOUCHES = 3
DUNNING_COOLDOWN_DAYS = 5
FORBIDDEN = ("collections", "legal action", "lawyer", "credit bureau", "final warning",
             "consequences")
DUNNING_COPY = {
    1: ("Hi {name} — the card on your wash membership didn't go through. Thirty seconds online "
        "fixes it, or the kiosk at any location. No fees stacked on."),
    2: ("Hi {name} — second note: the card still isn't going through, so the membership pauses "
        "at the gate until it's updated. Takes a minute online whenever you're ready."),
    3: ("Hi {name} — last note from us. If you'd rather cancel than update the card, reply "
        "CANCEL and we'll process it same-day, no questions. Otherwise the update link is below."),
}


def dunning_plan(member, ref=None):
    ref = ref or now()
    fails = [p for p in store.load("payments")
             if p.get("member_id") == member["id"] and p.get("failed") and not p.get("recovered_at")]
    if not fails:
        return {"action": "none", "why": "no unrecovered failed payment"}
    touches = member.get("dunning_touches") or []
    if len(touches) >= DUNNING_MAX_TOUCHES:
        return {"action": "human", "why": f"ladder exhausted at {DUNNING_MAX_TOUCHES} — a person decides"}
    if touches:
        last = parse(touches[-1]["at"])
        if last and (ref - last).days < DUNNING_COOLDOWN_DAYS:
            return {"action": "none", "why": f"inside the {DUNNING_COOLDOWN_DAYS}-day cooldown"}
    n = len(touches) + 1
    return {"action": "draft", "touch": n, "why": f"touch {n} of {DUNNING_MAX_TOUCHES}",
            "text": DUNNING_COPY[n].format(name=member.get("name", "there"))}


def dunning_text_ok(text):
    t = (text or "").lower()
    hits = [w for w in FORBIDDEN if w in t]
    if hits:
        return False, f"dunning never threatens — forbidden language: {', '.join(hits)}"
    return True, "ok"


def recovered_this_week(ref=None):
    """Counted: payments recovered, claims resolved by a human, details kept."""
    ref = ref or now()
    recovered = [p for p in store.load("payments")
                 if p.get("recovered_at") and (ref - (parse(p["recovered_at"]) or ref)).days <= 7]
    resolved = [c for c in store.load("claims")
                if c.get("resolved_at") and (ref - (parse(c["resolved_at"]) or ref)).days <= 7]
    kept = [d for d in store.load("details")
            if d.get("completed_at") and (ref - (parse(d["completed_at"]) or ref)).days <= 7]
    return {"payments_recovered": len(recovered),
            "recovered_value": round(sum(p.get("amount", 0) for p in recovered), 2),
            "claims_resolved": len(resolved), "details_kept": len(kept),
            "note": "counted from the ledgers — never asserted"}


# ---------------------------------------------------------------- eval

triage_eval = Eval("message triage",
                   costly_label="damage_claim",
                   costly_note=("A DAMAGE CLAIM ANSWERED DEFENSIVELY IS A ONE-STAR STORY WITH "
                                "YOUR TUNNEL IN IT. Over-routing a billing note costs a read."))

EVAL_CASES = [
    {"input": "your wash snapped my antenna clean off", "label": "damage_claim"},
    {"input": "there are swirl scratches all over the hood since the tunnel", "label": "damage_claim"},
    {"input": "the dryer ripped the trim off my back window", "label": "damage_claim"},
    {"input": "my mirror is bent back and cracked after going through", "label": "damage_claim"},
    {"input": "cancel my membership please, we moved across town", "label": "cancellation"},
    {"input": "stop charging my card, I sold the car", "label": "cancellation"},
    {"input": "I was charged twice this month", "label": "billing"},
    {"input": "card was declined but there's money in the account", "label": "billing"},
    {"input": "can I book a full detail for saturday", "label": "detail"},
    {"input": "need to reschedule my ceramic coating appointment", "label": "detail"},
    {"input": "", "label": "human"},
    {"input": "you guys did a great job on the truck", "label": "human"},
    {"input": "the machine bent my wiper arm", "label": "damage_claim"},
    {"input": "is the interior detail available sunday", "label": "detail"},
    {"input": "wrong amount on my receipt from tuesday", "label": "billing"},
]


def run_eval():
    return triage_eval.run(EVAL_CASES, lambda t: read_message(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_message":       {"rung": "R3", "reason": "routing only; damage-first is the point"},
    "log_damage_claim":   {"rung": "R2", "reason": "the verbatim log and the footage pull cannot wait"},
    "deny_damage_claim":  {"rung": "R0", "reason": "software never argues physics — a manager decides with the footage", "never_promote": True},
    "delay_cancellation": {"rung": "R0", "reason": "a cancellation is processed, not negotiated", "never_promote": True},
    "charge_after_cancel_request": {"rung": "R0", "reason": "a charge after the recorded request cannot be expressed", "never_promote": True},
    "threaten_in_dunning": {"rung": "R0", "reason": "dunning never threatens", "never_promote": True},
    "start_cancel_clock": {"rung": "R2", "reason": "recording the request starts the clock — delay is the harm"},
    "draft_save_offer":   {"rung": "R1", "reason": "a human may offer — processing never waits on it"},
    "draft_dunning":      {"rung": "R1", "reason": "outward money message — a human sends"},
    "draft_billing_reply": {"rung": "R1", "reason": "outward reply — a human sends"},
    "draft_detail_booking": {"rung": "R1", "reason": "outward booking — a human sends"},
    "pull_footage_task":  {"rung": "R2", "reason": "an internal task — the footage is the answer"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Shine OS — what it computes to")
        .line("Failed payments recovered", "revenue", "open failures × recovery rate × dues × 12",
              ["open_failures", "recovery_rate", "avg_dues"],
              lambda g: float(g["open_failures"]) * float(g["recovery_rate"]) * float(g["avg_dues"]) * 12,
              assumption="assumes a recovered member stays the year — argue with this one")
        .line("Details kept through weather", "revenue", "rescheduled-not-lost × avg detail",
              ["details_rescheduled", "avg_detail"],
              lambda g: float(g["details_rescheduled"]) * float(g["avg_detail"]))
        .line("Desk hours", "time_saved", "hrs/wk × 52 × rate",
              ["desk_hours_wk", "desk_rate"],
              lambda g: float(g["desk_hours_wk"]) * 52 * float(g["desk_rate"]))
        .line("The claims file", "scenario", "you decide what the footage-first record is worth",
              ["claims_value"], lambda g: float(g["claims_value"]),
              assumption="never a saving — the protocol is the product"))


def roi(given):
    rec = {}
    rec["open_failures"] = len([p for p in store.load("payments")
                                if p.get("failed") and not p.get("recovered_at")])
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("read_message", "log_damage_claim", "start_cancel_clock", "draft_dunning",
          "draft_billing_reply", "draft_detail_booking", "pull_footage_task")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("member:",))
