#!/usr/bin/env python3
"""Plat OS — domain core (land surveying).

Rules live here: boundary-question-first triage (software never states where a
line falls — the licensed PLS seals or nobody does), the seal gate (a plat is
"sealed" only with its recorded seal reference), the research chain (a draft
citing nothing is refused), the closing-date deadline board, crew day sheets
(fieldwork without a same-day sheet reads incomplete, never assumed), quotes
from recorded comparables or not at all, and the matrix.

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

TABLES = ("config", "jobs", "day_sheets", "boundary_log", "messages",
          "title_companies", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="PLATOS_DATA_ROOT")

STAGES = ("research", "field", "draft", "pls_review", "sealed")
CLOSING_WEEK_DAYS = 7


def recorded_pls():
    return store.load("config").get("pls") or {"name": "the licensed surveyor",
                                               "license": "unrecorded"}


# ---------------------------------------------------------------- triage

BOUNDARY = (
    r"\b(fence|shed|driveway|garage|wall|barn|pool|tree)\b.*\b(my|our|his|her|their|the "
    r"neighbou?r'?s?)\b.*\b(property|land|lot|side)\b",
    r"\bencroach\w*",
    r"\bover the line\b",
    r"\bconfirm\w*\b.*\b(line|boundary|corner|pin)\b",
    r"\b(line|boundary|corner|pin)\b.*\bconfirm\w*",
    r"\bwhere\b.*\b(property )?(line|boundary)\b.*\b(fall|is|run|sit)\w*",
)
DEADLINE = (
    r"\bclos(ing|e)\b.*\b(survey|plat|done|ready|time|make it)\b",
    r"\b(survey|plat)\b.*\b(before|by|ahead of)\b.*\bclos\w*",
    r"\bclos(ing|e)\b.*\b(moved|pushed|bumped)\b|\b(moved|pushed|bumped)\b.*\bclos\w*",
)
STATUS = (
    r"\b(where|status|update)\b.*\b(survey|plat|job|crew)\b",
    r"\b(survey|plat)\b.*\b(ready|done|status|finished|eta)\b",
    r"\bis (my|the|our) survey\b",
)
QUOTE = (
    r"\b(quote|price|cost|estimate|run|charge|bid)\b.*\b(survey|acres?|alta|topo|lot|parcel)\b",
    r"\b(how much|what would)\b.*\b(survey|acres?|parcel)\b",
    r"\bacres?\b.*\b(quote|price|cost|run|charge)\b",
)
RECORDS = (
    r"\b(deed|prior plat|plat of record|book and page|courthouse|county record|instrument|"
    r"chain of title)\w*",
    r"\b(pull|find|look up|locate)\b.*\b(deed|plat|records?)\b",
)


def read_message(text):
    """boundary_question | deadline_risk | status | quote | records | human.
    The boundary question reads FIRST — an unlicensed boundary opinion is
    practicing surveying without a license."""
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty message — a person reads it"}
    for rx in BOUNDARY:
        if re.search(rx, t):
            return {"label": "boundary_question",
                    "why": "a boundary/encroachment question — recorded verbatim, routed to "
                           "the recorded PLS; software never states where a line falls"}
    for rx in DEADLINE:
        if re.search(rx, t):
            return {"label": "deadline_risk",
                    "why": "a closing-date question — answered from the recorded stage clocks "
                           "and flagged to a human before closing week"}
    for rx in STATUS:
        if re.search(rx, t):
            return {"label": "status", "why": "status — answered from the pipeline record"}
    for rx in QUOTE:
        if re.search(rx, t):
            return {"label": "quote",
                    "why": "a price ask — priced from recorded comparable jobs or refused"}
    for rx in RECORDS:
        if re.search(rx, t):
            return {"label": "records", "why": "record research — the cited chain does the talking"}
    return {"label": "human", "why": "no clean signal — a person reads it"}


# ---------------------------------------------------------------- the boundary rule

FORBIDDEN_CONCLUSIONS = ("encroach", "is on your property", "is not on your property",
                         "on the neighbor", "over the line", "the line is",
                         "the line runs", "inside your boundary", "your side of")


def boundary_reply_ok(text):
    """No draft leaving this software may contain a boundary conclusion."""
    t = (text or "").lower()
    hits = [w for w in FORBIDDEN_CONCLUSIONS if w in t]
    if hits:
        return False, f"a boundary conclusion from software — forbidden language: {', '.join(hits)}"
    return True, "ok"


def record_boundary_question(text, source, job_id=None):
    """Append-only. The verbatim question and its route to the PLS is the ONLY
    thing software produces; there is no edit and no delete in this module —
    that absence is the rule."""
    row = {"id": store.nid("bq"), "at": iso(), "verbatim": text, "from": source,
           "job_id": job_id, "routed_to": recorded_pls()}
    store.upsert("boundary_log", row)
    store.log_event("boundary_question_recorded", row["id"], "agent:desk", "R2",
                    {"routed_to": recorded_pls()["name"]})
    return row


# ---------------------------------------------------------------- the research chain

def chain_check(job):
    """A draft citing nothing is refused — a boundary without its chain is an
    opinion. Cited instruments: deed book/page, prior plats, POBs."""
    chain = job.get("research_chain") or []
    if not chain:
        return {"refused": ("no cited instruments on this job — a boundary without its chain "
                            "is an opinion. Drafting waits for the deed book/page and prior "
                            "plats to be on the record.")}
    return {"ok": True, "cited": len(chain),
            "instruments": [_cite(c) for c in chain]}


def _cite(c):
    if c.get("kind") == "deed":
        return f"deed book {c.get('book')}, page {c.get('page')}"
    if c.get("kind") == "plat":
        return f"prior plat, cabinet {c.get('cabinet')}, slide {c.get('slide')}"
    return f"{c.get('kind')}: {c.get('ref', '?')}"


# ---------------------------------------------------------------- crew day sheets

def day_sheet_status(job):
    """Fieldwork without a same-day crew sheet reads incomplete via unmeasured
    — never assumed complete."""
    fd = parse(job.get("fieldwork_done_at"))
    if not fd:
        return {"applies": False, "note": "no fieldwork recorded yet"}
    date_str = fd.date().isoformat()
    for s in store.load("day_sheets"):
        if s.get("job_id") == job.get("id") and s.get("date") == date_str:
            return {"applies": True, "complete": True, "sheet": s["id"],
                    "points": s.get("points"), "crew": s.get("crew")}
    return unmeasured(f"fieldwork on {date_str} has no same-day crew sheet — the field data "
                      f"reads incomplete, never assumed", field="day_sheet", applies=True)


# ---------------------------------------------------------------- stage clocks + the closing promise

def stage_medians(rows=None):
    """Median days per stage, COUNTED from sealed jobs' own stage logs. The
    only permitted basis for any closing-date answer."""
    if rows is None:
        rows = [j for j in store.load("jobs") if j.get("stage") == "sealed"]
    durations = {s: [] for s in STAGES[:-1]}
    for j in rows:
        log = {e["stage"]: parse(e["at"]) for e in (j.get("stage_log") or []) if parse(e["at"])}
        for i, s in enumerate(STAGES[:-1]):
            a, b = log.get(s), log.get(STAGES[i + 1])
            if a and b:
                durations[s].append((b - a).total_seconds() / 86400.0)
    meds = {s: round(median(v), 1) for s, v in durations.items() if v}
    if len(meds) < len(STAGES) - 1:
        return unmeasured(f"only {len(meds)} of {len(STAGES) - 1} stage clocks have recorded "
                          f"history — a projection needs all of them", field="medians")
    return {"medians": meds, "n": len(rows),
            "basis": f"median stage clocks from {len(rows)} sealed jobs"}


def closing_projection(job, ref=None):
    """Projected days-to-seal vs days-to-closing, from the recorded clocks
    only. A missing input is named, never guessed."""
    ref = ref or now()
    if not job.get("closing_date"):
        return unmeasured("no closing date recorded on this job", field="days_to_closing")
    if job.get("stage") == "sealed":
        return {"sealed": True, "note": "already sealed — nothing to project"}
    clocks = stage_medians()
    if "_missing" in clocks:
        return clocks
    try:
        idx = STAGES.index(job.get("stage"))
    except ValueError:
        return unmeasured(f"job stage {job.get('stage')!r} is not on the pipeline", field="stage")
    projected = round(sum(clocks["medians"][s] for s in STAGES[idx:-1]), 1)
    dtc = days_until(job["closing_date"], ref)
    return {"projected_days_to_seal": projected, "days_to_closing": dtc,
            "makes_it": projected <= dtc, "stage": job["stage"],
            "basis": clocks["basis"] + " — never a gut answer"}


def promise_closing_reply(job):
    """The only closing-date answer software drafts: the projection, with its
    basis, for a human to send. No recorded clocks → a refusal, not a guess."""
    p = closing_projection(job)
    if "_missing" in p:
        return {"refused": (f"cannot promise a date — {p['_missing']}. A closing promise not "
                            f"computed from recorded stage clocks is a guess with someone's "
                            f"closing.")}
    return {"projection": p}


# ---------------------------------------------------------------- quotes from comparables

ACRE_BUCKETS = ((1, "under 1 acre"), (5, "1–5 acres"), (20, "5–20 acres"),
                (100, "20–100 acres"), (float("inf"), "100+ acres"))
MIN_COMPARABLES = 3


def acre_bucket(acreage):
    for top, label in ACRE_BUCKETS:
        if acreage < top:
            return label
    return ACRE_BUCKETS[-1][1]


def quote_math(job_type, acreage):
    """A quote is the median of recorded sealed jobs in the same type and
    acreage bucket — or a refusal. Never a guess."""
    if acreage in (None, ""):
        return {"refused": "cannot quote — no acreage given; the comparables are bucketed by it"}
    bucket = acre_bucket(float(acreage))
    comps = [j for j in store.load("jobs")
             if j.get("stage") == "sealed" and j.get("job_type") == job_type
             and j.get("price") and acre_bucket(j.get("acreage") or 0) == bucket]
    if len(comps) < MIN_COMPARABLES:
        return {"refused": (f"no recorded comparables — {len(comps)} sealed {job_type} job(s) "
                            f"at {bucket}; we need {MIN_COMPARABLES} to quote. A price without "
                            f"its comparables is a guess, and we don't guess with your money.")}
    prices = [j["price"] for j in comps]
    return {"amount": round(median(prices), 2), "comparables": len(comps), "bucket": bucket,
            "range": [min(prices), max(prices)],
            "basis": (f"median of {len(comps)} recorded sealed {job_type} jobs at {bucket} — "
                      f"our own book, not a rate card")}


# ---------------------------------------------------------------- the deadline board

def deadline_board(ref=None):
    """Every open job, ranked by days-to-closing — the master clock. Blockers
    are named, never summarized away."""
    ref = ref or now()
    rows = []
    for j in store.load("jobs"):
        if j.get("stage") == "sealed" or j.get("demo_tag"):
            continue
        dtc = days_until(j.get("closing_date"), ref) if j.get("closing_date") else None
        blockers = []
        if not (j.get("research_chain") or []):
            blockers.append("no research chain cited — drafting is blocked")
        ds = day_sheet_status(j)
        if ds.get("applies") and "_missing" in ds:
            blockers.append("field data incomplete — no same-day crew sheet")
        if dtc is not None and dtc <= CLOSING_WEEK_DAYS:
            blockers.append("CLOSING WEEK — flagged to a human")
        row = {"job": j["id"], "client": j.get("client"), "job_type": j.get("job_type"),
               "stage": j.get("stage"), "county": j.get("county"),
               "days_to_closing": dtc, "closing_date": j.get("closing_date"),
               "blockers": blockers}
        if dtc is None:
            row["note"] = "no closing date recorded — ranked last, never guessed"
        rows.append(row)
    rows.sort(key=lambda r: (r["days_to_closing"] is None, r["days_to_closing"] or 0))
    return {"rows": rows,
            "closing_week": sum(1 for r in rows if r["days_to_closing"] is not None
                                and r["days_to_closing"] <= CLOSING_WEEK_DAYS),
            "note": "ranked by the closing date — the master clock; blockers named"}


def recovered_this_week(ref=None):
    """Counted: plats sealed, closings kept, boundary questions routed to the
    PLS, deadline alerts a human sent — inside 7 days."""
    ref = ref or now()
    sealed = [j for j in store.load("jobs")
              if (j.get("seal") or {}).get("date")
              and 0 <= (ref - (parse(j["seal"]["date"]) or ref)).days <= 7]
    kept = [j for j in sealed if j.get("closing_date")
            and (parse(j["seal"]["date"]) or ref) <= (parse(j["closing_date"]) or ref)]
    routed = sum(1 for e in store.events(kind="refused")
                 if (e.get("detail") or {}).get("action") == "state_boundary_conclusion"
                 and (ref - (parse(e.get("at")) or ref)).days <= 7)
    alerts = sum(1 for e in store.events(kind="draft_deadline_reply")
                 if str(e.get("actor", "")).startswith("human:")
                 and (ref - (parse(e.get("at")) or ref)).days <= 7)
    return {"plats_sealed": len(sealed), "closings_kept": len(kept),
            "boundary_questions_routed": routed, "deadline_alerts_sent": alerts,
            "note": "counted from the job records and the event log — never asserted"}


# ---------------------------------------------------------------- eval

triage_eval = Eval("message triage",
                   costly_label="boundary_question",
                   costly_note=("AN UNLICENSED BOUNDARY OPINION IS PRACTICING SURVEYING WITHOUT "
                                "A LICENSE — the line exists when the PLS seals it, not before. "
                                "Over-routing a status ask costs a read."))

EVAL_CASES = [
    {"input": "is my neighbor's fence on my property", "label": "boundary_question"},
    {"input": "did you confirm the line yet", "label": "boundary_question"},
    {"input": "the buyer says the shed encroaches on the lot next door", "label": "boundary_question"},
    {"input": "where does the property line actually fall between our yards", "label": "boundary_question"},
    {"input": "the stake makes it look like the driveway is over the line", "label": "boundary_question"},
    {"input": "closing moved to friday, will the survey be done", "label": "deadline_risk"},
    {"input": "we need the plat before closing on the 28th", "label": "deadline_risk"},
    {"input": "is my survey ready yet", "label": "status"},
    {"input": "any update on the survey for 45 maple street", "label": "status"},
    {"input": "what would a boundary survey run on 3 acres", "label": "quote"},
    {"input": "how much to survey a 12 acre parcel", "label": "quote"},
    {"input": "can you pull the deed book and page for the ferris parcel", "label": "records"},
    {"input": "do you have the prior plat from the courthouse", "label": "records"},
    {"input": "", "label": "human"},
    {"input": "thanks for getting the crew out so fast", "label": "human"},
]


def run_eval():
    return triage_eval.run(EVAL_CASES, lambda t: read_message(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_message":       {"rung": "R3", "reason": "routing only; the boundary question reads first"},
    "state_boundary_conclusion": {"rung": "R0", "reason": "an unlicensed boundary opinion is practicing surveying without a license — the PLS seals or nobody does", "never_promote": True},
    "seal_without_reference": {"rung": "R0", "reason": "a plat is sealed by its recorded seal reference — number and date — and there is no path to 'sealed' without them", "never_promote": True},
    "draft_without_research_chain": {"rung": "R0", "reason": "a boundary without its chain is an opinion", "never_promote": True},
    "quote_without_comparables": {"rung": "R0", "reason": "a price without recorded comparables is a guess", "never_promote": True},
    "mark_plat_sealed":   {"rung": "R1", "reason": "licensure — the seal is the PLS's act; software records the reference, a human seals"},
    "promise_closing_date": {"rung": "R1", "reason": "a date promise computes from the pipeline's own recorded stage clocks, and a human sends it"},
    "advance_stage":      {"rung": "R2", "reason": "internal pipeline move, reversible, logged — the chain check gates the draft stage structurally"},
    "draft_boundary_reply": {"rung": "R1", "reason": "outward reply — conclusion-checked structurally, routed to the recorded PLS"},
    "draft_deadline_reply": {"rung": "R1", "reason": "outward reply to a title company — the closing is their deal and our referral source"},
    "draft_status_reply": {"rung": "R1", "reason": "outward reply — answered from the pipeline record, a human sends"},
    "draft_quote":        {"rung": "R1", "reason": "money — the comparables' median drafts, a human sends"},
    "draft_records_reply": {"rung": "R1", "reason": "outward reply — the cited chain does the talking"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Plat OS — what it computes to")
        .line("Crew-week throughput", "revenue", "crews × extra jobs/crew-week × avg fee × 50",
              ["crews", "extra_jobs_crew_wk", "avg_fee"],
              lambda g: float(g["crews"]) * float(g["extra_jobs_crew_wk"]) * float(g["avg_fee"]) * 50,
              note="crews is counted; the lift from a tracked pipeline is your call")
        .line("Research hours returned", "time_saved", "hrs/job × jobs/mo × 12 × rate",
              ["research_hrs_job", "jobs_mo", "researcher_rate"],
              lambda g: float(g["research_hrs_job"]) * float(g["jobs_mo"]) * 12 * float(g["researcher_rate"]))
        .line("The lost title company", "scenario", "you decide what keeping the relationship is worth",
              ["title_company_value"], lambda g: float(g["title_company_value"]),
              assumption="never a saving — the referral source that feeds everything; a missed "
                         "closing is how it ends, and a kept one is not our number"))


def roi(given):
    rec = {}
    rec["crews"] = len(store.load("config").get("crews") or [])
    rec["jobs_mo"] = len([j for j in store.load("jobs")
                          if (j.get("seal") or {}).get("date")
                          and (now() - (parse(j["seal"]["date"]) or now())).days <= 30])
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("read_message", "advance_stage", "mark_plat_sealed", "draft_boundary_reply",
          "draft_deadline_reply", "draft_status_reply", "draft_quote", "draft_records_reply")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("client:", "title:"))
