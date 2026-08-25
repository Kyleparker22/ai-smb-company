#!/usr/bin/env python3
"""Halflife OS — domain core (evidence half-life ledger for small law firms).

The product thesis: cases are not lost in court — they evaporate in the first
weeks, when the gas-station tape overwrites itself, the EDR gets crushed with
the car, and the witness's memory of the light goes soft. No product treats
evidence as PERISHABLE INVENTORY with expiry clocks. This one does nothing else.

Rules that live here: the recorded retention table (a custodian type not in the
table reads UNKNOWN and sorts FIRST — unknown decay is the scariest), the item
state machine (at_large → on_notice → secured, or LOST — and LOST is
permanent), the dies-first queue, witness memory freshness, intake triage with
the evidence-exists tip as the costly label, the autonomy matrix, evals and the
typed ROI panel.

The UPL rule from the Case OS line holds here: no legal advice, no deadline
opinions, no case value — routed to a licensed attorney unanswered.

Stdlib only. Honesty rules come from `_kit`.
"""
import re, sys
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent))

from _kit.moat import Eval, Gate, Matrix, Roi                       # noqa: E402
from _kit.store import (Store, automation_rate, iso, now,           # noqa: E402
                        parse, unmeasured)

TABLES = ("config", "matters", "evidence", "messages", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="HALFLIFEOS_DATA_ROOT")


# ---------------------------------------------------------------- the retention table
#
# THE load-bearing record. Every clock in the building computes from this table
# or reads UNKNOWN — there is no third option, and no function anywhere can
# extend a clock (extend_clock_without_policy is R0: hope is not a retention
# policy). Witness memory is a row like any other: a freshness window that runs
# from the last RECORDED contact.

DEFAULT_RETENTION = {
    "_source": ("DEFAULT retention schedule, simplified from common custodian practice — "
                "replace each row with the custodian's RECORDED policy as preservation "
                "letters are answered. A custodian type not in this table reads UNKNOWN "
                "and sorts first: unknown decay is the scariest."),
    "days": {
        "gas_station_cctv":      30,
        "municipal_camera":      14,
        "retail_cctv":           45,
        "residential_doorbell":  60,
        "transit_bus_camera":    30,
        "rideshare_dashcam":     90,
        "vehicle_edr":           60,
        "tow_yard_vehicle_hold": 30,
        "cell_carrier_records":  180,
        "police_bodycam":        180,
        "hospital_records":      2555,   # 7 years
        "witness_memory":        120,    # freshness window from last recorded contact
    },
}

ITEM_STATES = ("at_large", "on_notice", "secured", "LOST")


def retention_table():
    return store.load("config").get("retention_table") or DEFAULT_RETENTION


def clock(item, ref=None):
    """The item's decay clock, from the recorded table — or UNKNOWN, honestly.

    The incident date starts the clock (footage of the crash began overwriting
    the moment it was recorded, not the day the client called). Witness items
    run their freshness window from the last RECORDED contact instead.
    """
    ref = ref or now()
    table = retention_table()
    ct = item.get("custodian_type")
    days = (table.get("days") or {}).get(ct)
    if days is None:
        return {"unknown": True, "expiry": None, "days_left": None,
                "basis": (f"no recorded retention policy for '{ct}' — expiry UNKNOWN. "
                          f"It sorts first in the dies-first queue; unknown decay is "
                          f"the scariest")}
    if item.get("type") == "witness":
        anchor = parse(item.get("last_contact")) or parse(item.get("created_at"))
        basis = f"{days}d memory-freshness window from the last recorded contact"
    else:
        anchor = parse(item.get("created_at"))
        basis = f"{days}d recorded retention for {ct}, running from the incident"
    if not anchor:
        return {"unknown": True, "expiry": None, "days_left": None,
                "basis": "no start date recorded — the clock cannot be computed, so it "
                         "sorts first"}
    expiry = anchor + timedelta(days=days)
    return {"unknown": False, "expiry": iso(expiry), "days_left": (expiry - ref).days,
            "basis": basis}


def can_secure(item, receipt_ref):
    """Only a recorded possession receipt makes an item 'secured'. A sent
    letter is notice; notice is not possession."""
    if item.get("state") == "LOST":
        return False, ("this item is LOST and LOST is permanent — the ledger does not "
                       "forgive. If a copy surfaces later, it is inventoried as a NEW "
                       "item; the loss stays on the record")
    if not receipt_ref:
        return False, ("no possession receipt — only a recorded receipt makes an item "
                       "'secured'. A sent preservation letter is 'on notice', never "
                       "'secured': a letter is notice, not possession")
    return True, "a recorded possession receipt is on file"


# ---------------------------------------------------------------- the dies-first queue

def dies_first_queue(ref=None):
    """Every matter's evidence merged, ranked by what dies first.

    UNKNOWN clocks sort FIRST — an expiry nobody can state is scarier than a
    short one. LOST is excluded but counted (the ledger does not forgive);
    secured is excluded but counted (possession ends the race). Demo fixtures
    are skipped.
    """
    ref = ref or now()
    matters = store.index("matters")
    rows, lost_rows, secured_n = [], [], 0
    for i in store.load("evidence"):
        if i.get("demo_tag"):
            continue
        if i.get("state") == "LOST":
            lost_rows.append({
                "item": i["id"], "matter": i.get("matter_id"),
                "client": (matters.get(i.get("matter_id")) or {}).get("client"),
                "type": i.get("type"), "source": i.get("source"),
                "custodian": i.get("custodian"), "died_at": i.get("died_at"),
                "was_on_notice": bool(i.get("was_on_notice"))})
            continue
        if i.get("state") == "secured":
            secured_n += 1
            continue
        c = clock(i, ref)
        m = matters.get(i.get("matter_id")) or {}
        rows.append({
            "item": i["id"], "matter": i.get("matter_id"), "client": m.get("client"),
            "opposing": m.get("opposing"), "type": i.get("type"),
            "source": i.get("source"), "custodian": i.get("custodian"),
            "custodian_type": i.get("custodian_type"), "state": i.get("state"),
            "last_contact": i.get("last_contact"),
            "unknown": c["unknown"], "days_left": c["days_left"],
            "expiry": c["expiry"], "basis": c["basis"]})
    rows.sort(key=lambda r: (0 if r["unknown"] else 1,
                             r["days_left"] if r["days_left"] is not None else 0))
    lost_rows.sort(key=lambda r: r.get("died_at") or "", reverse=True)
    return {"generated": iso(ref), "rows": rows,
            "lost_rows": lost_rows[:30], "lost_count": len(lost_rows),
            "secured_count": secured_n,
            "unknown_count": sum(1 for r in rows if r["unknown"]),
            "dying_14": sum(1 for r in rows
                            if not r["unknown"] and r["days_left"] is not None
                            and r["days_left"] <= 14),
            "source": retention_table()["_source"],
            "note": "ranked by days-to-expiry, UNKNOWN first. LOST is excluded but "
                    "counted — the ledger does not forgive"}


# ---------------------------------------------------------------- intake triage
#
# The costly label is the evidence-exists tip: "the gas station probably has it
# on camera" is a 30-day clock that started at the incident, already running.
# Routed casually, the case dies quietly. It reads FIRST.

TIP = (
    r"\b(has|have|had|keeps?|there'?s|might have|probably)\b[^.]*"
    r"\b(camera|cctv|footage|video|dashcam|doorbell|on tape)\b",
    r"\b(camera|cctv|dashcam|doorbell|footage|video)\b[^.]*"
    r"\b(caught|might have|probably|recorded|saw)\b",
    r"\bwitness(es)?\b[^.]*\b(saw|heard)\b",
    r"\bsaw the whole thing\b",
    r"\b(tow ?yard|impound)\b[^.]*\b(has|still)\b",
    r"\bstill has the (car|truck|vehicle)\b",
)
DEADLINE = (
    r"\bhow long do i have\b", r"\bdeadline\b", r"\bstatute of limitations\b",
    r"\btoo late to (file|sue)\b",
)
NEW_MATTER = (
    r"\brear-?ended\b", r"\bhit by a (car|truck|bus|van)\b",
    r"\bslip(ped)? and f[ae]ll\b", r"\bfell (at|in|on)\b", r"\bdog (bit|bite)\b",
    r"\bcar (accident|crash|wreck)\b", r"\bt-?boned\b",
)
STATUS = (
    r"\bany update\b", r"\bwhat'?s (happening|going on)\b", r"\bstatus of\b",
    r"\bdid you (get|receive)\b", r"\bheard? (anything|back)\b",
)

LEGAL_QUESTION = (
    r"do i have a case", r"what('s| is) (my|the) case worth",
    r"how much (will|can) i get", r"should i (sue|settle|accept|sign)",
    r"whose fault", r"can i sue", r"what are my (chances|options|rights)",
    r"am i (going to|gonna) win",
)
_LQ = [re.compile(p, re.I) for p in LEGAL_QUESTION]


def legal_question(text):
    for rx in _LQ:
        m = rx.search(text or "")
        if m:
            return {"is_legal": True, "matched": m.group(0).strip()}
    return {"is_legal": False, "matched": None}


def read_message(text):
    """evidence_tip | new_matter | deadline_ask | status | human.
    The tip reads first — every hour it sits in a pile is clock burned."""
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty message — a person reads it"}
    for rx in TIP:
        if re.search(rx, t):
            return {"label": "evidence_tip",
                    "why": "an evidence-exists tip — NEVER routed casually. The clock "
                           "started at the incident and is already running; the item is "
                           "inventoried and a preservation letter drafts NOW"}
    for rx in DEADLINE:
        if re.search(rx, t):
            return {"label": "deadline_ask",
                    "why": "a deadline question is legal advice — routed to a licensed "
                           "attorney unanswered; software states no dates"}
    for rx in NEW_MATTER:
        if re.search(rx, t):
            return {"label": "new_matter",
                    "why": "a new matter — the evidence inventory starts NOW; every day "
                           "of delay is evidence gone"}
    for rx in STATUS:
        if re.search(rx, t):
            return {"label": "status", "why": "status ask — answered from the ledger, "
                                              "facts only"}
    if legal_question(t)["is_legal"]:
        return {"label": "human", "why": "a legal question — routed to a licensed "
                                         "attorney unanswered"}
    return {"label": "human", "why": "no clean signal — a person reads it"}


def tip_custodian(text):
    """Best-effort custodian typing from the tip. An unrecognizable custodian
    reads 'unstated' — NOT in the retention table, so the item's clock is
    UNKNOWN and it tops the queue. That is the honest outcome."""
    t = (text or "").lower()
    for pat, ct, typ in (
            (r"gas station", "gas_station_cctv", "footage"),
            (r"doorbell", "residential_doorbell", "footage"),
            (r"\bbus\b", "transit_bus_camera", "footage"),
            (r"\b(store|shop|market|mall)\b", "retail_cctv", "footage"),
            (r"\b(intersection|traffic|city) (cam|camera)\b", "municipal_camera", "footage"),
            (r"\b(uber|lyft|rideshare)\b", "rideshare_dashcam", "footage"),
            (r"\b(tow ?yard|impound)\b|still has the (car|truck|vehicle)",
             "tow_yard_vehicle_hold", "edr"),
            (r"\bwitness|saw the whole thing\b", "witness_memory", "witness")):
        if re.search(pat, t):
            return {"custodian_type": ct, "type": typ}
    return {"custodian_type": "unstated", "type": "footage"}


# ---------------------------------------------------------------- eval

triage_eval = Eval(
    "intake triage", costly_label="evidence_tip",
    costly_note=("AN EVIDENCE-EXISTS TIP ROUTED CASUALLY IS FOOTAGE THAT OVERWRITES "
                 "ITSELF WHILE THE MESSAGE SITS IN A PILE — the case dies quietly, "
                 "weeks before anyone knows it mattered. Over-routing a status ask "
                 "costs a read."))

EVAL_CASES = [
    {"input": "the gas station across the street probably has it on camera", "label": "evidence_tip"},
    {"input": "my neighbor's doorbell camera might have caught the whole thing", "label": "evidence_tip"},
    {"input": "the bus that hit me has a dashcam i think", "label": "evidence_tip"},
    {"input": "the store keeps security video of the parking lot", "label": "evidence_tip"},
    {"input": "there was a witness who saw the accident from the corner", "label": "evidence_tip"},
    {"input": "the tow yard still has the car", "label": "evidence_tip"},
    {"input": "i was rear-ended on route 9 yesterday and my neck hurts", "label": "new_matter"},
    {"input": "my mother fell at a grocery store and broke her hip", "label": "new_matter"},
    {"input": "how long do i have to file after a car accident", "label": "deadline_ask"},
    {"input": "is there a deadline for my slip and fall claim", "label": "deadline_ask"},
    {"input": "any update on my case", "label": "status"},
    {"input": "what's happening with the insurance claim", "label": "status"},
    {"input": "did you get my medical records yet", "label": "status"},
    {"input": "", "label": "human"},
    {"input": "what time does your office open", "label": "human"},
    {"input": "do i have a case", "label": "human"},
]


def run_eval():
    return triage_eval.run(EVAL_CASES, lambda t: read_message(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_message":        {"rung": "R3", "reason": "routing only; the evidence-exists tip reads first"},
    "open_matter":         {"rung": "R2", "reason": "the inventory starts the day of intake — every day of delay is evidence gone"},
    "inventory_evidence":  {"rung": "R2", "reason": "recording an item and its clock from typed facts and the recorded retention table"},
    "rank_queue":          {"rung": "R2", "reason": "the dies-first ranking is arithmetic on recorded clocks"},
    "mark_lost":           {"rung": "R2", "reason": "an expired clock is a fact; the ledger records the death with its dates and does not forgive"},
    "draft_preservation_letter": {"rung": "R1", "reason": "an outward legal letter citing the item, the custodian and the clock — DRAFT for attorney review; a human sends"},
    "draft_witness_outreach": {"rung": "R1", "reason": "outward contact with a witness — a human reaches out; the freshness window is cited"},
    "draft_status_reply":  {"rung": "R1", "reason": "outward reply to a client — factual status from the ledger, no advice"},
    "assert_evidence_secured": {"rung": "R0", "reason": "only a recorded possession receipt is 'secured' — a sent letter is 'on notice', never 'secured'; a letter is notice, not possession", "never_promote": True},
    "extend_clock_without_policy": {"rung": "R0", "reason": "clocks come from the recorded retention table or read UNKNOWN — hope is not a retention policy", "never_promote": True},
    "legal_advice_to_nonclient": {"rung": "R0", "reason": "no case value, no deadline opinion, no liability read — routed to a licensed attorney unanswered", "never_promote": True},
})
gate = Gate(store, matrix)

MOVING = ("read_message", "open_matter", "inventory_evidence", "rank_queue", "mark_lost",
          "draft_preservation_letter", "draft_witness_outreach", "draft_status_reply")


def automation(days=90):
    return automation_rate(store.events(), MOVING, days,
                           exclude_actors=("client:", "caller:"))


# ---------------------------------------------------------------- counted, this week

def ledger_this_week(ref=None):
    """Counted from the ledger and the event log — never asserted. Letters and
    receipts count only when a HUMAN did them; agent drafts are not sends."""
    ref = ref or now()
    items = store.load("evidence")
    secured = [i for i in items if i.get("secured_at")
               and (ref - (parse(i["secured_at"]) or ref)).days <= 7]
    lost = [i for i in items if i.get("state") == "LOST" and i.get("died_at")
            and 0 <= (ref - (parse(i["died_at"]) or ref)).days <= 7]
    letters = sum(1 for e in store.events(kind="preservation_letter_sent")
                  if str(e.get("actor", "")).startswith("human:")
                  and (ref - (parse(e.get("at")) or ref)).days <= 7)
    contacts = sum(1 for e in store.events(kind="witness_contact")
                   if str(e.get("actor", "")).startswith("human:")
                   and (ref - (parse(e.get("at")) or ref)).days <= 7)
    return {"secured": len(secured), "letters_sent": letters,
            "witness_contacts": contacts, "lost": len(lost),
            "note": "counted from the ledger and the event log — never asserted"}


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Halflife OS — what a preserved tape is worth")
        .line("Evidence preserved before expiry", "scenario",
              "items secured before their clock × the value you assign each",
              ["items_preserved", "value_per_item"],
              lambda g: float(g["items_preserved"]) * float(g["value_per_item"]),
              note="the count is the ledger's own stat; the value of a preserved tape "
                   "is yours to assign",
              assumption="never a promised win — preservation keeps the option alive; "
                         "it does not decide the case")
        .line("Footage that made liability", "scenario",
              "matters where footage decided liability × YOUR average case fee",
              ["cases_footage_decided", "avg_case_fee"],
              lambda g: float(g["cases_footage_decided"]) * float(g["avg_case_fee"]),
              assumption="A SCENARIO, never a promised win. Contingency outcomes are "
                         "wide and lumpy; this line stays blank until you put your own "
                         "numbers in it")
        .line("The malpractice shield", "scenario",
              "you decide what a documented preservation record is worth",
              ["spoliation_exposure"], lambda g: float(g["spoliation_exposure"]),
              note="the spoliation claim that never gets filed cannot be counted — the "
                   "recorded letters and receipts are the evidence, not this number")
        .line("Paralegal chase hours", "time_saved",
              "chase hrs/wk × 48 × loaded rate",
              ["chase_hours_wk", "loaded_rate"],
              lambda g: float(g["chase_hours_wk"]) * 48 * float(g["loaded_rate"])))


def roi(given=None):
    recorded = {"items_preserved": sum(1 for i in store.load("evidence")
                                       if i.get("state") == "secured")}
    cfg = store.load("config")
    merged = dict(recorded)
    merged.update({k: v for k, v in (cfg.get("roi_inputs") or {}).items()
                   if v not in (None, "")})
    merged.update({k: v for k, v in (given or {}).items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = recorded
    out["operator_supplied"] = {k: v for k, v in merged.items() if k not in recorded}
    return out
