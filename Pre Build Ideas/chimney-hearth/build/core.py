#!/usr/bin/env python3
"""Flue OS — domain core (chimney sweeps & hearth services).

Rules live here: CO/smoke-first triage with the evacuate script, the
burn-verdict rule (the recorded inspection speaks or nothing does), the
hazard-verbatim rule (stage-3 / blockage / CO language is never softened),
the chimney-fire aftermath rule (Level 3 per the recorded rule), the
due-for-annual recall ladder (bounded, seasonal-aware), the season scheduler,
and the matrix.

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

TABLES = ("config", "households", "techs", "messages", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="FLUEOS_DATA_ROOT")

EVACUATE_SCRIPT = ("CO / SMOKE PROTOCOL, verbatim: get everyone out of the house NOW, pets "
                   "included — do not stop to open windows, do not hunt for the source. From "
                   "outside, call 911 and let them clear the house. Call us back after, from "
                   "outside — the flue gets inspected before the next fire is lit. An active CO "
                   "or smoke event is never a booking; nothing about it is scheduled by this "
                   "message.")

# ---------------------------------------------------------------- triage

CO_SMOKE = (
    r"\bcarbon monoxide\b",
    r"\bco (alarms?|detectors?|monitors?)\b",
    r"\b(alarms?|detectors?)\b.*\bco\b",
    r"\bco\b.*\b(going off|went off|beeping|alarming)\b",
    r"\bsmoke\b.*\b(filling|pouring|backing up|rolling|into the (house|room|basement)|in the (house|room|basement|living room))\b",
    r"\b(filling|full of|fills?) (the )?(house|room|living room)? ?with smoke\b",
    r"\b(house|room|living room|basement)\b.*\b(full of|filling with) smoke\b",
    r"\b(dizzy|light-?headed|nauseous|headaches?)\b.*\b(fireplace|furnace|stove|fire|flue)\b",
)
FIRE_AFTERMATH = (
    r"\bchimney fires?\b",
    r"\bflames?\b.*\b(chimney|flue)\b",
    r"\b(chimney|flue)\b.*\b(caught fire|on fire|glowing|roaring)\b",
    r"\bcreosote\b.*\b(caught|fire|burn)\w*",
    r"\bfire (department|dept|trucks?|fighters?)\b.*\b(chimney|flue|fireplace)\b",
)
SAFE_TO_BURN = (
    r"\bsafe to (burn|use|light)\b",
    r"\b(safe|okay|ok)\b.*\b(fireplace|wood ?stove|insert|flue|chimney|fire)\b",
    r"\b(fireplace|wood ?stove|insert|chimney)\b.*\b(safe|okay|ok)\b",
    r"\bcan (we|i) (light|use|start)\b.*\b(fire|fireplace|stove|insert)\b",
    r"\b(light|start) a fire\b",
)
BOOKING = (
    r"\b(schedule|book|set up|appointment|reschedule)\b.*\b(sweep|sweeping|cleaning|inspection|annual|chimney)\b",
    r"\b(sweeps?|cleanings?|inspections?|annuals?)\b.*\b(schedule|book|appointment|slot|when can|available)\b",
    r"\b(need|due for|time for)\b.*\b(annual|sweep|cleaning|inspection)\b",
    r"\b(when can|any (openings?|availability)|fit .{0,12}in)\b.*\b(sweeps?|cleanings?|inspections?|annuals?)\b",
    r"\b(sweeps?|cleanings?|inspections?|annuals?)\b.*\b(when can|fit .{0,12}in|openings?|availability)\b",
)
QUOTE = (
    r"\b(quotes?|estimates?|price|pricing|cost|how much)\b.*\b(caps?|liners?|reline|reli(n|m)ing|crowns?|repairs?|dampers?|sweeps?|cleanings?|chase|masonry|tuckpoint|flue|chimney)\w*",
    r"\b(caps?|liners?|reline|crowns?|repairs?|dampers?|chimney|flue)\b.*\b(quotes?|estimates?|price|pricing|cost)\b",
)


def read_message(text):
    """co_smoke_event | chimney_fire_aftermath | safe_to_burn_ask | booking |
    quote | human. The CO/smoke event reads FIRST — an active CO event is 911
    and the evacuate script, never a booking."""
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty message — a person reads it"}
    for rx in CO_SMOKE:
        if re.search(rx, t):
            return {"label": "co_smoke_event", "script": EVACUATE_SCRIPT,
                    "why": "an active CO / smoke event — the evacuate script verbatim, 911 first; "
                           "nothing about it becomes a booking"}
    for rx in FIRE_AFTERMATH:
        if re.search(rx, t):
            return {"label": "chimney_fire_aftermath",
                    "why": "chimney-fire aftermath — the recorded rule requires a Level 3 "
                           "inspection before the next fire; a sweep is not the response"}
    for rx in SAFE_TO_BURN:
        if re.search(rx, t):
            return {"label": "safe_to_burn_ask",
                    "why": "the safe-to-burn question — the recorded inspection speaks (level, "
                           "date, findings) or the answer is book the inspection"}
    for rx in BOOKING:
        if re.search(rx, t):
            return {"label": "booking", "why": "a booking ask — drafted against the season book"}
    for rx in QUOTE:
        if re.search(rx, t):
            return {"label": "quote", "why": "a quote ask — the recorded price book answers; "
                                             "structural work gets eyes on it first"}
    return {"label": "human", "why": "no clean signal — a person reads it"}


# ---------------------------------------------------------------- the burn verdict

BURN_CURRENT_DAYS = 365


def latest_inspection(hh):
    ins = sorted((hh or {}).get("inspections") or [], key=lambda i: i.get("date") or "")
    return ins[-1] if ins else None


def burn_verdict(hh, ref=None):
    """The only honest answers to 'safe to burn': cite the recorded inspection
    (level 1/2/3 + date + findings), or say 'book the inspection'. Software
    never declares safe beyond the record — that is the R0."""
    ref = ref or now()
    insp = latest_inspection(hh)
    if not insp or not insp.get("level") or not insp.get("date"):
        return {"verdict": "book_the_inspection",
                "why": "no recorded inspection on file — 'safe to burn' without the record is a "
                       "house fire with a chat log; the only honest answer is book the inspection"}
    age = (ref - (parse(insp["date"]) or ref)).days
    cite = {"level": insp["level"], "date": insp["date"], "tech": insp.get("tech"),
            "age_days": age, "findings": [f.get("text") for f in insp.get("findings") or []]}
    if age > BURN_CURRENT_DAYS:
        return {"verdict": "book_the_inspection", "recorded": cite,
                "why": f"the last recorded inspection is {age} days old — past the annual "
                       f"standard, the record is stale; the answer is book the inspection"}
    hazards = [f.get("text") for f in insp.get("findings") or [] if f.get("hazard")]
    if hazards:
        return {"verdict": "hazard_on_record", "citation": cite, "hazards": hazards,
                "why": "the recorded inspection carries a hazard finding — it is cited verbatim, "
                       "never softened, and the answer is remediation before the next fire"}
    return {"verdict": "record_cited", "citation": cite,
            "why": "the recorded inspection is the answer — level, date, findings, cited; "
                   "nothing beyond the record is declared"}


# ---------------------------------------------------------------- the hazard-verbatim rule

FORBIDDEN_SOFTENERS = ("could use a cleaning", "a little buildup", "a bit of buildup",
                       "minor buildup", "nothing to worry about", "probably fine",
                       "should be fine", "just some soot", "some light creosote")


def soften_ok(text):
    t = (text or "").lower()
    hits = [w for w in FORBIDDEN_SOFTENERS if w in t]
    if hits:
        return False, f"hazard-softening language forbidden: {', '.join(hits)}"
    return True, "ok"


def hazard_verbatim_ok(draft, findings):
    """Every hazard finding's recorded text must appear in the draft VERBATIM.
    Rephrasing a stage-3 / blockage / CO finding is the R0 this rule enforces."""
    missing = [f.get("text") for f in (findings or [])
               if f.get("hazard") and (f.get("text") or "") not in (draft or "")]
    if missing:
        return False, "hazard finding rephrased or dropped — forbidden: " + " | ".join(missing)
    return True, "every hazard finding survives verbatim"


# ---------------------------------------------------------------- chimney-fire aftermath

DEFAULT_LEVEL3_RULE = {
    "_source": ("DEFAULT recorded rule, simplified from NFPA 211's inspection levels — after a "
                "chimney fire or any event likely to have damaged the flue, a Level 3 inspection "
                "before further use. Replace with the operator's adopted edition text before "
                "go-live."),
    "required_level": 3,
}


def aftermath_rule():
    return store.load("config").get("level3_rule") or DEFAULT_LEVEL3_RULE


# ---------------------------------------------------------------- the household book

def service_age_days(hh, ref=None):
    """Days since the last recorded service (sweep or inspection). No record
    at all returns None — UNKNOWN, never 'recent'."""
    ref = ref or now()
    dates = []
    if hh.get("last_sweep"):
        dates.append(parse(hh["last_sweep"]))
    li = latest_inspection(hh)
    if li and li.get("date"):
        dates.append(parse(li["date"]))
    dates = [d for d in dates if d]
    if not dates:
        return None
    return (ref - max(dates)).days


def due_board(ref=None):
    """The revenue engine, counted: households a year or more past their last
    recorded service. No-record households are counted separately — a recall
    that cannot cite the household's own record is spam, not revenue."""
    ref = ref or now()
    cfg = store.load("config")
    rows, no_record = [], 0
    for hh in store.load("households"):
        if hh.get("demo_tag"):
            continue
        age = service_age_days(hh, ref)
        if age is None:
            no_record += 1
            continue
        if age >= 365:
            rows.append({"household": hh["id"], "name": hh.get("name"),
                         "days_since_service": age,
                         "touches": len(hh.get("recall_touches") or [])})
    rows.sort(key=lambda r: -r["days_since_service"])
    ticket = cfg.get("avg_ticket")
    out = {"rows": rows[:200], "due": len(rows), "no_record": no_record,
           "value": round(len(rows) * ticket, 2) if ticket else None}
    if ticket is None:
        out["value_missing"] = ("no recorded average ticket — the due book is counted; "
                                "its value is not invented")
    return out


def hazard_households():
    """Households whose latest recorded inspection carries a hazard finding."""
    out = []
    for hh in store.load("households"):
        if hh.get("demo_tag"):
            continue
        li = latest_inspection(hh)
        if li and any(f.get("hazard") for f in li.get("findings") or []):
            out.append({"household": hh["id"], "name": hh.get("name"),
                        "hazards": [f["text"] for f in li["findings"] if f.get("hazard")]})
    return out


# ---------------------------------------------------------------- the recall ladder

RECALL_MAX_TOUCHES = 3
RECALL_COOLDOWN_DAYS = 21
PEAK_MONTHS = (9, 10, 11, 12, 1)


def recall_plan(hh, ref=None):
    ref = ref or now()
    if hh.get("demo_tag"):
        return {"action": "none", "why": "demo fixture — never recalled"}
    age = service_age_days(hh, ref)
    if age is None:
        return {"action": "none", "why": "no recorded service date — a recall that cannot cite "
                                         "the household's own record is spam"}
    if age < 365:
        return {"action": "none", "why": "not due — the annual is not yet a year out"}
    touches = hh.get("recall_touches") or []
    if len(touches) >= RECALL_MAX_TOUCHES:
        return {"action": "none",
                "why": f"ladder exhausted at {RECALL_MAX_TOUCHES} — silence is an answer"}
    last = parse(touches[-1]["at"]) if touches else None
    if last and (ref - last).days < RECALL_COOLDOWN_DAYS:
        return {"action": "none", "why": f"inside the {RECALL_COOLDOWN_DAYS}-day cooldown"}
    return {"action": "draft_recall", "why": f"touch {len(touches)+1} of {RECALL_MAX_TOUCHES}",
            "age_days": age}


# ---------------------------------------------------------------- the season scheduler

WORKDAYS_PER_MONTH = 22


def month_capacity():
    cfg = store.load("config")
    techs = store.load("techs")
    jobs = cfg.get("jobs_per_tech_day")
    if not techs or not jobs:
        return None
    return len(techs) * jobs * WORKDAYS_PER_MONTH


def february_offer():
    """The overflow offer comes from the RECORDED off-season rate — a discount
    nobody recorded is a discount nobody offered."""
    d = store.load("config").get("off_season_discount")
    if not d:
        return {"slot": "February", "discount_pct": None,
                "note": "no recorded off-season rate — the February slot is offered; "
                        "a discount is not invented"}
    return {"slot": "February", "discount_pct": d.get("pct"), "source": d.get("_source")}


def season_board(ref=None):
    """Capacity by tech-day vs the due book. In peak months, overflow is
    offered February — the recorded off-season rate — instead of silently
    lost."""
    ref = ref or now()
    cap = month_capacity()
    db = due_board(ref)
    if cap is None:
        return unmeasured("no techs or per-tech-day capacity recorded — a season plan without "
                          "capacity is a guess", field="month_capacity",
                          due_book=db["due"], peak=ref.month in PEAK_MONTHS, offer=None)
    overflow = max(0, db["due"] - cap)
    peak = ref.month in PEAK_MONTHS
    return {"month_capacity": cap, "due_book": db["due"], "overflow": overflow, "peak": peak,
            "offer": february_offer() if (peak and overflow) else None,
            "note": "capacity = techs × jobs per tech-day × workdays; the due book is counted"}


# ---------------------------------------------------------------- the report

def report_draft(hh):
    """The inspection report assembles from RECORDED findings only. No
    inspection or no findings → refused, never padded. Hazard text verbatim."""
    if not hh:
        return {"refused": "no such household — a report assembles from a record, not a name"}
    insp = latest_inspection(hh)
    if not insp:
        return {"refused": "cannot draft a report — no recorded inspection for this household; "
                           "a report assembles from the record, never from memory"}
    if not insp.get("findings"):
        return {"refused": "cannot draft a report — the recorded inspection has no findings on "
                           "file; an empty record produces no prose"}
    lines = []
    for i, f in enumerate(insp["findings"], 1):
        photo = f" [photo {f['photo']} referenced]" if f.get("photo") else ""
        flag = " — HAZARD" if f.get("hazard") else ""
        lines.append(f"  {i}. {f.get('text')}{photo}{flag}")
    body = (f"INSPECTION REPORT — DRAFT (assembled from recorded findings only)\n"
            f"Household: {hh.get('name')}, {hh.get('address', '')}\n"
            f"Inspection: Level {insp.get('level')} — {str(insp.get('date'))[:10]} — "
            f"tech {insp.get('tech')}\n"
            f"Liner: {hh.get('liner', 'not recorded')} · Cap: {hh.get('cap', 'not recorded')}\n"
            f"Findings, verbatim from the record:\n" + "\n".join(lines) + "\n"
            f"Every recorded finding appears above, unedited. A human reviews and sends.")
    okv, whyv = hazard_verbatim_ok(body, insp["findings"])
    assert okv, whyv  # structural: the draft cannot ship with a softened hazard
    oks, whys = soften_ok(body)
    assert oks, whys
    return {"body": body, "findings": insp["findings"], "level": insp.get("level")}


# ---------------------------------------------------------------- recovered, counted

def recovered_this_week(ref=None):
    """Counted: households swept, recalls sent by humans, CO events escalated,
    inside 7 days."""
    ref = ref or now()
    swept = [hh for hh in store.load("households")
             if not hh.get("demo_tag") and hh.get("last_sweep")
             and (ref - (parse(hh["last_sweep"]) or ref)).days <= 7]
    ticket = store.load("config").get("avg_ticket")
    recalls = sum(1 for e in store.events(kind="draft_recall")
                  if str(e.get("actor", "")).startswith("human:")
                  and (ref - (parse(e.get("at")) or ref)).days <= 7)
    co = sum(1 for e in store.events(kind="escalate_co_event")
             if (ref - (parse(e.get("at")) or ref)).days <= 7)
    return {"households_swept": len(swept),
            "sweep_revenue": round(len(swept) * ticket, 2) if ticket else None,
            "recalls_sent": recalls, "co_events_escalated": co,
            "note": "counted from the household book and the event log — never asserted"}


# ---------------------------------------------------------------- eval

triage_eval = Eval("message triage",
                   costly_label="co_smoke_event",
                   costly_note=("A CARBON MONOXIDE EVENT TRIAGED AS A BOOKING IS A FAMILY "
                                "SLEEPING IN THE HOUSE THAT KILLS THEM. The evacuate script IS "
                                "the product. Over-routing a booking ask costs a phone call."))

EVAL_CASES = [
    {"input": "the carbon monoxide alarm keeps going off when the furnace runs",
     "label": "co_smoke_event"},
    {"input": "smoke filling the living room when we light a fire", "label": "co_smoke_event"},
    {"input": "our co detector went off twice last night", "label": "co_smoke_event"},
    {"input": "smoke is pouring into the house from the fireplace", "label": "co_smoke_event"},
    {"input": "we had a chimney fire last night, the fire department came",
     "label": "chimney_fire_aftermath"},
    {"input": "flames were shooting out of the chimney top yesterday",
     "label": "chimney_fire_aftermath"},
    {"input": "is it safe to use the fireplace this winter", "label": "safe_to_burn_ask"},
    {"input": "safe to burn after last year's sweep", "label": "safe_to_burn_ask"},
    {"input": "can we light a fire before the holidays", "label": "safe_to_burn_ask"},
    {"input": "need to schedule our annual sweep", "label": "booking"},
    {"input": "book a chimney cleaning before october please", "label": "booking"},
    {"input": "how much for a new chimney cap", "label": "quote"},
    {"input": "price to reline the flue", "label": "quote"},
    {"input": "", "label": "human"},
    {"input": "do you sell firewood", "label": "human"},
]


def run_eval():
    return triage_eval.run(EVAL_CASES, lambda t: read_message(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_message":         {"rung": "R3", "reason": "routing only; the CO/smoke event reads first"},
    "escalate_co_event":    {"rung": "R2", "reason": "the evacuate script and the 911 call cannot wait for a click"},
    "declare_safe_to_burn": {"rung": "R0", "reason": "the recorded inspection speaks — level, date, findings — or the answer is book the inspection; software never declares beyond the record", "never_promote": True},
    "soften_hazard_finding": {"rung": "R0", "reason": "stage-3 / blockage / CO language survives verbatim into every draft — softened findings are how house fires get scheduled", "never_promote": True},
    "co_event_as_booking":  {"rung": "R0", "reason": "an active CO or smoke event is 911 and the evacuate script — never a booking", "never_promote": True},
    "sweep_after_chimney_fire": {"rung": "R0", "reason": "after a chimney fire the recorded rule requires a Level 3 inspection — a sweep is not the response", "never_promote": True},
    "draft_burn_reply":     {"rung": "R1", "reason": "outward reply — a human sends, the record cited"},
    "draft_recall":         {"rung": "R1", "reason": "outward reminder — a human sends; bounded, cooled-down, seasonal-aware"},
    "draft_booking_reply":  {"rung": "R1", "reason": "outward reply — a human sends, against the season book"},
    "draft_quote_reply":    {"rung": "R1", "reason": "outward money figure — a human sends, from the recorded price book"},
    "draft_report":         {"rung": "R1", "reason": "the report assembles from recorded findings only; a human reviews and sends"},
    "season_alert":         {"rung": "R2", "reason": "an internal capacity alert; the arithmetic is the point"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Flue OS — what it computes to")
        .line("The due book, re-called", "revenue",
              "due-for-annual households × recorded ticket × your booking rate",
              ["due_book", "avg_ticket", "booking_rate"],
              lambda g: float(g["due_book"]) * float(g["avg_ticket"]) * float(g["booking_rate"]),
              note="the due book is counted and the ticket is recorded; the booking rate is your call")
        .line("October overflow captured in February", "revenue",
              "counted overflow × recorded ticket × your off-season capture",
              ["october_overflow", "avg_ticket", "offseason_capture"],
              lambda g: float(g["october_overflow"]) * float(g["avg_ticket"]) * float(g["offseason_capture"]),
              note="the overflow is counted against tech-day capacity — the season smoothed, not lost")
        .line("Office hours", "time_saved", "hrs/wk × 52 × rate",
              ["office_hours_wk", "office_rate"],
              lambda g: float(g["office_hours_wk"]) * 52 * float(g["office_rate"]))
        .line("The house-fire file", "scenario",
              "you decide what the cited-record answer is worth",
              ["housefire_value"], lambda g: float(g["housefire_value"]),
              assumption="never a saving — the house fire that didn't happen is not our number to model"))


def roi(given):
    rec = {}
    db = due_board()
    rec["due_book"] = db["due"]
    cfg = store.load("config")
    if cfg.get("avg_ticket") is not None:
        rec["avg_ticket"] = cfg["avg_ticket"]
    cap = month_capacity()
    if cap is not None:
        rec["october_overflow"] = max(0, db["due"] - cap)
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("read_message", "escalate_co_event", "draft_burn_reply", "draft_recall",
          "draft_booking_reply", "draft_quote_reply", "draft_report")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("homeowner:",))
