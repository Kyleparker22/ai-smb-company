#!/usr/bin/env python3
"""Fix OS — domain core (appliance repair).

Rules live here: safety-first intake triage (the gas smell reads before
everything else and the customer's own words survive verbatim), the warranty
claim gate (an incomplete claim cannot be submitted and every missing field is
named), unit memory → parts-to-bring (the first-visit-fix economics), the COD
authorization clamp, the recall notice carried verbatim, and the matrix.

The thesis: half the shop's revenue is manufacturer reimbursement that dies on
clerical errors — a missing serial, an absent proof-of-purchase reference, a
failure code that doesn't match the parts. A denied claim is free work. The
gate makes the incomplete submission structurally unexpressable; the second
truck roll dies the same way, because the likely-parts list was on file the
whole time.

Stdlib only. Honesty rules come from `_kit`.
"""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent))

from _kit.moat import Eval, Gate, Matrix, Roi                       # noqa: E402
from _kit.store import (Store, automation_rate, iso, median, now,   # noqa: E402
                        parse, unmeasured)

TABLES = ("config", "customers", "units", "jobs", "claims", "messages",
          "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="FIXOS_DATA_ROOT")

# ---------------------------------------------------------------- the safety script

SAFETY_SCRIPT_GAS = ("Stop using the appliance now. If you smell gas: leave the house, and call "
                     "the gas utility's emergency line from outside — before you call us back.")
SAFETY_SCRIPT_GENERAL = ("Stop using the appliance now — switch it off at the breaker, or unplug "
                         "it only if you can reach the plug safely, and keep everyone away from "
                         "it.")

# ---------------------------------------------------------------- triage

GAS = (
    r"\b(smell|smells|smelling|smelt)\b.*\bgas\b",
    r"\bgas\b.*\b(smell|leak|odou?r)\b",
)
SAFETY = (
    r"\bspark(ed|ing|s)?\b",
    r"\bburning smell\b",
    r"\bsmoke|smoking\b",
    r"\b(caught|on) fire\b|\bflames?\b",
    r"\bleak(ed|ing)?\b.*\ball over\b",
    r"\bflood(ed|ing)?\b|\bwater everywhere\b",
    r"\bshocked? me\b",
)
WARRANTY = (r"\bwarranty\b", r"\bstill covered\b", r"\bjust bought\b")
STATUS = (
    r"\bany update\b", r"\bstatus\b", r"\beta\b",
    r"\bwhen will (the )?(tech|technician|part|someone)\b",
    r"\bis my (part|repair|unit)\b.*\b(in|done|ready|fixed)\b",
)
PARTS_ASK = (
    r"\b(part|relay|compressor|element|board|pump|motor|gasket|belt)s?\b.*"
    r"\b(in stock|in yet|available|order(ed)?|arrive[ds]?)\b",
    r"\bdo you (have|stock|carry)\b.*\b(part|relay|compressor|element|board|pump|motor|gasket|belt)s?\b",
)

APPLIANCE_RX = (
    (r"\bdishwasher\b", "dishwasher"),
    (r"\b(fridge|refrigerator|freezer)\b", "refrigerator"),
    (r"\b(oven|range|stove)\b", "range"),
    (r"\bdryer\b", "dryer"),
    (r"\bwash(er|ing machine)\b", "washer"),
    (r"\bice maker\b", "ice_maker"),
    (r"\bmicrowave\b", "microwave"),
)
SYMPTOM_RX = (
    (r"not cooling|isn'?t cold|warm inside|stopped cooling", "not_cooling"),
    (r"won'?t heat|no heat|not heating|stopped heating|runs cold", "no_heat"),
    (r"won'?t drain|not draining|standing water", "not_draining"),
    (r"stopped spinning|won'?t spin|not spinning", "not_spinning"),
    (r"won'?t start|won'?t turn on|\bdead\b|quit( working)?|stopped working|not working", "wont_start"),
    (r"leak(s|ed|ing)?", "leaking"),
    (r"\bnoise|noisy|grinding|squeal|rattl", "noisy"),
)


def _appliance(t):
    for rx, name in APPLIANCE_RX:
        if re.search(rx, t):
            return name
    return None


def _symptom(t):
    for rx, name in SYMPTOM_RX:
        if re.search(rx, t):
            return name
    return None


def read_message(text):
    """safety_symptom | warranty_repair | cod_repair | status | parts_ask |
    human. The safety symptom reads FIRST — the gas smell outranks everything,
    including the customer's own warranty question in the same breath."""
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty message — a person reads it"}
    appliance, symptom = _appliance(t), _symptom(t)
    for rx in GAS:
        if re.search(rx, t):
            return {"label": "safety_symptom", "gas": True, "appliance": appliance,
                    "symptom": symptom,
                    "why": "gas language — the safety script leads, the customer's words ride "
                           "verbatim, a technician calls ahead of everything routine"}
    for rx in SAFETY:
        if re.search(rx, t):
            return {"label": "safety_symptom", "gas": False, "appliance": appliance,
                    "symptom": symptom,
                    "why": "spark/burn/flood language — the safety script leads, never softened"}
    for rx in WARRANTY:
        if re.search(rx, t):
            return {"label": "warranty_repair", "appliance": appliance, "symptom": symptom,
                    "why": "warranty language — routing is confirmed against the RECORDED "
                           "coverage, not the customer's memory of it"}
    for rx in STATUS:
        if re.search(rx, t):
            return {"label": "status", "why": "status ask — answered from the job record"}
    for rx in PARTS_ASK:
        if re.search(rx, t):
            return {"label": "parts_ask", "why": "parts ask — the recorded order does the talking"}
    if appliance and symptom:
        return {"label": "cod_repair", "appliance": appliance, "symptom": symptom,
                "why": "repair symptom with no warranty language — coverage still checked "
                       "against the record before routing COD"}
    return {"label": "human", "why": "no clean signal — a person reads it"}


# ---------------------------------------------------------------- coverage (recorded, not remembered)

def warranty_active(unit, ref=None):
    """Warranty vs COD routes from the RECORDED coverage — the make must be one
    we're authorized for and the recorded warranty end date must be ahead."""
    ref = ref or now()
    makes = store.load("config").get("warranty_makes") or []
    if unit.get("make") not in makes:
        return False, f"{unit.get('make')} is not an authorized make for us — COD"
    until = parse(unit.get("warranty_until"))
    if not until:
        return False, "no recorded warranty end date — COD until a proof of purchase is recorded"
    if until < ref:
        return False, f"warranty ended {str(unit.get('warranty_until'))[:10]} — COD"
    return True, (f"in warranty until {str(unit.get('warranty_until'))[:10]} "
                  f"({unit.get('make')} — authorized)")


# ---------------------------------------------------------------- unit memory → parts-to-bring

DEFAULT_PARTS_MAP = {
    "_source": ("DEFAULT likely-parts map, seeded from common failure modes — it grows from THIS "
                "shop's own closed jobs, and a symptom with no recorded parts stays blank rather "
                "than guessed."),
    "refrigerator|not_cooling": ["start relay", "evaporator fan motor", "defrost thermostat"],
    "refrigerator|wont_start": ["start relay", "control board"],
    "refrigerator|leaking": ["defrost drain kit", "water inlet valve"],
    "range|no_heat": ["bake element", "igniter"],
    "range|wont_start": ["control board", "surface element switch"],
    "dryer|no_heat": ["heating element", "thermal fuse", "cycling thermostat"],
    "dryer|wont_start": ["door switch", "thermal fuse"],
    "washer|not_spinning": ["drive belt", "lid switch", "motor coupler"],
    "washer|not_draining": ["drain pump"],
    "washer|leaking": ["tub seal", "inlet hose"],
    "dishwasher|not_draining": ["drain pump", "check valve"],
    "dishwasher|wont_start": ["door latch", "control board"],
    "dishwasher|leaking": ["door gasket", "tub seal"],
}


def parts_map():
    return store.load("config").get("parts_map") or DEFAULT_PARTS_MAP


def parts_to_bring(appliance, symptom, unit=None):
    """Symptom + model + the unit's own history → the recorded likely-parts
    list. The first-visit fix IS the margin; the second truck roll is the
    quiet leak. The unit's own history outranks the map."""
    if not appliance or not symptom:
        return {"parts": [], "basis": "appliance or symptom not recorded — nothing is guessed; "
                                      "the tech triages by phone"}
    pm = parts_map()
    base = pm.get(f"{appliance}|{symptom}") or []
    history = []
    for h in (unit or {}).get("history") or []:
        if h.get("symptom") == symptom:
            history += h.get("parts_used") or []
    parts, seen = [], set()
    for p in history + list(base):
        if p not in seen:
            seen.add(p)
            parts.append(p)
    if not parts:
        return {"parts": [], "basis": f"no recorded likely-parts for {appliance}/{symptom} — "
                                      f"the tech triages by phone; nothing is guessed"}
    basis = []
    if history:
        basis.append("this unit's own repair history")
    if base:
        basis.append("the recorded likely-parts map")
    return {"parts": parts, "basis": " + ".join(basis), "map_source": pm["_source"]}


# ---------------------------------------------------------------- the recall list

DEFAULT_RECALL_LIST = {
    "_source": ("DEFAULT recall list, synthetic — wire the manufacturers' actual recall feeds "
                "before go-live. A notice rides the ticket VERBATIM; software never summarizes "
                "a safety recall."),
    "entries": [
        {"make": "Kelmore", "model": "KD-450",
         "notice": ("Kelmore Safety Recall K-24-07 (KD-450 dishwasher): the heating element can "
                    "overheat and pose a fire hazard. Inspect the element harness before any "
                    "service; do not run a dry cycle in the home.")},
        {"make": "HausWerk", "model": "HW-DR60",
         "notice": ("HausWerk Safety Recall HW-23-11 (HW-DR60 dryer): lint bypass at the blower "
                    "housing can contact the heater and ignite. Replace the blower housing seal "
                    "kit on every service visit.")},
    ],
}


def recall_list():
    return store.load("config").get("recall_list") or DEFAULT_RECALL_LIST


def recall_check(unit):
    for e in recall_list()["entries"]:
        if unit.get("make") == e["make"] and unit.get("model") == e["model"]:
            return {"flagged": True, "notice": e["notice"],
                    "note": "the notice rides the ticket verbatim — never summarized, never dropped"}
    return {"flagged": False}


def recall_flagged(include_demo=False):
    rl = recall_list()
    rows = []
    for u in store.load("units"):
        if u.get("demo_tag") and not include_demo:
            continue
        rc = recall_check(u)
        if rc.get("flagged"):
            rows.append({"unit": u["id"], "customer": u.get("customer"), "make": u.get("make"),
                         "model": u.get("model"), "serial": u.get("serial"),
                         "notice": rc["notice"]})
    return {"rows": rows, "source": rl["_source"]}


# ---------------------------------------------------------------- the claim gate

REQUIRED_CLAIM_FIELDS = ("serial", "purchase_proof_ref", "failure_code", "parts", "narrative")


def claim_completeness(claim):
    """Every missing field named, including the narrative-matches-parts check.
    There is deliberately no force-submit anywhere in this build."""
    missing = [f for f in REQUIRED_CLAIM_FIELDS if claim.get(f) in (None, "", [])]
    unmatched = []
    if claim.get("narrative") and claim.get("parts"):
        low = str(claim["narrative"]).lower()
        unmatched = [p for p in claim["parts"] if str(p).lower() not in low]
        if unmatched:
            missing.append("narrative-matches-parts")
    return missing, unmatched


def can_submit(claim):
    missing, unmatched = claim_completeness(claim)
    if missing:
        why = f"cannot submit — missing: {', '.join(missing)}."
        if unmatched:
            why += f" The narrative never mentions: {', '.join(unmatched)}."
        why += (" A denied claim is free work — the manufacturer's clerk is paid to find this "
                "gap, so the gate finds it first.")
        return False, why
    return True, ("complete claim — every field recorded and the narrative matches the parts; "
                  "drafts for a human to release")


def claims_board():
    """Open, unsubmitted claims split into blocked (incomplete — dead money
    walking) and ready (complete — waiting on a human release). Counted."""
    rows = []
    for c in store.load("claims"):
        if c.get("submitted_at") or c.get("demo_tag"):
            continue
        missing, _ = claim_completeness(c)
        rows.append({"claim": c["id"], "make": c.get("make"), "amount": c.get("amount", 0),
                     "missing": missing, "ready": not missing})
    rows.sort(key=lambda r: (-len(r["missing"]), -(r["amount"] or 0)))
    blocked = [r for r in rows if not r["ready"]]
    ready = [r for r in rows if r["ready"]]
    return {"rows": rows, "blocked": len(blocked),
            "blocked_value": round(sum(r["amount"] or 0 for r in blocked), 2),
            "ready": len(ready),
            "ready_value": round(sum(r["amount"] or 0 for r in ready), 2),
            "note": "an incomplete claim is counted as blocked money, not submitted hope"}


# ---------------------------------------------------------------- the narrative rule

NARRATIVE_FIELDS = ("appliance", "symptom", "diagnosis", "failure_code", "parts")


def assemble_narrative(claim, fields=None):
    """The failure narrative assembles from RECORDED diagnosis fields only.
    A field outside the diagnosis record cannot be written into it, and a
    recorded field that is empty is named — never filled with prose."""
    fields = tuple(fields or NARRATIVE_FIELDS)
    invented = [f for f in fields if f not in NARRATIVE_FIELDS]
    if invented:
        return {"refused": (f"cannot write {', '.join(invented)} into a failure narrative — not "
                            f"a recorded diagnosis field. The narrative assembles from what the "
                            f"tech recorded ({', '.join(NARRATIVE_FIELDS)}), or it does not "
                            f"assemble.")}
    absent = [f for f in fields if claim.get(f) in (None, "", [])]
    if absent:
        return {"refused": (f"cannot assemble — not recorded on this claim: {', '.join(absent)}. "
                            f"The tech records the diagnosis; software never fills the gap with "
                            f"prose.")}
    parts = ", ".join(claim["parts"])
    return {"narrative": (f"Unit presented with {str(claim['symptom']).replace('_', ' ')}. "
                          f"Diagnosis: {claim['diagnosis']}. Failure code "
                          f"{claim['failure_code']}. Corrected by replacing: {parts}."),
            "basis": "assembled from recorded diagnosis fields only — nothing invented"}


# ---------------------------------------------------------------- the COD clamp

def job_total(job):
    return round(sum(w.get("amount", 0) for w in job.get("work") or []), 2)


def authorization(job):
    amt = job.get("authorized_amount")
    if amt in (None, ""):
        return None
    return float(amt)


def can_add_work(job, amount):
    """COD work past the customer's recorded authorized amount has no path.
    The overage drafts back for the customer's approval — that is the ONLY way
    the number moves."""
    if job.get("kind") != "cod":
        return True, "warranty job — the manufacturer's authorization governs, tracked on the claim"
    auth = authorization(job)
    if auth is None:
        return False, ("no recorded authorization on this COD job — record the customer's "
                       "authorized amount before any work; a verbal 'whatever it takes' is a "
                       "dispute in writing")
    total = job_total(job)
    if total + amount > auth:
        return False, (f"${total + amount:,.2f} would exceed the customer's recorded "
                       f"authorization of ${auth:,.2f} (work so far ${total:,.2f}). Work past "
                       f"the authorized amount has no path — the overage drafts back for the "
                       f"customer's approval first.")
    return True, f"inside the recorded authorization (${total + amount:,.2f} of ${auth:,.2f})"


# ---------------------------------------------------------------- recovered, counted

def recovered_this_week(ref=None):
    """Counted, never asserted: claims paid inside 7 days, claims a human
    actually released, and jobs closed in one visit."""
    ref = ref or now()
    paid = [c for c in store.load("claims")
            if c.get("paid_at") and not c.get("demo_tag")
            and (ref - (parse(c["paid_at"]) or ref)).days <= 7]
    submitted = sum(1 for e in store.events(kind="submit_claim")
                    if str(e.get("actor", "")).startswith("human:")
                    and (ref - (parse(e.get("at")) or ref)).days <= 7)
    first_visit = [j for j in store.load("jobs")
                   if j.get("closed_at") and not j.get("demo_tag") and j.get("visits") == 1
                   and (ref - (parse(j["closed_at"]) or ref)).days <= 7]
    return {"claims_paid": len(paid),
            "paid_value": round(sum(c.get("amount", 0) for c in paid), 2),
            "claims_submitted": submitted, "first_visit_fixes": len(first_visit),
            "note": "counted from the claim ledger and the event log — never asserted"}


# ---------------------------------------------------------------- eval

triage_eval = Eval("intake triage",
                   costly_label="safety_symptom",
                   costly_note=("A GAS SMELL ROUTED AS A ROUTINE TICKET IS THE HOUSE FIRE WITH "
                                "OUR NAME IN THE CALL LOG. Over-routing a noisy dryer to the "
                                "safety script costs a read."))

EVAL_CASES = [
    {"input": "I smell gas when the oven is on", "label": "safety_symptom"},
    {"input": "the dryer sparked and there's a burning smell", "label": "safety_symptom"},
    {"input": "dishwasher leaked all over the kitchen floor", "label": "safety_symptom"},
    {"input": "there's smoke coming from the back of the fridge", "label": "safety_symptom"},
    {"input": "my fridge is not cooling and it's still under warranty", "label": "warranty_repair"},
    {"input": "the Kelmore range we bought in march just quit, warranty repair?", "label": "warranty_repair"},
    {"input": "my dryer won't heat, what would a repair cost", "label": "cod_repair"},
    {"input": "the washer stopped spinning mid cycle", "label": "cod_repair"},
    {"input": "our dishwasher won't drain", "label": "cod_repair"},
    {"input": "the ice maker quit working yesterday", "label": "cod_repair"},
    {"input": "any update on my refrigerator repair", "label": "status"},
    {"input": "when will the tech be out for my range", "label": "status"},
    {"input": "is the compressor part in yet", "label": "parts_ask"},
    {"input": "do you have the door gasket in stock for my washer", "label": "parts_ask"},
    {"input": "", "label": "human"},
    {"input": "what are your weekend hours", "label": "human"},
]


def run_eval():
    return triage_eval.run(EVAL_CASES, lambda t: read_message(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_message":             {"rung": "R3", "reason": "routing only; the safety symptom reads first"},
    "log_ticket":               {"rung": "R2", "reason": "an internal ticket carrying the recorded parts list — the second truck roll dies here"},
    "flag_recall":              {"rung": "R2", "reason": "internal flag; the notice rides the ticket verbatim"},
    "add_work":                 {"rung": "R2", "reason": "inside the customer's recorded authorization — logged, visible on the ticket"},
    "submit_incomplete_claim":  {"rung": "R0", "reason": "the claim builder names every missing field and has no force-submit — a denied claim is free work", "never_promote": True},
    "exceed_authorized_amount": {"rung": "R0", "reason": "COD work past the recorded authorization has no path — the overage drafts back for the customer's approval", "never_promote": True},
    "dismiss_safety_symptom":   {"rung": "R0", "reason": "gas/spark/flood language survives verbatim into every draft — software never downgrades a safety symptom", "never_promote": True},
    "invent_failure_narrative": {"rung": "R0", "reason": "a narrative assembles from recorded diagnosis fields only — an invented sentence on a claim form is fraud", "never_promote": True},
    "submit_claim":             {"rung": "R1", "reason": "a reimbursement claim to a manufacturer — a human releases, past the completeness gate"},
    "draft_overage_request":    {"rung": "R1", "reason": "money past the customer's recorded authorization — the customer approves before the work exists"},
    "draft_safety_reply":       {"rung": "R1", "reason": "outward on a safety symptom — the script leads, a human sends, a technician calls"},
    "draft_repair_reply":       {"rung": "R1", "reason": "outward booking reply — a human sends"},
    "draft_status_reply":       {"rung": "R1", "reason": "outward reply — status comes from the job record, a human sends"},
    "draft_parts_reply":        {"rung": "R1", "reason": "outward reply — the recorded parts order does the talking"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Fix OS — what it computes to")
        .line("Warranty claims that clear the gate", "revenue",
              "blocked claim value × your historical denial rate",
              ["blocked_claim_value", "denial_rate"],
              lambda g: float(g["blocked_claim_value"]) * float(g["denial_rate"]),
              note="blocked value is counted from claims failing the gate right now; the denial "
                   "rate is your own history, not an industry number")
        .line("Second truck rolls that don't happen", "revenue",
              "re-rolled visits × your cost per truck roll",
              ["re_rolled_visits", "truck_roll_cost"],
              lambda g: float(g["re_rolled_visits"]) * float(g["truck_roll_cost"]),
              note="re-rolled visits are counted from jobs that took more than one visit — the "
                   "parts list was on file the whole time")
        .line("Office / paperwork hours", "time_saved", "hrs/wk × 52 × rate",
              ["office_hours_wk", "office_rate"],
              lambda g: float(g["office_hours_wk"]) * 52 * float(g["office_rate"]),
              note="reported separately; never summed into revenue")
        .line("COD disputes that never start", "scenario",
              "you decide what an argument that never happens is worth",
              ["cod_dispute_value"], lambda g: float(g["cod_dispute_value"]),
              assumption="never a saving — a prevented argument cannot be counted"))


def roi(given):
    rec = {}
    cb = claims_board()
    rec["blocked_claim_value"] = cb["blocked_value"]
    rec["re_rolled_visits"] = len([j for j in store.load("jobs")
                                   if j.get("closed_at") and not j.get("demo_tag")
                                   and (j.get("visits") or 1) > 1])
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("read_message", "log_ticket", "add_work", "submit_claim", "draft_overage_request",
          "draft_safety_reply", "draft_repair_reply", "draft_status_reply", "draft_parts_reply")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("customer:",))
