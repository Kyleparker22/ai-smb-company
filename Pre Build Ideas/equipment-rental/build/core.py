#!/usr/bin/env python3
"""Yard OS — domain core (equipment rental).

Rules live here: billable-day arithmetic that stops at the recorded off-rent
call by construction, the damage-evidence rule, call triage with its off-rent
bias, utilization counting that refuses over missing fleet data, and the
autonomy matrix with the standing-limit waiver.

The thesis: a rental house's disputes are almost all self-inflicted — a bill
that ran past the off-rent call, a damage charge with no checkout photo behind
it. Make the first impossible and the second a matter of evidence.

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

TABLES = ("config", "customers", "fleet", "rentals", "calls", "conditions",
          "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="YARDOS_DATA_ROOT")


# ---------------------------------------------------------------- billing integrity

def billable_days(rental, ref=None):
    """Days that can be billed. The end of the billable window is the recorded
    off-rent call — BY CONSTRUCTION. There is no argument to this function that
    can produce a day after the call; that absence is the guarantee."""
    start = parse(rental.get("on_rent_at"))
    if not start:
        return unmeasured("no on-rent date recorded — nothing can be billed", field="days")
    end = parse(rental.get("off_rent_called_at")) or (ref or now())
    days = max(1, math.ceil((end - start).total_seconds() / 86400))
    out = {"days": days, "start": iso(start), "end": iso(end),
           "ends_at": "the recorded off-rent call" if rental.get("off_rent_called_at") else "today (still on rent)"}
    return out


def invoice_preview(rental, through=None, ref=None):
    """What an invoice through a given date would bill. A `through` past the
    off-rent call is CLAMPED to the call, and the clamp is named on the row."""
    bd = billable_days(rental, ref)
    if "_missing" in bd:
        return bd
    rate = rental.get("day_rate")
    if not rate:
        return unmeasured("no day rate on the rental — nothing can be priced", field="amount")
    requested_end = parse(through) if through else parse(bd["end"])
    off = parse(rental.get("off_rent_called_at"))
    clamped = False
    end = requested_end or parse(bd["end"])
    if off and end > off:
        end = off
        clamped = True
    start = parse(rental["on_rent_at"])
    days = max(1, math.ceil((end - start).total_seconds() / 86400))
    out = {"days": days, "amount": round(days * rate, 2), "rate": rate}
    if clamped:
        out["clamped"] = ("requested billing through "
                          f"{iso(requested_end)} but the off-rent call is recorded at {iso(off)} — "
                          "billing stops at the call; the days past it do not exist")
    return out


def pickup_queue(ref=None):
    """Off rent, not picked up: deployed, not earning, invisible until now."""
    ref = ref or now()
    rows = []
    for r in store.load("rentals"):
        if r.get("off_rent_called_at") and not r.get("picked_up_at"):
            called = parse(r["off_rent_called_at"])
            rows.append({"rental": r["id"], "unit": r.get("unit_id"),
                         "customer": r.get("customer_id"),
                         "days_waiting": (ref - called).days,
                         "note": "not billing (the call stopped it) and not re-rentable — the yard leak"})
    return sorted(rows, key=lambda x: -x["days_waiting"])


# ---------------------------------------------------------------- damage evidence

def damage_claim(rental_id):
    """A damage charge needs the checkout AND check-in condition records. One
    missing → 'cannot assert damage', with the missing record named."""
    conds = [c for c in store.load("conditions") if c.get("rental_id") == rental_id]
    out_rec = next((c for c in conds if c.get("kind") == "checkout"), None)
    in_rec = next((c for c in conds if c.get("kind") == "checkin"), None)
    missing = []
    if not out_rec:
        missing.append("checkout condition record")
    if not in_rec:
        missing.append("check-in condition record")
    if missing:
        return {"assertable": False,
                "refused": f"cannot assert damage — missing: {', '.join(missing)}. A charge "
                           f"without the evidence pair is an argument, not a claim."}
    new_damage = [d for d in (in_rec.get("damage") or []) if d not in (out_rec.get("damage") or [])]
    if not new_damage:
        return {"assertable": False,
                "refused": "no damage on check-in that was not already on checkout — nothing to charge"}
    return {"assertable": True, "new_damage": new_damage,
            "evidence": {"checkout": out_rec["id"], "checkin": in_rec["id"],
                         "checkout_photos": out_rec.get("photos", 0),
                         "checkin_photos": in_rec.get("photos", 0)},
            "note": "drafts at R1 — a human sends the claim with the evidence attached"}


# ---------------------------------------------------------------- call triage

CALL_PATTERNS = (
    ("off_rent", r"\b(off ?rent|pick (it |this )?up|come get|done with (it|the)|"
                 r"finished with|stop the (rental|billing)|call it off)\b"),
    ("breakdown", r"\b(broke|broken|won'?t start|died|blew a|hydraulic|leak(ing)?|"
                  r"stopped working|error code)\b"),
    ("extension", r"\b(keep it|extend|another (week|month|day)|little longer|through the)\b"),
    ("new_rental", r"\b(rent|need|looking for|do you have|availability)\b.*"
                   r"\b(excavator|skid ?steer|lift|generator|compactor|trencher|mini ?ex)\b"),
)


def classify_call(text):
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty transcript — a person answers"}
    for label, rx in CALL_PATTERNS:
        if re.search(rx, t):
            whys = {"off_rent": "off-rent request — the billing clock stops at THIS call",
                    "breakdown": "machine down — service dispatch and the billing question, a human decides",
                    "extension": "extension request",
                    "new_rental": "new rental inquiry"}
            return {"label": label, "why": whys[label]}
    return {"label": "human", "why": "no clean signal — a person answers"}


# ---------------------------------------------------------------- utilization

def utilization(ref=None):
    """Per class: units on rent / fleet, counted. A class with no fleet count
    is refused, not shown as 0% or 100%."""
    fleet = store.load("fleet")
    rentals = [r for r in store.load("rentals")
               if not r.get("off_rent_called_at") and not r.get("demo_tag")]
    on_rent_by_unit = {r.get("unit_id") for r in rentals}
    classes = {}
    for u in fleet:
        classes.setdefault(u.get("cls", "unknown"), {"fleet": 0, "on_rent": 0})
        classes[u.get("cls", "unknown")]["fleet"] += 1
        if u["id"] in on_rent_by_unit:
            classes[u.get("cls", "unknown")]["on_rent"] += 1
    rows = []
    for cls, c in sorted(classes.items()):
        if c["fleet"] == 0:
            rows.append({"cls": cls, **unmeasured("no fleet units recorded for this class", field="rate")})
        else:
            rows.append({"cls": cls, "fleet": c["fleet"], "on_rent": c["on_rent"],
                         "rate": round(c["on_rent"] / c["fleet"], 3)})
    # a class referenced by rentals but absent from the fleet file is named
    rented_classes = {r.get("cls") for r in rentals if r.get("cls")}
    for cls in sorted(rented_classes - set(classes)):
        rows.append({"cls": cls, **unmeasured("rentals reference this class but the fleet file has "
                                              "no units in it — the denominator is missing", field="rate")})
    return rows


def recovered_this_week(ref=None):
    """Counted, never asserted: units picked up (back in the yard, re-rentable),
    damage claims a human sent, and waivers issued, all inside 7 days."""
    ref = ref or now()
    picked = [r for r in store.load("rentals")
              if r.get("picked_up_at") and (ref - (parse(r["picked_up_at"]) or ref)).days <= 7]
    claims = sum(1 for e in store.events(kind="draft_damage_claim")
                 if str(e.get("actor", "")).startswith("human:")
                 and (ref - (parse(e.get("at")) or ref)).days <= 7)
    waivers = [e for e in store.events(kind="waiver_issued")
               if (ref - (parse(e.get("at")) or ref)).days <= 7]
    return {"units_picked_up": len(picked), "claims_sent": claims,
            "waivers_issued": len(waivers),
            "waiver_total": round(sum((e.get("detail") or {}).get("amount", 0) for e in waivers), 2),
            "note": "counted from the book and the event log — never asserted"}


# ---------------------------------------------------------------- eval

call_eval = Eval("call triage",
                 costly_label="off_rent",
                 costly_note=("A MISSED OFF-RENT CALL BECOMES AN OVERBILLED INVOICE, A DISPUTE, "
                              "AND A CUSTOMER SHOPPING YOUR COMPETITOR. Over-routing costs a shrug."))

EVAL_CASES = [
    {"input": "we're done with the mini ex, come get it", "label": "off_rent"},
    {"input": "you can pick up the scissor lift tomorrow, job's wrapped", "label": "off_rent"},
    {"input": "stop the billing on the generator, we finished friday", "label": "off_rent"},
    {"input": "call it off rent as of today please", "label": "off_rent"},
    {"input": "the skid steer won't start this morning", "label": "breakdown"},
    {"input": "hydraulic line is leaking on the excavator", "label": "breakdown"},
    {"input": "we need to keep the compactor another week", "label": "extension"},
    {"input": "do you have a 5k generator available next monday", "label": "new_rental"},
    {"input": "looking for a trencher for a weekend job", "label": "new_rental"},
    {"input": "", "label": "human"},
    {"input": "can you email me the invoice from last month", "label": "human"},
    {"input": "job's finished with the boom lift, come grab it whenever", "label": "off_rent"},
    {"input": "the trencher died halfway through the run", "label": "breakdown"},
    {"input": "gonna need the mini ex a little longer, through the 20th", "label": "extension"},
    {"input": "do you have availability on a skid steer this week", "label": "new_rental"},
    {"input": "error code 52 on the telehandler screen", "label": "breakdown"},
]


def run_eval():
    return call_eval.run(EVAL_CASES, lambda t: classify_call(t)["label"])


# ---------------------------------------------------------------- autonomy

WAIVER_LIMIT = 100

matrix = Matrix({
    "classify_call":     {"rung": "R3", "reason": "routing only; the off-rent bias is the point"},
    "record_off_rent":   {"rung": "R2", "reason": "recording the call stops the clock — delaying it is the harm"},
    "schedule_pickup":   {"rung": "R1", "reason": "a truck roll is a promise — a human dispatches"},
    "draft_damage_claim": {"rung": "R1", "reason": "money + relationship — and structurally needs the evidence pair"},
    "issue_waiver":      {"rung": "R2", "reason": "small goodwill credits execute and log", "limit": WAIVER_LIMIT},
    "backdate_off_rent": {"rung": "R0", "reason": "the record is the record — a backdated call is a falsified log", "never_promote": True},
    "assert_damage_without_evidence": {"rung": "R0", "reason": "a charge without the evidence pair is an argument, not a claim", "never_promote": True},
    "draft_extension_confirm": {"rung": "R1", "reason": "outward message — a human sends"},
    "pickup_overdue":    {"rung": "R2", "reason": "an internal dispatch alert — the queue is money idling"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Yard OS — what it computes to")
        .line("Pickup-queue days put back on rent", "revenue", "queue days × median day rate × re-rent share",
              ["queue_days", "median_day_rate", "rerent_share"],
              lambda g: float(g["queue_days"]) * float(g["median_day_rate"]) * float(g["rerent_share"]),
              note="queue days and the rate are counted; the re-rent share is your call")
        .line("Damage recovered with evidence", "revenue", "assertable claims × avg claim",
              ["assertable_claims", "avg_claim"],
              lambda g: float(g["assertable_claims"]) * float(g["avg_claim"]))
        .line("Billing-audit and dispute time", "time_saved", "hrs/wk × 52 × rate",
              ["dispute_hours_wk", "office_rate"],
              lambda g: float(g["dispute_hours_wk"]) * 52 * float(g["office_rate"]),
              note="reported separately; never summed into revenue")
        .line("Credit memos avoided", "scenario", "disputed invoices × avg credit",
              ["disputes_yr", "avg_credit"],
              lambda g: float(g["disputes_yr"]) * float(g["avg_credit"]),
              assumption="an exposure you weigh — avoided disputes cannot be counted"))


def roi(given):
    rec = {}
    q = pickup_queue()
    rec["queue_days"] = sum(r["days_waiting"] for r in q)
    rates = [r.get("day_rate") for r in store.load("rentals") if r.get("day_rate")]
    if len(rates) >= 20:
        rec["median_day_rate"] = round(median(rates), 2)
    assertable = 0
    for r in store.load("rentals"):
        if r.get("damage_suspected") and damage_claim(r["id"]).get("assertable"):
            assertable += 1
    rec["assertable_claims"] = assertable
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("classify_call", "record_off_rent", "schedule_pickup", "draft_damage_claim",
          "issue_waiver", "draft_extension_confirm")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("customer:",))
