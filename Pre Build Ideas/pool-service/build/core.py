#!/usr/bin/env python3
"""Pool OS — domain core (pool service & maintenance).

Rules live here: injury-first message triage, the service-proof billing gate
(readings or no invoice), reading-vs-range reporting that never says "safe to
swim", the green-pool recovery plan, the equipment quote ladder, and the matrix.

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

TABLES = ("config", "customers", "pools", "stops", "messages", "quotes",
          "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="POOLOS_DATA_ROOT")

INJURY_PROTOCOL = ("Logged verbatim with a timestamp. A human calls back within minutes. "
                   "Software drafts no reply of any kind on an injury or drowning-adjacent "
                   "report — nothing is admitted, denied, or assessed.")

# ---------------------------------------------------------------- triage

INJURY = (
    r"\b(drown(ed|ing)?|almost drowned|went under|pulled (him|her|them) out)\b",
    r"\b(kid|child|toddler|son|daughter|guest|dog)\b.*\b(hospital|er\b|ambulance|911|urgent care)\b",
    r"\b(chemical )?burn(s|ed|ing)?\b.*\b(skin|legs?|arms?|eyes?|rash|swim|pool)\b|"
    r"\b(skin|eyes?)\b.*\b(burn(s|ing)?|red|sting(ing)?)\b.*\b(pool|swim|water)\b|"
    r"\b(eyes?|skin)\b.*\b(red|sting(ing)?|burn(s|ing)?)\b.*\bafter\b.*\bpool\b",
    r"\b(slipped|fell|hit (his|her|their) head)\b.*\b(deck|pool|ladder)\b",
    r"\b(suction|drain|entrap)\b.*\b(stuck|caught|held)\b",
)
CHEMICAL_QUESTION = (
    r"\b(how much|what amount|how many)\b.*\b(chlorine|shock|acid|algaecide|tabs?|stabilizer)\b",
    r"\bcan i (add|put|mix|dump)\b.*\b(chlorine|shock|acid|bleach|chemicals?)\b",
    r"\bwhat (should|do) i (add|put|use)\b",
)
GREEN_POOL = (
    r"\b(green|cloudy|murky|swampy?|algae)\b.*\b(pool|water)\b|\b(pool|water)\b.*\b(green|cloudy|murky|algae)\b",
    r"\bmosquito|tadpole|frog\b.*\bpool\b",
)
SCHEDULE = (
    r"\b(skip|reschedule|move)\b.*\b(service|stop|visit|this week)\b",
    r"\bwhat day\b.*\b(service|come|scheduled)\b|\bwhen (are you|is my)\b",
    r"\bgate (code|is|will be)\b|\bdog (is|will be) (out|inside)\b",
)


def read_message(text):
    """injury | chemical_question | green_pool | schedule | human. Injury reads
    first — always; the file starts at the first word."""
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty message — a person reads it"}
    for rx in INJURY:
        if re.search(rx, t):
            return {"label": "injury", "protocol": INJURY_PROTOCOL,
                    "why": "injury or drowning-adjacent report — a human now; software drafts "
                           "nothing, admits nothing, assesses nothing"}
    for rx in CHEMICAL_QUESTION:
        if re.search(rx, t):
            return {"label": "chemical_question",
                    "why": "chemical dosing question — the label is the law; a certified tech "
                           "answers, never software"}
    for rx in GREEN_POOL:
        if re.search(rx, t):
            return {"label": "green_pool",
                    "why": "water-quality complaint — a recovery-plan visit drafts with honest "
                           "multi-visit copy"}
    for rx in SCHEDULE:
        if re.search(rx, t):
            return {"label": "schedule", "why": "scheduling/access note — draft at R1"}
    return {"label": "human", "why": "no clean signal — a person reads it"}


# ---------------------------------------------------------------- service proof

REQUIRED_READINGS = ("fc", "ph", "ta")


def can_bill_stop(stop):
    """A stop bills only with its recorded reading set + arrival stamp.
    Unprovable service is a dispute."""
    readings = stop.get("readings") or {}
    missing = [k.upper() for k in REQUIRED_READINGS if readings.get(k) is None]
    if not stop.get("arrived_at"):
        missing.append("arrival stamp")
    if missing:
        return False, (f"cannot bill this stop — missing: {', '.join(missing)}. A stop without "
                       f"its readings is unprovable service, and unprovable service is a dispute.")
    return True, (f"FC {readings['fc']} · pH {readings['ph']} · TA {readings['ta']} recorded at "
                  f"{str(stop['arrived_at'])[:16]}")


def reading_report(pool, stop):
    """Readings vs the pool's OWN recorded target ranges. Flags out-of-range;
    NEVER a swim verdict — that word does not exist in this system."""
    ranges = pool.get("target_ranges") or {}
    readings = (stop or {}).get("readings") or {}
    rows = []
    for k in REQUIRED_READINGS:
        v = readings.get(k)
        rng = ranges.get(k)
        if v is None:
            rows.append({"param": k.upper(), **unmeasured("no reading recorded", field="value")})
            continue
        row = {"param": k.upper(), "value": v}
        if rng:
            row["range"] = rng
            row["in_range"] = rng[0] <= v <= rng[1]
        else:
            row["note"] = "no target range recorded for this pool — flagged, not judged"
        rows.append(row)
    return {"rows": rows,
            "note": "readings vs this pool's recorded ranges — a CPO judges water, software "
                    "reports numbers; 'safe to swim' never leaves this system"}


# ---------------------------------------------------------------- unbilled + quotes

def unbilled_proven_stops(ref=None):
    """Stops with complete proof that never billed — counted."""
    rows = []
    for s in store.load("stops"):
        if s.get("billed_at") or s.get("demo_tag"):
            continue
        okb, _ = can_bill_stop(s)
        if okb:
            rows.append(s)
    return {"count": len(rows),
            "value": round(sum(s.get("rate", 0) for s in rows), 2),
            "note": "counted from the stop records — proof complete, invoice missing"}


QUOTE_MAX_TOUCHES = 3
QUOTE_COOLDOWN_DAYS = 7


def quote_plan(q, ref=None):
    ref = ref or now()
    if q.get("won_at") or q.get("lost_at") or q.get("demo_tag"):
        return {"action": "none", "why": "closed"}
    touches = q.get("touches") or []
    if len(touches) >= QUOTE_MAX_TOUCHES:
        return {"action": "none", "why": f"ladder exhausted at {QUOTE_MAX_TOUCHES} — silence is an answer"}
    last = parse(touches[-1]["at"]) if touches else parse(q.get("sent_at"))
    if last and (ref - last).days < QUOTE_COOLDOWN_DAYS:
        return {"action": "none", "why": f"inside the {QUOTE_COOLDOWN_DAYS}-day cooldown"}
    return {"action": "draft_chase", "why": f"touch {len(touches)+1} of {QUOTE_MAX_TOUCHES}"}


def recovered_this_week(ref=None):
    """Counted, never asserted: stops billed, quotes won, recovery visits a
    human booked, inside 7 days."""
    ref = ref or now()
    billed = [s for s in store.load("stops")
              if s.get("billed_at") and (ref - (parse(s["billed_at"]) or ref)).days <= 7]
    won = [q for q in store.load("quotes")
           if q.get("won_at") and (ref - (parse(q["won_at"]) or ref)).days <= 7]
    recoveries = sum(1 for e in store.events(kind="draft_recovery_visit")
                     if str(e.get("actor", "")).startswith("human:")
                     and (ref - (parse(e.get("at")) or ref)).days <= 7)
    return {"stops_billed": len(billed),
            "billed_value": round(sum(s.get("rate", 0) for s in billed), 2),
            "quotes_won": len(won),
            "won_value": round(sum(q.get("amount", 0) for q in won), 2),
            "recovery_visits_booked": recoveries,
            "note": "counted from the records and the event log — never asserted"}


# ---------------------------------------------------------------- eval

triage_eval = Eval("message triage",
                   costly_label="injury",
                   costly_note=("AN INJURY REPORT ANSWERED BY SOFTWARE IS AN ADMISSION IN A "
                                "LAWSUIT ABOUT A POOL. Over-routing a green-pool gripe costs a "
                                "human thirty seconds."))

EVAL_CASES = [
    {"input": "my son got a chemical burn on his legs after swimming yesterday", "label": "injury"},
    {"input": "our guest slipped on the deck by the ladder and hit his head", "label": "injury"},
    {"input": "the neighbor kid almost drowned, we pulled him out ourselves", "label": "injury"},
    {"input": "my daughter's eyes are red and stinging after the pool", "label": "injury"},
    {"input": "the dog went under near the drain and got stuck for a second", "label": "injury"},
    {"input": "how much shock should I add after the party", "label": "chemical_question"},
    {"input": "can I dump bleach in until you get here", "label": "chemical_question"},
    {"input": "pool turned green over the weekend", "label": "green_pool"},
    {"input": "water's been cloudy since thursday", "label": "green_pool"},
    {"input": "skip this week's service, we're out of town", "label": "schedule"},
    {"input": "gate code is 7741 starting monday", "label": "schedule"},
    {"input": "", "label": "human"},
    {"input": "invoice received, thanks for the great work", "label": "human"},
    {"input": "there are tadpoles in the pool somehow", "label": "green_pool"},
    {"input": "what day do you come this week", "label": "schedule"},
    {"input": "what should I use for the yellow stuff on the steps", "label": "chemical_question"},
]


def run_eval():
    return triage_eval.run(EVAL_CASES, lambda t: read_message(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_message":        {"rung": "R3", "reason": "routing only; the injury-first read is the point"},
    "log_injury_report":   {"rung": "R2", "reason": "the verbatim log cannot wait for a click"},
    "respond_to_injury_report": {"rung": "R0", "reason": "software drafts nothing on an injury — nothing admitted, denied, or assessed", "never_promote": True},
    "declare_safe_to_swim": {"rung": "R0", "reason": "software reports readings vs ranges; a human judges water", "never_promote": True},
    "answer_chemical_dosing": {"rung": "R0", "reason": "the label is the law — a certified tech answers", "never_promote": True},
    "bill_unproven_stop":  {"rung": "R0", "reason": "the reading set is the proof of service", "never_promote": True},
    "draft_stop_invoice":  {"rung": "R1", "reason": "money — a human sends, past the proof gate"},
    "draft_recovery_visit": {"rung": "R1", "reason": "outward booking — a human sends; the copy promises visits, not a date the water clears"},
    "draft_quote_chase":   {"rung": "R1", "reason": "outward message — a human sends"},
    "draft_schedule_reply": {"rung": "R1", "reason": "outward reply — a human sends"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Pool OS — what it computes to")
        .line("Proven stops billed", "revenue", "unbilled proven stops × rate (counted)",
              ["unbilled_stops_value"], lambda g: float(g["unbilled_stops_value"]),
              note="counted from the stop records — proof complete, invoice missing")
        .line("Equipment quotes recovered", "revenue", "open quote value × your close rate",
              ["open_quote_value", "close_rate"],
              lambda g: float(g["open_quote_value"]) * float(g["close_rate"]),
              assumption="the close rate is yours — we do not invent one")
        .line("Route-office hours", "time_saved", "hrs/wk × 52 × rate",
              ["office_hours_wk", "office_rate"],
              lambda g: float(g["office_hours_wk"]) * 52 * float(g["office_rate"]))
        .line("The liability file", "scenario", "you decide what the recorded readings are worth",
              ["liability_value"], lambda g: float(g["liability_value"]),
              assumption="never a saving — a defensible file is not our number to model"))


def roi(given):
    rec = {}
    ub = unbilled_proven_stops()
    rec["unbilled_stops_value"] = ub["value"]
    open_q = [q for q in store.load("quotes")
              if not q.get("won_at") and not q.get("lost_at") and not q.get("demo_tag")]
    rec["open_quote_value"] = round(sum(q.get("amount", 0) for q in open_q), 2)
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("read_message", "log_injury_report", "draft_stop_invoice",
          "draft_recovery_visit", "draft_quote_chase", "draft_schedule_reply")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("customer:",))
