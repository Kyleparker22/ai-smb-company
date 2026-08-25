#!/usr/bin/env python3
"""Delta OS — domain core (drywall & framing subcontractor).

The never-seen mechanism: daily structured site-photo OBSERVATIONS are diffed
deterministically against RECORDED PLAN LINES. The day the built work departs
from the drawings, a DELTA exists with its photo ref and plan rev cited — and
the change order plus the contract's notice letter draft themselves the same
day, inside the notice window, not at closeout when memory and leverage are
gone.

The honest seam: no vision model runs in this demo. The field app records
structured observations (photo ref + what the wall measured or contained); the
diff engine downstream of that seam is what this build proves. README names it.

Rules that live here: the diff engine and its drafted-never-final
classification, the confirmed-before-priced structural gate, rate-schedule-only
pricing, the notice-clause-verbatim letter math, the closeout ledger with the
counted same-day stat, backcharge-first triage, and the matrix.

Stdlib only. Honesty rules come from `_kit`.
"""
import re, sys
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent))

from _kit.moat import Eval, Gate, Matrix, Roi                       # noqa: E402
from _kit.store import (Store, automation_rate, hours_between, iso,  # noqa: E402
                        now, parse, unmeasured)

TABLES = ("config", "jobs", "contracts", "plan_lines", "observations", "deltas",
          "messages", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="DELTAOS_DATA_ROOT")


def _norm(s):
    return " ".join(str(s or "").lower().split())


# ---------------------------------------------------------------- the rate schedule

DEFAULT_RATE_SCHEDULE = {
    "_source": ("DEFAULT rate schedule, shaped like a subcontract unit-price exhibit — replace "
                "with the schedule from the client's own master subcontract before go-live. A "
                "price this build produces comes from HERE or from a human; there is no third "
                "source."),
    "rates": {
        '5/8" Type X drywall':                  {"unit": "sf", "rate": 3.10},
        '5/8" Type X drywall, 2-hr shaft wall': {"unit": "sf", "rate": 5.40},
        '3-5/8" 20ga metal stud framing':       {"unit": "lf", "rate": 6.25},
        '6" 16ga metal stud framing':           {"unit": "lf", "rate": 8.90},
        "ACT ceiling grid 2x2":                 {"unit": "sf", "rate": 4.15},
        "FRP panel over drywall":               {"unit": "sf", "rate": 7.30},
        "soffit framing + drywall":             {"unit": "lf", "rate": 21.00},
        "level 5 finish":                       {"unit": "sf", "rate": 1.45},
    },
}


def rate_schedule():
    return store.load("config").get("rate_schedule") or DEFAULT_RATE_SCHEDULE


def schedule_entry(spec):
    sched = rate_schedule()
    for k, v in sched["rates"].items():
        if _norm(k) == _norm(spec):
            return v
    return None


def unit_for(spec, plan=None):
    e = schedule_entry(spec)
    if e:
        return e["unit"]
    return (plan or {}).get("unit") or "ea"


# ---------------------------------------------------------------- the diff engine

REWORK_SIGNALS = ("tore out", "torn out", "re-hung", "rehung", "re-framed", "reframed",
                  "redo", "redone", "re-ran", "reran", "rebuilt", "built twice", "demo'd and")


def draft_classification(plan, obs):
    """added_scope | changed_spec | rework — DRAFTED, never final; a human
    confirms. A clean match returns None: no delta, on purpose."""
    note = _norm(obs.get("note"))
    if plan is None:
        return {"classification": "added_scope", "unplanned": True,
                "why": "no plan line at this location — UNPLANNED; never assumed into the base contract"}
    hit = next((s for s in REWORK_SIGNALS if s in note), None)
    if hit:
        return {"classification": "rework", "unplanned": False,
                "why": f"rework language in the field note ({hit!r})"}
    if _norm(obs.get("observed_spec")) != _norm(plan.get("spec")):
        return {"classification": "changed_spec", "unplanned": False,
                "why": "the observed spec is not the plan spec"}
    oq, pq = obs.get("observed_qty"), plan.get("qty")
    if oq is not None and pq is not None and float(oq) != float(pq):
        side = "above" if float(oq) > float(pq) else "below"
        return {"classification": "added_scope" if side == "above" else "changed_spec",
                "unplanned": False,
                "why": f"quantity {side} plan: field {oq} vs plan {pq}"}
    return None  # a clean match produces NO delta


def diff(job_id, ref=None):
    """Observations vs plan lines for one job. Deterministic; idempotent (one
    delta per observation, keyed); a confirmed delta is never overwritten."""
    ref = ref or now()
    job = store.by_id("jobs", job_id)
    if not job:
        return {"error": "no such job"}
    plans = {_norm(p["location"]): p for p in store.load("plan_lines")
             if p["job_id"] == job_id}
    created, clean, already = [], 0, 0
    for o in store.load("observations"):
        if o.get("job_id") != job_id:
            continue
        did = "dl_" + o["id"]
        if store.by_id("deltas", did):
            already += 1
            continue
        p = plans.get(_norm(o["location"]))
        c = draft_classification(p, o)
        if c is None:
            clean += 1
            continue
        d = {"id": did, "job_id": job_id, "location": o["location"],
             "plan_line_id": p["id"] if p else None,
             "plan_says": (f"{p['spec']} — {p['qty']} {p['unit']} (rev {p['rev']})" if p
                           else "no plan line at this location"),
             "field_shows": f"{o['observed_spec']} — {o['observed_qty']} {unit_for(o['observed_spec'], p)}",
             "plan_spec": p["spec"] if p else None, "plan_qty": p["qty"] if p else None,
             "observed_spec": o["observed_spec"], "observed_qty": o["observed_qty"],
             "unit": (p or {}).get("unit") or unit_for(o["observed_spec"]),
             "plan_rev": p["rev"] if p else None,
             "photo_ref": o.get("photo_ref"), "observed_by": o.get("by"),
             "classification_draft": c["classification"], "unplanned": c["unplanned"],
             "classification_why": c["why"],
             "discovery_at": o.get("at"), "detected_at": iso(ref),
             "state": "detected", "confirmed": False,
             "note": "classification is a DRAFT — a human confirms before anything prices"}
        store.upsert("deltas", d)
        gate.act("detect_delta", "diff", did,
                 {"job": job.get("name"), "location": o["location"],
                  "photo_ref": o.get("photo_ref"), "plan_rev": d["plan_rev"],
                  "classification_draft": c["classification"], "why": c["why"]})
        created.append(did)
    return {"job": job_id, "created": created, "clean_matches": clean,
            "already_detected": already,
            "note": "a matching observation produces no delta — most days the field matches the plan"}


# ---------------------------------------------------------------- confirmed → priced (structural)

def can_price(delta):
    """THE structural gate this build is organised around: no path from
    detected to priced without a human confirmation."""
    if not delta.get("confirmed"):
        return False, ("unconfirmed — the classification is a DRAFT until a human confirms it; "
                       "a wrong delta invoiced is worse than a missed one, so there is no path "
                       "from detected to priced without the confirmation")
    return True, f"confirmed {delta.get('confirmed_class')} by {delta.get('confirmed_by')}"


def billable_qty(delta):
    cls = delta.get("confirmed_class") or delta.get("classification_draft")
    if delta.get("unplanned") or delta.get("plan_qty") in (None, ""):
        return float(delta["observed_qty"]), "the full observed quantity — no plan line to net against"
    if cls == "added_scope":
        q = float(delta["observed_qty"]) - float(delta["plan_qty"])
        return q, f"observed {delta['observed_qty']} minus plan {delta['plan_qty']}"
    return float(delta["observed_qty"]), ("the observed quantity at the field spec; any credit for the "
                                          "plan spec is a stated human line on the CO — never silently netted")


def co_math(delta):
    """Pricing: confirmed delta × the recorded rate schedule. Nothing else.
    The only pricing path in the build; it takes the delta and nothing more."""
    okp, why = can_price(delta)
    if not okp:
        return {"refused": why, "action": "invoice_unconfirmed_delta"}
    entry = schedule_entry(delta.get("observed_spec"))
    if not entry:
        return {"refused": (f"{delta.get('observed_spec')!r} is not on the recorded rate schedule — "
                            f"the recorded schedule or a human prices it; an ad-hoc unit price is "
                            f"how a change order becomes an argument"),
                "action": "price_off_rate_schedule", "off_schedule": True}
    qty, qty_basis = billable_qty(delta)
    amount = round(qty * entry["rate"], 2)
    return {"amount": amount, "qty": qty, "unit": entry["unit"], "rate": entry["rate"],
            "basis": f"{qty:g} {entry['unit']} × ${entry['rate']}/{entry['unit']} = "
                     f"${amount:,.2f} ({qty_basis})",
            "schedule_source": rate_schedule()["_source"],
            "note": "a DRAFT for a human send — priced only from the recorded schedule"}


# ---------------------------------------------------------------- the notice window

def clause_for_job(job_id):
    for c in store.load("contracts"):
        if c.get("job_id") == job_id:
            return c.get("notice_clause")
    return None


def notice_status(clause, discovery_at, ref=None):
    """The window math, anchored to the DATED PHOTO (discovery), never to when
    anyone got around to the paperwork."""
    ref = ref or now()
    disc = parse(discovery_at)
    if not disc:
        return unmeasured("no discovery date on the delta — the window cannot be computed",
                          field="days_remaining")
    since = (ref - disc).days
    remaining = int(clause["days"]) - since
    return {"days_allowed": int(clause["days"]), "days_since_discovery": since,
            "days_remaining": remaining, "expired": remaining < 0,
            "label": "DATE ALERT — computed from the recorded clause and the dated photo, "
                     "not legal advice"}


# ---------------------------------------------------------------- delta states + ledgers

DELTA_STATES = ("detected", "confirmed", "noticed", "priced", "signed", "rejected")


def advance_delta(d, to):
    order = {s: i for i, s in enumerate(DELTA_STATES)}
    if to == "rejected":
        d["state"] = "rejected"
        return d
    if order.get(to, -1) > order.get(d.get("state", "detected"), 0):
        d["state"] = to
    return d


def closeout_ledger(ref=None):
    """Every delta by state, unsigned ones aged — and the counted same-day
    stat, the product's own proof."""
    ref = ref or now()
    rows, by_state = [], {s: 0 for s in DELTA_STATES}
    same_day = later = 0
    jobs = store.index("jobs")
    for d in store.load("deltas"):
        st = d.get("state", "detected")
        by_state[st] = by_state.get(st, 0) + 1
        h = hours_between(d.get("discovery_at"), d.get("detected_at"))
        if h is not None and h <= 24:
            same_day += 1
        else:
            later += 1
        det = parse(d.get("detected_at"))
        rows.append({"delta": d["id"], "job": (jobs.get(d["job_id"]) or {}).get("name"),
                     "location": d.get("location"),
                     "classification": d.get("confirmed_class") or d.get("classification_draft"),
                     "confirmed": bool(d.get("confirmed")), "state": st,
                     "value": d.get("co_amount"),
                     "age_days": (ref - det).days if det else None})
    rows.sort(key=lambda r: -(r["age_days"] or 0))
    return {"rows": rows, "by_state": by_state,
            "detection": {"same_day": same_day, "found_later": later,
                          "note": "counted from photo dates vs detection dates — the closeout "
                                  "archaeology this build exists to end"}}


def this_week(ref=None):
    """Counted from the delta ledger and the event log — never asserted."""
    ref = ref or now()
    ds = store.load("deltas")

    def within(ts):
        t = parse(ts)
        return t is not None and (ref - t).days <= 7

    detected = [d for d in ds if within(d.get("detected_at"))]
    confirmed = [d for d in ds if within(d.get("confirmed_at"))]
    signed = [d for d in ds if within(d.get("signed_at"))]
    notices = sum(1 for e in store.events(kind="draft_notice_letter")
                  if str(e.get("actor", "")).startswith("human:") and within(e.get("at")))
    return {"deltas_detected": len(detected), "deltas_confirmed": len(confirmed),
            "notices_sent": notices, "cos_signed": len(signed),
            "co_value_signed": round(sum(d.get("co_amount") or 0 for d in signed), 2),
            "note": "counted from the delta ledger and the event log — never asserted"}


def kept_window_value():
    """Counted: confirmed CO value whose notice went out INSIDE its window."""
    total = 0.0
    for d in store.load("deltas"):
        if not d.get("noticed_at") or not d.get("co_amount"):
            continue
        clause = clause_for_job(d["job_id"])
        if not clause:
            continue
        st = notice_status(clause, d.get("discovery_at"), ref=parse(d["noticed_at"]))
        if not st.get("expired"):
            total += d["co_amount"]
    return round(total, 2)


# ---------------------------------------------------------------- backcharge evidence

def pull_backcharge_evidence(job_id):
    """A backcharge accusation gets the record pulled — dated photos, plan revs,
    the delta ledger. Software neither concedes nor argues; a human takes the position."""
    if not job_id or not store.by_id("jobs", job_id):
        return {"observations": [], "plan_lines": 0, "deltas": [],
                "note": "no job named on the message — a person attaches the job before this goes anywhere"}
    obs = [{"photo_ref": o.get("photo_ref"), "location": o.get("location"),
            "at": o.get("at"), "by": o.get("by")}
           for o in store.load("observations") if o.get("job_id") == job_id]
    plans = [p for p in store.load("plan_lines") if p.get("job_id") == job_id]
    deltas = [{"delta": d["id"], "location": d.get("location"), "state": d.get("state")}
              for d in store.load("deltas") if d.get("job_id") == job_id]
    return {"observations": obs, "plan_lines": len(plans),
            "plan_revs": sorted({p.get("rev") for p in plans}),
            "deltas": deltas,
            "note": "the dated record, pulled — never conceded, never argued by software"}


# ---------------------------------------------------------------- triage

BACKCHARGE = (
    r"\bback.?charg\w*",
    r"\b(deduct|withhold)\w*\b.*\b(pay app|payment|invoice|contract|billing)\b",
    r"\bcharg\w* (you|us) back\b",
    r"\bcharg\w* (you|keystone)\b.*\b(repair|damage|cleanup|patch|scratch)\w*",
)
VERBAL_DIRECTIVE = (
    r"\bgo ahead and (add|run|frame|hang|build|extend|move|do)\b",
    r"\b(add|frame|extend|run)\b.*\b(paper(work)? (it )?later|square (it )?up later|"
    r"co (to follow|later)|we'?ll get you a (co|change order))\b",
    r"\bproceed with the (extra|added|additional)\b",
    r"\bverbal (ok|go|authorization|approval)\b",
)
SCHEDULE_ASK = (
    r"\bwhen (will|can|do|are) (you|your)\b",
    r"\b(finish|finished|done|complete|wrap)\b.*\b(by|date)\b",
    r"\bschedule\b.*\b(update|slip|status|look)\b",
    r"\bmanpower\b",
)


def read_message(text):
    """backcharge | verbal_directive | schedule_ask | human. The backcharge
    reads FIRST — an accusation answered from memory is money gone."""
    t = _norm(text)
    if not t:
        return {"label": "human", "why": "empty message — a person reads it"}
    for rx in BACKCHARGE:
        if re.search(rx, t):
            return {"label": "backcharge",
                    "why": "a backcharge accusation — the dated record gets pulled; software "
                           "neither concedes nor argues, a human takes the position"}
    for rx in VERBAL_DIRECTIVE:
        if re.search(rx, t):
            return {"label": "verbal_directive",
                    "why": "a verbal go-ahead — recorded verbatim and quoted back; a note, "
                           "not a signed change order"}
    for rx in SCHEDULE_ASK:
        if re.search(rx, t):
            return {"label": "schedule_ask", "why": "a schedule ask — answered from the job record"}
    return {"label": "human", "why": "no clean signal — a person reads it"}


# ---------------------------------------------------------------- eval

triage_eval = Eval("message triage",
                   costly_label="backcharge",
                   costly_note=("A BACKCHARGE ACCUSATION ANSWERED FROM MEMORY IS MONEY GONE. "
                                "The record gets pulled — dated photos, plan revs, the delta "
                                "ledger — and a human takes the position. Over-routing a "
                                "schedule ask costs a read."))

EVAL_CASES = [
    {"input": "we're backcharging you for the patch repair on level 2", "label": "backcharge"},
    {"input": "the owner is deducting the cleanup cost from your next pay app", "label": "backcharge"},
    {"input": "charging you back for the damaged door frame your crew hit", "label": "backcharge"},
    {"input": "backcharge coming your way for the scratched storefront glass", "label": "backcharge"},
    {"input": "go ahead and add the soffit in the lobby, we'll paper it later", "label": "verbal_directive"},
    {"input": "super says go ahead and run the wall to deck, CO to follow", "label": "verbal_directive"},
    {"input": "proceed with the extra layer on the corridor, paperwork later", "label": "verbal_directive"},
    {"input": "go ahead and frame the extra opening, we'll square it up later", "label": "verbal_directive"},
    {"input": "when will your crew finish level 3", "label": "schedule_ask"},
    {"input": "need a schedule update, are you done by friday", "label": "schedule_ask"},
    {"input": "what's your manpower look like next week", "label": "schedule_ask"},
    {"input": "can you wrap the ceilings by the 20th", "label": "schedule_ask"},
    {"input": "", "label": "human"},
    {"input": "who do we send the insurance cert to", "label": "human"},
    {"input": "lunch truck is on site by the north gate", "label": "human"},
]


def run_eval():
    return triage_eval.run(EVAL_CASES, lambda t: read_message(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_message":     {"rung": "R3", "reason": "routing only; the backcharge reads first"},
    "detect_delta":     {"rung": "R2", "reason": "an internal detection — photo ref and plan rev cited; nothing moves outward"},
    "log_verbal_note":  {"rung": "R2", "reason": "recording the verbatim words cannot wait; the note stays a note"},
    "invoice_unconfirmed_delta": {"rung": "R0", "reason": "no path from detected to priced without a human confirmation — a wrong delta invoiced is worse than a missed one", "never_promote": True},
    "treat_verbal_as_signed": {"rung": "R0", "reason": "a verbal go-ahead is recorded and quoted back — a note, not a signed change order", "never_promote": True},
    "notice_without_recorded_clause": {"rung": "R0", "reason": "the letter cites the recorded clause verbatim or it does not draft", "never_promote": True},
    "price_off_rate_schedule": {"rung": "R0", "reason": "the recorded rate schedule or a human — an ad-hoc unit price is how a CO becomes an argument", "never_promote": True},
    "draft_change_order": {"rung": "R1", "reason": "outward + money — a human sends it, priced only from the recorded schedule"},
    "draft_notice_letter": {"rung": "R1", "reason": "outward + legal posture — a human sends; every date is a DATE ALERT, not legal advice"},
    "draft_verbal_quoteback": {"rung": "R1", "reason": "outward reply — the GC's words quoted back before memory rewrites them"},
    "draft_backcharge_response": {"rung": "R1", "reason": "outward + dispute — the record attached; software neither concedes nor argues"},
    "draft_schedule_reply": {"rung": "R1", "reason": "outward reply — answered from the job record, with the arithmetic shown"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Delta OS — what it computes to")
        .line("Change orders captured", "revenue",
              "deltas detected (counted) × avg CO value × your confirm rate",
              ["deltas_detected", "avg_co_value", "confirm_rate"],
              lambda g: float(g["deltas_detected"]) * float(g["avg_co_value"]) * float(g["confirm_rate"]),
              note="the count is counted from the delta ledger; the average fills from your own "
                   "priced COs once they exist; the confirm rate is your call — no single delta "
                   "is ever priced without a human confirmation")
        .line("CO value noticed inside its window", "cash_timing",
              "confirmed CO value with the notice out inside the window (counted)",
              ["kept_window_value"], lambda g: float(g["kept_window_value"]),
              note="cash timing — entitlement preserved, not new revenue; every window is a "
                   "DATE ALERT, not legal advice")
        .line("Closeout write-offs, your history", "scenario",
              "what you ate at closeout last year — your number",
              ["closeout_writeoffs"], lambda g: float(g["closeout_writeoffs"]),
              assumption="never a saving we claim — the stat this build exists to shrink is "
                         "counted on the board; the dollar value of it is yours")
        .line("PM hours on change paperwork", "time_saved", "hrs/wk × 52 × rate",
              ["pm_hours_wk", "pm_rate"],
              lambda g: float(g["pm_hours_wk"]) * 52 * float(g["pm_rate"])))


def roi(given):
    rec = {}
    ds = store.load("deltas")
    rec["deltas_detected"] = len(ds)
    priced = [d for d in ds if d.get("co_amount")]
    if priced:
        rec["avg_co_value"] = round(sum(d["co_amount"] for d in priced) / len(priced), 2)
    rec["kept_window_value"] = kept_window_value()
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


# ---------------------------------------------------------------- counted automation

MOVING = ("read_message", "detect_delta", "log_verbal_note", "draft_change_order",
          "draft_notice_letter", "draft_verbal_quoteback", "draft_backcharge_response",
          "draft_schedule_reply")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("gc:", "field:"))
