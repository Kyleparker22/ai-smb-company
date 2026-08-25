#!/usr/bin/env python3
"""Member OS — domain core (multi-location gym).

Rules live here: message triage with the injury and cancellation stops, the
cancellation clock under per-state rules, the bounded dunning ladder that
never threatens, churn signals with the two-signal floor, and the matrix.

The thesis: the gym's biggest leak is a failed card nobody owns, its silent
one is the member who stopped coming, and its newest legal exposure is a
cancellation handled like a sales objection. Recover, watch, process.

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

TABLES = ("config", "members", "payments", "messages", "cancellations",
          "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="MEMBEROS_DATA_ROOT")


# ---------------------------------------------------------------- triage

CANCEL = (r"\bcancel\b|\bend my membership\b|\bstop (my )?(billing|charging|membership)\b|"
          r"\bquit(ting)?\b.*\bgym\b|\bdon'?t renew\b",)
INJURY = (r"\b(hurt|injured|injury|fell|dropped .* on|pulled|tore|twisted|sprained)\b.*"
          r"\b(at|in|during)\b.*\b(gym|class|workout|session)\b|"
          r"\binjur(y|ed) (at|in|during)\b",)
BILLING = (r"\b(charged twice|double charge|wrong (charge|amount)|refund|card (was )?declined|"
           r"update (my )?card|billing\b)",)
FREEZE = (r"\b(freeze|pause|hold)\b.*\b(membership|account)\b",)
MEDICAL = (r"\b(fix|cure|heal|help with)\b.*\b(back|knee|injury|pain|condition)\b|"
           r"\bis it safe\b.*\b(condition|pregnan\w*|surgery|injury)\b",)


def read_message(text):
    """cancellation | injury | medical_question | billing | freeze | human."""
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty message — a person reads it"}
    for rx in INJURY:
        if re.search(rx, t):
            return {"label": "injury",
                    "why": "injury report — a human calls; software drafts nothing on an injury"}
    for rx in CANCEL:
        if re.search(rx, t):
            return {"label": "cancellation",
                    "why": "cancellation request — the processing clock starts NOW; a retention "
                           "offer may be drafted for a human, but processing never waits on it"}
    for rx in MEDICAL:
        if re.search(rx, t):
            return {"label": "medical_question",
                    "why": "health/medical question — a qualified human answers; software promises nothing"}
    for rx in FREEZE:
        if re.search(rx, t):
            return {"label": "freeze", "why": "freeze request — a churn signal and an admin task"}
    for rx in BILLING:
        if re.search(rx, t):
            return {"label": "billing", "why": "billing question — draft reply at R1"}
    return {"label": "human", "why": "no clean signal — a person reads it"}


# ---------------------------------------------------------------- cancellation clock

DEFAULT_CANCEL_RULES = {
    "_source": ("DEFAULT rule set, simplified — replace with counsel-reviewed rules per state "
                "before go-live. Auto-renewal and cancellation law is state-specific and moving."),
    "CA": {"must_process_days": 3, "note": "online cancellation must be as easy as signup"},
    "TX": {"must_process_days": 5, "note": "written confirmation required"},
    "_default": {"must_process_days": 5, "note": "default window — verify per state"},
}


def cancel_rules():
    cfg = store.load("config")
    return cfg.get("cancel_rules") or DEFAULT_CANCEL_RULES


def cancellation_clock(member, requested_at):
    """The statutory processing window, computed. The clock starts at the
    request — not at the end of the save attempt."""
    rules = cancel_rules()
    state = (member or {}).get("state_code")
    rule = rules.get(state) or rules["_default"]
    req = parse(requested_at) or now()
    deadline = req + timedelta(days=rule["must_process_days"])
    return {"state": state or "unknown", "requested_at": iso(req),
            "process_by": iso(deadline), "days": rule["must_process_days"],
            "note": rule["note"], "rules_source": rules["_source"],
            "rule_label": "the clock starts at the request, not after a save attempt"}


# ---------------------------------------------------------------- dunning

DUNNING_MAX_TOUCHES = 3
DUNNING_COOLDOWN_DAYS = 5
DUNNING_TEMPLATE = ("Hi {name} — the card on file didn't go through this month. You can update it "
                    "in thirty seconds here, or stop by the desk. No rush, no fees stacked on.")
FORBIDDEN_DUNNING = ("collections", "legal action", "lawyer", "credit bureau", "final notice",
                     "consequences")


def dunning_plan(member, ref=None):
    ref = ref or now()
    fails = [p for p in store.load("payments")
             if p.get("member_id") == member["id"] and p.get("failed") and not p.get("recovered_at")]
    if not fails:
        return {"action": "none", "why": "no unrecovered failed payment"}
    touches = member.get("dunning_touches") or []
    if len(touches) >= DUNNING_MAX_TOUCHES:
        return {"action": "human", "why": f"ladder exhausted at {DUNNING_MAX_TOUCHES} — a person "
                                          f"decides; the system never escalates to threats"}
    if touches:
        last = parse(touches[-1]["at"])
        if last and (ref - last).days < DUNNING_COOLDOWN_DAYS:
            return {"action": "none", "why": f"inside the {DUNNING_COOLDOWN_DAYS}-day cooldown"}
    return {"action": "draft", "why": f"touch {len(touches)+1} of {DUNNING_MAX_TOUCHES}",
            "text": DUNNING_TEMPLATE.format(name=member.get("name", "there"))}


def dunning_text_ok(text):
    """Structural check: a dunning draft can never carry threat language."""
    t = (text or "").lower()
    hits = [w for w in FORBIDDEN_DUNNING if w in t]
    if hits:
        return False, f"dunning never threatens — forbidden language: {', '.join(hits)}"
    return True, "ok"


def churn_split(window_days=90):
    """Voluntary vs involuntary cancellations, counted. Refuses below 10."""
    cutoff = now() - timedelta(days=window_days)
    rows = [c for c in store.load("cancellations")
            if (parse(c.get("at")) or now()) >= cutoff]
    if len(rows) < 10:
        return unmeasured(f"only {len(rows)} cancellations in {window_days} days — need 10",
                          field="involuntary_share", n=len(rows))
    inv = [c for c in rows if c.get("reason") == "payment_failure"]
    return {"involuntary_share": round(len(inv) / len(rows), 3), "involuntary": len(inv),
            "of": len(rows), "note": "a failed card is a service problem, not a sales problem"}


# ---------------------------------------------------------------- churn watch

RISK_SIGNAL_FLOOR = 2


def churn_signals(member, ref=None):
    ref = ref or now()
    sigs = []
    v30 = member.get("visits_30d")
    vprior = member.get("visits_prior_30d")
    if v30 is not None and vprior:
        if v30 <= vprior / 2:
            sigs.append({"signal": "visit_drop",
                         "detail": f"{v30} visits last 30d vs {vprior} the 30 before"})
    fails = [p for p in store.load("payments")
             if p.get("member_id") == member["id"] and p.get("failed") and not p.get("recovered_at")]
    if fails:
        sigs.append({"signal": "failed_payment", "detail": f"{len(fails)} unrecovered failed payment(s)"})
    if member.get("freeze_requested"):
        sigs.append({"signal": "freeze_request", "detail": "asked to pause the membership"})
    if member.get("no_future_booking"):
        sigs.append({"signal": "no_future_booking", "detail": "no class or session booked ahead"})
    return sigs


def churn_board():
    at_risk, single = [], 0
    for m in store.load("members"):
        if m.get("status") != "active":
            continue
        sigs = churn_signals(m)
        if len(sigs) >= RISK_SIGNAL_FLOOR:
            at_risk.append({"member": m["id"], "name": m.get("name"), "count": len(sigs),
                            "signals": sigs})
        elif len(sigs) == 1:
            single += 1
    at_risk.sort(key=lambda r: -r["count"])
    return {"n": len(at_risk), "rows": at_risk[:40], "single_signal": single,
            "floor": RISK_SIGNAL_FLOOR,
            "note": "one signal is a note; two is a pattern — a list that flags everyone is a "
                    "list nobody works"}


def recovered_this_week(ref=None):
    """Counted, never asserted: failed payments recovered (with dues value),
    dunning notes a human sent, and winback check-ins sent, inside 7 days."""
    ref = ref or now()
    recovered = [p for p in store.load("payments")
                 if p.get("recovered_at") and (ref - (parse(p["recovered_at"]) or ref)).days <= 7]
    dunning = winbacks = 0
    for e in store.events():
        at = parse(e.get("at"))
        if not at or (ref - at).days > 7 or not str(e.get("actor", "")).startswith("human:"):
            continue
        if e["kind"] == "draft_dunning":
            dunning += 1
        elif e["kind"] == "draft_winback":
            winbacks += 1
    return {"payments_recovered": len(recovered),
            "recovered_value": round(sum(p.get("amount", 0) for p in recovered), 2),
            "dunning_sent": dunning, "winbacks_sent": winbacks,
            "note": "counted from the ledger and the event log — never asserted"}


# ---------------------------------------------------------------- eval

triage_eval = Eval("message triage",
                   costly_label="critical",
                   costly_note=("A MISSED INJURY REPORT IS LIABILITY; A MISSED CANCELLATION IS "
                                "ILLEGAL CONTINUED BILLING. Both cost a human thirty seconds to route."))

CRITICAL = ("injury", "cancellation")

EVAL_CASES = [
    {"input": "I want to cancel my membership please", "label": "critical"},
    {"input": "stop charging my card, I moved away months ago", "label": "critical"},
    {"input": "please don't renew me in january", "label": "critical"},
    {"input": "I hurt my shoulder during the 6am class yesterday", "label": "critical"},
    {"input": "my husband fell off the treadmill at your downtown gym", "label": "critical"},
    {"input": "I was charged twice this month, need a refund", "label": "billing"},
    {"input": "can I freeze my membership for the summer", "label": "freeze"},
    {"input": "will lifting fix my back pain", "label": "medical_question"},
    {"input": "what time does the pool open saturday", "label": "human"},
    {"input": "", "label": "human"},
    {"input": "quitting the gym, it's too far from my new place", "label": "critical"},
    {"input": "dropped a dumbbell on my foot during open gym", "label": "critical"},
    {"input": "card was declined but I have money, what happened", "label": "billing"},
    {"input": "is it safe to do your classes while pregnant", "label": "medical_question"},
    {"input": "can you pause my account while I travel for work", "label": "freeze"},
]


def _eval_label(text):
    lbl = read_message(text)["label"]
    return "critical" if lbl in CRITICAL else lbl


def run_eval():
    return triage_eval.run(EVAL_CASES, _eval_label)


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_message":       {"rung": "R3", "reason": "routing only; the stops are the point"},
    "start_cancel_clock": {"rung": "R2", "reason": "recording the request starts the statutory clock — delay is the harm"},
    "draft_retention_offer": {"rung": "R1", "reason": "a human may offer — but processing never waits on this draft"},
    "delay_cancellation": {"rung": "R0", "reason": "a cancellation is processed, not negotiated — slow-walking is regulatory exposure", "never_promote": True},
    "respond_to_injury":  {"rung": "R0", "reason": "nothing in writing from software on an injury — a human calls", "never_promote": True},
    "medical_claim":      {"rung": "R0", "reason": "no health outcome is ever promised", "never_promote": True},
    "threaten_collections": {"rung": "R0", "reason": "dunning never threatens", "never_promote": True},
    "draft_dunning":      {"rung": "R1", "reason": "outward message about money — a human sends"},
    "draft_billing_reply": {"rung": "R1", "reason": "outward reply — a human sends"},
    "draft_winback":      {"rung": "R1", "reason": "outward check-in to a quiet member — a human sends, no guilt language"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Member OS — what it computes to")
        .line("Failed payments recovered", "revenue", "open failures × recovery rate × avg dues",
              ["open_failures", "recovery_rate", "avg_dues"],
              lambda g: float(g["open_failures"]) * float(g["recovery_rate"]) * float(g["avg_dues"]) * 12,
              note="failures counted; the recovery rate is yours; annualized at 12 months",
              assumption="assumes a recovered member stays the year — argue with this one")
        .line("At-risk members saved", "revenue", "at-risk × save rate × avg dues × 12",
              ["at_risk", "save_rate", "avg_dues"],
              lambda g: float(g["at_risk"]) * float(g["save_rate"]) * float(g["avg_dues"]) * 12)
        .line("Billing chase time", "time_saved", "hrs/wk × 52 × rate",
              ["chase_hours_wk", "staff_rate"],
              lambda g: float(g["chase_hours_wk"]) * 52 * float(g["staff_rate"]))
        .line("Slow-cancel regulatory exposure", "scenario", "you decide what a clean record is worth",
              ["cancel_exposure"], lambda g: float(g["cancel_exposure"]),
              assumption="never a saving — compliance speed is the product, not a number we invent"))


def roi(given):
    rec = {}
    fails = [p for p in store.load("payments") if p.get("failed") and not p.get("recovered_at")]
    rec["open_failures"] = len({p["member_id"] for p in fails})
    rec["at_risk"] = churn_board()["n"]
    dues = [m.get("dues") for m in store.load("members") if m.get("dues")]
    if len(dues) >= 30:
        rec["avg_dues"] = round(median(dues), 2)
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("read_message", "start_cancel_clock", "draft_retention_offer", "draft_dunning",
          "draft_billing_reply")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("member:",))
