#!/usr/bin/env python3
"""Haul OS — domain core (roll-off / waste hauling).

Rules live here: the prohibited-waste classifier that can never say yes to a
hazardous item, the charge-evidence rule, container idle aging, missed
pickups, and the matrix.

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

TABLES = ("config", "customers", "containers", "orders", "charges", "messages",
          "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="HAULOS_DATA_ROOT")


# ---------------------------------------------------------------- prohibited waste

# Typed hazardous classes. The rule is asymmetric on purpose: the classifier
# may wrongly say "ask a human" about drywall; it may never say "yes" to paint.
HAZARDOUS = (
    ("paint_solvents", r"\bpaint|stain|solvent|thinner|varnish\b"),
    ("batteries", r"\bbatter(y|ies)\b"),
    ("tires", r"\btires?\b"),
    ("chemicals", r"\bchemical|pesticide|herbicide|pool (chlorine|chemicals)|acid|bleach\b"),
    ("asbestos", r"\basbestos|popcorn ceiling|9x9 tile\b"),
    ("propane_fuel", r"\bpropane|gas (tank|can)|fuel|gasoline|kerosene|oil\b"),
    ("appliances_freon", r"\b(fridge|refrigerator|freezer|a/?c unit|air condition)\b"),
    ("electronics", r"\btvs?\b|\btelevision|monitor|computer|e-?waste\b"),
    ("medical", r"\bneedles?|sharps|medical waste|syringe\b"),
    ("mattress_restricted", r"\bmattress(es)?\b"),
)
ALLOWED = (
    r"\bdrywall|sheetrock\b", r"\broofing|shingles?\b", r"\blumber|wood|studs?\b",
    r"\bfurniture|couch|sofa|dresser|table\b", r"\byard waste|branches|brush\b",
    r"\bcarpet|flooring\b", r"\bcardboard|boxes\b", r"\bconcrete|brick|dirt\b",
    r"\bgeneral (junk|debris|trash)\b|\bhousehold (junk|items)\b",
)
WEIGHT_NOTE = ("heavy material (concrete, dirt, shingles) is billed by weight — the scale ticket "
               "decides, not an estimate")


def classify_item(text):
    """allowed | hazardous | unknown. The hazardous answer is a REFUSAL with
    disposal help routed to a human; the system can never approve one."""
    t = (text or "").lower().strip()
    if not t:
        return {"label": "unknown", "why": "empty question — a person answers"}
    for kind, rx in HAZARDOUS:
        if re.search(rx, t):
            return {"label": "hazardous", "kind": kind,
                    "why": f"prohibited class: {kind.replace('_', ' ')} — the system can never "
                           f"say yes to this; a human will call with disposal options"}
    for rx in ALLOWED:
        if re.search(rx, t):
            return {"label": "allowed", "note": WEIGHT_NOTE,
                    "why": "accepted material — the weight caveat rides along"}
    return {"label": "unknown",
            "why": "not on the accepted list — a person answers; 'probably fine' is how loads "
                   "get contaminated"}


# ---------------------------------------------------------------- charge evidence

def charge_check(charge):
    """overweight needs the scale ticket; contamination needs the photo record.
    Missing evidence → cannot assert, with the missing piece named."""
    kind = charge.get("kind")
    if kind == "overweight":
        if charge.get("scale_ticket_id"):
            return {"assertable": True, "evidence": charge["scale_ticket_id"],
                    "note": "drafts at R1 with the ticket attached"}
        return {"assertable": False,
                "refused": "cannot assert an overweight charge — no scale ticket on file. "
                           "'You say it was heavy' is a credit memo waiting to happen."}
    if kind == "contamination":
        if charge.get("photo_record_id"):
            return {"assertable": True, "evidence": charge["photo_record_id"],
                    "note": "drafts at R1 with the photo attached"}
        return {"assertable": False,
                "refused": "cannot assert a contamination charge — no photo record on file."}
    return {"assertable": False, "refused": f"unknown charge kind {kind!r} — a human prices it"}


# ---------------------------------------------------------------- containers

IDLE_FLAG_DAYS = 7


def idle_containers(ref=None):
    """Delivered, no pickup/swap order open — every idle day is a turn not made."""
    ref = ref or now()
    open_pulls = {o.get("container_id") for o in store.load("orders")
                  if o.get("kind") in ("pickup", "swap") and not o.get("completed_at")}
    rows = []
    for c in store.load("containers"):
        if c.get("status") != "on_site" or c["id"] in open_pulls:
            continue
        delivered = parse(c.get("delivered_at"))
        if not delivered:
            rows.append({"container": c["id"], "site": c.get("site"),
                         **unmeasured("no delivery date recorded — idle age unknowable", field="days")})
            continue
        days = (ref - delivered).days
        rows.append({"container": c["id"], "size": c.get("size"), "site": c.get("site"),
                     "days": days, "flagged": days >= IDLE_FLAG_DAYS})
    rows.sort(key=lambda r: -(r.get("days") or 0))
    return rows


def missed_pickups(ref=None):
    ref = ref or now()
    rows = []
    for o in store.load("orders"):
        if o.get("kind") not in ("pickup", "swap") or o.get("completed_at") or o.get("demo_tag"):
            continue
        promised = parse(o.get("promised_at"))
        if promised and promised < ref:
            rows.append({"order": o["id"], "container": o.get("container_id"),
                         "promised_at": o["promised_at"],
                         "days_late": (ref - promised).days})
    return sorted(rows, key=lambda r: -r["days_late"])


def recovered_this_week(ref=None):
    """Counted, never asserted: evidence-backed charges a human sent (with
    value), pulls completed, and idle flags raised, inside 7 days."""
    ref = ref or now()
    charges_sent = charge_value = idle_flags = 0
    for e in store.events():
        at = parse(e.get("at"))
        if not at or (ref - at).days > 7:
            continue
        if e["kind"] == "draft_charge" and str(e.get("actor", "")).startswith("human:"):
            charges_sent += 1
            ch = store.by_id("charges", e.get("subject")) or {}
            charge_value += ch.get("amount", 0)
        elif e["kind"] == "flag_idle_container":
            idle_flags += 1
    pulls = [o for o in store.load("orders")
             if o.get("kind") in ("pickup", "swap") and o.get("completed_at")
             and (ref - (parse(o["completed_at"]) or ref)).days <= 7]
    return {"charges_sent": charges_sent, "charge_value": round(charge_value, 2),
            "pulls_completed": len(pulls), "idle_flags": idle_flags,
            "note": "counted from the event log and the order book — never asserted"}


# ---------------------------------------------------------------- eval

item_eval = Eval("prohibited-waste triage",
                 costly_label="hazardous",
                 costly_note=("A HAZARDOUS ITEM APPROVED BY SOFTWARE IS A CONTAMINATED LOAD, A "
                              "REJECTED TIP, AND A FINE. Sending drywall to a human costs a text."))

EVAL_CASES = [
    {"input": "can I toss a few cans of old paint in there", "label": "hazardous"},
    {"input": "got some car batteries and two tires", "label": "hazardous"},
    {"input": "we're tearing out a popcorn ceiling from the 70s", "label": "hazardous"},
    {"input": "old fridge and a window AC unit", "label": "hazardous"},
    {"input": "half a propane tank from the grill", "label": "hazardous"},
    {"input": "can we throw in an old TV and a computer monitor", "label": "hazardous"},
    {"input": "drywall from the garage remodel", "label": "allowed"},
    {"input": "roofing shingles, one layer off a ranch house", "label": "allowed"},
    {"input": "old couch and a dresser", "label": "allowed"},
    {"input": "yard waste and branches from the storm", "label": "allowed"},
    {"input": "", "label": "unknown"},
    {"input": "some stuff from my uncle's shed", "label": "unknown"},
    {"input": "a couple gallons of leftover deck stain", "label": "hazardous"},
    {"input": "old queen mattress and box spring", "label": "hazardous"},
    {"input": "pool chlorine tubs, mostly empty", "label": "hazardous"},
    {"input": "carpet and padding from two bedrooms", "label": "allowed"},
    {"input": "concrete chunks from the patio demo", "label": "allowed"},
]


def run_eval():
    return item_eval.run(EVAL_CASES, lambda t: classify_item(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "classify_item":     {"rung": "R3", "reason": "the asymmetric classifier — it can refuse, it can never approve a hazard"},
    "answer_allowed_item": {"rung": "R2", "reason": "a yes on accepted material with the weight caveat, logged"},
    "approve_hazardous_item": {"rung": "R0", "reason": "the system can NEVER say yes to a prohibited item", "never_promote": True},
    "assert_charge_without_ticket": {"rung": "R0", "reason": "a charge without evidence is a credit memo waiting to happen", "never_promote": True},
    "draft_charge":      {"rung": "R1", "reason": "money — a human sends, with the evidence attached"},
    "draft_pickup_confirm": {"rung": "R1", "reason": "outward message — a human sends"},
    "flag_idle_container": {"rung": "R2", "reason": "an internal flag; every idle day is a turn not made"},
    "draft_pickup_makeright": {"rung": "R1", "reason": "outward make-right on a missed promise — a human sends; late is late"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Haul OS — what it computes to")
        .line("Idle container-days turned", "revenue", "flagged idle days × pull margin × turn share",
              ["idle_days", "pull_margin", "turn_share"],
              lambda g: float(g["idle_days"]) * float(g["pull_margin"]) / 7 * float(g["turn_share"]),
              note="idle days are counted; margin and the turn share are yours",
              assumption="divides by a 7-day rental cycle — argue with this one")
        .line("Charges recovered with evidence", "revenue", "assertable charges × avg charge",
              ["assertable_charges", "avg_charge"],
              lambda g: float(g["assertable_charges"]) * float(g["avg_charge"]))
        .line("Phone and text time", "time_saved", "hrs/wk × 52 × rate",
              ["phone_hours_wk", "office_rate"],
              lambda g: float(g["phone_hours_wk"]) * 52 * float(g["office_rate"]))
        .line("Contaminated-load exposure", "scenario", "you decide what the never-yes rule is worth",
              ["contamination_value"], lambda g: float(g["contamination_value"]),
              assumption="never a saving — prevented fines cannot be counted"))


def roi(given):
    rec = {}
    idle = [r for r in idle_containers() if r.get("flagged")]
    rec["idle_days"] = sum(r.get("days") or 0 for r in idle)
    assertable = sum(1 for c in store.load("charges") if charge_check(c).get("assertable"))
    rec["assertable_charges"] = assertable
    amts = [c.get("amount") for c in store.load("charges") if c.get("amount")]
    if len(amts) >= 10:
        rec["avg_charge"] = round(median(amts), 2)
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("classify_item", "answer_allowed_item", "draft_charge", "draft_pickup_confirm",
          "flag_idle_container")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("customer:",))
