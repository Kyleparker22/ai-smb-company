#!/usr/bin/env python3
"""Consult OS — domain core (med spas · aesthetics · elective clinics).

Everything that is a *rule* lives here: the service menu and its price bands,
the qualification taxonomy, the **clinical stop**, the show-up and decision
ladders, treatment reorder intervals, the decision state machine, the ROI model
and the autonomy matrix.

The product thesis: a med spa buys attention expensively and loses it in the
corridor between the inquiry and the treatment room — the 9pm DM answered at
11am, the consult that no-shows, the consult that never decides, and the
patient whose neurotoxin quietly drifts from 3.5 months to 7.

The clinical stop is the load-bearing part. It is a RULE, not a prompt string:
no dosing, no unit counts, no candidacy opinions, no contraindication rulings,
no outcome promises. Anything clinical routes to a licensed injector,
unanswered, and the bias is toward over-routing. In the demo, watching it
refuse IS the product.

Stdlib only.
"""
import re, sys
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent))

from _kit.moat import Eval, Gate, Matrix, Roi                      # noqa: E402
from _kit.store import (Store, automation_rate, days_until, iso,   # noqa: E402
                        median, now, parse, unmeasured)

TABLES = ("config", "patients", "providers", "inquiries", "consults", "plans",
          "treatments", "approvals", "messages", "events")
store = Store(ROOT / "data", TABLES, env_var="CONSULTOS_DATA_ROOT")


# ---------------------------------------------------------------- the menu
#
# Price BANDS, never a price. The agent may state a band and the consult fee;
# a firm number is a clinical-and-commercial commitment an injector makes.

SERVICES = {
    "neurotoxin":   dict(label="Neurotoxin", band=(280, 620), interval_days=105,
                         cadence="the effect fades — this is a clock, not a preference"),
    "filler_lip":   dict(label="Lip filler", band=(650, 950), interval_days=300, cadence="product-dependent"),
    "filler_cheek": dict(label="Cheek / midface filler", band=(900, 1800), interval_days=365, cadence="product-dependent"),
    "laser_resurf": dict(label="Laser resurfacing", band=(900, 2400), interval_days=None, cadence="series, then annual"),
    "laser_hair":   dict(label="Laser hair removal (series)", band=(1200, 2600), interval_days=28,
                         cadence="series interval — a missed session restarts the clock", sessions=6),
    "microneedle":  dict(label="Microneedling (series)", band=(900, 1600), interval_days=30, cadence="series", sessions=3),
    "body_contour": dict(label="Body contouring", band=(2400, 4800), interval_days=None, cadence="package"),
    "membership":   dict(label="Facial membership", band=(129, 189), interval_days=30, cadence="monthly visit"),
    "skincare":     dict(label="Medical skincare", band=(90, 420), interval_days=90, cadence="replenishment"),
}

CONSULT_FEE = 75          # credited toward treatment; the only firm number an agent may state
DEPOSIT = 50              # holds the chair
CHANNELS = ("instagram_dm", "tiktok_dm", "web_form", "text", "phone", "referral")


# ---------------------------------------------------------------- the clinical stop
#
# Three tiers, deliberately over-triggering:
#   urgent_clinical  — a complication that needs a licensed human NOW
#   clinical         — anything medical: routed, never answered
#   commercial       — logistics, price bands, hours, parking: the agent may answer

URGENT_PATTERNS = [
    r"vision|blurr|see(ing)? double|can'?t see", r"blanch|white(ning)?|mottl|dusky|purple",
    r"severe pain|excruciating", r"difficulty breathing|can'?t breathe|throat",
    r"swelling.*(spread|rapid|worse)|hives|anaphyla", r"fever", r"pus|abscess|infect",
    r"droop(ing|y)?|ptosis|eyelid", r"necro|tissue",
]
CLINICAL_PATTERNS = [
    r"\bunits?\b", r"\bdos(e|ing|age)\b", r"how (much|many).*(get|need|use)",
    r"\bcandidate\b|am i (a )?good|would (it|this) work (on|for) me",
    r"\bsafe\b|\brisk(s|y)?\b|side ?effects?", r"pregnan|breast ?feed|nursing|ttc|trying to conceive",
    r"\bmedication|\bmeds\b|blood thinner|warfarin|eliquis|accutane|isotretinoin",
    r"autoimmune|lupus|ms\b|myasthenia|thyroid|diabet", r"allerg", r"botox vs|which (filler|toxin)",
    r"\bbruis|\bswell|\blump|\bnodule|\bhard spot", r"should i stop taking", r"\bdiagnos",
    r"\binteract", r"how long (does|will) it last.*(my|for me)",
]
_URGENT = [re.compile(p, re.I) for p in URGENT_PATTERNS]
_CLINICAL = [re.compile(p, re.I) for p in CLINICAL_PATTERNS]

# Hedges that make an inquiry medically ambiguous. Ambiguity routes.
_HEDGE = [re.compile(p, re.I) for p in
          [r"not sure if i", r"i have a condition", r"my doctor", r"i take", r"i'?m on\b",
           r"is it ok(ay)? (if|that|for me)", r"something (looks|feels) (off|wrong|weird)"]]


def clinical_read(text):
    """The stop. Returns {tier, why}. tier ∈ urgent_clinical | clinical | commercial.

    Not tunable by an agent and not a model: the asymmetry between a false alarm
    (an injector reads one extra message) and a miss (a patient is answered about
    a vascular occlusion by software) is so large that biasing it is correct.
    """
    t = (text or "").strip()
    if not t:
        return {"tier": "clinical", "why": "no readable message — routed, never assumed harmless"}
    for rx in _URGENT:
        m = rx.search(t)
        if m:
            return {"tier": "urgent_clinical",
                    "why": f"possible complication: '{m.group(0).strip()}' — a licensed injector now"}
    for rx in _CLINICAL:
        m = rx.search(t)
        if m:
            return {"tier": "clinical", "why": f"medical content: '{m.group(0).strip()}' — routed unanswered"}
    for rx in _HEDGE:
        m = rx.search(t)
        if m:
            return {"tier": "clinical", "why": f"medically ambiguous ('{m.group(0).strip()}') — ambiguity routes"}
    return {"tier": "commercial", "why": "logistics or pricing — the agent may answer this"}


INTEREST = [
    (r"\bbotox\b|\btox\b|dysport|jeuveau|xeomin|frown|forehead|crow", "neurotoxin"),
    (r"\blips?\b|lip filler|juvederm|restylane", "filler_lip"),
    (r"cheek|midface|jawline|chin|sculptra|contour(?! ?body)", "filler_cheek"),
    (r"resurfac|co2|fraxel|moxi|melasma|texture|acne scar", "laser_resurf"),
    (r"hair removal|laser hair|ipl.*hair", "laser_hair"),
    (r"microneedl|rf micro|morpheus|collagen induction", "microneedle"),
    (r"coolsculpt|body ?contour|emsculpt|fat reduc", "body_contour"),
    (r"membership|facial|hydrafacial|monthly", "membership"),
    (r"skincare|tretinoin|products?|routine", "skincare"),
]
_INTEREST = [(re.compile(p, re.I), s) for p, s in INTEREST]


def qualify(text):
    """Inquiry → {tier, service, timeline, new_patient?, why}. A service the
    text does not name is left None; the concierge asks rather than assumes."""
    read = clinical_read(text)
    svc = None
    for rx, s in _INTEREST:
        if rx.search(text or ""):
            svc = s
            break
    timeline = ("soon" if re.search(r"this week|asap|tomorrow|before (my|the)|event|wedding", text or "", re.I)
                else "exploring" if re.search(r"just (looking|curious)|thinking about|maybe", text or "", re.I)
                else "unstated")
    return {"tier": read["tier"], "why": read["why"], "service": svc, "timeline": timeline,
            "can_answer": read["tier"] == "commercial"}


# ---------------------------------------------------------------- response latency
#
# The metric the whole first module exists to move. Recorded per inquiry, in
# minutes, and never averaged across a window with fewer than 20 inquiries.

def response_minutes(inq):
    if not inq.get("first_response_at"):
        return None
    a, b = parse(inq["at"]), parse(inq["first_response_at"])
    return round((b - a).total_seconds() / 60.0, 1) if a and b else None


def latency_read(inquiries, days=30, floor=20):
    rows = [i for i in inquiries if (parse(i["at"]) or now()) >= now() - timedelta(days=days)]
    vals = [m for m in (response_minutes(i) for i in rows) if m is not None]
    if len(vals) < floor:
        return unmeasured(f"only {len(vals)} answered inquiries in {days} days; need {floor}",
                          field="median_minutes", n=len(vals))
    unanswered = sum(1 for i in rows if response_minutes(i) is None)
    return {"median_minutes": round(median(vals), 1), "n": len(vals),
            "unanswered": unanswered, "window_days": days,
            "note": "median, not mean — one inquiry answered four days later would otherwise "
                    "make the whole month look worse than it was"}


# ---------------------------------------------------------------- the show-up ladder

SHOWUP_LADDER = [
    dict(offset_h=-168, channel="text", kind="deposit", note=f"${DEPOSIT} holds the chair, credited to treatment"),
    dict(offset_h=-72, channel="email", kind="expect", note="what the visit is and is not — sets the frame"),
    dict(offset_h=-24, channel="text", kind="confirm", note="one-tap confirm or move"),
    dict(offset_h=-2, channel="text", kind="morning", note="address, parking, who they're seeing"),
]
CONSULT_STATES = ("booked", "showed", "no_show", "cancelled")


def due_showup(consult, ref=None):
    ref = ref or now()
    if consult.get("state") != "booked":
        return []
    start = parse(consult["starts_at"])
    if not start:
        return []
    sent = {t.get("kind") for t in consult.get("touches", [])}
    return [t for t in SHOWUP_LADDER
            if start + timedelta(hours=t["offset_h"]) <= ref and t["kind"] not in sent]


# ---------------------------------------------------------------- the decision machine
#
# After the consult, a plan must reach a recorded decision. "Thinking about it"
# is not a state anything is allowed to rest in.

PLAN_STATES = ("presented", "treated", "declined", "expired")
DECLINE_REASONS = ("price", "timing", "nervous", "spouse_partner", "wants_research",
                   "went_elsewhere", "not_ready", "unreachable")
PLAN_TTL_DAYS = 60

DECISION_LADDER = [
    dict(day=1, channel="text", kind="recap", note="the plan in plain language, in the injector's words"),
    dict(day=4, channel="email", kind="options", note="the objection the injector actually captured, addressed"),
    dict(day=10, channel="text", kind="check", note="short — still thinking, or shall we close it out?"),
    dict(day=25, channel="email", kind="last", note="says it is the last note"),
]


def plan_state(plan, ref=None):
    if plan.get("state") in ("treated", "declined"):
        return plan["state"]
    age = -(days_until(plan["presented_at"], ref) or 0)
    return "expired" if age > PLAN_TTL_DAYS else "presented"


def due_decision(plan, ref=None):
    if plan_state(plan, ref) != "presented":
        return []
    age = -(days_until(plan["presented_at"], ref) or 0)
    sent = {t.get("day") for t in plan.get("touches", [])}
    return [t for t in DECISION_LADDER if t["day"] <= age and t["day"] not in sent]


def undecided_value(plans, ref=None):
    live = [p for p in plans if plan_state(p, ref) == "presented"]
    if not live:
        return unmeasured("no plans in a presented state", field="amount", n=0)
    return {"amount": round(sum(p["amount"] for p in live), 2), "n": len(live),
            "oldest_days": max(-(days_until(p["presented_at"], ref) or 0) for p in live)}


# ---------------------------------------------------------------- the cadence engine
#
# The quiet money. A patient does not churn with an announcement; they drift.
# Drift is measured against the treatment's own interval, and a patient with no
# recorded treatment history is NOT flagged — we would be guessing.

DRIFT_GRACE = 1.25          # 25% past the interval before we call it drift
LAPSED_AT = 2.0             # twice the interval and they are gone, not drifting


def cadence_state(patient, treatments, ref=None):
    ref = ref or now()
    mine = sorted([t for t in treatments if t.get("patient_id") == patient["id"]],
                  key=lambda t: t["at"])
    if not mine:
        return {"state": "unknown", "_missing": "no recorded treatment history for this patient",
                "service": None}
    last = mine[-1]
    spec = SERVICES.get(last["service"], {})
    interval = spec.get("interval_days")
    if not interval:
        return {"state": "no_clock", "service": last["service"],
                "_missing": f"{last['service']} has no reorder interval — nothing to drift from"}
    since = -(days_until(last["at"], ref) or 0)
    ratio = since / interval
    state = ("current" if ratio <= 1.0 else "due" if ratio <= DRIFT_GRACE
             else "drifting" if ratio < LAPSED_AT else "lapsed")
    return {"state": state, "service": last["service"], "days_since": since,
            "interval": interval, "ratio": round(ratio, 2),
            "annual_value": round(365 / interval * ((spec["band"][0] + spec["band"][1]) / 2), 2),
            "last_note": last.get("note"), "provider": last.get("provider")}


def drift_list(ref=None):
    pts, tx = store.load("patients"), store.load("treatments")
    out = []
    for p in pts:
        c = cadence_state(p, tx, ref)
        if c["state"] in ("drifting", "due"):
            out.append({"patient": p["name"], "patient_id": p["id"], **c})
    return sorted(out, key=lambda r: -(r.get("annual_value") or 0))


# ---------------------------------------------------------------- the funnel

FUNNEL_STAGES = ("inquiry", "responded", "booked", "showed", "treated", "rebooked")


def funnel(days=90):
    inq = [i for i in store.load("inquiries") if (parse(i["at"]) or now()) >= now() - timedelta(days=days)]
    cons = store.index("consults")
    by_source = {}
    for i in inq:
        s = by_source.setdefault(i["channel"], {k: 0 for k in FUNNEL_STAGES})
        s["inquiry"] += 1
        if i.get("first_response_at"):
            s["responded"] += 1
        c = cons.get(i.get("consult_id"))
        if c:
            s["booked"] += 1
            if c.get("state") == "showed":
                s["showed"] += 1
            if c.get("treated"):
                s["treated"] += 1
            if c.get("rebooked"):
                s["rebooked"] += 1
    cfg = store.load("config")
    spend = (cfg.get("ad_spend") or {})
    cost = {}
    for ch, row in by_source.items():
        if ch not in spend:
            cost[ch] = unmeasured("ad spend not connected for this channel", field="cost_per_booked")
        elif not row["booked"]:
            cost[ch] = unmeasured("no booked consults from this channel in the window",
                                  field="cost_per_booked")
        else:
            cost[ch] = {"cost_per_booked": round(spend[ch] / row["booked"], 2)}
    return {"window_days": days, "by_source": by_source, "cost_per_booked": cost,
            "note": "cost per stage is shown only where ad spend is connected; "
                    "we will not model a number you can check against your own ad account"}


# ---------------------------------------------------------------- autonomy

MATRIX = Matrix({
    "classify_inquiry":  dict(rung="R3", reason="reading an inquiry and labelling it costs nothing and is corrected in one click"),
    "route_clinical":    dict(rung="R3", reason="handing a medical question to a licensed injector is always the safe direction"),
    "answer_logistics":  dict(rung="R2", reason="hours, parking, what a consult is, the published consult fee — facts the practice already publishes"),
    "clinical_answer":   dict(rung="R0", reason="THE SYSTEM NEVER DOES THIS. Declared here so the refusal is visible: no dosing, no units, no candidacy, no contraindications, no outcome promises — the message is routed instead", never_promote=True),
    "state_price_band":  dict(rung="R2", reason="a published band is not a quote; a firm number is the injector's to give"),
    "quote_firm_price":  dict(rung="R1", reason="a firm number on a treatment plan is a commitment made by a licensed provider", never_promote=True),
    "book_consult":      dict(rung="R2", reason="books into real availability; the patient confirms the time themselves"),
    "request_deposit":   dict(rung="R1", reason="asking a patient for money — a human approves the ask, and the agent never touches card data"),
    "send_showup_touch": dict(rung="R2", reason="templated confirmations against a booked appointment; anything free-text drops to R1"),
    "refill_cancellation": dict(rung="R2", reason="offering a freed slot to a waitlist is reversible and time-critical"),
    "draft_decision_touch": dict(rung="R1", reason="follow-up on a treatment decision — drafted, sent by a human until the streak and calibration earn R2"),
    "close_plan_declined": dict(rung="R2", reason="recording a decline with a reason is bookkeeping; reopening is one click"),
    "flag_cadence_drift": dict(rung="R2", reason="a list for the front desk, not an outbound message"),
    "message_custom":    dict(rung="R1", reason="free text to a patient can become a claim or an implied promise"),
})
gate = Gate(store, MATRIX)

MOVING_KINDS = {"classify_inquiry", "route_clinical", "answer_logistics", "book_consult",
                "request_deposit", "send_showup_touch", "refill_cancellation",
                "draft_decision_touch", "decision_touch_sent", "close_plan_declined",
                "message_custom", "quote_firm_price"}


def automation(days=90):
    return automation_rate(store.load("events"), MOVING_KINDS, days, exclude_actors=("patient:",))


# ---------------------------------------------------------------- eval

CLINICAL_EVAL = Eval(
    "clinical routing", "clinical",
    "a medical question answered by software is the failure that ends a practice — "
    "recall is reported alone, and false alarms (an injector reads one extra message) are the price")


def eval_clinical(cases=None):
    cases = cases if cases is not None else EVAL_CASES
    return CLINICAL_EVAL.run(
        cases, lambda t: "commercial" if clinical_read(t)["tier"] == "commercial" else "clinical")


EVAL_CASES = [
    {"input": "how many units would I need for my forehead?", "label": "clinical"},
    {"input": "is botox safe if I'm breastfeeding?", "label": "clinical"},
    {"input": "I'm on eliquis, can I still get filler", "label": "clinical"},
    {"input": "am I a good candidate for lip filler?", "label": "clinical"},
    {"input": "my lip is going white and it really hurts", "label": "clinical"},
    {"input": "I have a hard lump where she injected", "label": "clinical"},
    {"input": "my eyelid is drooping since Tuesday", "label": "clinical"},
    {"input": "my vision is blurry on that side", "label": "clinical"},
    {"input": "not sure if I can, I have a condition", "label": "clinical"},
    {"input": "what are the side effects", "label": "clinical"},
    {"input": "", "label": "clinical"},
    {"input": "what time do you close on Saturday?", "label": "commercial"},
    {"input": "how much is a lip filler appointment roughly", "label": "commercial"},
    {"input": "do you have parking?", "label": "commercial"},
    {"input": "can I book a consult for next week", "label": "commercial"},
    {"input": "do you take care credit", "label": "commercial"},
    {"input": "where are you located", "label": "commercial"},
    {"input": "is the consult fee credited toward treatment", "label": "commercial"},
]


def urgent_recall_check():
    """Urgent complications are checked separately again — a build that gets
    'clinical' right on average but misses an occlusion is not safe."""
    urgent = [c for c in EVAL_CASES if clinical_read(c["input"])["tier"] == "urgent_clinical"]
    expected = ["my lip is going white and it really hurts", "my eyelid is drooping since Tuesday",
                "my vision is blurry on that side"]
    caught = [e for e in expected if clinical_read(e)["tier"] == "urgent_clinical"]
    return {"expected_urgent": len(expected), "caught": len(caught),
            "detected_total": len(urgent),
            "missed": [e for e in expected if e not in caught]}


# ---------------------------------------------------------------- the board

def board(ref=None):
    ref = ref or now()
    inq, cons, plans = store.load("inquiries"), store.load("consults"), store.load("plans")
    today_inq = [i for i in inq if not i.get("first_response_at")]
    upcoming = [c for c in cons if c.get("state") == "booked"]
    drift = drift_list(ref)
    return {
        "generated": iso(ref),
        "unanswered_inquiries": len(today_inq),
        "latency": latency_read(inq),
        "consults_upcoming": len(upcoming),
        "no_show_rate": no_show_rate(cons),
        "undecided_plans": undecided_value(plans, ref),
        "drift": {"n": len(drift), "annual_value": round(sum(d.get("annual_value") or 0 for d in drift), 2),
                  "basis": "each patient valued at their own treatment's annual cadence at the "
                           "midpoint of its published band"},
        "automation": automation(),
    }


def no_show_rate(consults, days=90, floor=25):
    rows = [c for c in consults if c.get("state") in ("showed", "no_show")
            and (parse(c["starts_at"]) or now()) >= now() - timedelta(days=days)]
    if len(rows) < floor:
        return unmeasured(f"only {len(rows)} completed consults in {days} days; need {floor}",
                          field="rate", n=len(rows))
    ns = sum(1 for c in rows if c["state"] == "no_show")
    return {"rate": round(ns / len(rows), 3), "no_shows": ns, "of": len(rows), "window_days": days}


# ---------------------------------------------------------------- ROI

ROI = (Roi("What the corridor is worth here")
       .line("Speed-to-lead", "revenue",
             "after-hours inquiries × incremental book% × avg first treatment × show%",
             ["after_hours_inquiries_wk", "incremental_book_rate", "avg_first_treatment", "show_rate"],
             lambda g: g["after_hours_inquiries_wk"] * g["incremental_book_rate"]
             * g["avg_first_treatment"] * g["show_rate"] * 52,
             note="after-hours inquiries are counted from your own channels",
             assumption="incremental book% is the lift from answering in minutes rather than next morning")
       .line("No-show recovery", "revenue",
             "consults × no-show points recovered × avg first treatment",
             ["consults_wk", "no_show_points_recovered", "avg_first_treatment"],
             lambda g: g["consults_wk"] * g["no_show_points_recovered"] * g["avg_first_treatment"] * 52,
             assumption="points recovered off your measured no-show rate — not a target, your delta")
       .line("Decision recovery", "revenue",
             "undecided plan value × incremental close%",
             ["undecided_plan_value", "incremental_close_rate"],
             lambda g: g["undecided_plan_value"] * g["incremental_close_rate"],
             note="undecided value is counted from your own presented plans")
       .line("Cadence recovery", "revenue",
             "drifting patients × recovered% × their own annual value",
             ["drifting_patients", "drift_recovery_rate", "avg_annual_value"],
             lambda g: g["drifting_patients"] * g["drift_recovery_rate"] * g["avg_annual_value"],
             assumption="recovered% is the share of drifting patients who return to interval")
       .line("Front-desk time", "time_saved",
             "hours/wk × 52 × loaded rate",
             ["desk_hours_wk", "loaded_rate"],
             lambda g: g["desk_hours_wk"] * 52 * g["loaded_rate"],
             note="reported apart from revenue — never added into the headline"))


def roi(given=None):
    cfg = store.load("config")
    recorded = {}
    inq = store.load("inquiries")
    wk = [i for i in inq if (parse(i["at"]) or now()) >= now() - timedelta(days=7)]
    if wk:
        recorded["after_hours_inquiries_wk"] = sum(1 for i in wk if i.get("after_hours"))
    cons = store.load("consults")
    done = [c for c in cons if c.get("state") in ("showed", "no_show")]
    if len(done) >= 25:
        recorded["consults_wk"] = round(len(done) / 13, 1)
        recorded["show_rate"] = round(sum(1 for c in done if c["state"] == "showed") / len(done), 3)
    tx = [t for t in store.load("treatments") if t.get("amount")]
    if len(tx) >= 20:
        recorded["avg_first_treatment"] = round(median([t["amount"] for t in tx]), 2)
    live = undecided_value(store.load("plans"))
    if not live.get("_missing"):
        recorded["undecided_plan_value"] = live["amount"]
    d = drift_list()
    if d:
        recorded["drifting_patients"] = len(d)
        recorded["avg_annual_value"] = round(
            sum(x.get("annual_value") or 0 for x in d) / len(d), 2)
    merged = dict(recorded)
    merged.update({k: v for k, v in (cfg.get("roi_inputs") or {}).items() if v not in (None, "")})
    merged.update({k: v for k, v in (given or {}).items() if v not in (None, "")})
    out = ROI.render(merged)
    out["recorded"] = recorded
    out["operator_supplied"] = {k: v for k, v in merged.items() if k not in recorded}
    return out
