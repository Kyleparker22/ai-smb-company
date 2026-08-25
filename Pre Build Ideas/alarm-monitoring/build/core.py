#!/usr/bin/env python3
"""Central OS — domain core (alarm monitoring & installation).

Rules live here: signal/message triage where the social-engineering surface IS
the product — test-mode-by-text refused, passcodes-in-text refused, fire
dispatch never cancelled — plus the permit & fine board, and the matrix.

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

TABLES = ("config", "accounts", "signals", "messages", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="CENTRALOS_DATA_ROOT")

CALLBACK_RULE = ("verification happens on a recorded callback to the number ON FILE — never in "
                 "this thread, never with a passcode typed into a message. That is not policy "
                 "theater; a text that can disarm an account is the burglar's front door.")

# ---------------------------------------------------------------- triage

TEST_MODE = (
    r"\b(put|place|set|switch)\b.*\b(test|maintenance) ?mode\b",
    r"\b(disable|turn off|pause|ignore)\b.*\b(alarm|monitoring|signals?|sensors?)\b",
    r"\bgoing to (trip|set off)\b.*\b(alarm|sensor)\b.*\b(ignore|don'?t)\b",
)
PASSCODE_IN_TEXT = (
    r"\b(passcode|password|safe ?word|code) (is|:)\s?\S+",
    r"\bmy (code|passcode)\b.*\b\d{3,}\b",
)
SIGNAL_FIRE = (
    r"\b(fire|smoke|co\b|carbon monoxide|heat detector)\b.*\b(signal|alarm|activation|going off)\b",
    r"\balarm\b.*\b(fire|smoke)\b",
)
SIGNAL_BURG = (
    r"\b(burglary|intrusion|motion|door|glass ?break)\b.*\b(signal|alarm|activation|tripped)\b",
    r"\balarm (went|going) off\b",
)
BILLING = (
    r"\b(bill|invoice|charge|payment|rate)\b",
)


def read_message(text):
    """test_mode_request | passcode_in_text | fire_signal | burglary_signal |
    billing | human. The social-engineering reads come FIRST."""
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty message — a person reads it"}
    for rx in TEST_MODE:
        if re.search(rx, t):
            return {"label": "test_mode_request",
                    "why": "a test-mode/disable request arriving by message — the burglar's "
                           "first move; refused, logged, verified-callback task opens"}
    for rx in PASSCODE_IN_TEXT:
        if re.search(rx, t):
            return {"label": "passcode_in_text",
                    "why": "a passcode offered in a text thread — never accepted, never compared; "
                           "the callback rule holds"}
    for rx in SIGNAL_FIRE:
        if re.search(rx, t):
            return {"label": "fire_signal",
                    "why": "a fire signal — dispatch proceeds and CANNOT be cancelled by "
                           "software, passcode or not"}
    for rx in SIGNAL_BURG:
        if re.search(rx, t):
            return {"label": "burglary_signal",
                    "why": "a burglary signal — operator flow; a cancel is a human decision "
                           "after verified callback"}
    for rx in BILLING:
        if re.search(rx, t):
            return {"label": "billing", "why": "billing — draft at R1"}
    return {"label": "human", "why": "no clean signal — a person reads it"}


# ---------------------------------------------------------------- the dispatch rules

def can_cancel_dispatch(signal, human=None, verified_callback=False):
    """Fire: never by software, never at all from this system. Burglary: a
    human after a verified callback — both facts recorded."""
    if signal.get("kind") == "fire":
        return False, ("a fire dispatch is never cancelled by this system — passcode or not, "
                       "human or not. If it turns out to be burnt toast, the fire department "
                       "forgives that; the other direction nobody forgives.")
    if not human:
        return False, "a burglary cancel is a human decision — software holds no cancel authority"
    if not verified_callback:
        return False, ("a burglary cancel needs a verified callback to the number on file, "
                       "recorded — " + CALLBACK_RULE)
    return True, f"cancelled by {human} after verified callback — both recorded"


# ---------------------------------------------------------------- permits & fines

DEFAULT_CITY_RULES = {
    "_source": ("DEFAULT city ordinance table, simplified — replace with each jurisdiction's "
                "actual permit and false-alarm fine schedule before go-live."),
    "Riverton": {"permit_years": 1, "fine_schedule": [0, 0, 50, 100, 200]},
    "Lakewood": {"permit_years": 2, "fine_schedule": [0, 25, 75, 150, 300]},
}


def city_rules():
    return store.load("config").get("city_rules") or DEFAULT_CITY_RULES


def permit_state(acct, ref=None):
    ref = ref or now()
    rules = city_rules()
    city = rules.get(acct.get("city") or "")
    if not city:
        return unmeasured(f"no ordinance table for city {acct.get('city')!r}", field="state")
    exp = parse(acct.get("permit_expires"))
    if not exp:
        return {"state": "unregistered",
                "why": "no permit on file — in most ordinances every dispatch to an unpermitted "
                       "address fines; a permit task drafts"}
    days = (exp - ref).days
    return {"state": "expired" if days < 0 else "expiring" if days <= 30 else "current",
            "expires": acct.get("permit_expires"), "days": days,
            "label": "DATE ALERT — the ordinance's date, not legal advice"}


def fine_exposure(acct):
    """This year's false alarms × the city's recorded schedule — counted."""
    rules = city_rules()
    city = rules.get(acct.get("city") or "")
    if not city:
        return unmeasured(f"no ordinance table for {acct.get('city')!r}", field="exposure")
    fa = acct.get("false_alarms_ytd") or 0
    sched = city["fine_schedule"]
    total = sum(sched[min(i, len(sched) - 1)] for i in range(fa))
    nxt = sched[min(fa, len(sched) - 1)]
    return {"false_alarms_ytd": fa, "accrued": total, "next_costs": nxt,
            "note": "counted against the city's recorded schedule"}


def recovered_this_week(ref=None):
    """Counted: social-engineering attempts refused, callbacks verified,
    permits renewed."""
    ref = ref or now()
    refused_se = sum(1 for e in store.events(kind="refused")
                     if (e.get("detail") or {}).get("action") in
                     ("enter_test_mode_from_message", "accept_passcode_in_text")
                     and (ref - (parse(e.get("at")) or ref)).days <= 7)
    callbacks = sum(1 for e in store.events(kind="callback_verified")
                    if (ref - (parse(e.get("at")) or ref)).days <= 7)
    renewed = [a for a in store.load("accounts")
               if a.get("permit_renewed_at")
               and (ref - (parse(a["permit_renewed_at"]) or ref)).days <= 7]
    return {"social_engineering_refused": refused_se, "callbacks_verified": callbacks,
            "permits_renewed": len(renewed),
            "note": "counted from the event log — never asserted"}


# ---------------------------------------------------------------- eval

triage_eval = Eval("message triage",
                   costly_label="test_mode_request",
                   costly_note=("A TEST-MODE REQUEST GRANTED FROM A TEXT IS AN ACCOUNT DISARMED "
                                "BY WHOEVER HOLDS THE PHONE — the burglar's first move. "
                                "Over-routing costs a callback."))

EVAL_CASES = [
    {"input": "put my account in test mode for the afternoon", "label": "test_mode_request"},
    {"input": "can you set the system to maintenance mode, electrician coming", "label": "test_mode_request"},
    {"input": "disable the motion sensors this weekend, we have guests", "label": "test_mode_request"},
    {"input": "going to trip the alarm moving furniture, just ignore it", "label": "test_mode_request"},
    {"input": "my passcode is 4471, go ahead and cancel that", "label": "passcode_in_text"},
    {"input": "the safe word is bluebird, disregard the signal", "label": "passcode_in_text"},
    {"input": "smoke alarm activation at the warehouse on 5th", "label": "fire_signal"},
    {"input": "co detector signal at the riverside house", "label": "fire_signal"},
    {"input": "motion signal tripped in zone 4 at the office", "label": "burglary_signal"},
    {"input": "the alarm went off at my shop, what happened", "label": "burglary_signal"},
    {"input": "question about my bill this month", "label": "billing"},
    {"input": "", "label": "human"},
    {"input": "what time does the office open", "label": "human"},
    {"input": "pause monitoring while we renovate the kitchen", "label": "test_mode_request"},
    {"input": "glass break signal at the storefront", "label": "burglary_signal"},
]


def run_eval():
    return triage_eval.run(EVAL_CASES, lambda t: read_message(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_message":       {"rung": "R3", "reason": "routing only; the social-engineering reads come first"},
    "enter_test_mode_from_message": {"rung": "R0", "reason": "an account never changes state from a message thread — the burglar's front door", "never_promote": True},
    "accept_passcode_in_text": {"rung": "R0", "reason": "a passcode in a thread is never accepted, compared, or confirmed", "never_promote": True},
    "cancel_fire_dispatch": {"rung": "R0", "reason": "a fire dispatch is never cancelled by this system — no exceptions exist", "never_promote": True},
    "open_callback_task": {"rung": "R2", "reason": "the verified-callback task is the safe path — it cannot wait"},
    "cancel_burglary_dispatch": {"rung": "R1", "reason": "a human, after a verified recorded callback — never promoted", "never_promote": True},
    "draft_permit_renewal": {"rung": "R1", "reason": "outward filing draft — a human sends"},
    "draft_billing_reply": {"rung": "R1", "reason": "outward reply — a human sends"},
    "permit_alert":       {"rung": "R2", "reason": "an internal date alert; the ordinance date is the point"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Central OS — what it computes to")
        .line("False-alarm fine exposure surfaced", "scenario", "counted per account against city schedules",
              ["fine_exposure"], lambda g: float(g["fine_exposure"]),
              assumption="an exposure you weigh — prevented fines cannot be counted")
        .line("Permit lapses caught", "revenue", "lapses × avg dispatch-fine avoided (yours)",
              ["lapses", "avg_fine"],
              lambda g: float(g["lapses"]) * float(g["avg_fine"]),
              assumption="your city's numbers, not ours")
        .line("Operator hours", "time_saved", "hrs/wk × 52 × rate",
              ["operator_hours_wk", "operator_rate"],
              lambda g: float(g["operator_hours_wk"]) * 52 * float(g["operator_rate"]))
        .line("The verified-callback file", "scenario", "you decide what the refusal log is worth",
              ["callback_value"], lambda g: float(g["callback_value"]),
              assumption="never a saving — the refusals are the product"))


def roi(given):
    rec = {}
    total = 0.0
    lapses = 0
    for a in store.load("accounts"):
        fe = fine_exposure(a)
        if fe.get("accrued"):
            total += fe["accrued"]
        ps = permit_state(a)
        if ps.get("state") in ("expired", "unregistered"):
            lapses += 1
    rec["fine_exposure"] = round(total, 2)
    rec["lapses"] = lapses
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("read_message", "open_callback_task", "draft_permit_renewal",
          "draft_billing_reply", "permit_alert")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("subscriber:",))
