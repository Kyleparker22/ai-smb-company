#!/usr/bin/env python3
"""Garment OS — domain core (dry cleaning & laundry).

Rules live here: claim-first triage (never denied by software, settled from the
recorded fair-claims schedule), the stain-promise rule (outcome promises can't
be produced), the ready-rack ladder, the unclaimed-disposal clock, wholesale
route counts, and the matrix.

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

TABLES = ("config", "customers", "orders", "claims", "messages", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="GARMENTOS_DATA_ROOT")

# ---------------------------------------------------------------- the claims schedule

DEFAULT_CLAIMS_SCHEDULE = {
    "_source": ("DEFAULT fair-claims schedule, simplified from industry practice — replace with "
                "the schedule the company actually adopts before go-live."),
    "life_years": {"suit": 4, "dress": 4, "gown": 6, "coat": 5, "shirt": 2, "other": 3},
    "depreciation": [1.0, 0.7, 0.5, 0.35, 0.2],  # by age year, floor at last
}


def claims_schedule():
    return store.load("config").get("claims_schedule") or DEFAULT_CLAIMS_SCHEDULE


def claim_math(claim):
    """The settlement DRAFTS from the recorded schedule: replacement value ×
    the depreciation for the garment's age. Ad-hoc numbers can't be produced;
    missing inputs are named."""
    sched = claims_schedule()
    missing = [f for f in ("garment_class", "age_years", "replacement_value")
               if claim.get(f) in (None, "")]
    if missing:
        return {"refused": (f"cannot draft a settlement — missing: {', '.join(missing)}. The "
                            f"schedule needs its inputs; an ad-hoc number is how a claim becomes "
                            f"a one-star story.")}
    dep = sched["depreciation"]
    factor = dep[min(int(claim["age_years"]), len(dep) - 1)]
    amount = round(claim["replacement_value"] * factor, 2)
    return {"amount": amount, "factor": factor,
            "basis": (f"${claim['replacement_value']:,.0f} replacement × {factor} "
                      f"({claim['age_years']}yr {claim['garment_class']}) — the recorded "
                      f"schedule's arithmetic"),
            "schedule_source": sched["_source"],
            "note": "a DRAFT for a human decision — software never denies and never freelances"}


def claim_evidence(claim):
    """A claim conversation needs the intake condition record (tag notes)."""
    if claim.get("intake_tag_notes"):
        return {"has_intake": True, "notes": claim["intake_tag_notes"]}
    return {"has_intake": False,
            "note": "no intake condition notes on the tag — the conversation happens without "
                    "them, honestly; the settlement math still drafts"}


# ---------------------------------------------------------------- the promise rule

FORBIDDEN_PROMISES = ("will come out", "guaranteed", "good as new", "no problem getting",
                      "definitely remove", "completely remove")


def promise_ok(text):
    t = (text or "").lower()
    hits = [w for w in FORBIDDEN_PROMISES if w in t]
    if hits:
        return False, f"no stain-outcome promises — forbidden language: {', '.join(hits)}"
    return True, "ok"


# ---------------------------------------------------------------- triage

CLAIM_MSG = (
    r"\b(ruined|damaged|shrunk|shrank|torn|tore|hole|melted|discolou?red|bleached|lost)\b.*"
    r"\b(dress|suit|gown|shirt|jacket|coat|garment|blouse)\b",
    r"\b(dress|suit|gown|shirt|jacket|coat|blouse)\b.*\b(ruined|damaged|shrunk|shrank|missing|"
    r"lost|torn|hole|discolou?red|bleached|melted)\b",
    r"\bwedding (dress|gown)\b.*\b(stain|mark|damage|ruin)\w*",
)
STAIN_ASK = (
    r"\b(can you (get|remove)|will (it|the stain)|able to (get|remove))\b.*\b(out|stain|remove)\b",
    r"\b(red wine|ink|oil|grease|blood|coffee)\b.*\b(stain|out|shirt|dress|remove)\b",
)
PICKUP = (
    r"\b(ready|pick ?up|done|finished)\b.*\b(order|cleaning|clothes|shirts?|dress)\b",
    r"\b(order|cleaning|clothes|shirts?|dress)\b.*\b(ready|done|finished)\b",
    r"\b(is|are) my\b.*\b(ready|done)\b",
)
WHOLESALE = (
    r"\b(hotel|restaurant|linen|route|napkins|tablecloths|uniforms)\b.*\b(count|delivery|pickup|"
    r"invoice|order|service)\b",
)


def read_message(text):
    """claim | stain_ask | pickup | wholesale | human. The claim reads first —
    the wedding dress is the reputation event."""
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty message — a person reads it"}
    for rx in CLAIM_MSG:
        if re.search(rx, t):
            return {"label": "claim",
                    "why": "a damage/loss claim — never denied by software; the settlement "
                           "drafts from the recorded schedule and a human decides"}
    for rx in STAIN_ASK:
        if re.search(rx, t):
            return {"label": "stain_ask",
                    "why": "a stain question — 'we'll try' is expressible; a promised outcome "
                           "is not"}
    for rx in PICKUP:
        if re.search(rx, t):
            return {"label": "pickup", "why": "pickup/ready — answered from the rack record"}
    for rx in WHOLESALE:
        if re.search(rx, t):
            return {"label": "wholesale", "why": "wholesale route — counts recorded vs billed"}
    return {"label": "human", "why": "no clean signal — a person reads it"}


# ---------------------------------------------------------------- ready rack + disposal

RACK_MAX_TOUCHES = 3
RACK_COOLDOWN_DAYS = 10

DEFAULT_DISPOSAL_RULES = {
    "_source": ("DEFAULT unclaimed-property clock, simplified — replace with the state's actual "
                "rule before go-live. Every date is a DATE ALERT, not legal advice."),
    "days_before_disposal": 90,
}


def disposal_rules():
    return store.load("config").get("disposal_rules") or DEFAULT_DISPOSAL_RULES


def rack_board(ref=None):
    ref = ref or now()
    rules = disposal_rules()
    rows = []
    for o in store.load("orders"):
        if not o.get("ready_at") or o.get("picked_up_at") or o.get("demo_tag"):
            continue
        ready = parse(o["ready_at"])
        days = (ref - ready).days if ready else None
        row = {"order": o["id"], "customer": o.get("customer_name"),
               "value": o.get("amount", 0), "days_on_rack": days,
               "touches": len(o.get("rack_touches") or [])}
        if days is not None:
            left = rules["days_before_disposal"] - days
            row["disposal_clock_days"] = left
            row["label"] = "DATE ALERT — disposal is a human act after the clock, never before"
        rows.append(row)
    rows.sort(key=lambda r: -(r.get("days_on_rack") or 0))
    return {"rows": rows, "value": round(sum(r["value"] for r in rows), 2),
            "rules_source": rules["_source"]}


def rack_plan(order, ref=None):
    ref = ref or now()
    touches = order.get("rack_touches") or []
    if len(touches) >= RACK_MAX_TOUCHES:
        return {"action": "none", "why": f"ladder exhausted at {RACK_MAX_TOUCHES} — the disposal "
                                         f"clock runs; disposal itself stays a human act"}
    last = parse(touches[-1]["at"]) if touches else parse(order.get("ready_at"))
    if last and (ref - last).days < RACK_COOLDOWN_DAYS:
        return {"action": "none", "why": f"inside the {RACK_COOLDOWN_DAYS}-day cooldown"}
    return {"action": "draft_reminder", "why": f"touch {len(touches)+1} of {RACK_MAX_TOUCHES}"}


def can_dispose(order, ref=None):
    ref = ref or now()
    rules = disposal_rules()
    ready = parse(order.get("ready_at"))
    if not ready:
        return False, "no ready date recorded — the clock never started"
    days = (ref - ready).days
    if days < rules["days_before_disposal"]:
        return False, (f"the state clock runs {rules['days_before_disposal']} days; this order "
                       f"is at {days}. Disposal before the clock is conversion, not cleanup.")
    return True, (f"clock complete ({days}d ≥ {rules['days_before_disposal']}d) — disposal is "
                  f"now a human decision, and only now")


def recovered_this_week(ref=None):
    """Counted: rack cash released, claims settled on schedule, reminders sent."""
    ref = ref or now()
    picked = [o for o in store.load("orders")
              if o.get("picked_up_at") and (ref - (parse(o["picked_up_at"]) or ref)).days <= 7]
    settled = [c for c in store.load("claims")
               if c.get("settled_at") and (ref - (parse(c["settled_at"]) or ref)).days <= 7]
    reminders = sum(1 for e in store.events(kind="draft_rack_reminder")
                    if str(e.get("actor", "")).startswith("human:")
                    and (ref - (parse(e.get("at")) or ref)).days <= 7)
    return {"orders_picked_up": len(picked),
            "rack_cash_released": round(sum(o.get("amount", 0) for o in picked), 2),
            "claims_settled": len(settled), "reminders_sent": reminders,
            "note": "counted from the rack and claim records — never asserted"}


# ---------------------------------------------------------------- eval

triage_eval = Eval("message triage",
                   costly_label="claim",
                   costly_note=("THE WEDDING DRESS CLAIM HANDLED AD-HOC IS THE ONE-STAR STORY "
                                "THAT OUTLIVES THE SHOP. Over-routing a pickup ask costs a read."))

EVAL_CASES = [
    {"input": "my wedding dress came back with a mark on the train", "label": "claim"},
    {"input": "you shrunk my husband's suit two sizes", "label": "claim"},
    {"input": "there's a hole in the silk blouse that wasn't there", "label": "claim"},
    {"input": "my coat is missing from the order", "label": "claim"},
    {"input": "can you get red wine out of a linen shirt", "label": "stain_ask"},
    {"input": "will the ink stain come out of this dress", "label": "stain_ask"},
    {"input": "is my order ready for pickup", "label": "pickup"},
    {"input": "are my shirts done for friday", "label": "pickup"},
    {"input": "the hotel needs the napkin count corrected on the invoice", "label": "wholesale"},
    {"input": "restaurant linen delivery moved to tuesday", "label": "wholesale"},
    {"input": "", "label": "human"},
    {"input": "what time do you close saturday", "label": "human"},
    {"input": "the gown came back discolored at the hem", "label": "claim"},
    {"input": "grease stain on my favorite jacket, any hope", "label": "stain_ask"},
]


def run_eval():
    return triage_eval.run(EVAL_CASES, lambda t: read_message(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_message":       {"rung": "R3", "reason": "routing only; the claim reads first"},
    "log_claim":          {"rung": "R2", "reason": "the claim record and the schedule math cannot wait"},
    "deny_claim":         {"rung": "R0", "reason": "software assembles the record and the math — a human decides", "never_promote": True},
    "settle_off_schedule": {"rung": "R0", "reason": "the recorded schedule's arithmetic or a human — never an ad-hoc number", "never_promote": True},
    "promise_stain_outcome": {"rung": "R0", "reason": "'we'll try' is expressible; a promised outcome is not", "never_promote": True},
    "dispose_before_clock": {"rung": "R0", "reason": "disposal before the state clock is conversion, not cleanup", "never_promote": True},
    "draft_settlement":   {"rung": "R1", "reason": "money — a human decides, with the schedule math attached"},
    "draft_rack_reminder": {"rung": "R1", "reason": "outward reminder — a human sends"},
    "draft_stain_reply":  {"rung": "R1", "reason": "outward reply — honest copy, promise-checked structurally"},
    "draft_wholesale_reply": {"rung": "R1", "reason": "outward reply — the counts cited"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Garment OS — what it computes to")
        .line("Ready-rack cash released", "cash_timing", "rack value × your pickup lift",
              ["rack_value", "pickup_lift"],
              lambda g: float(g["rack_value"]) * float(g["pickup_lift"]),
              note="the rack value is counted; the lift from reminders is your call")
        .line("Counter hours", "time_saved", "hrs/wk × 52 × rate",
              ["counter_hours_wk", "counter_rate"],
              lambda g: float(g["counter_hours_wk"]) * 52 * float(g["counter_rate"]))
        .line("The claims file", "scenario", "you decide what schedule-settled claims are worth",
              ["claims_value"], lambda g: float(g["claims_value"]),
              assumption="never a saving — the one-star story that didn't run is not our number"))


def roi(given):
    rec = {}
    rec["rack_value"] = rack_board()["value"]
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("read_message", "log_claim", "draft_settlement", "draft_rack_reminder",
          "draft_stain_reply", "draft_wholesale_reply")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("customer:",))
