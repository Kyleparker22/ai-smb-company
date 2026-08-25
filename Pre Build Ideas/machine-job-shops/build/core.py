#!/usr/bin/env python3
"""Traveler OS — domain core (CNC job shop).

Rules live here: RFQ cert-flag detection, the material freshness rule, the
cert gate on shipping, promise dates from recorded capacity, counted OTD,
and the matrix.

Stdlib only. Honesty rules come from `_kit`.
"""
import math, re, sys
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent))

from _kit.moat import Eval, Gate, Matrix, Roi                       # noqa: E402
from _kit.store import (Store, automation_rate, iso, median, now,   # noqa: E402
                        parse, unmeasured)

TABLES = ("config", "machines", "jobs", "materials", "rfqs", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="TRAVELEROS_DATA_ROOT")

MATERIAL_FRESH_DAYS = 14

# ---------------------------------------------------------------- RFQ cert flags

CERT_SIGNALS = (
    ("as9100", r"\bas ?9100\b|\baerospace\b|\bnadcap\b|\bflight (hardware|critical)\b|"
               r"\bsource inspection\b"),
    ("itar", r"\bitar\b|\bexport.?controll?ed\b|\bdfars\b"),
    ("medical", r"\bmedical\b|\biso ?13485\b|\bimplant|\bfda\b|\bsurgical\b|\bdhr\b|"
                r"\bdevice history\b"),
    ("traceability", r"\b(material )?certs?\b|\btraceab|\bcert(ification)?s? required\b|"
                     r"\bheat (lot|number)|\bmill cert\b|\bcofc\b|\bfirst article\b|\bppap\b"),
)


def rfq_flags(text):
    """Which cert regimes an RFQ names. Missing one is the costly error: the
    part gets quoted and built like a bracket for a barbecue."""
    t = (text or "").lower()
    flags = [kind for kind, rx in CERT_SIGNALS if re.search(rx, t)]
    return {"cert_required": bool(flags), "flags": flags,
            "why": ("cert language found: " + ", ".join(flags)) if flags
                   else "no cert language found — quoted as commercial work"}


# ---------------------------------------------------------------- material freshness

def material_check(key, ref=None):
    ref = ref or now()
    m = store.by_id("materials", key)
    if not m or m.get("price") is None:
        return {"ok": False,
                "refused": f"no recorded price for material {key!r} — nothing is quoted off a "
                           f"guess; record today's price first"}
    priced = parse(m.get("priced_at"))
    if not priced:
        return {"ok": False, "refused": f"material {key!r} has a price but no priced-at date — "
                                        f"an undated price is a guess with a number on it"}
    age = (ref - priced).days
    if age > MATERIAL_FRESH_DAYS:
        return {"ok": False,
                "refused": f"material {key!r} was priced {age} days ago (limit "
                           f"{MATERIAL_FRESH_DAYS}) — metal moved; reprice it before quoting"}
    return {"ok": True, "price": m["price"], "age_days": age}


def quote_rfq(rfq):
    """A quote needs a fresh material price and a recorded machine rate."""
    mat = material_check(rfq.get("material"))
    if not mat["ok"]:
        return {"refused": mat["refused"]}
    rate = store.load("config").get("machine_rate_hr")
    if not rate:
        return {"refused": "no machine rate recorded — shop cost is a fact, not a feeling"}
    hours = rfq.get("est_hours")
    if not hours:
        return {"refused": "no estimated hours on the RFQ — an estimator sets hours, then the "
                           "arithmetic runs"}
    material_cost = mat["price"] * (rfq.get("material_qty") or 1)
    labor = hours * rate
    margin = store.load("config").get("margin_floor", 0.35)
    total = (material_cost + labor) * (1 + margin)
    return {"total": round(total, 2),
            "lines": {"material": round(material_cost, 2), "labor": round(labor, 2),
                      "margin_floor": margin},
            "material_age_days": mat["age_days"],
            "note": "arithmetic shown — material is fresh, rate is recorded, margin floor applied"}


# ---------------------------------------------------------------- the cert gate

def can_ship(job):
    """A cert-required job cannot ship without its paper. 'Cannot certify.'"""
    if not job.get("cert_required"):
        return True, "commercial work — ships on inspection sign-off"
    missing = []
    if not job.get("material_cert_id"):
        missing.append("material cert (heat/lot traceability)")
    if not job.get("inspection_id"):
        missing.append("inspection record")
    if missing:
        return False, (f"cannot certify — missing: {', '.join(missing)}. A cert-required part "
                       f"without its paper is a customer gone and a liability held.")
    return True, f"certs on file ({job['material_cert_id']}, {job['inspection_id']})"


# ---------------------------------------------------------------- promise dates

def promise_date(hours_needed, ref=None):
    """Computed from recorded capacity minus booked hours. No capacity → no
    promise. A date without math is a broken promise scheduled early."""
    ref = ref or now()
    machines = store.load("machines")
    if not machines or not any(m.get("capacity_hrs_wk") for m in machines):
        return unmeasured("no machine capacity recorded — no date is promised without the math",
                          field="date")
    weekly = sum(m.get("capacity_hrs_wk") or 0 for m in machines)
    booked = sum(j.get("hours_remaining") or 0 for j in store.load("jobs")
                 if not j.get("shipped_at"))
    if weekly <= 0:
        return unmeasured("recorded capacity is zero", field="date")
    weeks_out = booked / weekly + (hours_needed or 0) / weekly
    d = ref + timedelta(weeks=weeks_out)
    return {"date": iso(d), "weeks_out": round(weeks_out, 1),
            "basis": f"{booked:.0f}h booked ÷ {weekly:.0f}h/wk capacity + this job's "
                     f"{hours_needed or 0}h — arithmetic, not optimism"}


OTD_FLOOR = 20


def otd(window_days=180):
    cutoff = now() - timedelta(days=window_days)
    done = [j for j in store.load("jobs")
            if j.get("shipped_at") and (parse(j["shipped_at"]) or now()) >= cutoff
            and j.get("promised_at")]
    if len(done) < OTD_FLOOR:
        return unmeasured(f"only {len(done)} shipped jobs with promise dates in {window_days} "
                          f"days — need {OTD_FLOOR}", field="rate", n=len(done))
    on_time = [j for j in done if parse(j["shipped_at"]) <= parse(j["promised_at"])]
    return {"rate": round(len(on_time) / len(done), 3), "on_time": len(on_time), "of": len(done),
            "note": "shipped-by-promise, counted — the number customers actually experience"}


def recovered_this_week(ref=None):
    """Counted, never asserted: quotes a human sent, jobs released to ship
    (through the cert gate), and promise dates a human committed, inside 7 days."""
    ref = ref or now()
    quotes = shipped = promised = 0
    for e in store.events():
        at = parse(e.get("at"))
        if not at or (ref - at).days > 7 or not str(e.get("actor", "")).startswith("human:"):
            continue
        if e["kind"] == "draft_quote":
            quotes += 1
        elif e["kind"] == "release_to_ship":
            shipped += 1
        elif e["kind"] == "draft_promise_date":
            promised += 1
    return {"quotes_sent": quotes, "jobs_shipped": shipped, "dates_committed": promised,
            "note": "counted from the event log — never asserted"}


# ---------------------------------------------------------------- eval

flag_eval = Eval("RFQ cert-flag detection",
                 costly_label="cert",
                 costly_note=("A MISSED CERT FLAG MEANS THE PART GETS QUOTED AND BUILT LIKE A "
                              "BRACKET FOR A BARBECUE — AND SHIPS WITHOUT ITS PAPER. "
                              "Over-flagging costs an estimator a question."))

EVAL_CASES = [
    {"input": "qty 200 brackets, 6061, AS9100 required, certs with shipment", "label": "cert"},
    {"input": "titanium spacers for a medical implant assembly, ISO 13485 shop preferred", "label": "cert"},
    {"input": "need full material traceability and first article inspection report", "label": "cert"},
    {"input": "ITAR controlled drawing attached, do not distribute", "label": "cert"},
    {"input": "mill certs and heat lot numbers required with delivery", "label": "cert"},
    {"input": "qty 50 pins, 303 stainless, no finish, need by friday", "label": "commercial"},
    {"input": "simple aluminum plate, 12x12, 10 pieces", "label": "commercial"},
    {"input": "rehearsal bracket for the bbq trailer build", "label": "commercial"},
    {"input": "flight hardware, source inspection required before ship", "label": "cert"},
    {"input": "parts go on a surgical robot arm, dhr paperwork needed", "label": "cert"},
    {"input": "export controlled per ear99, keep the prints in-house", "label": "cert"},
    {"input": "20 weld fixtures for the shop next door, no paper needed", "label": "commercial"},
    {"input": "cnc'd knobs for a guitar pedal run", "label": "commercial"},
]


def run_eval():
    return flag_eval.run(EVAL_CASES,
                         lambda t: "cert" if rfq_flags(t)["cert_required"] else "commercial")


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "scan_rfq":          {"rung": "R3", "reason": "flag detection with an over-flagging bias; the estimator reviews"},
    "draft_quote":       {"rung": "R1", "reason": "money + promise — a human sends, and only off fresh inputs"},
    "quote_stale_material": {"rung": "R0", "reason": "metal moved — a stale price is a guess with a number on it", "never_promote": True},
    "ship_without_certs": {"rung": "R0", "reason": "a cert-required part without its paper is a customer gone and a liability held", "never_promote": True},
    "waive_inspection":  {"rung": "R0", "reason": "nobody clicks past an inspection", "never_promote": True},
    "promise_without_capacity": {"rung": "R0", "reason": "a date without math is a broken promise scheduled early", "never_promote": True},
    "draft_promise_date": {"rung": "R1", "reason": "a promise is outward — a human commits, with the arithmetic shown"},
    "release_to_ship":   {"rung": "R1", "reason": "shipping is outward — a human releases, past the cert gate"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Traveler OS — what it computes to")
        .line("Same-day quotes won", "revenue", "RFQs/yr × win lift × avg job",
              ["rfqs_yr", "win_lift", "avg_job"],
              lambda g: float(g["rfqs_yr"]) * float(g["win_lift"]) * float(g["avg_job"]),
              note="RFQs are counted; the win lift is your history")
        .line("Quoting and paperwork time", "time_saved", "hrs/wk × 52 × rate",
              ["quote_hours_wk", "estimator_rate"],
              lambda g: float(g["quote_hours_wk"]) * 52 * float(g["estimator_rate"]))
        .line("Expedites avoided", "scenario", "broken promises/yr × avg expedite cost",
              ["broken_promises_yr", "avg_expedite"],
              lambda g: float(g["broken_promises_yr"]) * float(g["avg_expedite"]),
              assumption="an exposure you weigh")
        .line("The cert discipline", "scenario", "you decide what the aerospace customer is worth",
              ["cert_value"], lambda g: float(g["cert_value"]),
              assumption="never a saving — priced by you or blank"))


def roi(given):
    rec = {"rfqs_yr": len(store.load("rfqs"))}
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("scan_rfq", "draft_quote", "draft_promise_date", "release_to_ship")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("customer:",))
