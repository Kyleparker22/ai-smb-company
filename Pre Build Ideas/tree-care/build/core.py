#!/usr/bin/env python3
"""Canopy OS — domain core (tree care).

Rules live here: emergency-first storm triage, the power-line scheduling gate,
the hazard-assessment refusal (neither 'safe' nor 'hazardous' leaves software),
the estimate follow-up ladder, PHC renewals, and the matrix.

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

TABLES = ("config", "customers", "jobs", "estimates", "messages", "phc",
          "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="CANOPYOS_DATA_ROOT")

EMERGENCY_ACK = ("A crew coordinator is being reached right now and will call you back within "
                 "minutes. If anyone is trapped or lines are down, call 911 first — we work "
                 "after the scene is safe.")

# ---------------------------------------------------------------- triage

EMERGENCY = (
    r"\b(tree|limb|branch|trunk)\b.*\b(on|through|into|crushed)\b.*\b(house|roof|car|truck|garage|"
    r"fence|shed|line|wire)\b",
    r"\b(fell|came down|split|snapped|cracked)\b.*\b(storm|wind|last night|overnight|just)\b",
    r"\bhang(ing|er)?\b.*\b(over|above)\b.*\b(house|driveway|sidewalk|play|kids)\b|\bwidow ?maker\b",
    r"\b(blocking|across)\b.*\b(driveway|road|street|entrance)\b",
    r"\bsomeone|guy|worker\b.*\b(hurt|trapped|under)\b.*\b(tree|limb)\b",
)
HAZARD_ASK = (
    r"\bis (my|the|this|that)( big| old| tall| dead)? (tree|oak|maple|pine|elm|branch|limb)\b.*"
    r"\b(safe|dying|dead|dangerous|ok|going to fall)\b",
    r"\b(will|could|might) (it|the( \w+)? (tree|oak|maple|pine|elm|branch|limb))\b.*\b(fall|come down)\b",
    r"\b(leaning|lean)\b.*\b(worse|more|toward|house)\b",
    r"\bshould (i|we) (worry|be worried|take it down)\b",
)
QUOTE = (
    r"\b(quote|estimate|price|cost|bid|how much)\b.*\b(remov\w*|trim\w*|prun\w*|stump\w*|grind\w*|takedown|take down)\b",
    r"\b(remov|trim|prun|stump|grind)\w*\b.*\b(quote|estimate|price|cost|how much)\b",
    r"\bneed\b.*\b(tree|trees|stump)\b.*\b(removed|trimmed|pruned|ground|gone)\b",
)
SCHEDULE = (
    r"\b(what day|when (are you|is the crew)|reschedule|confirm)\b",
    r"\bgate|driveway (will be|is) (open|clear)\b",
)


def read_message(text):
    """emergency | hazard_ask | quote | schedule | human. Emergency first."""
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty message — a person reads it"}
    for rx in EMERGENCY:
        if re.search(rx, t):
            return {"label": "emergency", "ack": EMERGENCY_ACK,
                    "why": "storm/emergency signal — a human coordinator now; the ack promises a "
                           "callback and says 911 first if anyone is trapped"}
    for rx in HAZARD_ASK:
        if re.search(rx, t):
            return {"label": "hazard_ask",
                    "why": "a hazard-assessment question — neither 'safe' nor 'hazardous' leaves "
                           "software; the certified arborist assesses, we book the visit"}
    for rx in QUOTE:
        if re.search(rx, t):
            return {"label": "quote", "why": "quote request — estimate drafts after a site look"}
    for rx in SCHEDULE:
        if re.search(rx, t):
            return {"label": "schedule", "why": "scheduling — draft at R1"}
    return {"label": "human", "why": "no clean signal — a person reads it"}


# ---------------------------------------------------------------- the power-line gate

def can_schedule(job):
    """A job flagged near power lines cannot be scheduled without a recorded
    utility clearance reference. The crew doesn't roll on hope."""
    if not job.get("near_powerlines"):
        return True, "no power-line flag — schedules on the calendar"
    if job.get("utility_clearance_ref"):
        return True, f"power-line job with utility clearance {job['utility_clearance_ref']} on file"
    return False, ("this job is flagged near power lines and has no utility clearance on file — "
                   "the crew does not roll until the utility's clearance reference is recorded; "
                   "energized lines are the fatality mechanism of this trade")


# ---------------------------------------------------------------- estimates

ESTIMATE_MAX_TOUCHES = 3
ESTIMATE_COOLDOWN_DAYS = 6


def estimate_plan(e, ref=None):
    ref = ref or now()
    if e.get("won_at") or e.get("lost_at") or e.get("demo_tag"):
        return {"action": "none", "why": "closed"}
    touches = e.get("touches") or []
    if len(touches) >= ESTIMATE_MAX_TOUCHES:
        return {"action": "none", "why": f"ladder exhausted at {ESTIMATE_MAX_TOUCHES} — silence is an answer"}
    last = parse(touches[-1]["at"]) if touches else parse(e.get("sent_at"))
    if last and (ref - last).days < ESTIMATE_COOLDOWN_DAYS:
        return {"action": "none", "why": f"inside the {ESTIMATE_COOLDOWN_DAYS}-day cooldown"}
    return {"action": "draft_chase", "why": f"touch {len(touches)+1} of {ESTIMATE_MAX_TOUCHES}"}


def open_estimate_value():
    rows = [e for e in store.load("estimates")
            if not e.get("won_at") and not e.get("lost_at") and not e.get("demo_tag")]
    return {"count": len(rows), "value": round(sum(e.get("amount", 0) for e in rows), 2),
            "note": "counted from the estimate ledger"}


# ---------------------------------------------------------------- PHC renewals

def phc_due(ref=None):
    ref = ref or now()
    rows = []
    for p in store.load("phc"):
        if p.get("cancelled_at") or p.get("demo_tag"):
            continue
        due = parse(p.get("next_due"))
        if due and due <= ref + timedelta(days=30):
            rows.append({"phc": p["id"], "customer": p.get("customer_name"),
                         "program": p.get("program"), "next_due": p.get("next_due"),
                         "days": (due - ref).days,
                         "renewed": bool(p.get("renewed_at"))})
    return sorted(rows, key=lambda r: r["days"])


def recovered_this_week(ref=None):
    """Counted, never asserted: estimates won, PHC renewals recorded, and
    emergency callbacks a human made, inside 7 days."""
    ref = ref or now()
    won = [e for e in store.load("estimates")
           if e.get("won_at") and (ref - (parse(e["won_at"]) or ref)).days <= 7]
    renewed = [p for p in store.load("phc")
               if p.get("renewed_at") and (ref - (parse(p["renewed_at"]) or ref)).days <= 7]
    callbacks = sum(1 for e in store.events(kind="emergency_callback")
                    if str(e.get("actor", "")).startswith("human:")
                    and (ref - (parse(e.get("at")) or ref)).days <= 7)
    return {"estimates_won": len(won),
            "won_value": round(sum(e.get("amount", 0) for e in won), 2),
            "phc_renewed": len(renewed), "emergency_callbacks": callbacks,
            "note": "counted from the ledgers and the event log — never asserted"}


# ---------------------------------------------------------------- eval

triage_eval = Eval("message triage",
                   costly_label="emergency",
                   costly_note=("A STORM EMERGENCY READ AS A QUOTE REQUEST WAITS IN A QUEUE WHILE "
                                "A TREE SITS ON A HOUSE. Over-routing a pruning ask costs a call."))

EVAL_CASES = [
    {"input": "a tree came down on the garage last night", "label": "emergency"},
    {"input": "huge limb through the roof of my car", "label": "emergency"},
    {"input": "half the oak split in the storm and the rest is hanging over the driveway", "label": "emergency"},
    {"input": "there's a widow maker hanging over where the kids play", "label": "emergency"},
    {"input": "tree across the road at the end of our street", "label": "emergency"},
    {"input": "is my oak safe? it's leaning more than last year", "label": "hazard_ask"},
    {"input": "will the big pine come down in a storm", "label": "hazard_ask"},
    {"input": "should we worry about the dead maple by the fence", "label": "hazard_ask"},
    {"input": "how much to remove two trees in the backyard", "label": "quote"},
    {"input": "need a price on stump grinding for three stumps", "label": "quote"},
    {"input": "what day is the crew coming this week", "label": "schedule"},
    {"input": "", "label": "human"},
    {"input": "thanks, yard looks great", "label": "human"},
    {"input": "quote to trim the maples along the fence line", "label": "quote"},
    {"input": "the elm snapped halfway up in the wind just now", "label": "emergency"},
    {"input": "is that big branch over the house dangerous", "label": "hazard_ask"},
]


def run_eval():
    return triage_eval.run(EVAL_CASES, lambda t: read_message(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_message":       {"rung": "R3", "reason": "routing only; emergency-first is the point"},
    "route_emergency":    {"rung": "R2", "reason": "act now, tell the human — the ack cannot wait"},
    "assert_tree_safety": {"rung": "R0", "reason": "neither 'safe' nor 'hazardous' leaves software — the certified arborist assesses", "never_promote": True},
    "schedule_powerline_unclear": {"rung": "R0", "reason": "no utility clearance, no crew — energized lines are the fatality mechanism", "never_promote": True},
    "promise_no_damage":  {"rung": "R0", "reason": "felling promises are made by the foreman on site, if at all", "never_promote": True},
    "draft_assessment_visit": {"rung": "R1", "reason": "outward booking — a human sends; the visit is the answer"},
    "draft_estimate_chase": {"rung": "R1", "reason": "outward message — a human sends"},
    "draft_phc_renewal":  {"rung": "R1", "reason": "outward renewal — a human sends"},
    "draft_schedule_reply": {"rung": "R1", "reason": "outward reply — a human sends"},
    "schedule_job":       {"rung": "R1", "reason": "a crew day is a promise — a human books, past the power-line gate"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Canopy OS — what it computes to")
        .line("Estimates recovered by the ladder", "revenue", "open estimate value × your close rate",
              ["open_estimate_value", "close_rate"],
              lambda g: float(g["open_estimate_value"]) * float(g["close_rate"]),
              assumption="the close rate is yours — we do not invent one")
        .line("PHC renewals recalled", "revenue", "due programs × avg program (counted × yours)",
              ["phc_due_count", "avg_program"],
              lambda g: float(g["phc_due_count"]) * float(g["avg_program"]))
        .line("Office hours", "time_saved", "hrs/wk × 52 × rate",
              ["office_hours_wk", "office_rate"],
              lambda g: float(g["office_hours_wk"]) * 52 * float(g["office_rate"]))
        .line("Storm-call answer speed", "scenario", "you decide what the first hour is worth",
              ["storm_value"], lambda g: float(g["storm_value"]),
              assumption="never a saving — the first hour is not our number to model"))


def roi(given):
    rec = {}
    oe = open_estimate_value()
    rec["open_estimate_value"] = oe["value"]
    rec["phc_due_count"] = len(phc_due())
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("read_message", "route_emergency", "draft_assessment_visit",
          "draft_estimate_chase", "draft_phc_renewal", "draft_schedule_reply", "schedule_job")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("customer:",))
