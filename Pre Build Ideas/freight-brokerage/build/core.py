#!/usr/bin/env python3
"""Carrier OS — domain core (freight brokerages · 3PLs).

Everything that is a *rule* lives here: the carrier and load models, the trust
score and its components with timestamps and staleness de-rating, every fraud
tripwire as a separately testable function, the rate benchmark and its
minimum-sample rule, exception typing, the ROI model and the autonomy matrix.

The product thesis: a broker's business is a trust decision made under time
pressure, dozens of times a day. Getting it wrong means double-brokered freight,
a stolen load and a customer gone.

THE CENTRAL DESIGN IDEA — the autonomy asymmetry:
    the system may REFUSE a carrier on its own (refusing is the safe direction)
    but may NEVER approve one, never release a load, and never dispatch.
Human release is R1 permanently, excluded from promotion, and proved by a test.

The system also never asserts a carrier IS fraudulent. It reports which
tripwires fired and on what evidence.

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

TABLES = ("config", "carriers", "loads", "offers", "lanes", "checkcalls",
          "tripwire_log", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="CARRIEROS_DATA_ROOT")


# ---------------------------------------------------------------- staleness
#
# Public safety and authority data goes stale. A score component computed from a
# 400-day-old snapshot is not the same fact as one from this morning, and a
# system that treats them alike is lying quietly.

FRESH_DAYS = 7
STALE_DAYS = 60


def freshness(checked_at, ref=None):
    age = -(days_until(checked_at, ref) or 0) if checked_at else None
    if age is None:
        return {"weight": 0.0, "label": "never checked",
                "why": "no timestamp on this component — it contributes nothing to the score"}
    if age <= FRESH_DAYS:
        return {"weight": 1.0, "label": f"{age}d old", "why": "current"}
    if age <= STALE_DAYS:
        w = round(1.0 - (age - FRESH_DAYS) / (STALE_DAYS - FRESH_DAYS) * 0.6, 2)
        return {"weight": w, "label": f"{age}d old", "why": "ageing — de-rated"}
    return {"weight": 0.2, "label": f"{age}d old",
            "why": f"older than {STALE_DAYS} days — heavily de-rated, not treated as current"}


# ---------------------------------------------------------------- the trust file

COMPONENTS = ("authority", "insurance", "safety", "contact_consistency", "our_history")


def trust_file(carrier, load=None, ref=None):
    """A scored file where every component carries its evidence and timestamp.

    The score is never a bare number: `components` is the product, and a broker
    who disagrees with the number can see exactly which line to argue with.
    """
    ref = ref or now()
    comps, notes = {}, []

    # -- authority
    f = freshness(carrier.get("authority_checked_at"), ref)
    age_days = -(days_until(carrier.get("authority_since"), ref) or 0) if carrier.get("authority_since") else None
    if carrier.get("authority_status") != "active":
        auth = 0.0
        notes.append(f"authority is {carrier.get('authority_status', 'unknown')}")
    elif age_days is None:
        auth = 0.4
        notes.append("authority start date not on file")
    elif age_days < 90:
        auth = 0.25
        notes.append(f"authority is {age_days} days old")
    elif age_days < 365:
        auth = 0.65
        notes.append(f"authority is {age_days} days old")
    else:
        auth = 1.0
        notes.append(f"authority {round(age_days / 365, 1)} years old")
    comps["authority"] = {"raw": auth, "freshness": f, "evidence": carrier.get("authority_status"),
                          "checked_at": carrier.get("authority_checked_at")}

    # -- insurance, measured against THIS load's transit window
    f = freshness(carrier.get("insurance_checked_at"), ref)
    exp = carrier.get("insurance_expires")
    cargo = carrier.get("cargo_limit") or 0
    need = (load or {}).get("value", 0)
    ins = 1.0
    if not exp:
        ins = 0.3
        notes.append("no insurance expiry on file")
    else:
        left = days_until(exp, ref)
        deliver = (load or {}).get("deliver_by")
        if left is not None and left < 0:
            ins = 0.0
            notes.append("insurance expired")
        elif deliver and parse(deliver) and parse(exp) and parse(exp) < parse(deliver):
            ins = 0.0
            notes.append(f"insurance expires {exp[:10]}, inside the transit window "
                         f"(delivery {deliver[:10]})")
        elif left is not None and left < 14:
            ins = 0.5
            notes.append(f"insurance expires in {left} days")
    if need and cargo < need:
        ins = min(ins, 0.2)
        notes.append(f"cargo limit ${cargo:,} is below the ${need:,} load value")
    comps["insurance"] = {"raw": ins, "freshness": f,
                          "evidence": {"expires": exp, "cargo_limit": cargo},
                          "checked_at": carrier.get("insurance_checked_at")}

    # -- safety
    f = freshness(carrier.get("safety_checked_at"), ref)
    oos = carrier.get("oos_rate")
    if oos is None:
        saf = 0.5
        notes.append("no inspection history on file — scored neutral, not good")
    else:
        saf = 1.0 if oos < 0.10 else 0.7 if oos < 0.25 else 0.3
        notes.append(f"out-of-service rate {oos:.0%}")
    comps["safety"] = {"raw": saf, "freshness": f, "evidence": {"oos_rate": oos},
                       "checked_at": carrier.get("safety_checked_at")}

    # -- contact consistency (the cheapest fraud signal there is)
    f = freshness(carrier.get("contact_checked_at"), ref)
    mism = []
    if carrier.get("phone") and carrier.get("registered_phone") and \
            carrier["phone"] != carrier["registered_phone"]:
        mism.append("phone does not match the registered record")
    if carrier.get("email_domain") and carrier.get("registered_domain") and \
            carrier["email_domain"] != carrier["registered_domain"]:
        mism.append("email domain does not match the registered record")
    if carrier.get("domain_age_days") is not None and carrier["domain_age_days"] < 60:
        mism.append(f"email domain is {carrier['domain_age_days']} days old")
    if carrier.get("address") and carrier.get("registered_address") and \
            carrier["address"] != carrier["registered_address"]:
        mism.append("address does not match the registered record")
    cc = 1.0 if not mism else max(0.0, 1.0 - 0.4 * len(mism))
    notes.extend(mism)
    comps["contact_consistency"] = {"raw": cc, "freshness": f, "evidence": mism,
                                    "checked_at": carrier.get("contact_checked_at")}

    # -- our own history (the only component nobody can spoof)
    hist = carrier.get("loads_with_us", 0)
    claims = carrier.get("claims_with_us", 0)
    if hist == 0:
        oh = 0.35
        notes.append("never hauled for us")
    else:
        oh = min(1.0, 0.5 + hist / 40) - min(0.5, claims * 0.25)
        notes.append(f"{hist} loads with us, {claims} claim(s)")
    comps["our_history"] = {"raw": round(oh, 2),
                            "freshness": {"weight": 1.0, "label": "our own records", "why": "not spoofable"},
                            "evidence": {"loads": hist, "claims": claims},
                            "checked_at": iso(ref)}

    # Stale evidence pulls a component toward UNKNOWN, it does not merely count
    # for less. Re-weighting alone can never lower a perfect score, so a carrier
    # whose authority was last checked 400 days ago would score exactly as well
    # as one checked this morning — which is the quiet lie this whole module
    # exists to avoid.
    NEUTRAL = 0.5
    contribs, checked = [], 0
    for k, c in comps.items():
        w = 1.0 if k == "our_history" else c["freshness"]["weight"]
        if w > 0:
            checked += 1
        c["effective"] = round(c["raw"] * w + NEUTRAL * (1 - w), 3)
        contribs.append(c["effective"])
    if checked == 0:
        return {"carrier": carrier.get("id"), "name": carrier.get("name"), "score": None,
                "_missing": "every component is unchecked — there is no score to give",
                "components": comps, "notes": notes, "generated": iso(ref)}
    score = round(sum(contribs) / len(contribs), 3)
    if checked < len(comps):
        notes.append(f"{len(comps) - checked} component(s) never checked — pulled toward neutral, "
                     f"not toward good")
    return {"carrier": carrier.get("id"), "name": carrier.get("name"), "score": score,
            "components": comps, "notes": notes, "checked_components": checked,
            "generated": iso(ref)}


# ---------------------------------------------------------------- fraud tripwires
#
# Named, individually testable, each firing with its evidence. A broker should be
# able to read this list and add their own. NONE of them asserts fraud.

def tw_new_authority_high_value(carrier, load, ctx):
    age = -(days_until(carrier.get("authority_since")) or 0) if carrier.get("authority_since") else None
    if age is not None and age < 90 and (load or {}).get("value", 0) >= 50000:
        return f"authority is {age} days old and this load is ${load['value']:,}"
    return None


def tw_contact_mismatch(carrier, load, ctx):
    bad = []
    if carrier.get("phone") and carrier.get("registered_phone") and carrier["phone"] != carrier["registered_phone"]:
        bad.append("phone")
    if carrier.get("email_domain") and carrier.get("registered_domain") and \
            carrier["email_domain"] != carrier["registered_domain"]:
        bad.append("email domain")
    if carrier.get("address") and carrier.get("registered_address") and \
            carrier["address"] != carrier["registered_address"]:
        bad.append("address")
    return (f"{', '.join(bad)} does not match the registered record" if bad else None)


def tw_recent_domain_change(carrier, load, ctx):
    d = carrier.get("domain_age_days")
    if d is not None and d < 60:
        return f"email domain registered {d} days ago"
    return None


def tw_rate_implausibly_low(carrier, load, ctx):
    bench = ctx.get("benchmark") or {}
    if bench.get("_missing") or not load or load.get("offer_rate") is None:
        return None
    b = bench.get("median")
    if b and load["offer_rate"] < b * 0.7:
        return (f"offer ${load['offer_rate']:,.0f} is {round((1 - load['offer_rate'] / b) * 100)}% "
                f"below the lane median ${b:,.0f} — nobody hauls this for that")
    return None


def tw_insurance_expires_in_transit(carrier, load, ctx):
    exp, deliver = carrier.get("insurance_expires"), (load or {}).get("deliver_by")
    if exp and deliver and parse(exp) and parse(deliver) and parse(exp) < parse(deliver):
        return f"insurance expires {exp[:10]}, delivery is {deliver[:10]}"
    return None


def tw_equipment_mismatch(carrier, load, ctx):
    need = (load or {}).get("equipment")
    have = carrier.get("equipment") or []
    if need and have and need not in have:
        return f"load needs {need}, carrier is registered for {', '.join(have)}"
    return None


def tw_cargo_below_value(carrier, load, ctx):
    cargo, value = carrier.get("cargo_limit") or 0, (load or {}).get("value") or 0
    if value and cargo < value:
        return f"cargo limit ${cargo:,} is below the ${value:,} load value"
    return None


def tw_authority_not_active(carrier, load, ctx):
    st = carrier.get("authority_status")
    if st and st != "active":
        return f"authority status is '{st}'"
    return None


TRIPWIRES = {
    "new_authority_high_value": tw_new_authority_high_value,
    "contact_mismatch": tw_contact_mismatch,
    "recent_domain_change": tw_recent_domain_change,
    "rate_implausibly_low": tw_rate_implausibly_low,
    "insurance_expires_in_transit": tw_insurance_expires_in_transit,
    "equipment_mismatch": tw_equipment_mismatch,
    "cargo_below_value": tw_cargo_below_value,
    "authority_not_active": tw_authority_not_active,
}

# Any of these firing is enough to refuse on its own.
HARD_STOPS = {"authority_not_active", "insurance_expires_in_transit", "cargo_below_value"}


def run_tripwires(carrier, load, ctx=None):
    ctx = ctx or {}
    fired = []
    for name, fn in TRIPWIRES.items():
        ev = fn(carrier, load, ctx)
        if ev:
            fired.append({"tripwire": name, "evidence": ev, "hard_stop": name in HARD_STOPS})
    return fired


# ---------------------------------------------------------------- the rate benchmark

MIN_SAMPLE = 8


def benchmark(lane_key, equipment, ref=None, weeks=26):
    """From OUR OWN booked history. Below the minimum sample it refuses — a
    benchmark computed off three loads is a number a broker will disprove from
    memory in the same meeting."""
    ref = ref or now()
    rows = [l for l in store.load("loads")
            if l.get("lane") == lane_key and l.get("equipment") == equipment
            and l.get("carrier_rate") and (parse(l.get("booked_at")) or ref) >= ref - timedelta(weeks=weeks)]
    if len(rows) < MIN_SAMPLE:
        return unmeasured(f"only {len(rows)} booked loads on {lane_key}/{equipment} in {weeks} "
                          f"weeks; need {MIN_SAMPLE} before a benchmark means anything",
                          field="median", n=len(rows))
    rates = [l["carrier_rate"] for l in rows]
    return {"median": round(median(rates), 2), "low": round(min(rates), 2),
            "high": round(max(rates), 2), "n": len(rates), "weeks": weeks}


def margin_by_lane(weeks=26, floor=MIN_SAMPLE):
    out = {}
    for l in store.load("loads"):
        if not (l.get("customer_rate") and l.get("carrier_rate")):
            continue
        out.setdefault(l["lane"], []).append(l["customer_rate"] - l["carrier_rate"])
    res = {}
    for lane, margins in out.items():
        if len(margins) < floor:
            res[lane] = unmeasured(f"only {len(margins)} booked loads on this lane; need {floor}",
                                   field="median_margin", n=len(margins))
        else:
            res[lane] = {"median_margin": round(median(margins), 2), "n": len(margins)}
    return res


# ---------------------------------------------------------------- exceptions

EXCEPTION_TYPES = {
    "late_departure": dict(label="Late departure", severity="medium"),
    "dwell": dict(label="Excessive dwell", severity="medium"),
    "off_route": dict(label="Off route", severity="high"),
    "silence": dict(label="No contact past threshold", severity="high"),
    "late_delivery_risk": dict(label="Will miss delivery", severity="high"),
}
SILENCE_HOURS = 6
DWELL_HOURS = 3


def load_exceptions(load, ref=None):
    ref = ref or now()
    out = []
    last = load.get("last_contact_at")
    if load.get("state") == "in_transit":
        if not last:
            out.append({"type": "silence", "evidence": "no contact recorded since dispatch"})
        else:
            hrs = -(days_until(last, ref) or 0) * 24
            gap = round((ref - (parse(last) or ref)).total_seconds() / 3600, 1)
            if gap > SILENCE_HOURS:
                out.append({"type": "silence", "evidence": f"{gap}h since last contact"})
        if load.get("dwell_hours", 0) > DWELL_HOURS:
            out.append({"type": "dwell", "evidence": f"{load['dwell_hours']}h at the shipper"})
        if load.get("off_route_miles", 0) > 50:
            out.append({"type": "off_route", "evidence": f"{load['off_route_miles']} miles off route"})
        eta, due = load.get("eta"), load.get("deliver_by")
        if eta and due and parse(eta) and parse(due) and parse(eta) > parse(due):
            out.append({"type": "late_delivery_risk",
                        "evidence": f"ETA {eta[:16]} is past the {due[:16]} appointment"})
    for o in out:
        o["severity"] = EXCEPTION_TYPES[o["type"]]["severity"]
        o["label"] = EXCEPTION_TYPES[o["type"]]["label"]
        o["suggested"] = _suggested(o["type"])
    return out


def _suggested(kind):
    return {
        "silence": "text the driver; if no answer in 30 minutes, call the carrier's dispatch line",
        "dwell": "call the shipper for a loading status and reset the customer's expectation",
        "off_route": "call the driver — confirm route, then decide whether the customer needs telling",
        "late_delivery_risk": "call the receiver about the appointment before the customer does",
        "late_departure": "confirm the driver is rolling and reset the ETA",
    }[kind]


# ---------------------------------------------------------------- autonomy

MATRIX = Matrix({
    "score_carrier":      dict(rung="R3", reason="assembling a file from data we already hold commits nobody"),
    "refuse_carrier":     dict(rung="R3", reason="REFUSING is the safe direction. A wrong refusal costs one phone call; a wrong approval costs a cargo claim and a customer — so this is the one action that is safer automatic than gated"),
    "approve_carrier":    dict(rung="R1", reason="THE SYSTEM NEVER DOES THIS ALONE. A human approves every carrier, whatever the score, and this action is permanently excluded from promotion", never_promote=True),
    "release_load":       dict(rung="R1", reason="THE SYSTEM NEVER RELEASES A LOAD. Tendering freight is the moment the money is at risk", never_promote=True),
    "dispatch":           dict(rung="R1", reason="dispatching is a commitment to a customer and a driver", never_promote=True),
    "rank_offers":        dict(rung="R3", reason="ranking offers against our own booked history is arithmetic"),
    "collect_status":     dict(rung="R2", reason="asking a driver where they are, on a load-appropriate cadence"),
    "raise_exception":    dict(rung="R3", reason="raising a hand is always the safe direction"),
    "notify_customer":    dict(rung="R1", reason="what a customer is told about their freight is the broker's word, not ours"),
    "log_tripwire":       dict(rung="R3", reason="recording that a pattern fired, with its evidence"),
    "assert_fraud":       dict(rung="R0", reason="THE SYSTEM NEVER DOES THIS. It reports which tripwires fired and on what evidence. Calling a company fraudulent is a claim with legal consequences and we do not make it", never_promote=True),
})
gate = Gate(store, MATRIX)

MOVING_KINDS = {"score_carrier", "refuse_carrier", "approve_carrier", "release_load", "dispatch",
                "rank_offers", "collect_status", "raise_exception", "notify_customer"}


def automation(days=90):
    return automation_rate(store.load("events"), MOVING_KINDS, days, exclude_actors=("carrier:",))


# ---------------------------------------------------------------- evals
#
# Each tripwire is scored INDEPENDENTLY, and the false-NEGATIVE rate is reported
# separately: a missed fraud costs a claim, a false positive costs a phone call.

TRIPWIRE_EVAL = Eval(
    "tripwires (all)", "should_fire",
    "a missed pattern costs a cargo claim; a false alarm costs a phone call — the false-negative "
    "rate is what matters and it is reported alone")


def eval_tripwires():
    ref = now()
    clean = dict(id="c_clean", name="Clean", authority_status="active",
                 authority_since=iso(ref - timedelta(days=1500)),
                 insurance_expires=iso(ref + timedelta(days=200)), cargo_limit=100000,
                 phone="555-0100", registered_phone="555-0100",
                 email_domain="clean.example", registered_domain="clean.example",
                 address="1 Main", registered_address="1 Main", domain_age_days=2000,
                 equipment=["van", "reefer"], oos_rate=0.04, loads_with_us=30, claims_with_us=0)
    load = {"value": 60000, "equipment": "van", "deliver_by": iso(ref + timedelta(days=3)),
            "offer_rate": 2400}
    ctx = {"benchmark": {"median": 2500}}
    cases = []
    per = {}
    for name, mutation in [
        ("new_authority_high_value", dict(authority_since=iso(ref - timedelta(days=30)))),
        ("contact_mismatch", dict(phone="555-0999")),
        ("recent_domain_change", dict(domain_age_days=12)),
        ("insurance_expires_in_transit", dict(insurance_expires=iso(ref + timedelta(days=1)))),
        ("equipment_mismatch", dict(equipment=["flatbed"])),
        ("cargo_below_value", dict(cargo_limit=25000)),
        ("authority_not_active", dict(authority_status="revoked")),
    ]:
        dirty = {**clean, **mutation}
        per[f"{name}:dirty"] = (dirty, load, ctx)
        per[f"{name}:clean"] = (clean, load, ctx)
        cases.append({"input": f"{name}:dirty", "label": "should_fire"})
        cases.append({"input": f"{name}:clean", "label": "quiet"})
    # the rate tripwire needs a low offer, not a carrier mutation
    per["rate_implausibly_low:dirty"] = (clean, {**load, "offer_rate": 1400}, ctx)
    per["rate_implausibly_low:clean"] = (clean, load, ctx)
    cases.append({"input": "rate_implausibly_low:dirty", "label": "should_fire"})
    cases.append({"input": "rate_implausibly_low:clean", "label": "quiet"})

    def predict(key):
        name = key.split(":")[0]
        c, l, x = per[key]
        return "should_fire" if TRIPWIRES[name](c, l, x) else "quiet"

    res = TRIPWIRE_EVAL.run(cases, predict)
    res["per_tripwire"] = {
        n: {"fires_on_its_pattern": bool(TRIPWIRES[n](*per[f"{n}:dirty"])),
            "quiet_otherwise": not TRIPWIRES[n](*per[f"{n}:clean"])}
        for n in TRIPWIRES}
    return res


# ---------------------------------------------------------------- the load board

def load_board(ref=None):
    ref = ref or now()
    loads = store.load("loads")
    live = [l for l in loads if l.get("state") in ("tendered", "in_transit")]
    rows = []
    for l in live:
        ex = load_exceptions(l, ref)
        rows.append({"load": l["id"], "lane": l.get("lane"), "customer": l.get("customer"),
                     "carrier": l.get("carrier_name"), "state": l.get("state"),
                     "deliver_by": l.get("deliver_by"), "exceptions": ex,
                     "worst": max((EXCEPTION_TYPES[e["type"]]["severity"] for e in ex),
                                  key=lambda s: {"high": 2, "medium": 1}.get(s, 0), default=None)})
    rows.sort(key=lambda r: (0 if r["worst"] == "high" else 1 if r["worst"] == "medium" else 2))
    carriers = store.load("carriers")
    scored = [trust_file(c, ref=ref) for c in carriers[:400]]
    dist = {"strong": 0, "middling": 0, "weak": 0, "unscoreable": 0}
    for s in scored:
        if s["score"] is None:
            dist["unscoreable"] += 1
        elif s["score"] >= 0.75:
            dist["strong"] += 1
        elif s["score"] >= 0.5:
            dist["middling"] += 1
        else:
            dist["weak"] += 1
    return {"generated": iso(ref), "rows": rows[:60],
            "at_risk": sum(1 for r in rows if r["worst"] == "high"),
            "in_transit": len(live), "trust_distribution": dist,
            "margin_by_lane": margin_by_lane(),
            "automation": automation()}


# ---------------------------------------------------------------- ROI

ROI = (Roi("What the desk is worth here")
       .line("Vetting time", "time_saved",
             "loads/wk × minutes saved × 52 × loaded ops rate",
             ["loads_wk", "vetting_minutes_saved", "loaded_rate"],
             lambda g: g["loads_wk"] * (g["vetting_minutes_saved"] / 60) * 52 * g["loaded_rate"],
             note="loads per week are counted from your own board")
       .line("Check-call time", "time_saved",
             "active loads/wk × calls each × minutes × 52 × loaded rate",
             ["loads_wk", "calls_each", "minutes_per_call", "loaded_rate"],
             lambda g: g["loads_wk"] * g["calls_each"] * (g["minutes_per_call"] / 60) * 52
             * g["loaded_rate"])
       .line("Margin capture", "revenue",
             "loads/yr × basis points from benchmark discipline × avg revenue per load",
             ["loads_yr", "margin_bps", "avg_revenue_per_load"],
             lambda g: g["loads_yr"] * (g["margin_bps"] / 10000) * g["avg_revenue_per_load"],
             assumption="basis points are yours — this is the discipline of quoting against your "
                        "own lane history rather than the last thing you paid")
       .line("Fraud exposure", "scenario",
             "loads at risk × exposure per event",
             ["loads_flagged_yr", "exposure_per_event"],
             lambda g: g["loads_flagged_yr"] * g["exposure_per_event"],
             note="A SCENARIO, NOT A SAVING. Prevented incidents cannot be counted — nobody can "
                  "tell you what a load that never got stolen was worth. What we can show is what "
                  "the tripwires caught in YOUR recorded history and what one event costs you. "
                  "You decide what that is worth."))


def roi(given=None):
    cfg = store.load("config")
    recorded = {}
    loads = store.load("loads")
    wk = [l for l in loads if (parse(l.get("booked_at")) or now()) >= now() - timedelta(days=7)]
    if wk:
        recorded["loads_wk"] = len(wk)
    if loads:
        recorded["loads_yr"] = len(loads)
        rev = [l["customer_rate"] for l in loads if l.get("customer_rate")]
        if len(rev) >= 20:
            recorded["avg_revenue_per_load"] = round(median(rev), 2)
    tw = store.load("tripwire_log")
    if tw:
        recorded["loads_flagged_yr"] = len({t["load_id"] for t in tw if t.get("load_id")})
    merged = dict(recorded)
    merged.update({k: v for k, v in (cfg.get("roi_inputs") or {}).items() if v not in (None, "")})
    merged.update({k: v for k, v in (given or {}).items() if v not in (None, "")})
    out = ROI.render(merged)
    out["recorded"] = recorded
    out["operator_supplied"] = {k: v for k, v in merged.items() if k not in recorded}
    return out
