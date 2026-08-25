#!/usr/bin/env python3
"""Move OS — domain core (moving & storage).

Rules live here: the binding-estimate survey requirement, the charge clamp,
the claims evidence pair and its acknowledgment clock, message triage, and
the matrix.

The thesis: the industry's reputation problem is a pricing problem. A
reputable mover's weapon is PROVABLE discipline — the estimate that required
a survey, the invoice that cannot exceed it, the claim resolved on records.

Stdlib only. Honesty rules come from `_kit`.
"""
import re, sys
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent))

from _kit.moat import Eval, Gate, Matrix, Roi                       # noqa: E402
from _kit.store import (Store, automation_rate, days_until, iso,    # noqa: E402
                        median, now, parse, unmeasured)

TABLES = ("config", "moves", "conditions", "claims", "messages", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="MOVEOS_DATA_ROOT")


# ---------------------------------------------------------------- the quote rules

def can_issue_binding(move):
    """THE first refusal: a binding estimate needs a recorded survey with an
    inventory. A guess is not a binding number."""
    if move.get("survey_id") and move.get("inventory_items"):
        return True, f"survey {move['survey_id']} on file, {move['inventory_items']} items inventoried"
    missing = []
    if not move.get("survey_id"):
        missing.append("survey")
    if not move.get("inventory_items"):
        missing.append("inventory")
    return False, (f"a binding estimate cannot be issued without a recorded {' and '.join(missing)}"
                   f" — a guess is not a binding number; quote non-binding or book the survey")


# ---------------------------------------------------------------- the charge clamp

def final_charges(move):
    """Final charges = binding estimate + recorded SIGNED change orders — by
    construction. There is no argument that produces a higher number."""
    if move.get("estimate_type") == "binding":
        if not move.get("binding_amount"):
            return unmeasured("binding move with no recorded estimate amount — nothing can be charged",
                              field="total")
        cos = [c for c in (move.get("change_orders") or []) if c.get("signed_at")]
        unsigned = [c for c in (move.get("change_orders") or []) if not c.get("signed_at")]
        total = move["binding_amount"] + sum(c.get("amount", 0) for c in cos)
        out = {"total": round(total, 2), "estimate": move["binding_amount"],
               "signed_change_orders": [{"desc": c.get("desc"), "amount": c.get("amount")} for c in cos],
               "basis": "binding estimate + signed change orders — nothing else exists"}
        if unsigned:
            out["excluded"] = [{"desc": c.get("desc"), "amount": c.get("amount"),
                                "why": "no signature recorded — an unsigned change order is a "
                                       "conversation, not a charge"} for c in unsigned]
        return out
    # non-binding: hours × rate from records, labelled as such
    if move.get("actual_hours") and move.get("hourly_rate"):
        return {"total": round(move["actual_hours"] * move["hourly_rate"], 2),
                "basis": f"non-binding: {move['actual_hours']}h × ${move['hourly_rate']}/h from the job record"}
    return unmeasured("non-binding move with no recorded hours — nothing can be charged", field="total")


# ---------------------------------------------------------------- claims

DEFAULT_CLAIM_RULES = {
    "_source": ("DEFAULT rule set, simplified — replace with counsel-reviewed rules before "
                "go-live; interstate claims carry federal clocks. Every date is a DATE ALERT."),
    "acknowledge_days": 30, "resolve_days": 120,
}


def claim_rules():
    return store.load("config").get("claim_rules") or DEFAULT_CLAIM_RULES


def claim_check(claim):
    """A damage claim needs the load AND delivery condition records for the
    item. Missing either → cannot assess, the missing record named."""
    conds = [c for c in store.load("conditions")
             if c.get("move_id") == claim.get("move_id") and c.get("item") == claim.get("item")]
    load = next((c for c in conds if c.get("kind") == "load"), None)
    dlv = next((c for c in conds if c.get("kind") == "delivery"), None)
    missing = []
    if not load:
        missing.append("load condition record")
    if not dlv:
        missing.append("delivery condition record")
    if missing:
        return {"assessable": False,
                "refused": f"cannot assess this claim — missing: {', '.join(missing)}. It goes to "
                           f"a human with what exists; the system asserts nothing either way."}
    new_damage = [d for d in (dlv.get("damage") or []) if d not in (load.get("damage") or [])]
    return {"assessable": True, "new_damage": new_damage,
            "evidence": {"load": load["id"], "delivery": dlv["id"]},
            "note": ("damage new at delivery — settlement drafts at R1" if new_damage else
                     "no new damage between load and delivery — the records say so, a human decides")}


def claim_clock(claim, ref=None):
    ref = ref or now()
    rules = claim_rules()
    filed = parse(claim.get("filed_at"))
    if not filed:
        return unmeasured("no filed date on the claim", field="ack_due")
    ack_due = filed + timedelta(days=rules["acknowledge_days"])
    out = {"ack_due": iso(ack_due), "ack_days_left": (ack_due - ref).days,
           "acknowledged": bool(claim.get("acknowledged_at")),
           "label": "DATE ALERT — not legal advice", "rules_source": rules["_source"]}
    if claim.get("acknowledged_at"):
        out["ack_days_left"] = None
    return out


def claims_board(ref=None):
    rows = []
    for c in store.load("claims"):
        if c.get("resolved_at") or c.get("demo_tag"):
            continue
        clock = claim_clock(c, ref)
        rows.append({"claim": c["id"], "move": c.get("move_id"), "item": c.get("item"),
                     "filed_at": c.get("filed_at"), **clock})
    rows.sort(key=lambda r: (r.get("ack_days_left") is None, r.get("ack_days_left") or 0))
    return rows


# ---------------------------------------------------------------- triage

CLAIM_RX = (r"\b(broke(n)?|damaged?|cracked|scratched|dented|missing|smashed|chipped)\b.*"
            r"\b(dresser|table|tv|sofa|couch|box|piano|mirror|leg|item|furniture|washer|dryer|fridge|appliance)\b",
            r"\bclaim\b|\bfile a claim\b",
            r"\b(dresser|table|tv|sofa|couch|piano|mirror|washer|dryer|fridge|appliance)\b.*"
            r"\b(broke(n)?|damaged?|cracked|missing|scratched|dented|smashed|chipped)\b",
            r"\b(box(es)?|items?)\b.*\b(never (showed|arrived|made it)|didn'?t (arrive|show|make it)|lost)\b")
QUOTE_RX = (r"\b(quote|estimate|how much|price)\b.*\b(move|moving|bedroom|apartment|house)\b",
            r"\bmoving\b.*\b(in|next|this)\b.*\b(month|week|june|july|spring)\b")
DATE_RX = (r"\b(change|move|push|reschedule)\b.*\b(date|day|closing)\b",)


def read_message(text):
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty message — a person reads it"}
    for rx in CLAIM_RX:
        if re.search(rx, t):
            return {"label": "claim_report",
                    "why": "damage claim — the acknowledgment clock starts NOW; routed with its evidence check"}
    for rx in DATE_RX:
        if re.search(rx, t):
            return {"label": "date_change", "why": "date change — scheduling drafts at R1"}
    for rx in QUOTE_RX:
        if re.search(rx, t):
            return {"label": "quote_request", "why": "quote request — survey first, binding second"}
    return {"label": "human", "why": "no clean signal — a person reads it"}


def recovered_this_week(ref=None):
    """Counted, never asserted: claim acks and settlements a human sent,
    binding estimates a human issued, inside 7 days."""
    ref = ref or now()
    acks = settlements = bindings = 0
    for e in store.events():
        at = parse(e.get("at"))
        if not at or (ref - at).days > 7 or not str(e.get("actor", "")).startswith("human:"):
            continue
        if e["kind"] == "draft_claim_ack":
            acks += 1
        elif e["kind"] == "draft_claim_settlement":
            settlements += 1
        elif e["kind"] == "draft_binding_estimate":
            bindings += 1
    return {"acks_sent": acks, "settlements_sent": settlements, "bindings_issued": bindings,
            "note": "counted from the event log — never asserted"}


# ---------------------------------------------------------------- eval

triage_eval = Eval("message triage",
                   costly_label="claim_report",
                   costly_note=("A CLAIM THAT SITS UNACKNOWLEDGED BREEDS ONE-STAR REVIEWS AND, "
                                "INTERSTATE, REGULATORY EXPOSURE. Routing a quote ask costs nothing."))

EVAL_CASES = [
    {"input": "the dresser arrived with a cracked leg", "label": "claim_report"},
    {"input": "our TV is damaged and a box is missing", "label": "claim_report"},
    {"input": "I need to file a claim for the mirror", "label": "claim_report"},
    {"input": "the piano got scratched on the stairs", "label": "claim_report"},
    {"input": "how much to move a 3 bedroom house across town", "label": "quote_request"},
    {"input": "can we push the date, closing slipped a week", "label": "date_change"},
    {"input": "what time does the crew arrive tomorrow", "label": "human"},
    {"input": "", "label": "human"},
    {"input": "two boxes never showed up at the new house", "label": "claim_report"},
    {"input": "the washer got dented somewhere between the truck and the basement", "label": "claim_report"},
    {"input": "price for moving a 2 bedroom apartment to austin", "label": "quote_request"},
    {"input": "we need to push the move date, closing slipped again", "label": "date_change"},
    {"input": "can you confirm the crew size for saturday", "label": "human"},
]


def run_eval():
    return triage_eval.run(EVAL_CASES, lambda t: read_message(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_message":       {"rung": "R3", "reason": "routing only; the claim clock is the point"},
    "start_claim_clock":  {"rung": "R2", "reason": "recording the claim starts the clock — delay is the harm"},
    "issue_binding_without_survey": {"rung": "R0", "reason": "a guess is not a binding number", "never_promote": True},
    "charge_above_estimate": {"rung": "R0", "reason": "final charges are the estimate plus signed change orders — nothing else exists", "never_promote": True},
    "condition_delivery_on_extra_payment": {"rung": "R0", "reason": "the hostage load is the industry's shame; this system cannot express it", "never_promote": True},
    "draft_binding_estimate": {"rung": "R1", "reason": "money + promise — a human issues, and only with a survey on file"},
    "draft_claim_settlement": {"rung": "R1", "reason": "money — a human settles, with the evidence attached"},
    "draft_scheduling_reply": {"rung": "R1", "reason": "outward reply — a human sends"},
    "draft_claim_ack":    {"rung": "R1", "reason": "outward acknowledgment — a human sends; no fault taken, no claim denied"},
    "draft_survey_offer": {"rung": "R1", "reason": "outward reply — a human sends; survey first, binding second"},
    "claim_deadline_alert": {"rung": "R2", "reason": "an internal alarm on the claim clock — the date is the point"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Move OS — what it computes to")
        .line("Survey-backed binding margin", "revenue", "binding moves × avg margin lift",
              ["binding_moves_yr", "margin_lift"],
              lambda g: float(g["binding_moves_yr"]) * float(g["margin_lift"]),
              note="binding moves are counted; the lift vs phone-guess quotes is your number")
        .line("Claims-desk time", "time_saved", "claims/yr × hrs × rate",
              ["claims_yr", "hours_per_claim", "office_rate"],
              lambda g: float(g["claims_yr"]) * float(g["hours_per_claim"]) * float(g["office_rate"]))
        .line("Moving-day disputes avoided", "scenario", "disputes/yr × avg concession",
              ["disputes_yr", "avg_concession"],
              lambda g: float(g["disputes_yr"]) * float(g["avg_concession"]),
              assumption="an exposure you weigh — avoided fights cannot be counted")
        .line("The clamp, as reputation", "scenario", "you decide what never-overcharging is worth",
              ["clamp_value"], lambda g: float(g["clamp_value"]),
              assumption="never a saving — yours or blank"))


def roi(given):
    rec = {}
    moves = store.load("moves")
    rec["binding_moves_yr"] = len([m for m in moves if m.get("estimate_type") == "binding"])
    rec["claims_yr"] = len(store.load("claims"))
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("read_message", "start_claim_clock", "draft_binding_estimate",
          "draft_claim_settlement", "draft_scheduling_reply")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("customer:",))
