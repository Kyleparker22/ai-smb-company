#!/usr/bin/env python3
"""Shift OS — domain core (private-duty home care · small home health).

Everything that is a *rule* lives here: client, caregiver, care-plan, shift and
authorization models; the fill-ranking composite with overtime math;
approved-pairing enforcement; retention signal definitions; EVV rule
configuration; the crisis and clinical classifiers; the ROI model and the
autonomy matrix.

The product thesis: it is 6:12am, a caregiver called out of a 7am shift, and a
scheduler has forty minutes to find someone qualified, available, close enough
and acceptable to that client and family. Do it well and the agency keeps both.

THE GUARDRAILS — the strictest in this set, and they are rules, not prompts:
  1. No clinical advice of any kind. No medication guidance, no dosing, no
     symptom interpretation, no care-plan change, no condition opinion.
  2. ANY crisis signal — fall, chest pain, breathing difficulty, sudden
     confusion, self-harm, suspected abuse or neglect — routes to a human
     immediately AND displays the emergency instruction. Suspected abuse also
     raises a mandatory-reporting flag that the system never handles itself.
  3. A caregiver is NEVER auto-assigned to a client pairing that has not been
     previously approved.
EVV rules are configurable per state; no state's requirements are hardcoded.

Stdlib only.
"""
import re, sys
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent))

from _kit.moat import Eval, Gate, Matrix, Roi                       # noqa: E402
from _kit.store import (Store, automation_rate, days_until, iso,    # noqa: E402
                        median, now, parse, unmeasured)

TABLES = ("config", "clients", "caregivers", "shifts", "pairings", "authorizations",
          "evv", "messages", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="SHIFTOS_DATA_ROOT")


# ---------------------------------------------------------------- care plans

TASKS = {
    "transfer":      dict(label="Transfer assistance", skill="transfer", risk="high"),
    "bathing":       dict(label="Bathing / personal care", skill="personal_care", risk="medium"),
    "med_reminder":  dict(label="Medication REMINDERS only", skill=None, risk="high",
                          note="reminders only — this agency does not administer"),
    "meal_prep":     dict(label="Meal preparation", skill=None, risk="low"),
    "companionship": dict(label="Companionship", skill=None, risk="low"),
    "transport":     dict(label="Transportation", skill="driving", risk="medium"),
    "housekeeping":  dict(label="Light housekeeping", skill=None, risk="low"),
    "dementia_care": dict(label="Dementia care", skill="dementia", risk="high"),
    "hoyer":         dict(label="Hoyer lift", skill="hoyer", risk="high"),
}
SKILLS = ("transfer", "personal_care", "driving", "dementia", "hoyer")

OT_THRESHOLD_HOURS = 40
OT_PREMIUM = 1.5


# ---------------------------------------------------------------- the crisis + clinical stops

CRISIS_PATTERNS = [
    (r"\bfell\b|\bfall(en|ing)?\b|on the floor|can'?t get (her|him|them) up", "fall"),
    (r"chest pain|clutching (her|his) chest|pressure in (her|his) chest", "cardiac"),
    (r"can'?t breathe|trouble breathing|gasping|blue lips|not breathing", "respiratory"),
    (r"unrespons|won'?t wake|passed out|slumped", "unresponsive"),
    (r"sudden(ly)? confus|doesn'?t know where|slurred|face is droop|weak on one side", "stroke_signs"),
    (r"bleeding (a lot|badly)|won'?t stop bleeding|blood everywhere", "bleeding"),
    (r"hurt (her|him|them)self|wants? to die|kill (her|him)self|suicid", "self_harm"),
    (r"bruis(es|ing) (i|we) can'?t explain|afraid of (her|his) (son|daughter|aide)|"
     r"took (her|his) money|hasn'?t eaten in days|left (her|him) alone all", "suspected_abuse"),
]
_CRISIS = [(re.compile(p, re.I), k) for p, k in CRISIS_PATTERNS]

CLINICAL_PATTERNS = [
    r"\bdos(e|age|ing)\b", r"should (she|he|they|we) (take|stop|skip|double)",
    r"is (it|this) safe (to|for)", r"\bpills?\b|\bmedication\b|\bmeds\b", r"side ?effects?",
    r"\bmg\b|\bmilligrams?\b", r"blood pressure (is|reading|was)", r"blood sugar",
    r"(is|does) (this|that) (mean|sound like)", r"diagnos", r"\binfect", r"wound|pressure sore|ulcer",
    r"change (her|his|the) (care plan|medication|dose)", r"\bcatheter\b|\boxygen\b|\binsulin\b",
    r"do (you|we) think (she|he|they)", r"getting worse", r"new symptom",
]
_CLINICAL = [re.compile(p, re.I) for p in CLINICAL_PATTERNS]

EMERGENCY_INSTRUCTION = ("If this is an emergency, call 911 now. Then call our on-call line — "
                         "a nurse will speak with you directly.")
MANDATORY_REPORT_NOTE = ("Possible abuse or neglect. This agency has mandatory-reporting "
                         "obligations. The system has flagged it for a human and has taken NO "
                         "other action — reporting decisions are never made by software.")


def read_message(text):
    """Returns {tier, kind, why}. tier ∈ crisis | clinical | routine.

    Biased to over-route in both directions. A missed crisis is the worst
    outcome this system can produce, and the cost of a false alarm is a nurse
    reading one extra message.
    """
    t = (text or "").strip()
    if not t:
        return {"tier": "clinical", "kind": None,
                "why": "no readable message — routed, never assumed harmless"}
    for rx, kind in _CRISIS:
        m = rx.search(t)
        if m:
            return {"tier": "crisis", "kind": kind,
                    "why": f"crisis signal ({kind}): '{m.group(0).strip()}'",
                    "mandatory_report": kind == "suspected_abuse"}
    for rx in _CLINICAL:
        m = rx.search(t)
        if m:
            return {"tier": "clinical", "kind": "clinical_question",
                    "why": f"clinical content: '{m.group(0).strip()}' — routed to a nurse unanswered"}
    return {"tier": "routine", "kind": None, "why": "scheduling or logistics — answerable"}


# ---------------------------------------------------------------- pairings

def pairing_approved(caregiver_id, client_id, pairings=None):
    rows = pairings if pairings is not None else store.load("pairings")
    return any(p["caregiver_id"] == caregiver_id and p["client_id"] == client_id
               and p.get("state") == "approved" for p in rows)


def pairing_state(caregiver_id, client_id, pairings=None):
    rows = pairings if pairings is not None else store.load("pairings")
    for p in rows:
        if p["caregiver_id"] == caregiver_id and p["client_id"] == client_id:
            return p.get("state")
    return None


# ---------------------------------------------------------------- the fill engine

MAX_TRAVEL = 40


def fill_candidates(shift, client, caregivers=None, ref=None, pairings=None, shifts=None):
    """Ranked, explainable, and overtime-aware.

    Overtime cost appears on ANY option that would trigger it — the scheduler
    should never learn on Friday that the 6am fix cost time-and-a-half.
    """
    ref = ref or now()
    caregivers = caregivers if caregivers is not None else store.load("caregivers")
    shifts = shifts if shifts is not None else store.load("shifts")
    plan = client.get("care_plan", [])
    needed = {TASKS[t]["skill"] for t in plan if TASKS.get(t, {}).get("skill")}
    hours_this_week = _hours_by_caregiver(shifts, ref)

    ranked, blocked = [], []
    for cg in caregivers:
        if cg.get("id") == shift.get("caregiver_id"):
            continue
        reasons, score = [], 0.0

        have = set(cg.get("skills") or [])
        missing = needed - have
        if missing:
            blocked.append({"caregiver_id": cg["id"], "name": cg.get("name"),
                            "why": f"care plan needs {', '.join(sorted(missing))}"})
            continue
        reasons.append(f"has every skill this care plan needs ({', '.join(sorted(needed)) or 'none required'})")

        if not cg.get("available"):
            blocked.append({"caregiver_id": cg["id"], "name": cg.get("name"),
                            "why": "not available for this window"})
            continue

        travel = (cg.get("travel_minutes") or {}).get(client.get("zone"))
        if travel is None:
            reasons.append("travel time to this client not recorded")
        elif travel > MAX_TRAVEL:
            blocked.append({"caregiver_id": cg["id"], "name": cg.get("name"),
                            "why": f"{travel} minutes away, over the {MAX_TRAVEL}-minute line"})
            continue
        else:
            score += (1 - travel / MAX_TRAVEL) * 1.5
            reasons.append(f"{travel} minutes away")

        approved = pairing_approved(cg["id"], client["id"], pairings)
        state = pairing_state(cg["id"], client["id"], pairings)
        if approved:
            score += 2.5
            reasons.append("already an approved pairing with this client")
        elif state == "declined":
            blocked.append({"caregiver_id": cg["id"], "name": cg.get("name"),
                            "why": "the family previously declined this caregiver"})
            continue
        else:
            reasons.append("NEW PAIRING — needs approval before this can be assigned")

        worked = hours_this_week.get(cg["id"], 0)
        shift_hours = shift.get("hours", 4)
        ot_hours = max(0, (worked + shift_hours) - OT_THRESHOLD_HOURS)
        ot_cost = round(ot_hours * (cg.get("pay_rate", 0)) * (OT_PREMIUM - 1), 2)
        if ot_hours:
            score -= min(1.5, ot_hours * 0.2)
            reasons.append(f"OVERTIME: {worked}h worked, this shift adds {shift_hours}h — "
                           f"{ot_hours}h at time-and-a-half, about ${ot_cost} extra")
        else:
            reasons.append(f"{worked}h worked this week — no overtime")

        if cg["id"] in (client.get("preferred_caregivers") or []):
            score += 1.5
            reasons.append("on the family's preferred list")
        cont = sum(1 for s in shifts if s.get("client_id") == client["id"]
                   and s.get("caregiver_id") == cg["id"] and s.get("state") == "completed")
        if cont:
            score += min(1.5, cont * 0.1)
            reasons.append(f"has worked this client {cont} time(s) before")

        sn = cg.get("short_notice_accepted")
        if sn is None:
            reasons.append("short-notice history not recorded")
        else:
            score += sn * 0.2
            reasons.append(f"accepted short notice {sn} of the last 5 asks")

        ranked.append({"caregiver_id": cg["id"], "name": cg.get("name"),
                       "score": round(score, 2), "reasons": reasons,
                       "approved_pairing": approved, "overtime_cost": ot_cost,
                       "overtime_hours": ot_hours})
    ranked.sort(key=lambda r: (-(1 if r["approved_pairing"] else 0), -r["score"]))
    return {"ranked": ranked, "blocked": blocked,
            "note": "approved pairings first, then score. A new pairing can be proposed but never "
                    "assigned without a human — and every option that would trigger overtime shows "
                    "what it costs"}


def _hours_by_caregiver(shifts, ref):
    # floor to Monday MIDNIGHT — without the floor, "this week" started at the
    # current clock time and silently excluded same-day shifts (worst on
    # Mondays, when it excluded the entire day so far)
    start = (ref - timedelta(days=ref.weekday())).replace(hour=0, minute=0,
                                                          second=0, microsecond=0)
    out = {}
    for s in shifts:
        if s.get("state") not in ("completed", "scheduled"):
            continue
        d = parse(s.get("starts_at"))
        if not d or d < start or d > ref + timedelta(days=7):
            continue
        out[s.get("caregiver_id")] = out.get(s.get("caregiver_id"), 0) + s.get("hours", 4)
    return out


# ---------------------------------------------------------------- retention signals
#
# A caregiver does not quit with an announcement. These are the signals already
# in the data, and each one is stated on the row — the list is for a HUMAN
# conversation, and the system never messages a caregiver about retention.

RETENTION_SIGNALS = {
    "hours_below_preference": "working fewer hours than they said they wanted",
    "cancelled_shifts": "cancelled shifts recently",
    "commute_creep": "their average travel time has grown",
    "no_office_contact": "nobody from the office has spoken to them",
    "declined_in_a_row": "declined several asks in a row",
}
NO_CONTACT_DAYS = 21
# One signal is a note; two is a pattern. A retention list that flags 88% of the
# roster is a list nobody works — which is worse than no list.
RISK_SIGNAL_FLOOR = 2


def retention_risk(cg, shifts=None, ref=None):
    ref = ref or now()
    shifts = shifts if shifts is not None else store.load("shifts")
    mine = [s for s in shifts if s.get("caregiver_id") == cg["id"]]
    signals = []

    want = cg.get("preferred_hours_week")
    recent = [s for s in mine if s.get("state") == "completed"
              and (parse(s.get("starts_at")) or ref) >= ref - timedelta(days=21)]
    if want:
        avg = round(sum(s.get("hours", 4) for s in recent) / 3, 1) if recent else 0
        if avg < want * 0.7:
            signals.append({"signal": "hours_below_preference",
                            "detail": f"wants {want}h/wk, averaging {avg}h over three weeks"})
    else:
        pass  # no stated preference — we do not infer one

    cancels = [s for s in mine if s.get("state") == "caregiver_cancelled"
               and (parse(s.get("starts_at")) or ref) >= ref - timedelta(days=30)]
    if len(cancels) >= 2:
        signals.append({"signal": "cancelled_shifts",
                        "detail": f"{len(cancels)} cancellations in 30 days"})

    last = cg.get("last_office_contact")
    if not last:
        signals.append({"signal": "no_office_contact", "detail": "no office contact ever recorded"})
    else:
        d = -(days_until(last, ref) or 0)
        if d > NO_CONTACT_DAYS:
            signals.append({"signal": "no_office_contact", "detail": f"{d} days since anyone called"})

    dec = cg.get("declined_in_a_row")
    if dec and dec >= 3:
        signals.append({"signal": "declined_in_a_row", "detail": f"{dec} asks declined in a row"})

    if not signals:
        return None
    return {"caregiver_id": cg["id"], "name": cg.get("name"), "signals": signals,
            "count": len(signals), "at_risk": len(signals) >= RISK_SIGNAL_FLOOR,
            "why": "; ".join(f"{RETENTION_SIGNALS[s['signal']]} — {s['detail']}" for s in signals)}


# ---------------------------------------------------------------- EVV
#
# Rules are CONFIGURABLE PER STATE. Nothing here hardcodes one state's
# requirements, because that is the thing an agency in the next state over
# discovers the expensive way.

DEFAULT_EVV_RULES = {
    "require_clock_in": True, "require_clock_out": True, "require_task_notes": True,
    "max_late_minutes": 15, "require_gps": False,
    "_source": "agency default — replace with the state's own rule set before go-live",
}

EVV_EXCEPTIONS = {
    "missed_clock_in": dict(label="No clock-in", billing="the visit may not be billable"),
    "missed_clock_out": dict(label="No clock-out", billing="duration is unverifiable; payroll and billing both stall"),
    "no_notes": dict(label="No care notes", billing="documentation gap — a payer can claw this back"),
    "late": dict(label="Late clock-in", billing="within tolerance is fine; past it, the payer may reduce the unit"),
    "no_gps": dict(label="No location captured", billing="required in some states, not all — see the rule set"),
    "over_authorization": dict(label="Beyond authorized hours", billing="hours past the authorization are not billable"),
}


def evv_exceptions(shift, rules=None, authorization=None):
    rules = rules or DEFAULT_EVV_RULES
    out = []
    if rules.get("require_clock_in") and not shift.get("clock_in"):
        out.append("missed_clock_in")
    if rules.get("require_clock_out") and not shift.get("clock_out"):
        out.append("missed_clock_out")
    if rules.get("require_task_notes") and not shift.get("notes"):
        out.append("no_notes")
    if rules.get("require_gps") and not shift.get("gps"):
        out.append("no_gps")
    ci, planned = parse(shift.get("clock_in")), parse(shift.get("starts_at"))
    if ci and planned:
        late = (ci - planned).total_seconds() / 60
        if late > rules.get("max_late_minutes", 15):
            out.append("late")
    # Over-authorization is deliberately NOT evaluated here. It is a fact about
    # the CLIENT'S period, not about this visit — flagging every completed visit
    # once a client passes their cap turned 58% of the book into "exceptions"
    # and made the real documentation gaps impossible to see.
    return [{"type": t, **EVV_EXCEPTIONS[t]} for t in out]


def authorization_drift(ref=None):
    """Clients at or past their authorized hours for the period. One row per
    client, which is what a biller actually works."""
    out = []
    for a in store.load("authorizations"):
        auth, used = a.get("authorized_hours"), a.get("used_hours")
        if not auth:
            out.append({"client_id": a.get("client_id"), "used": used,
                        "_missing": "no authorized hours on file — drift is unknowable"})
            continue
        if used is None:
            out.append({"client_id": a.get("client_id"), "authorized": auth,
                        "_missing": "no used hours recorded"})
            continue
        if used >= auth * 0.9:
            out.append({"client_id": a.get("client_id"), "authorized": auth, "used": used,
                        "pct": round(used / auth, 3),
                        "state": "over" if used > auth else "near",
                        "billing": ("hours past the authorization are not billable" if used > auth
                                    else "inside 10% of the cap")})
    return out


# ---------------------------------------------------------------- autonomy

MATRIX = Matrix({
    "read_message":       dict(rung="R3", reason="classifying an inbound message costs nothing and is corrected in one click"),
    "route_crisis":       dict(rung="R3", reason="putting a human on it immediately is always the safe direction — the one action safer automatic than gated"),
    "route_clinical":     dict(rung="R3", reason="handing a clinical question to a nurse is the safe direction"),
    "clinical_answer":    dict(rung="R0", reason="THE SYSTEM NEVER DOES THIS. No medication guidance, no dosing, no symptom interpretation, no care-plan change, no condition opinion — it routes to a licensed nurse instead", never_promote=True),
    "mandatory_report":   dict(rung="R0", reason="THE SYSTEM NEVER DOES THIS. Suspected abuse or neglect is flagged for a human. Reporting decisions are made by people with licences and legal duties", never_promote=True),
    "offer_shift_approved_pairing": dict(rung="R2", reason="offering an open shift to a caregiver already approved for that client, in waves, is reversible and time-critical"),
    "assign_new_pairing": dict(rung="R1", reason="a caregiver who has never worked this client goes to a human. A stranger arriving unannounced is how a family starts shopping", never_promote=True),
    "flag_overtime":      dict(rung="R3", reason="showing what an option costs is information, not a decision"),
    "retention_list":     dict(rung="R2", reason="a ranked internal list for the office"),
    "message_caregiver_retention": dict(rung="R0", reason="THE SYSTEM NEVER DOES THIS. A retention conversation is a human one; an automated 'we noticed you seem unhappy' is worse than silence", never_promote=True),
    "evv_flag":           dict(rung="R3", reason="raising a documentation exception is always the safe direction"),
    "family_update":      dict(rung="R1", reason="what a family is told about their parent is the agency's word"),
    "referral_response":  dict(rung="R2", reason="acknowledging a referral and capturing the need, fast, is what wins census"),
})
gate = Gate(store, MATRIX)

MOVING_KINDS = {"read_message", "route_crisis", "route_clinical", "offer_shift_approved_pairing",
                "assign_new_pairing", "shift_filled", "retention_list", "evv_flag",
                "family_update", "referral_response"}


def automation(days=90):
    return automation_rate(store.load("events"), MOVING_KINDS, days,
                           exclude_actors=("family:", "caregiver:"))


# ---------------------------------------------------------------- evals

CRISIS_EVAL = Eval(
    "crisis routing", "crisis",
    "A MISSED CRISIS IS THE WORST FAILURE THIS SYSTEM CAN PRODUCE. Recall is reported alone and "
    "prominently; false alarms cost a nurse one extra message and are accepted without argument")

CLINICAL_EVAL = Eval(
    "clinical routing", "not_routine",
    "a clinical question answered by software is practising nursing without a licence")

CRISIS_CASES = [
    ("she fell in the bathroom and I can't get her up", "crisis"),
    ("mom is complaining of chest pain", "crisis"),
    ("he can't breathe properly, gasping", "crisis"),
    ("she's unresponsive, won't wake up", "crisis"),
    ("suddenly confused and her face is drooping", "crisis"),
    ("there's blood everywhere, it won't stop bleeding", "crisis"),
    ("she said she wants to die", "crisis"),
    ("there are bruises we can't explain and she's afraid of her son", "crisis"),
    ("should she take her pill twice today?", "not_crisis"),
    ("can we move Thursday to Friday", "not_crisis"),
    ("the aide was 20 minutes late", "not_crisis"),
    ("what time is the visit tomorrow", "not_crisis"),
    ("can you send the invoice again", "not_crisis"),
]

CLINICAL_CASES = [
    ("should she take her pill twice today?", "not_routine"),
    ("what is this new pill for", "not_routine"),
    ("her blood pressure was 180 over 100", "not_routine"),
    ("is that wound getting infected", "not_routine"),
    ("do you think she's getting worse", "not_routine"),
    ("can we change her care plan to add oxygen", "not_routine"),
    ("", "not_routine"),
    ("she fell in the bathroom", "not_routine"),
    ("can we move Thursday to Friday", "routine"),
    ("what time is the visit tomorrow", "routine"),
    ("please send the invoice again", "routine"),
    ("the aide was 20 minutes late", "routine"),
    ("can we add a Saturday shift", "routine"),
]


def eval_crisis():
    return CRISIS_EVAL.run([{"input": t, "label": l} for t, l in CRISIS_CASES],
                           lambda t: "crisis" if read_message(t)["tier"] == "crisis" else "not_crisis")


def eval_clinical():
    return CLINICAL_EVAL.run(
        [{"input": t, "label": l} for t, l in CLINICAL_CASES],
        lambda t: "routine" if read_message(t)["tier"] == "routine" else "not_routine")


# ---------------------------------------------------------------- the ops board

def ops_board(ref=None):
    ref = ref or now()
    shifts = store.load("shifts")
    clients = store.index("clients")
    unfilled = []
    for s in shifts:
        if s.get("state") != "open":
            continue
        d = parse(s.get("starts_at"))
        if not d or d < ref or d > ref + timedelta(hours=72):
            continue
        c = clients.get(s.get("client_id"), {})
        risk = "high" if any(TASKS.get(t, {}).get("risk") == "high"
                             for t in c.get("care_plan", [])) else "standard"
        unfilled.append({"shift": s["id"], "client": c.get("name"), "client_id": c.get("id"),
                         "starts_at": s["starts_at"], "hours": s.get("hours"),
                         "risk": risk,
                         "why_risky": ", ".join(TASKS[t]["label"] for t in c.get("care_plan", [])
                                                if TASKS.get(t, {}).get("risk") == "high")})
    unfilled.sort(key=lambda r: (0 if r["risk"] == "high" else 1, r["starts_at"]))

    ot = overtime_exposure(shifts, ref)
    all_signals = [r for r in (retention_risk(cg, shifts, ref) for cg in store.load("caregivers")) if r]
    at_risk = [r for r in all_signals if r["at_risk"]]
    at_risk.sort(key=lambda r: -r["count"])
    exceptions = evv_board(ref)
    return {"generated": iso(ref), "unfilled_72h": unfilled[:40],
            "unfilled_count": len(unfilled),
            "overtime": ot,
            "retention_at_risk": at_risk[:30], "retention_count": len(at_risk),
            "retention_single_signal": len(all_signals) - len(at_risk),
            "evv_exceptions": exceptions["count"],
            "authorization_drift": exceptions["over_auth"],
            "automation": automation()}


def overtime_exposure(shifts=None, ref=None, floor=10):
    ref = ref or now()
    shifts = shifts if shifts is not None else store.load("shifts")
    hours = _hours_by_caregiver(shifts, ref)
    if len(hours) < floor:
        return unmeasured(f"only {len(hours)} caregivers with scheduled hours this week; need {floor}",
                          field="cost", n=len(hours))
    cgs = store.index("caregivers")
    cost, people = 0.0, 0
    for cid, h in hours.items():
        if h > OT_THRESHOLD_HOURS:
            rate = (cgs.get(cid) or {}).get("pay_rate", 0)
            cost += (h - OT_THRESHOLD_HOURS) * rate * (OT_PREMIUM - 1)
            people += 1
    return {"cost": round(cost, 2), "people": people, "of": len(hours),
            "basis": "scheduled hours over 40 this week at time-and-a-half, from the roster's own "
                     "pay rates"}


def evv_board(ref=None):
    ref = ref or now()
    cfg = store.load("config")
    rules = cfg.get("evv_rules") or DEFAULT_EVV_RULES
    auths = {a["client_id"]: a for a in store.load("authorizations")}
    rows = []
    for s in store.load("shifts"):
        if s.get("state") != "completed":
            continue
        ex = evv_exceptions(s, rules, auths.get(s.get("client_id")))
        if ex:
            rows.append({"shift": s["id"], "client_id": s.get("client_id"),
                         "caregiver_id": s.get("caregiver_id"), "exceptions": ex,
                         "starts_at": s.get("starts_at")})
    return {"rows": rows[:60], "count": len(rows), "rules": rules,
            "over_auth": sum(1 for d in authorization_drift() if d.get("state") == "over"),
            "authorization_drift": authorization_drift()[:40]}


# ---------------------------------------------------------------- ROI

ROI = (Roi("What the 6am call is worth here")
       .line("Fill value", "revenue",
             "unfilled shifts/wk × fill% gained × revenue per shift × margin",
             ["unfilled_shifts_wk", "fill_points_gained", "revenue_per_shift", "margin"],
             lambda g: g["unfilled_shifts_wk"] * g["fill_points_gained"] * g["revenue_per_shift"]
             * g["margin"] * 52,
             note="unfilled shifts are counted from your own board")
       .line("Overtime avoided", "revenue",
             "OT hours/wk × premium × avoidable%",
             ["ot_hours_wk", "avg_pay_rate", "avoidable_share"],
             lambda g: g["ot_hours_wk"] * g["avg_pay_rate"] * (OT_PREMIUM - 1)
             * g["avoidable_share"] * 52,
             note="computed from the ranked-fill choices actually taken — the engine shows the "
                  "overtime cost on every option, so avoiding it is a decision somebody made, "
                  "not an assumption we get to bank")
       .line("Billing exceptions", "revenue",
             "EVV exceptions/mo × denial rate × avg visit value × 12",
             ["evv_exceptions_month", "denial_rate", "avg_visit_value"],
             lambda g: g["evv_exceptions_month"] * g["denial_rate"] * g["avg_visit_value"] * 12,
             note="exception count is counted from your own completed visits")
       .line("Turnover", "scenario",
             "departures/yr × replacement cost × prevention%",
             ["departures_per_year", "replacement_cost", "prevention_share"],
             lambda g: g["departures_per_year"] * g["replacement_cost"] * g["prevention_share"],
             note="A SCENARIO, NOT A SAVING. Prevented departures cannot be counted — nobody can "
                  "tell you which caregiver would have quit. This line is driven by YOUR OWN "
                  "departure history, and the prevention share is a visible, editable assumption "
                  "you should argue with",
             assumption="prevention% — the share of at-risk caregivers a conversation actually keeps"))


def roi(given=None):
    cfg = store.load("config")
    recorded = {}
    ref = now()
    shifts = store.load("shifts")
    wk = [s for s in shifts if s.get("state") == "open"
          and (parse(s.get("starts_at")) or ref) <= ref + timedelta(days=7)]
    if wk:
        recorded["unfilled_shifts_wk"] = len(wk)
    ot = overtime_exposure(shifts, ref)
    if not ot.get("_missing"):
        hours = _hours_by_caregiver(shifts, ref)
        recorded["ot_hours_wk"] = round(sum(max(0, h - OT_THRESHOLD_HOURS) for h in hours.values()), 1)
    rates = [c["pay_rate"] for c in store.load("caregivers") if c.get("pay_rate")]
    if len(rates) >= 20:
        recorded["avg_pay_rate"] = round(median(rates), 2)
    ev = evv_board(ref)
    if ev["count"]:
        recorded["evv_exceptions_month"] = ev["count"]
    merged = dict(recorded)
    merged.update({k: v for k, v in (cfg.get("roi_inputs") or {}).items() if v not in (None, "")})
    merged.update({k: v for k, v in (given or {}).items() if v not in (None, "")})
    out = ROI.render(merged)
    out["recorded"] = recorded
    out["operator_supplied"] = {k: v for k, v in merged.items() if k not in recorded}
    return out
