#!/usr/bin/env python3
"""Well OS — domain core (well drilling & water treatment).

Rules live here: contamination-first triage, the lab rule (a potability verdict
cites a recorded lab report or does not exist), the consumable clocks that never
claim "protected" past their date, the measure-then-price quote gate, the
per-county permit clocks as DATE ALERTS, and the matrix.

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

TABLES = ("config", "customers", "wells", "systems", "jobs", "lab_reports",
          "messages", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="WELLOS_DATA_ROOT")

CONTAMINATION_PROTOCOL = ("Logged verbatim with a timestamp. A sampling visit goes to the top "
                          "of the route and a human calls back the same day. Software never "
                          "says the water is fine — the lab does, by report, or nobody does.")

# ---------------------------------------------------------------- the soothe rule

FORBIDDEN_SOOTHING = ("probably fine", "nothing to worry about", "no need to worry",
                      "perfectly safe", "should be fine", "totally normal", "harmless",
                      "don't worry")


def soothe_ok(text):
    t = (text or "").lower()
    hits = [w for w in FORBIDDEN_SOOTHING if w in t]
    if hits:
        return False, f"no soothing a contamination worry — forbidden language: {', '.join(hits)}"
    return True, "ok"


# ---------------------------------------------------------------- triage

CONTAMINATION = (
    r"\b(smells?|smelling|odor|stinks?)\b.*\b(rotten|sulfur|sulphur|eggs?|sewage|gasoline|"
    r"chemicals?|weird|off)\b",
    r"\b(tastes?|tasting)\b.*\b(metallic|metal|rusty?|salty|chemical|bitter|off|funny|weird)\b",
    r"\b(brown|black|orange|yellow|cloudy|murky|oily|discolou?red)\b.*\bwater\b",
    r"\bwater\b.*\b(brown|black|orange|cloudy|murky|oily|discolou?red|smells?|stinks?|tastes?)\b",
    r"\b(sick|ill|vomit\w*|diarrhea|nausea\w*|stomach)\b.*\b(water|drinking|well|tap)\b|"
    r"\b(water|drinking|well|tap)\b.*\b(sick|ill|vomit\w*|diarrhea|nausea\w*)\b",
    r"\bwater\b.*\bsafe\b|\bsafe\b.*\b(water|to drink)\b",
    r"\b(grit|sand|sediment|particles?)\b.*\b(water|tap|faucet)\b|"
    r"\bwater\b.*\b(grit|sand|sediment|particles?)\b",
)
NO_WATER = (
    r"\bno water\b|\bout of water\b|\bwater( is|'s)? (gone|out|stopped)\b",
    r"\b(pump|well)\b.*\b(stopped|quit|died|dead|won'?t (run|start|turn on)|"
    r"not (working|running))\b",
    r"\b(faucets?|taps?|spigots?)\b.*\b(dry|sputter\w*|nothing|just air)\b",
    r"\b(lost|losing|no)\b.*\bpressure\b",
    r"\bhouse\b.*\b(dry|no water)\b|\bdry\b.*\b(house|faucets?|taps?)\b",
)
SERVICE_DUE = (
    r"\b(filters?|uv|lamp|softener|salt|media|cartridge)\b.*\b(due|change\w*|replace\w*|"
    r"service\w*|swap\w*|maintenance)\b",
    r"\b(due|change|changing|replace|replacing|service|servicing|swap|swapping|time)\b.*"
    r"\b(filters?|uv lamp|lamp|softener|media|cartridge)\b",
    r"\bannual\b.*\b(service|filter|maintenance)\b",
)
QUOTE = (
    r"\b(quote|estimate|price|cost|how much)\b.*\b(well|drill\w*|pump|softener|treatment|"
    r"system|deepen\w*|install\w*)\b",
    r"\b(well|drill\w*|pump|softener|treatment)\b.*\b(quote|estimate|price|cost)\b",
)
STATUS = (
    r"\b(status|update|progress|where are we|any word|when)\b.*\b(permit|drill\w*|rig|job|"
    r"pump test|water test|state report|install\w*)\b",
    r"\b(permit|drill\w*|rig|pump test|state report)\b.*\b(status|update|approved|filed|"
    r"scheduled|when|coming)\b",
)


def read_message(text):
    """contamination | no_water | service_due | quote | status | human. The
    contamination worry reads FIRST — health rides on it; everything else can
    wait a beat."""
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty message — a person reads it"}
    for rx in CONTAMINATION:
        if re.search(rx, t):
            return {"label": "contamination", "protocol": CONTAMINATION_PROTOCOL,
                    "why": "water-quality worry — recorded verbatim, never soothed; the lab "
                           "answers potability, software never does"}
    for rx in NO_WATER:
        if re.search(rx, t):
            return {"label": "no_water",
                    "why": "a dry house is a P1 — the record starts now and a human "
                           "dispatches today"}
    for rx in SERVICE_DUE:
        if re.search(rx, t):
            return {"label": "service_due",
                    "why": "consumable clock question — answered from the system's own "
                           "recorded intervals"}
    for rx in QUOTE:
        if re.search(rx, t):
            return {"label": "quote",
                    "why": "quote ask — we measure, then we price; the well log does the "
                           "talking"}
    for rx in STATUS:
        if re.search(rx, t):
            return {"label": "status", "why": "job status — answered from the pipeline record"}
    return {"label": "human", "why": "no clean signal — a person reads it"}


# ---------------------------------------------------------------- the lab rule

def water_safety(well_id):
    """The one answer software may give about potability: a recorded lab report,
    cited by id + date + result, verbatim. No report → 'we don't know yet, the
    lab does.' Nothing in between exists."""
    reports = sorted((r for r in store.load("lab_reports") if r.get("well_id") == well_id),
                     key=lambda r: r.get("sampled_at") or "")
    if not reports:
        return {"refused": ("we don't know yet, the lab does — no recorded lab report for "
                            "this well. A sample goes out; the verdict arrives as a report "
                            "id, a date, and a result, or it does not exist.")}
    latest = reports[-1]
    if not latest.get("result"):
        return {"refused": (f"we don't know yet, the lab does — report {latest.get('report_no')} "
                            f"is at the lab, result pending. Until it lands, no potability "
                            f"statement leaves this system."), "pending": latest.get("report_no")}
    return {"report": latest,
            "answer": (f"Lab report {latest['report_no']} ({latest.get('lab')}), sampled "
                       f"{str(latest.get('sampled_at'))[:10]}: \"{latest['result']}\" — that is "
                       f"the lab's answer, as of that sample date. This system quotes it; it "
                       f"does not add to it.")}


# ---------------------------------------------------------------- the well log + quote gate

WELL_LOG_FIELDS = ("depth_ft", "casing_ft", "yield_gpm", "static_level_ft")


def quote_basis(well):
    """A quote cites the recorded well log or it does not draft. We measure,
    then we price."""
    if not well:
        return {"refused": "cannot quote — no well on record. We measure, then we price: a "
                           "site visit records depth, casing, yield, and static level, and "
                           "the quote cites them."}
    missing = [f for f in WELL_LOG_FIELDS if well.get(f) in (None, "")]
    if missing:
        return {"refused": (f"cannot quote — no recorded well log for this well (missing: "
                            f"{', '.join(missing)}). We measure, then we price: a camera-and-"
                            f"gauge visit records depth, casing, yield, and static level, and "
                            f"the quote cites them. A number without the log is a guess in "
                            f"writing.")}
    return {"basis": (f"depth {well['depth_ft']} ft · casing {well['casing_ft']} ft · yield "
                      f"{well['yield_gpm']} gpm · static level {well['static_level_ft']} ft — "
                      f"the recorded well log, measured {str(well.get('logged_at'))[:10]}"),
            "log": {k: well[k] for k in WELL_LOG_FIELDS}}


# ---------------------------------------------------------------- consumable clocks

DUE_SOON_DAYS = 14


def component_clock(comp, ref=None):
    ref = ref or now()
    last = parse(comp.get("last_service_at"))
    if not last:
        return unmeasured("no service on record — the clock never started; due status "
                          "cannot be stated", field="days_over")
    due_at = last + timedelta(days=int(comp.get("interval_days", 365)))
    return {"days_over": (ref - due_at).days, "due_at": iso(due_at),
            "last_service_at": comp.get("last_service_at")}


def due_board(ref=None):
    """Every component at or near its recorded clock — counted, with the
    unmeasured ones listed as unmeasured, never assumed current."""
    ref = ref or now()
    rows, unknown = [], 0
    for s in store.load("systems"):
        if s.get("demo_tag"):
            continue
        for comp in s.get("components") or []:
            ck = component_clock(comp, ref)
            if "_missing" in ck:
                unknown += 1
                continue
            if ck["days_over"] < -DUE_SOON_DAYS:
                continue
            rows.append({"system": s["id"], "customer": s.get("customer_name"),
                         "component": comp.get("kind"), "days_over": ck["days_over"],
                         "ticket": comp.get("ticket", 0),
                         "status": "OVERDUE" if ck["days_over"] > 0 else "due soon"})
    rows.sort(key=lambda r: -r["days_over"])
    overdue = [r for r in rows if r["days_over"] > 0]
    return {"rows": rows, "due_value": round(sum(r["ticket"] for r in rows), 2),
            "overdue_count": len(overdue),
            "overdue_value": round(sum(r["ticket"] for r in overdue), 2),
            "unknown_clocks": unknown,
            "note": "counted from the recorded intervals; a clock nobody recorded reads "
                    "unmeasured, never current"}


def protection_status(system, ref=None):
    """Per-component honesty: in-clock cites its dates; past-clock is never
    'protected'; no recorded service is unmeasured, not assumed fine."""
    ref = ref or now()
    rows = []
    for comp in system.get("components") or []:
        ck = component_clock(comp, ref)
        if "_missing" in ck:
            rows.append({"component": comp.get("kind"), "protected": None,
                         "_missing": ck["_missing"]})
            continue
        if ck["days_over"] > 0:
            rows.append({"component": comp.get("kind"), "protected": False,
                         "why": (f"{ck['days_over']} days past the recorded clock — a "
                                 f"{comp.get('kind')} past its interval is not doing what "
                                 f"it is there for")})
        else:
            rows.append({"component": comp.get("kind"), "protected": True,
                         "why": (f"inside the recorded clock — last serviced "
                                 f"{str(ck['last_service_at'])[:10]}, due "
                                 f"{ck['due_at'][:10]}")})
    return {"rows": rows}


def can_claim_protected(system, ref=None):
    st = protection_status(system, ref)
    overdue = [r for r in st["rows"] if r.get("protected") is False]
    unknown = [r for r in st["rows"] if r.get("protected") is None]
    if overdue:
        r = overdue[0]
        return False, (f"an overdue {r['component']} is never 'still fine' — {r['why']}. A UV "
                       f"lamp past its clock still glows; it just stops sterilizing. "
                       f"'Protected' is a claim the clocks make, and these clocks say no.")
    if unknown:
        return False, (f"cannot claim protection — {unknown[0]['component']} has "
                       f"{unknown[0]['_missing']}")
    return True, ("every consumable clock is inside its recorded interval — 'protected' here "
                  "means the clocks, cited by date, not a promise")


# ---------------------------------------------------------------- the reminder ladder

LADDER_MAX_TOUCHES = 3
LADDER_COOLDOWN_DAYS = 14


def service_plan(system, ref=None):
    ref = ref or now()
    overdue = [c for c in system.get("components") or []
               if (component_clock(c, ref).get("days_over") or 0) > 0]
    if not overdue:
        return {"action": "none", "why": "all recorded clocks current — nothing to say"}
    touches = system.get("reminder_touches") or []
    if len(touches) >= LADDER_MAX_TOUCHES:
        return {"action": "none", "why": f"ladder exhausted at {LADDER_MAX_TOUCHES} — silence "
                                         f"is an answer; the clock stays on the board"}
    last = parse(touches[-1]["at"]) if touches else None
    if last and (ref - last).days < LADDER_COOLDOWN_DAYS:
        return {"action": "none", "why": f"inside the {LADDER_COOLDOWN_DAYS}-day cooldown"}
    return {"action": "draft_reminder", "why": f"touch {len(touches)+1} of {LADDER_MAX_TOUCHES}",
            "component": overdue[0].get("kind")}


# ---------------------------------------------------------------- the job pipeline

STAGES = ("permit", "drill", "pump_test", "water_test", "state_report", "complete")

DEFAULT_PERMIT_RULES = {
    "_source": ("DEFAULT per-county permit clocks, simplified — replace with each county's "
                "actual rules before go-live. Every date here is a DATE ALERT, not legal "
                "advice; the county's rule decides."),
    "counties": {
        "Harlan":   {"permit_valid_days": 180, "completion_report_days": 30},
        "Beaufort": {"permit_valid_days": 120, "completion_report_days": 45},
        "Watauga":  {"permit_valid_days": 365, "completion_report_days": 30},
        "default":  {"permit_valid_days": 180, "completion_report_days": 30},
    },
}


def permit_rules():
    return store.load("config").get("permit_rules") or DEFAULT_PERMIT_RULES


def job_board(ref=None):
    """The pipeline, with every county clock as a DATE ALERT — a date and a
    label, never a legal opinion."""
    ref = ref or now()
    rules = permit_rules()
    rows = []
    for j in store.load("jobs"):
        if j.get("stage") == "complete" or j.get("demo_tag"):
            continue
        county = rules["counties"].get(j.get("county")) or rules["counties"]["default"]
        row = {"job": j["id"], "customer": j.get("customer_name"),
               "county": j.get("county"), "stage": j.get("stage")}
        issued = parse(j.get("permit_issued_at"))
        if j.get("stage") == "permit" and issued:
            left = (issued + timedelta(days=county["permit_valid_days"]) - ref).days
            row["clock"] = {"kind": "permit_expiry", "days_left": left,
                            "label": "DATE ALERT — the permit clock; drilling starts inside "
                                     "it or the permit refiles"}
        drilled = parse(j.get("drilled_at"))
        if drilled and not j.get("state_report_filed_at"):
            left = (drilled + timedelta(days=county["completion_report_days"]) - ref).days
            row["clock"] = {"kind": "state_report_due", "days_left": left,
                            "label": "DATE ALERT — the completion-report clock; late filing "
                                     "is a fine, and the county's rule decides"}
        rows.append(row)
    rows.sort(key=lambda r: (r.get("clock") or {}).get("days_left", 9999))
    return {"rows": rows, "rules_source": rules["_source"]}


# ---------------------------------------------------------------- recovered, counted

def recovered_this_week(ref=None):
    """Counted, never asserted: services completed, lab reports landed, and
    reminders a HUMAN sent — an agent's draft moves nothing until a person
    sends it."""
    ref = ref or now()
    serviced, value = 0, 0.0
    for s in store.load("systems"):
        for comp in s.get("components") or []:
            at = parse(comp.get("last_service_at"))
            if at and (ref - at).days <= 7:
                serviced += 1
                value += comp.get("ticket", 0)
    reports = [r for r in store.load("lab_reports")
               if r.get("result") and r.get("received_at")
               and (ref - (parse(r["received_at"]) or ref)).days <= 7]
    reminders = sum(1 for e in store.events(kind="draft_service_reminder")
                    if str(e.get("actor", "")).startswith("human:")
                    and (ref - (parse(e.get("at")) or ref)).days <= 7)
    return {"services_completed": serviced, "renewal_value": round(value, 2),
            "lab_reports_landed": len(reports), "reminders_sent": reminders,
            "note": "counted from the service book and the event log — human sends count; "
                    "agent drafts do not"}


# ---------------------------------------------------------------- eval

triage_eval = Eval("message triage",
                   costly_label="contamination",
                   costly_note=("A CONTAMINATION WORRY SOOTHED OR MISSED BY SOFTWARE IS A "
                                "FAMILY DRINKING BAD WATER ON OUR SAY-SO. Over-routing a "
                                "filter question costs a human a read."))

EVAL_CASES = [
    {"input": "my water smells like rotten eggs", "label": "contamination"},
    {"input": "the water tastes metallic and my kid got sick", "label": "contamination"},
    {"input": "brown water since yesterday", "label": "contamination"},
    {"input": "is our water safe to drink", "label": "contamination"},
    {"input": "there's sand and grit coming out of the tap water", "label": "contamination"},
    {"input": "we have no water at the house this morning", "label": "no_water"},
    {"input": "the pump won't start and the faucets are sputtering", "label": "no_water"},
    {"input": "is my uv lamp due for a change", "label": "service_due"},
    {"input": "time to swap the sediment filter?", "label": "service_due"},
    {"input": "how much to drill a new well on our property", "label": "quote"},
    {"input": "can you price a softener install", "label": "quote"},
    {"input": "any update on our drilling permit", "label": "status"},
    {"input": "when is the rig coming out", "label": "status"},
    {"input": "", "label": "human"},
    {"input": "what time do you open saturday", "label": "human"},
    {"input": "do you sell bags of softener salt at the shop", "label": "human"},
]


def run_eval():
    return triage_eval.run(EVAL_CASES, lambda t: read_message(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_message":          {"rung": "R3", "reason": "routing only; the contamination worry reads first"},
    "log_contamination":     {"rung": "R2", "reason": "the verbatim record and the sampling dispatch cannot wait for a click"},
    "log_no_water":          {"rung": "R2", "reason": "a dry house is a P1 — the record starts the clock"},
    "declare_water_safe":    {"rung": "R0", "reason": "potability belongs to an accredited lab report, cited by id, date, and result — no report, no verdict", "never_promote": True},
    "downgrade_contamination_worry": {"rung": "R0", "reason": "a smells-wrong message never gets a soothing auto-reply — record, escalate, human", "never_promote": True},
    "claim_protection_past_clock": {"rung": "R0", "reason": "an overdue UV lamp is sterilization theater — 'protected' is never claimed past the clock", "never_promote": True},
    "quote_without_well_log": {"rung": "R0", "reason": "we measure, then we price — a quote with no recorded log is a guess in writing", "never_promote": True},
    "draft_contamination_ack": {"rung": "R1", "reason": "outward reply on a health worry — a human sends, soothe-checked structurally"},
    "draft_dispatch_reply":  {"rung": "R1", "reason": "outward reply — the P1 goes to a human's route board and a human sends"},
    "draft_service_reply":   {"rung": "R1", "reason": "outward reply — the recorded clocks cited, a human sends"},
    "draft_service_reminder": {"rung": "R1", "reason": "outward reminder — a human sends; three touches, then silence is an answer"},
    "draft_quote":           {"rung": "R1", "reason": "money — a human sends, the well log cited"},
    "draft_status_reply":    {"rung": "R1", "reason": "outward reply — the pipeline record does the talking"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Well OS — what it computes to")
        .line("Treatment renewals recovered", "revenue",
              "due-service book (counted) × your renewal rate",
              ["due_service_value", "renewal_rate"],
              lambda g: float(g["due_service_value"]) * float(g["renewal_rate"]),
              note="the due book is counted from the recorded clocks; the renewal rate is yours")
        .line("Missed-service revenue on the books", "revenue",
              "overdue components × recorded ticket (counted)",
              ["overdue_service_value"], lambda g: float(g["overdue_service_value"]),
              note="counted from the service book — clocks past due, tickets recorded")
        .line("Office hours", "time_saved", "hrs/wk × 52 × rate",
              ["office_hours_wk", "office_rate"],
              lambda g: float(g["office_hours_wk"]) * 52 * float(g["office_rate"]))
        .line("Permit fines avoided", "scenario",
              "you decide what a never-missed filing clock is worth",
              ["fine_exposure"], lambda g: float(g["fine_exposure"]),
              assumption="never a saving — a fine that didn't land cannot be counted; this "
                         "line stays blank until you put your own number on it"))


def roi(given):
    db = due_board()
    rec = {"due_service_value": db["due_value"],
           "overdue_service_value": db["overdue_value"]}
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("read_message", "log_contamination", "log_no_water", "draft_contamination_ack",
          "draft_dispatch_reply", "draft_service_reply", "draft_service_reminder",
          "draft_quote", "draft_status_reply")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("customer:",))
