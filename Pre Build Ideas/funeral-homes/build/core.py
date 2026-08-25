#!/usr/bin/env python3
"""Arrangement OS — domain core (funeral homes).

Rules live here: first-call triage, the GPL-grounded quote engine, the
document chase with its date alerts, the pre-need ledger, and the matrix.

Written with restraint: this vertical's product is trust at the worst moment
of someone's life. The system handles logistics and refuses everything that
must stay human.

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

TABLES = ("config", "cases", "gpl", "preneed", "calls", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="ARRANGEOS_DATA_ROOT")


# ---------------------------------------------------------------- first-call triage

FIRST_CALL = (
    r"\b(passed away|passed|died|deceased)\b|\bdeath\b(?!\s+certificates?)",
    r"\b(hospice|nursing home|hospital|coroner|medical examiner)\b.*\b(said to call|referred|gave us)\b",
    r"\b(my|our) (father|mother|dad|mom|husband|wife|son|daughter|brother|sister)\b.*\b(just|this morning|last night|tonight)\b",
    r"\bneed to (arrange|make arrangements)\b",
)
PRENEED = (r"\b(plan(ning)? ahead|pre-?need|pre-?arrange|for myself|before (I|we) need)\b",)
PRICE = (r"\b(how much|price|cost|pricing)\b.*\b(cremation|burial|service|casket|funeral)\b",
         r"\b(cremation|burial|service|casket|funeral)\b.*\b(cost|price|pricing|how much|run)\b",)
DOCS = (r"\b(death certificate|certificates?|permit|insurance assignment)\b.*\b(ready|status|when|copies)\b",)


def read_call(text):
    """first_call | preneed | price_question | document_status | human.
    A first call reads first — always."""
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty — a person answers, always"}
    for rx in FIRST_CALL:
        if re.search(rx, t):
            return {"label": "first_call",
                    "why": "a death notification — the on-call director, immediately; the system "
                           "captures logistics (place, contact, callback) and says nothing else"}
    for rx in PRENEED:
        if re.search(rx, t):
            return {"label": "preneed", "why": "pre-need inquiry — appointment draft at R1"}
    for rx in DOCS:
        if re.search(rx, t):
            return {"label": "document_status", "why": "document status — answered from the case record"}
    for rx in PRICE:
        if re.search(rx, t):
            return {"label": "price_question",
                    "why": "price question — every number comes itemized from the recorded GPL"}
    return {"label": "human", "why": "no clean signal — a person answers"}


# ---------------------------------------------------------------- the GPL quote engine

def quote(item_keys):
    """Every quote is itemized from the recorded General Price List. No GPL,
    or an item not on it → refused. Bundles are always shown as their items."""
    gpl = store.load("gpl")
    if not gpl:
        return {"refused": "no General Price List on file — no number can be quoted; the Funeral "
                           "Rule runs on the GPL, and so does this system"}
    index = {g["key"]: g for g in gpl}
    lines, missing = [], []
    for k in item_keys or []:
        if k in index:
            lines.append({"item": index[k]["label"], "price": index[k]["price"], "key": k})
        else:
            missing.append(k)
    if missing:
        return {"refused": f"item(s) not on the recorded GPL: {', '.join(missing)} — nothing is "
                           f"priced off-list"}
    if not lines:
        return {"refused": "no items requested"}
    return {"lines": lines, "total": round(sum(l["price"] for l in lines), 2),
            "note": "itemized from the recorded GPL — always itemized, never bundle-only"}


# ---------------------------------------------------------------- document chase

DOC_TYPES = ("death_certificate", "burial_permit", "cremation_permit", "insurance_assignment")
CHASE_MAX_TOUCHES = 4
CHASE_COOLDOWN_DAYS = 2


def case_documents(case):
    rows = []
    for d in case.get("documents") or []:
        row = {"kind": d["kind"], "state": "received" if d.get("received_at") else "open",
               "requested_at": d.get("requested_at")}
        if d.get("needed_by") and not d.get("received_at"):
            due = parse(d["needed_by"])
            row["needed_by"] = d["needed_by"]
            row["days_left"] = (due - now()).days if due else None
            row["label"] = "DATE ALERT — a service date depends on this"
        rows.append(row)
    return rows


def chase_plan(item, ref=None):
    ref = ref or now()
    if item.get("received_at"):
        return {"action": "none", "why": "received"}
    touches = item.get("touches") or []
    if len(touches) >= CHASE_MAX_TOUCHES:
        return {"action": "human", "why": f"ladder exhausted at {CHASE_MAX_TOUCHES} — the director calls"}
    last = parse(touches[-1]["at"]) if touches else parse(item.get("requested_at"))
    if last and (ref - last).days < CHASE_COOLDOWN_DAYS:
        return {"action": "none", "why": f"inside the {CHASE_COOLDOWN_DAYS}-day cooldown"}
    return {"action": "draft_chase", "why": f"touch {len(touches)+1} of {CHASE_MAX_TOUCHES}"}


# ---------------------------------------------------------------- pre-need ledger

def preneed_ledger():
    rows = store.load("preneed")
    funded = [p for p in rows if p.get("funding_recorded")]
    out = {"contracts": len(rows), "funded_recorded": len(funded)}
    unfunded_docs = [p for p in rows if not p.get("funding_recorded")]
    if unfunded_docs:
        out["funding_note"] = (f"{len(unfunded_docs)} contract(s) with no funding record — their "
                               f"value is unmeasured, not assumed")
    return out


def recovered_this_week(ref=None):
    """Counted, never asserted: documents received, chases a human sent, and
    first calls paged to a director, inside 7 days."""
    ref = ref or now()
    received = 0
    for case in store.load("cases"):
        for d in case.get("documents") or []:
            if d.get("received_at") and (ref - (parse(d["received_at"]) or ref)).days <= 7:
                received += 1
    chases = pages = 0
    for e in store.events():
        at = parse(e.get("at"))
        if not at or (ref - at).days > 7:
            continue
        if e["kind"] == "draft_document_chase" and str(e.get("actor", "")).startswith("human:"):
            chases += 1
        elif e["kind"] == "page_director":
            pages += 1
    return {"documents_received": received, "chases_sent": chases, "first_calls_paged": pages,
            "note": "counted from the cases and the event log — never asserted"}


# ---------------------------------------------------------------- eval

call_eval = Eval("call triage",
                 costly_label="first_call",
                 costly_note=("A FIRST CALL THAT WAITS IS A FAMILY THAT CALLS THE NEXT NAME ON "
                              "THE LIST — AND A FAMILY FAILED AT THE WORST MOMENT. Everything "
                              "else can wait five minutes."))

EVAL_CASES = [
    {"input": "my father just passed at the hospice, they said to call you", "label": "first_call"},
    {"input": "mom died this morning at the hospital, we don't know what to do", "label": "first_call"},
    {"input": "the nursing home gave us your number, my husband passed last night", "label": "first_call"},
    {"input": "we need to make arrangements for my sister", "label": "first_call"},
    {"input": "I'd like to plan ahead for myself, what does that look like", "label": "preneed"},
    {"input": "how much is cremation with a small service", "label": "price_question"},
    {"input": "are the death certificates ready? we need copies for the bank", "label": "document_status"},
    {"input": "", "label": "human"},
    {"input": "thank you all for everything last week", "label": "human"},
    {"input": "the coroner's office gave us your number this morning", "label": "first_call"},
    {"input": "we want to pre-arrange for my wife and me together", "label": "preneed"},
    {"input": "what does a graveside burial service cost", "label": "price_question"},
    {"input": "is the burial permit ready, the cemetery is asking", "label": "document_status"},
    {"input": "can someone call me back about flowers for saturday", "label": "human"},
]


def run_eval():
    return call_eval.run(EVAL_CASES, lambda t: read_call(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_call":         {"rung": "R3", "reason": "routing only; the first-call priority is the point"},
    "page_director":     {"rung": "R2", "reason": "the on-call director is paged the moment a first call is recognized"},
    "automate_grief_support": {"rung": "R0", "reason": "compassion is not a template — every human word comes from a human", "never_promote": True},
    "quote_off_gpl":     {"rung": "R0", "reason": "no recorded GPL, no numbers — the Funeral Rule runs on the list", "never_promote": True},
    "handle_remains_decision": {"rung": "R0", "reason": "software never touches a disposition decision", "never_promote": True},
    "pressure_sale_at_need": {"rung": "R0", "reason": "no upsell language is ever drafted toward a grieving family", "never_promote": True},
    "draft_preneed_appointment": {"rung": "R1", "reason": "outward message — a human sends"},
    "draft_document_chase": {"rung": "R1", "reason": "outward chase to an institution — a human sends"},
    "answer_document_status": {"rung": "R2", "reason": "a factual answer from the case record, logged"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Arrangement OS — what it computes to")
        .line("Pre-need follow-ups converted", "revenue", "inquiries × conversion × avg contract",
              ["preneed_inquiries", "conversion", "avg_contract"],
              lambda g: float(g["preneed_inquiries"]) * float(g["conversion"]) * float(g["avg_contract"]),
              note="inquiries are counted; conversion is your history")
        .line("Document-chase time", "time_saved", "cases × hrs × rate",
              ["cases_yr", "hours_per_case", "staff_rate"],
              lambda g: float(g["cases_yr"]) * float(g["hours_per_case"]) * float(g["staff_rate"]))
        .line("First calls that reached you", "scenario", "you decide what an answered 2am call is worth",
              ["first_call_value"], lambda g: float(g["first_call_value"]),
              assumption="never framed as revenue-per-death — this line is yours or blank")
        .line("Funeral Rule discipline", "scenario", "you decide what the clean GPL record is worth",
              ["rule_value"], lambda g: float(g["rule_value"]),
              assumption="never a saving"))


def roi(given):
    rec = {"cases_yr": len(store.load("cases")),
           "preneed_inquiries": len([c for c in store.load("calls") if c.get("label") == "preneed"])}
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("read_call", "page_director", "draft_preneed_appointment", "draft_document_chase",
          "answer_document_status")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("family:",))
