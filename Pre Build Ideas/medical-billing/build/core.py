#!/usr/bin/env python3
"""Claim OS — domain core (medical billing service).

Rules live here: denial triage by reason, the timely-filing calendar (per-payer
DATE ALERTS), the upcoding refusal (a higher-RVU code without provider
documentation is structurally unexpressable), the clean-claim gate, the appeal
ladder, PHI discipline in outward drafts, and the matrix.

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

TABLES = ("config", "practices", "claims", "denials", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="CLAIMOS_DATA_ROOT")

# ---------------------------------------------------------------- payers

DEFAULT_PAYER_RULES = {
    "_source": ("DEFAULT payer windows, simplified — replace with each contract's actual "
                "timely-filing and appeal windows before go-live. Every date is a DATE ALERT."),
    "BlueCap": {"timely_days": 90, "appeal_days": 60},
    "Medicare": {"timely_days": 365, "appeal_days": 120},
    "UnitedH": {"timely_days": 90, "appeal_days": 180},
    "_default": {"timely_days": 90, "appeal_days": 60},
}


def payer_rules():
    return store.load("config").get("payer_rules") or DEFAULT_PAYER_RULES


# ---------------------------------------------------------------- denial triage

DENIAL_KINDS = {
    "CO-29": ("untimely", "filed past the window — a write-off CANDIDATE; a human decides"),
    "CO-16": ("needs_info", "claim lacks information — fix and refile inside the window"),
    "CO-11": ("miscoded", "diagnosis inconsistent with procedure — correct and refile; "
              "correcting DOWN is mechanical, UP needs the provider's documentation"),
    "CO-50": ("needs_provider_doc", "medical-necessity denial — the provider's documentation "
              "decides the appeal; software drafts, the provider supplies"),
    "CO-97": ("bundled", "bundled service — appealable only with documentation of distinct service"),
    "PR-1": ("patient_resp", "deductible — patient responsibility, statement drafts"),
}


def triage_denial(denial):
    code = denial.get("carc")
    kind, why = DENIAL_KINDS.get(code, ("unknown", f"unrecognized reason code {code!r} — a human reads it"))
    return {"kind": kind, "why": why, "code": code}


# ---------------------------------------------------------------- the filing clock

def filing_clock(claim, ref=None):
    ref = ref or now()
    rules = payer_rules()
    payer = rules.get(claim.get("payer")) or rules["_default"]
    dos = parse(claim.get("date_of_service"))
    if not dos:
        return unmeasured("no date of service — the window is unknowable", field="days_left")
    deadline = dos + timedelta(days=payer["timely_days"])
    return {"deadline": iso(deadline), "days_left": (deadline - ref).days,
            "label": "DATE ALERT — the payer contract's number, not legal advice",
            "rules_source": rules["_source"]}


def at_risk_board(ref=None):
    """Unresolved claims inside 21 days of their filing deadline — the money
    that dies quietly. Counted with dollars."""
    ref = ref or now()
    rows = []
    for c in store.load("claims"):
        if c.get("paid_at") or c.get("written_off_at") or c.get("demo_tag"):
            continue
        clock = filing_clock(c, ref)
        if clock.get("days_left") is not None and clock["days_left"] <= 21:
            rows.append({"claim": c["id"], "payer": c.get("payer"),
                         "amount": c.get("amount", 0), "days_left": clock["days_left"],
                         "expired": clock["days_left"] < 0})
    rows.sort(key=lambda r: r["days_left"])
    return {"rows": rows,
            "at_risk_value": round(sum(r["amount"] for r in rows if not r["expired"]), 2),
            "expired_value": round(sum(r["amount"] for r in rows if r["expired"]), 2),
            "note": "counted per claim from each payer's own window"}


# ---------------------------------------------------------------- the coding rule

RVU_ORDER = ["99211", "99212", "99213", "99214", "99215"]


def can_recode(claim, new_code):
    """Correcting DOWN is mechanical. UP requires a recorded provider-
    documentation reference — the fraud line, held shut structurally."""
    old, new = claim.get("cpt"), new_code
    if old in RVU_ORDER and new in RVU_ORDER:
        if RVU_ORDER.index(new) > RVU_ORDER.index(old):
            if claim.get("provider_doc_ref"):
                return True, (f"upcode {old}→{new} permitted by provider documentation "
                              f"{claim['provider_doc_ref']} — still drafts at R1")
            return False, (f"cannot change {old}→{new}: a higher-paying code without provider "
                           f"documentation is upcoding, and upcoding is fraud with our name on "
                           f"the 837. The provider documents, or the code stands.")
        return True, f"downcode {old}→{new} — mechanical correction, drafts at R2"
    return True, "non-E/M recode — a human reviews"


# ---------------------------------------------------------------- the clean-claim gate

REQUIRED_FIELDS = ("payer", "cpt", "icd10", "date_of_service", "rendering_npi", "amount")


def can_submit(claim):
    missing = [f for f in REQUIRED_FIELDS if not claim.get(f)]
    if missing:
        return False, (f"cannot submit — required fields missing: {', '.join(missing)}. An "
                       f"incomplete claim is a guaranteed denial with a slower clock.")
    return True, "clean claim — submits"


# ---------------------------------------------------------------- PHI discipline

def phi_scrub_ok(text):
    """Outward drafts carry claim references, never patient identifiers.
    A name+DOB pair or an SSN pattern fails the draft."""
    t = text or ""
    if re.search(r"\b\d{3}-\d{2}-\d{4}\b", t):
        return False, "an SSN pattern never appears in an outward draft"
    if re.search(r"\b(dob|date of birth)\b", t, re.I) and re.search(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b", t):
        return False, "a DOB never appears in an outward draft — the claim reference is enough"
    return True, "ok"


# ---------------------------------------------------------------- appeal ladder

APPEAL_MAX_TOUCHES = 2
APPEAL_COOLDOWN_DAYS = 14


def appeal_plan(d, ref=None):
    ref = ref or now()
    if d.get("resolved_at") or d.get("demo_tag"):
        return {"action": "none", "why": "resolved"}
    kind = triage_denial(d)["kind"]
    if kind not in ("needs_provider_doc", "bundled", "miscoded", "needs_info"):
        return {"action": "human", "why": f"{kind} — a human decides this class"}
    touches = d.get("touches") or []
    if len(touches) >= APPEAL_MAX_TOUCHES:
        return {"action": "human", "why": f"ladder exhausted at {APPEAL_MAX_TOUCHES} — a human calls the payer"}
    last = parse(touches[-1]["at"]) if touches else parse(d.get("denied_at"))
    if last and (ref - last).days < APPEAL_COOLDOWN_DAYS:
        return {"action": "none", "why": f"inside the {APPEAL_COOLDOWN_DAYS}-day cooldown"}
    return {"action": "draft_appeal", "why": f"touch {len(touches)+1} of {APPEAL_MAX_TOUCHES}"}


def recovered_this_week(ref=None):
    """Counted: claims paid, appeals a human sent, denials resolved, inside 7d."""
    ref = ref or now()
    paid = [c for c in store.load("claims")
            if c.get("paid_at") and (ref - (parse(c["paid_at"]) or ref)).days <= 7]
    appeals = sum(1 for e in store.events(kind="draft_appeal")
                  if str(e.get("actor", "")).startswith("human:")
                  and (ref - (parse(e.get("at")) or ref)).days <= 7)
    resolved = [d for d in store.load("denials")
                if d.get("resolved_at") and (ref - (parse(d["resolved_at"]) or ref)).days <= 7]
    return {"claims_paid": len(paid),
            "paid_value": round(sum(c.get("amount", 0) for c in paid), 2),
            "appeals_sent": appeals, "denials_resolved": len(resolved),
            "note": "counted from the ledgers and the event log — never asserted"}


# ---------------------------------------------------------------- eval

triage_eval = Eval("denial triage",
                   costly_label="needs_provider_doc",
                   costly_note=("A MEDICAL-NECESSITY DENIAL MISSED IS AN APPEAL WINDOW CLOSED AND "
                                "THE CLIENT'S MONEY GONE FOREVER. Over-routing costs a read."))

EVAL_CASES = [
    {"input": {"carc": "CO-50"}, "label": "needs_provider_doc"},
    {"input": {"carc": "CO-29"}, "label": "untimely"},
    {"input": {"carc": "CO-16"}, "label": "needs_info"},
    {"input": {"carc": "CO-11"}, "label": "miscoded"},
    {"input": {"carc": "CO-97"}, "label": "bundled"},
    {"input": {"carc": "PR-1"}, "label": "patient_resp"},
    {"input": {"carc": "XX-99"}, "label": "unknown"},
    {"input": {"carc": None}, "label": "unknown"},
]


def run_eval():
    return triage_eval.run(EVAL_CASES, lambda d: triage_denial(d)["kind"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "triage_denial":     {"rung": "R3", "reason": "typed by reason code; the queue is visible"},
    "upcode_without_documentation": {"rung": "R0", "reason": "upcoding is fraud with our name on the 837", "never_promote": True},
    "submit_incomplete_claim": {"rung": "R0", "reason": "an incomplete claim is a guaranteed denial with a slower clock", "never_promote": True},
    "send_phi_in_draft": {"rung": "R0", "reason": "outward drafts carry claim references, never identifiers", "never_promote": True},
    "write_off_claim":   {"rung": "R1", "reason": "a write-off is the client's money — a human decides, always", "never_promote": True},
    "downcode_claim":    {"rung": "R2", "reason": "correcting down is mechanical and conservative"},
    "draft_appeal":      {"rung": "R1", "reason": "outward to a payer — a human sends with the documentation attached"},
    "submit_claim":      {"rung": "R1", "reason": "an 837 is a legal statement — a human releases, past the clean gate"},
    "filing_alert":      {"rung": "R2", "reason": "an internal date alert; the window is the point"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Claim OS — what it computes to")
        .line("Denials worked before the window", "revenue", "at-risk value × your recovery rate",
              ["at_risk_value", "recovery_rate"],
              lambda g: float(g["at_risk_value"]) * float(g["recovery_rate"]),
              note="at-risk dollars are counted per claim from each payer's own window")
        .line("Posting/chase hours", "time_saved", "hrs/wk × 52 × rate",
              ["office_hours_wk", "office_rate"],
              lambda g: float(g["office_hours_wk"]) * 52 * float(g["office_rate"]))
        .line("The audit file", "scenario", "you decide what a clean coding record is worth",
              ["audit_value"], lambda g: float(g["audit_value"]),
              assumption="never a saving — the upcoding refusal is the product"))


def roi(given):
    rec = {}
    rec["at_risk_value"] = at_risk_board()["at_risk_value"]
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("triage_denial", "draft_appeal", "submit_claim", "downcode_claim", "filing_alert")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("payer:",))
