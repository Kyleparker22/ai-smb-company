#!/usr/bin/env python3
"""Chair OS — domain core (general dental practices · small DSOs).

Everything that is a *rule* lives here: the fee schedule and chair-time model,
the unscheduled-treatment ranking, plan-rule evaluation, the same-day fill
logic, recall intervals, the ROI model and the autonomy matrix.

The product thesis: a practice's largest asset is already inside its own
software, unscheduled. Alongside it sit two daily wounds — the 7am cancellation
that cannot be recovered later (chair-hours do not bank) and the hours on hold
verifying benefits.

Two prohibitions are rules here, not prompt text:
  1. The system never diagnoses, never suggests treatment, never interprets a
     clinical finding. It moves treatment a dentist already diagnosed.
  2. The system never makes an insurance determination. It reports what the
     payer returned and flags what it could not confirm. `verify()` can return
     `unconfirmed` on every field and that is a correct answer.

Stdlib only.
"""
import sys
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent))

from _kit.moat import Eval, Gate, Matrix, Roi                       # noqa: E402
from _kit.store import (Store, automation_rate, days_until, iso,    # noqa: E402
                        median, now, parse, unmeasured)

TABLES = ("config", "patients", "providers", "procedures", "treatment_plan",
          "appointments", "payers", "verifications", "recall", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="CHAIROS_DATA_ROOT")


# ---------------------------------------------------------------- the fee schedule
#
# `provider` is which chair it needs — a hygiene opening cannot be filled with a
# crown, which is the constraint that makes most "fill the schedule" tools wrong.

PROCEDURES = {
    "exam_periodic":  dict(label="Periodic exam", fee=68, minutes=20, provider="dds", cat="diagnostic", urgency="elective"),
    "prophy":         dict(label="Prophylaxis", fee=112, minutes=50, provider="rdh", cat="preventive", urgency="elective"),
    "perio_maint":    dict(label="Periodontal maintenance", fee=148, minutes=60, provider="rdh", cat="preventive", urgency="soon"),
    "srp_quad":       dict(label="Scaling & root planing (quad)", fee=295, minutes=60, provider="rdh", cat="perio", urgency="soon"),
    "filling_post":   dict(label="Posterior composite", fee=248, minutes=50, provider="dds", cat="restorative", urgency="soon"),
    "crown":          dict(label="Crown", fee=1340, minutes=90, provider="dds", cat="major", urgency="soon"),
    "endo_molar":     dict(label="Molar root canal", fee=1420, minutes=110, provider="dds", cat="endo", urgency="urgent"),
    "extraction":     dict(label="Extraction", fee=310, minutes=45, provider="dds", cat="oral_surgery", urgency="urgent"),
    "implant":        dict(label="Implant placement", fee=2450, minutes=120, provider="dds", cat="major", urgency="elective"),
    "night_guard":    dict(label="Night guard", fee=620, minutes=40, provider="dds", cat="adjunct", urgency="elective"),
}

URGENCY_WEIGHT = {"urgent": 1.6, "soon": 1.2, "elective": 1.0}


# ---------------------------------------------------------------- payer plans
#
# Modelled as rules, not as a template: a frequency limit, a waiting period and
# an alternate-benefit downgrade behave differently and each one has its own way
# of being UNKNOWABLE without the payer answering.

PAYERS = {
    "meridian": dict(label="Meridian Dental", annual_max=1500,
                     freq={"prophy": 2, "exam_periodic": 2, "srp_quad": 1},
                     waiting={"major": 12}, downgrade={"filling_post": "amalgam"},
                     responds=True),
    "cardinal": dict(label="Cardinal Health Dental", annual_max=2000,
                     freq={"prophy": 2, "exam_periodic": 2},
                     waiting={"major": 6}, downgrade={}, responds=True),
    "brightway": dict(label="Brightway PPO", annual_max=1000,
                      freq={"prophy": 2}, waiting={}, downgrade={"crown": "porcelain_to_metal"},
                      responds=True),
    # This one deliberately does not answer. Its patients must read `unconfirmed`.
    "keystone_admin": dict(label="Keystone Administrators", annual_max=None,
                           freq={}, waiting={}, downgrade={}, responds=False),
}


def verify(patient, payer_key, procedure, ref=None):
    """What the payer said — and, loudly, what it did not.

    Every field is either a value the payer returned or `unconfirmed` with the
    reason. There is no code path that infers a benefit from a plan template,
    because a patient surprised at checkout is where write-offs and one-star
    reviews come from.
    """
    ref = ref or now()
    p = PAYERS.get(payer_key)
    out = {"patient": patient["id"], "payer": payer_key, "procedure": procedure,
           "checked_at": iso(ref), "fields": {}}
    if not p:
        out["fields"] = {k: {"value": None, "_missing": "unknown payer on file"}
                         for k in ("eligible", "remaining_max", "frequency_ok", "waiting_ok", "downgrade")}
        out["verdict"] = "unconfirmed"
        return out
    if not p["responds"]:
        why = f"{p['label']} did not return a benefit response — a human must call"
        out["fields"] = {k: {"value": None, "_missing": why}
                         for k in ("eligible", "remaining_max", "frequency_ok", "waiting_ok", "downgrade")}
        out["verdict"] = "unconfirmed"
        return out

    spec = PROCEDURES.get(procedure, {})
    f = out["fields"]
    f["eligible"] = {"value": bool(patient.get("coverage_active"))}
    used = patient.get("benefits_used", 0)
    f["remaining_max"] = ({"value": None, "_missing": "plan has no stated annual maximum"}
                          if p["annual_max"] is None
                          else {"value": round(max(0, p["annual_max"] - used), 2)})
    # A responding payer returns its whole rule set, so the ABSENCE of a rule is
    # itself an answer ("no limitation applies"), not an unknown. Refusing to
    # confirm what the payer did tell us would be its own dishonesty — it makes
    # every sheet an exception and the exception list stops meaning anything.
    limit = p["freq"].get(procedure)
    if limit is None:
        f["frequency_ok"] = {"value": True, "detail": "no frequency limitation on this procedure"}
    else:
        done = patient.get("procedures_this_year", {}).get(procedure, 0)
        f["frequency_ok"] = {"value": done < limit, "detail": f"{done} of {limit} used this benefit year"}
    wait = p["waiting"].get(spec.get("cat"))
    if wait is None:
        f["waiting_ok"] = {"value": True, "detail": "no waiting period on this category"}
    else:
        months = patient.get("months_enrolled")
        f["waiting_ok"] = ({"value": None, "_missing": "enrollment date not on file — waiting period unknowable"}
                           if months is None else
                           {"value": months >= wait, "detail": f"{months} of {wait} months enrolled"})
    f["downgrade"] = ({"value": p["downgrade"][procedure],
                       "detail": "plan pays an alternate benefit — the patient owes the difference"}
                      if procedure in p["downgrade"]
                      else {"value": "none", "detail": "no alternate-benefit rule on this procedure"})

    unconfirmed = [k for k, v in f.items() if v.get("_missing")]
    # A field we could not confirm never rounds up to "covered".
    out["verdict"] = ("confirmed" if not unconfirmed else "partial")
    out["unconfirmed_fields"] = unconfirmed
    out["estimate_ok"] = (out["verdict"] == "confirmed"
                          and f["eligible"]["value"] and f.get("frequency_ok", {}).get("value") is not False)
    return out


def can_state_coverage(v):
    """The one-line rule the whole verification module exists to enforce."""
    return v.get("verdict") == "confirmed" and v.get("estimate_ok") is True


# ---------------------------------------------------------------- unscheduled treatment
#
# The ranking. Every component is defensible out loud, because the office
# manager will ask why patient A is above patient B.

def benefit_days_left(patient, ref=None):
    ref = ref or now()
    end = patient.get("benefit_year_end")
    return days_until(end, ref) if end else None


def rank_unscheduled(rows=None, ref=None, limit=None):
    ref = ref or now()
    rows = rows if rows is not None else [t for t in store.load("treatment_plan")
                                          if t.get("state") == "unscheduled"]
    pts = store.index("patients")
    out = []
    for t in rows:
        spec = PROCEDURES.get(t["procedure"])
        if not spec:
            continue
        pt = pts.get(t["patient_id"], {})
        days = benefit_days_left(pt, ref)
        expiry_boost = 1.0
        expiry_note = "benefit year end not on file"
        if days is not None:
            expiry_boost = 1.5 if days <= 60 else 1.25 if days <= 120 else 1.0
            expiry_note = f"{days} days of benefit year left"
        resp = pt.get("responsiveness")
        resp_factor = 1.0 if resp is None else 0.7 + 0.6 * resp
        score = spec["fee"] * URGENCY_WEIGHT[spec["urgency"]] * expiry_boost * resp_factor
        out.append({
            "id": t["id"], "patient_id": t["patient_id"], "patient": pt.get("name"),
            "procedure": t["procedure"], "label": spec["label"], "fee": spec["fee"],
            "tooth": t.get("tooth"), "diagnosed_at": t.get("diagnosed_at"),
            "diagnosed_by": t.get("diagnosed_by"),
            "score": round(score, 1),
            "why": [f"${spec['fee']:,} production", f"{spec['urgency']} clinically (as diagnosed)",
                    expiry_note,
                    "responsiveness not recorded" if resp is None else f"answers {round(resp*100)}% of the time"],
        })
    out.sort(key=lambda r: -r["score"])
    return out[:limit] if limit else out


def unscheduled_total(ref=None):
    rows = rank_unscheduled(ref=ref)
    if not rows:
        return unmeasured("no diagnosed-unscheduled treatment on file", field="amount", n=0)
    return {"amount": round(sum(r["fee"] for r in rows), 2), "n": len(rows)}


# ---------------------------------------------------------------- the same-day fill

def fits(freed, procedure):
    """A hygiene opening cannot be filled with a crown. This is the constraint
    most schedule-filling tools quietly ignore."""
    spec = PROCEDURES.get(procedure)
    if not spec:
        return False, "unknown procedure"
    if spec["provider"] != freed["provider_type"]:
        return False, f"needs a {spec['provider']} chair, this opening is {freed['provider_type']}"
    if spec["minutes"] > freed["minutes"]:
        return False, f"needs {spec['minutes']}m, the opening is {freed['minutes']}m"
    return True, f"{spec['minutes']}m fits the {freed['minutes']}m {freed['provider_type']} opening"


def fill_candidates(freed, ref=None):
    """Ranked ASAP list for one freed slot: fit first, then value, then the
    human factors (distance, stated flexibility, history of taking short notice)."""
    ref = ref or now()
    pts = store.index("patients")
    out, rejected = [], []
    for t in rank_unscheduled(ref=ref):
        ok, why = fits(freed, t["procedure"])
        if not ok:
            rejected.append({"patient": t["patient"], "procedure": t["procedure"], "why": why})
            continue
        pt = pts.get(t["patient_id"], {})
        sn = pt.get("short_notice_history")
        out.append({**t, "distance_min": pt.get("distance_min"),
                    "flexible": bool(pt.get("flexible")),
                    "short_notice_history": sn,
                    "fit_why": why,
                    "rank_why": ("flexible" if pt.get("flexible") else "not on the flexible list")
                    + (f", took short notice {sn} of the last 5 times" if sn is not None
                       else ", no short-notice history recorded")})
    out.sort(key=lambda r: (-(1 if r["flexible"] else 0), -(r["short_notice_history"] or 0),
                            r["distance_min"] or 99, -r["fee"]))
    return {"candidates": out[:12], "rejected_sample": rejected[:8],
            "note": "ranked by who will actually come, then by value — a $2,450 implant that "
                    "cannot get here in 40 minutes fills nothing"}


# ---------------------------------------------------------------- recall

RECALL_INTERVALS = {"prophy": 182, "perio_maint": 91}


def recall_due(patient, ref=None):
    ref = ref or now()
    last = patient.get("last_hygiene")
    interval = RECALL_INTERVALS.get(patient.get("hygiene_type", "prophy"), 182)
    if not last:
        return {"state": "unknown", "_missing": "no hygiene history on file for this patient"}
    since = -(days_until(last, ref) or 0)
    days_left = benefit_days_left(patient, ref)
    hook = ("benefits" if days_left is not None and days_left <= 75 and since >= interval * 0.8
            else "due" if since >= interval else "not_yet")
    return {"state": "overdue" if since > interval else "due" if since >= interval * 0.9 else "current",
            "days_since": since, "interval": interval, "hook": hook,
            "benefit_days_left": days_left,
            "why": ("their benefits expire before their next due date — that is the honest hook"
                    if hook == "benefits" else "standard interval")}


# ---------------------------------------------------------------- autonomy

MATRIX = Matrix({
    "rank_unscheduled":   dict(rung="R3", reason="ranking treatment a dentist already diagnosed is arithmetic over the ledger"),
    "draft_reactivation": dict(rung="R1", reason="outbound about someone's treatment — drafted, sent by a human until the streak and calibration earn R2"),
    "offer_fill_slot":    dict(rung="R2", reason="offering an existing opening to a patient whose treatment genuinely fits it; the patient accepts or ignores it"),
    "book_from_fill":     dict(rung="R2", reason="books only into the freed slot, only a procedure that fits the chair and the provider"),
    "run_verification":   dict(rung="R3", reason="asking a payer what it covers changes nothing and commits nobody"),
    "state_coverage":     dict(rung="R1", reason="telling a patient what will be paid is a financial statement the practice owns — and it is blocked outright unless the payer confirmed it", never_promote=True),
    "clinical_opinion":   dict(rung="R0", reason="THE SYSTEM NEVER DOES THIS. No diagnosis, no treatment suggestion, no interpretation of a finding — it only moves what a dentist already diagnosed", never_promote=True),
    "recall_touch":       dict(rung="R2", reason="a due-date reminder against a recorded interval"),
    "message_custom":     dict(rung="R1", reason="free text to a patient can become a clinical or financial claim"),
    "close_unscheduled":  dict(rung="R2", reason="recording a decline with a reason is bookkeeping; reopening is one click"),
})
gate = Gate(store, MATRIX)

MOVING_KINDS = {"draft_reactivation", "reactivation_sent", "offer_fill_slot", "book_from_fill",
                "run_verification", "state_coverage", "recall_touch", "message_custom",
                "close_unscheduled"}


def automation(days=90):
    return automation_rate(store.load("events"), MOVING_KINDS, days, exclude_actors=("patient:",))


# ---------------------------------------------------------------- eval
#
# The costly error here is not "got the plan rule wrong". It is telling the
# practice something is COVERED when the payer never confirmed it — that error
# has a dollar value and a patient attached to it.

COVERAGE_EVAL = Eval(
    "coverage confirmation", "unconfirmed",
    "a benefit reported as covered when the payer never confirmed it is the error that costs "
    "the practice money and the patient their trust — measured alone, and it must be zero")


def eval_coverage():
    cases = []
    for key, p in PAYERS.items():
        pt = {"id": f"t_{key}", "coverage_active": True, "benefits_used": 300,
              "procedures_this_year": {"prophy": 2}, "months_enrolled": 3}
        cases.append({"input": f"{key}|crown", "label": "unconfirmed" if not p["responds"] else "confirmable"})
        cases.append({"input": f"{key}|prophy", "label": "unconfirmed" if not p["responds"] else "confirmable"})
    # a patient with no enrollment date can never be confirmed on a waiting-period plan
    cases.append({"input": "meridian|crown|no_enroll", "label": "unconfirmed"})
    cases.append({"input": "cardinal|implant|no_enroll", "label": "unconfirmed"})

    def predict(inp):
        parts = inp.split("|")
        key, proc = parts[0], parts[1]
        pt = {"id": "t", "coverage_active": True, "benefits_used": 300,
              "procedures_this_year": {"prophy": 0},
              "months_enrolled": None if len(parts) > 2 else 24}
        v = verify(pt, key, proc)
        return "confirmable" if v["verdict"] == "confirmed" else "unconfirmed"

    return COVERAGE_EVAL.run(cases, predict)


# ---------------------------------------------------------------- the chair board

def chair_board(ref=None):
    ref = ref or now()
    tomorrow = (ref + timedelta(days=1)).date()
    appts = [a for a in store.load("appointments")
             if (parse(a["starts_at"]) or ref).date() == tomorrow]
    scheduled = sum(PROCEDURES.get(a["procedure"], {}).get("fee", 0) for a in appts
                    if a.get("state") == "scheduled")
    holes = [a for a in appts if a.get("state") == "open"]
    hole_value = sum(_hole_value(h) for h in holes)
    ver = [v for v in store.load("verifications")
           if (parse(v.get("checked_at")) or ref).date() >= ref.date()]
    exceptions = [v for v in ver if v.get("verdict") != "confirmed"]
    return {
        "generated": iso(ref),
        "tomorrow_production": {"amount": round(scheduled, 2), "appointments": len(appts),
                                "basis": "scheduled procedures at the practice's own fee schedule"},
        "holes": {"n": len(holes), "amount": round(hole_value, 2),
                  "basis": "each opening valued at the best-fitting unscheduled treatment for that "
                           "chair, not at an average"},
        "verification_exceptions": len(exceptions),
        "unscheduled": unscheduled_total(ref),
        "automation": automation(),
        "recovered": recovered(ref),
    }


def _hole_value(hole):
    freed = {"provider_type": hole.get("provider_type", "dds"), "minutes": hole.get("minutes", 60)}
    c = fill_candidates(freed)["candidates"]
    return c[0]["fee"] if c else 0


def recovered(ref=None, days=7):
    """Counted, and narrow: production scheduled out of the unscheduled ledger or
    a fill offer, whose event log shows an agent touch first."""
    ref = ref or now()
    since = ref - timedelta(days=days)
    hits = [e for e in store.load("events")
            if e["kind"] in ("book_from_fill", "reactivation_sent")
            and (parse(e["at"]) or ref) >= since]
    if not hits:
        return unmeasured(f"nothing recovered in the last {days} days that the log can attribute",
                          field="amount", n=0)
    amt = sum((e.get("detail") or {}).get("fee", 0) for e in hits)
    return {"amount": round(amt, 2), "n": len(hits),
            "basis": "only production whose event log shows an agent touch before it was booked"}


# ---------------------------------------------------------------- ROI

ROI = (Roi("What the chair is worth here")
       .line("Unscheduled recovery", "revenue",
             "unscheduled treatment $ × contact% × acceptance%",
             ["unscheduled_value", "contact_rate", "acceptance_rate"],
             lambda g: g["unscheduled_value"] * g["contact_rate"] * g["acceptance_rate"],
             note="unscheduled value is counted from your own ledger",
             assumption="acceptance% is on treatment a dentist already diagnosed and presented")
       .line("Fill recovery", "revenue",
             "canceled chair-hours/wk × fill% × production per chair-hour × 48",
             ["canceled_hours_wk", "fill_rate", "production_per_chair_hour"],
             lambda g: g["canceled_hours_wk"] * g["fill_rate"] * g["production_per_chair_hour"] * 48,
             note="chair-hours do not bank — an unfilled hour is gone, not deferred")
       .line("Recall recovery", "revenue",
             "overdue patients × reactivation% × annual patient value",
             ["overdue_patients", "reactivation_rate", "annual_patient_value"],
             lambda g: g["overdue_patients"] * g["reactivation_rate"] * g["annual_patient_value"])
       .line("Verification time", "time_saved",
             "verifications/wk × minutes each × 48 × loaded rate",
             ["verifications_wk", "minutes_each", "loaded_rate"],
             lambda g: g["verifications_wk"] * (g["minutes_each"] / 60) * 48 * g["loaded_rate"],
             note="staff time. Reported apart from production and never added into it — an ROI "
                  "panel that sums hours-saved with dollars-earned is how you lose a technical "
                  "owner in one meeting"))


def roi(given=None):
    cfg = store.load("config")
    recorded = {}
    u = unscheduled_total()
    if not u.get("_missing"):
        recorded["unscheduled_value"] = u["amount"]
    pts = store.load("patients")
    overdue = [p for p in pts if recall_due(p).get("state") == "overdue"]
    if overdue:
        recorded["overdue_patients"] = len(overdue)
    appts = [a for a in store.load("appointments") if a.get("state") == "complete"]
    if len(appts) >= 40:
        fees = [PROCEDURES.get(a["procedure"], {}).get("fee", 0) for a in appts]
        mins = [PROCEDURES.get(a["procedure"], {}).get("minutes", 60) for a in appts]
        recorded["production_per_chair_hour"] = round(sum(fees) / (sum(mins) / 60), 2)
    merged = dict(recorded)
    merged.update({k: v for k, v in (cfg.get("roi_inputs") or {}).items() if v not in (None, "")})
    merged.update({k: v for k, v in (given or {}).items() if v not in (None, "")})
    out = ROI.render(merged)
    out["recorded"] = recorded
    out["operator_supplied"] = {k: v for k, v in merged.items() if k not in recorded}
    return out
