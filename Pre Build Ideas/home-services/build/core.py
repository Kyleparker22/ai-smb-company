#!/usr/bin/env python3
"""Dispatch OS — domain core (residential HVAC · plumbing · electrical).

Everything that is a *rule* lives here, not in the agents and not in the UI:
the price book, the urgency taxonomy and the emergency stop, capacity and
drive-time math, the estimate state machine, the recovery cadence, the
seasonal re-offer calendar, the ROI model and the autonomy matrix.

The product thesis, in three lines of code's worth of English: a contractor's
revenue leaks where demand was ALREADY earned — the call that rang while the
CSR was busy, the estimate presented and never followed up, and the repair the
technician recommended and nobody re-offered. Those three, and nothing else.

Honesty rules are enforced by `_kit.store` (see `unmeasured()` and the
append-only event log) and are not re-implemented here.

Stdlib only.
"""
import re, sys
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent))          # so `_kit` imports

from _kit.moat import Eval, Gate, Matrix, Roi        # noqa: E402
from _kit.store import (Store, automation_rate, days_until, hours_between,  # noqa: E402
                        iso, median, now, parse, unmeasured)

TABLES = ("config", "customers", "technicians", "jobs", "calls", "estimates",
          "recommendations", "slots", "approvals", "messages", "events")
store = Store(ROOT / "data", TABLES, env_var="DISPATCHOS_DATA_ROOT")


# ---------------------------------------------------------------- the trades

TRADES = ("hvac", "plumbing", "electrical")

# Job classes with the chair-time equivalent: how long a truck is tied up, and
# what the work is typically worth. Ranges, not promises — the seed draws from
# them and the ROI panel uses the client's OWN recorded average instead.
JOB_CLASSES = {
    "hvac_no_cool":      dict(trade="hvac", label="No cooling", minutes=90, ticket=(220, 1400), season="summer"),
    "hvac_no_heat":      dict(trade="hvac", label="No heat", minutes=90, ticket=(220, 1600), season="winter"),
    "hvac_maintenance":  dict(trade="hvac", label="Maintenance", minutes=60, ticket=(120, 260), season="shoulder"),
    "hvac_replacement":  dict(trade="hvac", label="System replacement", minutes=480, ticket=(6500, 18000), season="any"),
    "plumb_leak":        dict(trade="plumbing", label="Leak", minutes=90, ticket=(240, 1200), season="any"),
    "plumb_clog":        dict(trade="plumbing", label="Drain / clog", minutes=75, ticket=(190, 900), season="any"),
    "plumb_water_heater": dict(trade="plumbing", label="Water heater", minutes=180, ticket=(1400, 4200), season="any"),
    "elec_no_power":     dict(trade="electrical", label="Partial power loss", minutes=90, ticket=(240, 1100), season="any"),
    "elec_panel":        dict(trade="electrical", label="Panel / service", minutes=360, ticket=(2200, 6500), season="any"),
    "elec_fixture":      dict(trade="electrical", label="Fixture / device", minutes=60, ticket=(160, 620), season="any"),
}

DIAGNOSTIC_FEE = 89          # published; the ONLY price an agent may state
AFTER_HOURS_FEE = 189        # a premium — a price commitment, therefore gated
MEMBERSHIP_FEE = 19          # per month; members get fee waived + priority


# ---------------------------------------------------------------- urgency + the emergency stop
#
# Four urgency bands. The band matters for scheduling; the EMERGENCY flag is a
# separate, deliberately over-triggering circuit that bypasses everything and
# puts a human on the phone. The bias is stated in code, not in a comment:
# `emergency_signal` returns True on a partial match, on an ambiguous match,
# and on an unparseable input. A false alarm costs one phone call. A miss costs
# a house.

EMERGENCY_PATTERNS = [
    r"\bgas\b", r"smell(s|ing)? gas", r"\bpropane\b", r"rotten egg",
    r"carbon monoxide", r"\bco\b alarm", r"co detector",
    r"burn(ing|t)?\s*(smell|odor|odour|plastic|wire|wiring)?", r"\bsmoke\b", r"\bsmoking\b",
    r"\bspark(s|ed|ing)?\b", r"\bshock(ed|ing)?\b", r"\barc(ing)?\b", r"\bflame\b", r"\bfire\b",
    r"flood(ing|ed)?", r"water\b.{0,15}\b(everywhere|pouring|gushing|spraying)", r"burst pipe", r"pipe burst",
    r"sewage|sewer back", r"\bgeyser\b",
    r"can'?t breathe", r"dizzy", r"headache.*(furnace|heater|gas)",
    r"no heat.*(baby|infant|newborn|elderly|oxygen)", r"no (a/?c|cool).*(oxygen|infant|newborn)",
]
_EMERG_RE = [re.compile(p, re.I) for p in EMERGENCY_PATTERNS]

# Phrases that make a caller's report ambiguous. Ambiguity routes to a human —
# it does not get resolved by guessing.
AMBIGUOUS = [re.compile(p, re.I) for p in
             [r"\bnot sure\b", r"\bsomething\b.*\bwrong\b", r"\bweird\b", r"\bstrange (smell|noise|sound)\b",
              r"\bmight be\b", r"\bi think\b.*\b(leak|gas|burn)"]]

URGENCY = {
    "emergency": dict(label="Emergency", book_within_h=0, note="a human takes this call now"),
    "same_day":  dict(label="Same day", book_within_h=8, note="no heat/cool, active leak, no hot water"),
    "next_day":  dict(label="Next day", book_within_h=24, note="degraded but liveable"),
    "scheduled": dict(label="Scheduled", book_within_h=168, note="maintenance, quotes, cosmetic"),
}


def emergency_signal(text):
    """The stop. Returns (True, why) on ANY signal, ambiguity included.

    Deliberately not a model and deliberately not tunable by an agent: this is
    the one classifier in the build whose false-positive cost (a phone call) is
    so much lower than its false-negative cost that biasing it is correct.
    """
    t = (text or "").strip()
    if not t:
        return True, "no text to read — an unreadable report is routed, never assumed safe"
    for rx in _EMERG_RE:
        m = rx.search(t)
        if m:
            return True, f"matched emergency pattern: '{m.group(0).strip()}'"
    for rx in AMBIGUOUS:
        m = rx.search(t)
        if m:
            return True, f"caller is unsure ('{m.group(0).strip()}') — ambiguity routes to a human"
    return False, ""


SYMPTOMS = [
    (r"no (a/?c|cool|cooling)|not cooling|blowing warm", "hvac_no_cool", "same_day"),
    (r"no heat|not heating|furnace (is )?out|blowing cold", "hvac_no_heat", "same_day"),
    (r"tune ?up|maintenance|service (plan|visit)|check ?up", "hvac_maintenance", "scheduled"),
    (r"new (system|unit|furnace|a/?c)|replace(ment)? (system|unit)|quote for a", "hvac_replacement", "scheduled"),
    (r"no hot water|water heater|hot water heater", "plumb_water_heater", "same_day"),
    (r"leak|drip|dripping|wet spot", "plumb_leak", "same_day"),
    (r"clog|backed? ?up|slow drain|won'?t drain|toilet", "plumb_clog", "next_day"),
    (r"no power|breaker|outlet(s)? (dead|out)|half the house", "elec_no_power", "same_day"),
    (r"panel|service upgrade|amps?|sub ?panel", "elec_panel", "scheduled"),
    (r"light|fixture|switch|fan install|ceiling fan", "elec_fixture", "scheduled"),
]
_SYMPTOM_RE = [(re.compile(p, re.I), cls, urg) for p, cls, urg in SYMPTOMS]


def classify(text):
    """Call → {emergency, job_class, trade, urgency, confidence, why}.

    An unmatched symptom is NOT guessed into a job class. It comes back as
    `job_class: None` with a reason, and the intake agent asks a question
    instead of booking the wrong truck.
    """
    emerg, why = emergency_signal(text)
    if emerg:
        return {"emergency": True, "urgency": "emergency", "job_class": None,
                "trade": None, "confidence": 1.0, "why": why}
    for rx, cls, urg in _SYMPTOM_RE:
        m = rx.search(text or "")
        if m:
            return {"emergency": False, "urgency": urg, "job_class": cls,
                    "trade": JOB_CLASSES[cls]["trade"], "confidence": 0.9,
                    "why": f"matched '{m.group(0).strip()}'"}
    return {"emergency": False, "urgency": "next_day", "job_class": None, "trade": None,
            "confidence": 0.0,
            "why": "no symptom matched — the agent asks a clarifying question rather than booking a guess"}


# ---------------------------------------------------------------- service area + capacity

# Zones with a drive-time matrix. Not a mapping API — a demo build makes no
# network calls — but the SHAPE is right, and the adapter seam is named.
ZONES = ("north", "central", "south", "west")
DRIVE_MIN = {
    ("north", "north"): 10, ("north", "central"): 22, ("north", "south"): 44, ("north", "west"): 31,
    ("central", "central"): 12, ("central", "south"): 20, ("central", "west"): 18,
    ("south", "south"): 11, ("south", "west"): 33, ("west", "west"): 13,
}
OUT_OF_AREA = "out_of_area"


def drive_minutes(a, b):
    if a == b:
        return DRIVE_MIN.get((a, a), 15)
    return DRIVE_MIN.get((a, b)) or DRIVE_MIN.get((b, a)) or 45


def in_service_area(zone):
    return zone in ZONES


WORK_START, WORK_END = 8, 17          # local hours
AFTER_HOURS = "after_hours"


def slot_class(hour):
    return "standard" if WORK_START <= hour < WORK_END else AFTER_HOURS


def open_slots(day_slots, job_class, customer_zone, want_after=None):
    """Only slots that GENUINELY exist: right skill, room for the job's minutes,
    and drive time from the tech's prior stop actually fits.

    A booking agent that offers a slot the board cannot honour is worse than one
    that offers nothing, so this refuses rather than rounds.
    """
    spec = JOB_CLASSES.get(job_class)
    if not spec:
        return []
    out = []
    for s in day_slots:
        if s.get("booked_job"):
            continue
        if spec["trade"] not in s.get("skills", []):
            continue
        drive = drive_minutes(s.get("from_zone", "central"), customer_zone)
        if s.get("minutes_free", 0) < spec["minutes"] + drive:
            continue
        if want_after and s["starts_at"] < want_after:
            continue
        out.append(dict(s, drive_minutes=drive, needs_minutes=spec["minutes"],
                        slot_class=slot_class(int((parse(s["starts_at"]) or now()).hour))))
    return sorted(out, key=lambda s: s["starts_at"])


# ---------------------------------------------------------------- the estimate state machine
#
# The rule that IS the product: an estimate may not rest in "presented". It
# must reach a terminal state, and "lost" must carry a reason, because the
# reason is what the next quarter's pricing conversation is built from.

ESTIMATE_STATES = ("presented", "won", "lost", "expired")
TERMINAL = ("won", "lost", "expired")
LOSS_REASONS = ("price", "timing", "went_with_competitor", "did_it_themselves",
                "no_longer_needed", "unreachable", "financing_declined")
ESTIMATE_TTL_DAYS = 45

# The ladder. Bounded on purpose: five touches then a human decision, never an
# infinite drip. Day offsets from presentation.
LADDER = [
    dict(day=1, channel="text", kind="recap", note="the scope in the tech's own words + the photo"),
    dict(day=3, channel="email", kind="options", note="good/better/best and the financing link"),
    dict(day=7, channel="call_task", kind="call", note="the tech who quoted it calls — not the CSR"),
    dict(day=14, channel="text", kind="check", note="short: still deciding, or should we close it out?"),
    dict(day=30, channel="email", kind="last", note="last touch, states it is the last touch"),
]


def estimate_state(est, ref=None):
    """Derived, never trusted from a field alone — an estimate past its TTL is
    expired whatever the record says."""
    if est.get("state") in ("won", "lost"):
        return est["state"]
    age = days_until(est["presented_at"], ref)
    if age is not None and -age > ESTIMATE_TTL_DAYS:
        return "expired"
    return "presented"


def due_touches(est, ref=None):
    """Which ladder steps are due and not yet sent."""
    if estimate_state(est, ref) != "presented":
        return []
    age_days = -(days_until(est["presented_at"], ref) or 0)
    sent = {t.get("day") for t in est.get("touches", [])}
    return [t for t in LADDER if t["day"] <= age_days and t["day"] not in sent]


def aging_buckets(estimates, ref=None):
    b = {"0-3": [], "4-7": [], "8-14": [], "15-30": [], "31-45": []}
    for e in estimates:
        if estimate_state(e, ref) != "presented":
            continue
        d = -(days_until(e["presented_at"], ref) or 0)
        key = ("0-3" if d <= 3 else "4-7" if d <= 7 else "8-14" if d <= 14 else
               "15-30" if d <= 30 else "31-45")
        b[key].append(e)
    return b


def undecided_value(estimates, ref=None):
    live = [e for e in estimates if estimate_state(e, ref) == "presented"]
    if not live:
        return unmeasured("no estimates in a presented state", field="amount", n=0)
    return {"amount": round(sum(e["amount"] for e in live), 2), "n": len(live),
            "oldest_days": max((-(days_until(e["presented_at"], ref) or 0)) for e in live)}


# ---------------------------------------------------------------- deferred work
#
# The technician wrote "capacitor weak, customer declined". That note is worth
# money in August. The rule is the seasonal trigger calendar + a cooling-off
# period so we never re-offer something declined last week.

COMPONENTS = {
    "capacitor":     dict(trade="hvac", reoffer_month=(4, 5), typical=340, urgency="soon"),
    "contactor":     dict(trade="hvac", reoffer_month=(4, 5), typical=290, urgency="soon"),
    "coil_clean":    dict(trade="hvac", reoffer_month=(3, 4), typical=420, urgency="routine"),
    "duct_seal":     dict(trade="hvac", reoffer_month=(9, 10), typical=1250, urgency="routine"),
    "heat_exchanger": dict(trade="hvac", reoffer_month=(9,), typical=2400, urgency="safety"),
    "water_heater_age": dict(trade="plumbing", reoffer_month=(1, 6), typical=2100, urgency="soon"),
    "pressure_valve": dict(trade="plumbing", reoffer_month=(3,), typical=380, urgency="soon"),
    "panel_age":     dict(trade="electrical", reoffer_month=(2,), typical=3200, urgency="routine"),
    "gfci_missing":  dict(trade="electrical", reoffer_month=(5,), typical=260, urgency="safety"),
}
REOFFER_COOLDOWN_DAYS = 120

# Parsing tech notes. Messy human prose in, structured recommendation out — and
# a note that matches nothing is surfaced for a human to read, never dropped.
NOTE_PATTERNS = [
    (r"cap(acitor)?\b.*(weak|low|failing|out of spec|bad)", "capacitor"),
    (r"contactor.*(pitted|burn|weld|bad)", "contactor"),
    (r"coil.*(dirty|clogged|restricted|needs clean)", "coil_clean"),
    (r"duct.*(leak|loose|unsealed|disconnect)", "duct_seal"),
    (r"heat exchanger.*(crack|rust|corros|suspect)", "heat_exchanger"),
    (r"(water heater|wh).*(\b1[2-9]|2\d)\s*(yr|year)|water heater.*(old|rust|corros)", "water_heater_age"),
    (r"(prv|pressure reducing|pressure valve).*(fail|high|bad)", "pressure_valve"),
    (r"(panel|fpe|zinsco|federal pacific).*(old|obsolete|unsafe|recall)", "panel_age"),
    (r"(no gfci|missing gfci|ungrounded).*(kitchen|bath|exterior|garage)?", "gfci_missing"),
]
_NOTE_RE = [(re.compile(p, re.I), c) for p, c in NOTE_PATTERNS]


def parse_note(text):
    """Tech note → [{component, ...}] plus an explicit unparsed remainder."""
    hits = []
    for rx, comp in _NOTE_RE:
        m = rx.search(text or "")
        if m:
            hits.append({"component": comp, "matched": m.group(0).strip(),
                         **{k: v for k, v in COMPONENTS[comp].items()}})
    if not hits:
        return {"recommendations": [], "unparsed": text,
                "_note": "nothing matched — surfaced for a human to read, never discarded"}
    return {"recommendations": hits, "unparsed": None}


def reoffer_due(rec, ref=None):
    """Is this declined recommendation due to be re-offered?"""
    ref = ref or now()
    comp = COMPONENTS.get(rec.get("component"))
    if not comp:
        return False, "unknown component — a human decides"
    if rec.get("state") != "declined":
        return False, f"state is {rec.get('state')}, not declined"
    since = -(days_until(rec.get("declined_at"), ref) or 0)
    if since < REOFFER_COOLDOWN_DAYS:
        return False, f"declined {since}d ago — inside the {REOFFER_COOLDOWN_DAYS}d cooling-off"
    if rec.get("reoffered_at") and -(days_until(rec["reoffered_at"], ref) or 0) < 330:
        return False, "already re-offered within the year"
    if ref.month not in comp["reoffer_month"] and comp["urgency"] != "safety":
        return False, f"out of season — {rec['component']} re-offers in month(s) {comp['reoffer_month']}"
    return True, ("safety item — re-offered out of season on purpose" if comp["urgency"] == "safety"
                  else f"in season (month {ref.month})")


# ---------------------------------------------------------------- the autonomy matrix

MATRIX = Matrix({
    "classify_call":        dict(rung="R3", reason="a wrong guess costs a re-route, not money; the CSR corrects it in one click"),
    "ask_clarifying":       dict(rung="R3", reason="asking the caller a question is free and reversible"),
    "route_emergency":      dict(rung="R3", reason="putting a human on the phone is always the safe direction — the only action here that is safer automatic than gated"),
    "book_standard_slot":   dict(rung="R2", reason="books only into slot classes the owner pre-approved, at the published diagnostic fee; the customer confirms the window themselves"),
    "book_after_hours":     dict(rung="R1", reason="the after-hours premium is a price commitment — a human approves", never_promote=True),
    "quote_price":          dict(rung="R1", reason="any number beyond the published diagnostic fee is a commitment to a homeowner", never_promote=True),
    "draft_estimate_touch": dict(rung="R1", reason="outbound copy in the technician's voice — drafted, then sent by a human until the streak earns R2"),
    "close_estimate_lost":  dict(rung="R2", reason="recording a loss with a reason is bookkeeping, and reopening is one click"),
    "log_deferred_work":    dict(rung="R3", reason="writing a structured recommendation from a note the tech already wrote adds nothing new"),
    "stage_seasonal_campaign": dict(rung="R1", reason="a campaign is a batch of outbound offers — the owner sees the list before it moves"),
    "propose_board":        dict(rung="R0", reason="dispatch proposes; the dispatcher moves the board. This never climbs — the board is a human's judgement about people", never_promote=True),
    "message_custom":       dict(rung="R1", reason="free text to a homeowner carries commitments we cannot take back"),
})
gate = Gate(store, MATRIX)

# What counts as "pipeline-moving": an action that advances a customer's job or
# a dollar. Deliberately EXCLUDES `log_deferred_work` — parsing a note the
# technician already wrote into a ledger row is bookkeeping, and counting nine
# hundred of those would inflate the automation rate to meaninglessness, which
# is the exact move this figure exists to refuse.
MOVING_KINDS = {"classify_call", "book_standard_slot", "book_after_hours", "route_emergency",
                "draft_estimate_touch", "estimate_touch_sent", "close_estimate_lost",
                "stage_seasonal_campaign", "message_custom", "quote_price"}


def automation(days=90):
    # Customer-originated events are excluded by design: a homeowner calling is
    # not the OS automating anything.
    return automation_rate(store.load("events"), MOVING_KINDS, days, exclude_actors=("customer:",))


# ---------------------------------------------------------------- the eval sets

INTAKE_EVAL = Eval(
    "intake triage", "emergency",
    "a missed emergency is the only error in this build that can hurt somebody — "
    "it is reported alone, and false alarms are accepted as the price of that")


def eval_intake(cases=None):
    cases = cases if cases is not None else EVAL_CASES
    return INTAKE_EVAL.run(cases, lambda t: "emergency" if classify(t)["emergency"] else "routine")


EVAL_CASES = [
    {"input": "I smell gas in the basement", "label": "emergency"},
    {"input": "there's a burning smell from the vents", "label": "emergency"},
    {"input": "my CO detector is going off", "label": "emergency"},
    {"input": "water is pouring out from under the water heater", "label": "emergency"},
    {"input": "the outlet sparked when I plugged in the kettle", "label": "emergency"},
    {"input": "sewage is backing up into the tub", "label": "emergency"},
    {"input": "not sure, something smells weird near the furnace", "label": "emergency"},
    {"input": "no heat and we have a newborn", "label": "emergency"},
    {"input": "", "label": "emergency"},
    {"input": "my ac is not cooling, house is 81", "label": "routine"},
    {"input": "kitchen drain is slow again", "label": "routine"},
    {"input": "I'd like a quote for a new system", "label": "routine"},
    {"input": "need a tune up before summer", "label": "routine"},
    {"input": "half the outlets in the living room are dead", "label": "routine"},
    {"input": "ceiling fan install, second floor", "label": "routine"},
    {"input": "toilet keeps running", "label": "routine"},
    {"input": "no hot water since this morning", "label": "routine"},
    {"input": "want to add a subpanel in the garage", "label": "routine"},
]


# ---------------------------------------------------------------- the board reads

def revenue_at_risk(ref=None):
    """The owner's one screen. Every line is counted or it is blank."""
    ref = ref or now()
    calls, ests, recs = store.load("calls"), store.load("estimates"), store.load("recommendations")

    today = [c for c in calls if (parse(c["at"]) or ref).date() == ref.date()]
    unanswered = [c for c in today if c.get("outcome") == "missed"]
    unbooked = [c for c in today if c.get("outcome") == "answered" and not c.get("booked_job")]

    avg = avg_ticket()
    # Valued at the MEDIAN, not the mean. A handful of $18k system replacements
    # drags the mean somewhere no missed service call actually lands, and a
    # number the owner can pull apart in ten seconds costs more than it earns.
    missed_value = (unmeasured(avg["_missing"], field="amount")
                    if avg.get("_missing") else
                    {"amount": round(len(unanswered) * avg["median"], 2),
                     "basis": f"{len(unanswered)} missed × your median ticket "
                              f"(${avg['median']:,.0f}) — the median, because your mean "
                              f"(${avg['amount']:,.0f}) is pulled up by system replacements "
                              f"that a missed service call is not"})

    live = undecided_value(ests, ref)
    due = [e for e in ests if due_touches(e, ref)]

    due_recs = [r for r in recs if reoffer_due(r, ref)[0]]
    rec_value = (round(sum(COMPONENTS[r["component"]]["typical"] for r in due_recs), 2)
                 if due_recs else 0)

    return {
        "generated": iso(ref),
        "calls_today": {"total": len(today), "missed": len(unanswered),
                        "answered_unbooked": len(unbooked)},
        "missed_call_value": missed_value,
        "undecided_estimates": live,
        "estimates_needing_a_touch": len(due),
        "deferred_due_now": {"n": len(due_recs), "amount": rec_value,
                             "basis": "each valued at the price book's typical amount for that component"},
        "automation": automation(),
    }


def avg_ticket(days=180):
    jobs = [j for j in store.load("jobs") if j.get("invoiced")
            and (parse(j.get("completed_at")) or now()) >= now() - timedelta(days=days)]
    if len(jobs) < 20:
        return unmeasured(f"only {len(jobs)} invoiced jobs in {days} days; need 20 before an average means anything",
                          field="amount", n=len(jobs))
    amts = [j["invoiced"] for j in jobs]
    return {"amount": round(sum(amts) / len(amts), 2), "median": round(median(amts), 2),
            "n": len(amts), "window_days": days}


def recovered_this_week(ref=None):
    """What the OS actually put back on the board — counted from events, never
    asserted. A recovered dollar is one whose event log shows an agent touch
    before the win."""
    ref = ref or now()
    since = ref - timedelta(days=7)
    ests = {e["id"]: e for e in store.load("estimates")}
    wins = [e for e in ests.values() if e.get("state") == "won"
            and (parse(e.get("decided_at")) or now()) >= since]
    touched, untouched = [], []
    for e in wins:
        evs = store.events(subject=e["id"])
        agent_touch = any(v["actor"].startswith("agent:") and v["kind"] in
                          ("draft_estimate_touch", "estimate_touch_sent") for v in evs)
        (touched if agent_touch else untouched).append(e)
    if not wins:
        return unmeasured("no estimates were won in the last 7 days", field="amount",
                          attributable=0, unattributable=0)
    return {"amount": round(sum(e["amount"] for e in touched), 2),
            "attributable": len(touched), "unattributable": len(untouched),
            "basis": "only wins whose event log shows an agent touch before the decision; "
                     "the rest are the shop's own work and are not claimed"}


# ---------------------------------------------------------------- the ROI model

ROI = (Roi("What the three leaks are worth here")
       .line("Missed-call recovery", "revenue",
             "missed calls/wk × booked% × avg ticket × 52",
             ["missed_calls_wk", "recovered_book_rate", "avg_ticket"],
             lambda g: g["missed_calls_wk"] * g["recovered_book_rate"] * g["avg_ticket"] * 52,
             note="missed calls are counted from your phone log; the booking rate is yours to set",
             assumption="booked% is the share of recovered calls that become a booked job")
       .line("Estimate recovery", "revenue",
             "open estimate value × incremental close%",
             ["open_estimate_value", "incremental_close_rate"],
             lambda g: g["open_estimate_value"] * g["incremental_close_rate"],
             note="open estimate value is counted from your own presented-and-undecided estimates",
             assumption="incremental close% is the lift over what you close today with no follow-up")
       .line("Deferred work re-offered", "revenue",
             "logged recommendations × accept% × typical job",
             ["deferred_count", "reoffer_accept_rate", "deferred_avg"],
             lambda g: g["deferred_count"] * g["reoffer_accept_rate"] * g["deferred_avg"],
             assumption="accept% on a seasonal re-offer of work a technician already recommended; "
                        "the count is every declined recommendation on file, because each one gets "
                        "exactly one re-offer window per year — not all of them this month")
       .line("Dispatch + follow-up time", "time_saved",
             "hours/wk × 52 × loaded rate",
             ["admin_hours_wk", "loaded_rate"],
             lambda g: g["admin_hours_wk"] * 52 * g["loaded_rate"],
             note="staff time, reported apart from revenue — never added into the headline"))


def roi(given=None):
    """Recorded facts come from the store; assumptions come from the operator.
    A rate the operator has not given us leaves its line blank."""
    cfg = store.load("config")
    recorded = {}
    a = avg_ticket()
    if not a.get("_missing"):
        # the median is the default; the operator can overwrite it with their own
        recorded["avg_ticket"] = a["median"]
    calls = store.load("calls")
    wk = [c for c in calls if (parse(c["at"]) or now()) >= now() - timedelta(days=7)]
    if wk:
        recorded["missed_calls_wk"] = sum(1 for c in wk if c.get("outcome") == "missed")
    live = undecided_value(store.load("estimates"))
    if not live.get("_missing"):
        recorded["open_estimate_value"] = live["amount"]
    recs = [r for r in store.load("recommendations") if r.get("state") == "declined"]
    if recs:
        recorded["deferred_count"] = len(recs)
        recorded["deferred_avg"] = round(
            sum(COMPONENTS[r["component"]]["typical"] for r in recs) / len(recs), 2)
    merged = dict(recorded)
    merged.update({k: v for k, v in (cfg.get("roi_inputs") or {}).items() if v not in (None, "")})
    merged.update({k: v for k, v in (given or {}).items() if v not in (None, "")})
    out = ROI.render(merged)
    out["recorded"] = recorded
    out["operator_supplied"] = {k: v for k, v in merged.items() if k not in recorded}
    return out
