#!/usr/bin/env python3
"""Gate OS — domain core (self-storage).

Rules live here: the bounded non-threatening delinquency ladder, the per-state
lien calendar (date alerts), THE SCRA stop on every lien step, message triage
with the military-signal bias, occupancy counting, and the matrix.

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

TABLES = ("config", "facilities", "tenants", "messages", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="GATEOS_DATA_ROOT")


# ---------------------------------------------------------------- the SCRA stop

SCRA_RULE = ("a lien step against a servicemember is a federal violation with statutory damages "
             "(SCRA) — and against an UNVERIFIED tenant it is a gamble with the same downside. "
             "Verify status first; a human runs verification.")


def can_lien_step(tenant):
    """THE refusal. A lien step needs: verified SCRA status AND not military.
    Flagged or unverified → refused with the federal stake named."""
    if tenant.get("military_flag"):
        return False, f"tenant is flagged military — {SCRA_RULE}"
    if not tenant.get("scra_verified_at"):
        return False, f"SCRA status unverified — {SCRA_RULE}"
    return True, "SCRA verified non-military — the calendar may proceed"


# ---------------------------------------------------------------- lien calendar

DEFAULT_LIEN_RULES = {
    "_source": ("DEFAULT rule set, simplified — replace with counsel-reviewed rules per state "
                "before go-live. Lien law is state-specific and unforgiving; every date below is "
                "a DATE ALERT, not legal advice."),
    "TX": {"steps": [{"key": "lien_notice", "label": "lien notice", "days_delinquent": 30},
                     {"key": "advertise", "label": "advertisement", "days_delinquent": 45},
                     {"key": "earliest_sale", "label": "earliest sale date", "days_delinquent": 60}]},
    "CO": {"steps": [{"key": "lien_notice", "label": "lien notice", "days_delinquent": 30},
                     {"key": "earliest_sale", "label": "earliest sale date", "days_delinquent": 75}]},
}


def lien_rules():
    return store.load("config").get("lien_rules") or DEFAULT_LIEN_RULES


def lien_calendar(tenant, ref=None):
    """Computed dates for one delinquent tenant — after the SCRA gate."""
    ref = ref or now()
    okl, why = can_lien_step(tenant)
    if not okl:
        return {"refused": why}
    rules = lien_rules()
    state_rules = rules.get(tenant.get("state_code") or "")
    if not state_rules:
        return unmeasured(f"no lien rule set for state {tenant.get('state_code')!r}", field="steps")
    delinquent_since = parse(tenant.get("delinquent_since"))
    if not delinquent_since:
        return unmeasured("no delinquency date recorded", field="steps")
    steps = []
    for s in state_rules["steps"]:
        due = delinquent_since + timedelta(days=s["days_delinquent"])
        steps.append({"step": s["label"], "due": iso(due), "days_left": (due - ref).days,
                      "label": "DATE ALERT — not legal advice"})
    return {"steps": steps, "rules_source": rules["_source"]}


# ---------------------------------------------------------------- dunning ladder

DUNNING_MAX_TOUCHES = 3
DUNNING_COOLDOWN_DAYS = 5
DUNNING_TEMPLATE = ("Hi {name} — your unit {unit} payment didn't come through. You can pay online "
                    "in a minute or call us; we're happy to work something out.")
DUNNING_COPY = {
    1: ("Hi {name} — your unit {unit} payment didn't come through. You can pay online in a "
        "minute or call us; we're happy to work something out."),
    2: ("Hi {name} — second note on unit {unit}: the balance is {balance} as of today. Paying "
        "online takes a minute, and a payment plan is a phone call — either works for us."),
    3: ("Hi {name} — last note from us on unit {unit} before a person calls you directly. The "
        "balance is {balance}. We would much rather sort this on the phone than let the "
        "calendar do it."),
}
FORBIDDEN = ("auction", "sell your", "cut the lock", "lose everything", "legal action",
             "collections", "final warning")


def dunning_plan(tenant, ref=None):
    ref = ref or now()
    if not tenant.get("delinquent_since"):
        return {"action": "none", "why": "not delinquent"}
    touches = tenant.get("dunning_touches") or []
    if len(touches) >= DUNNING_MAX_TOUCHES:
        return {"action": "human", "why": f"ladder exhausted at {DUNNING_MAX_TOUCHES} — a person "
                                          f"calls; the lien calendar runs on dates, not threats"}
    if touches:
        last = parse(touches[-1]["at"])
        if last and (ref - last).days < DUNNING_COOLDOWN_DAYS:
            return {"action": "none", "why": f"inside the {DUNNING_COOLDOWN_DAYS}-day cooldown"}
    touch_n = len(touches) + 1
    balance = tenant.get("balance")
    return {"action": "draft", "why": f"touch {touch_n} of {DUNNING_MAX_TOUCHES}",
            "touch": touch_n,
            "text": DUNNING_COPY[touch_n].format(
                name=tenant.get("name", "there"), unit=tenant.get("unit", ""),
                balance=f"${balance:,.0f}" if balance else "on your statement")}


def dunning_text_ok(text):
    t = (text or "").lower()
    hits = [w for w in FORBIDDEN if w in t]
    if hits:
        return False, f"a reminder never threatens — forbidden language: {', '.join(hits)}"
    return True, "ok"


# ---------------------------------------------------------------- triage

MILITARY = (r"\b(deployed|deployment|active duty|pcs orders?|stationed at|servicemember|"
            r"national guard.*activated|shipping out)\b",)
PROMISE = (r"\b(pay|payment)\b.*\b(friday|monday|next week|on the \d+|when i get paid)\b|"
           r"\bi('?ll| will) pay\b",)
MOVEOUT = (r"\b(mov(e|ing) out|vacat(e|ing)|empty(ing)? (the|my) unit|done with the unit)\b",)
ACCESS = (r"\b(gate|code|keypad)\b.*\b(not working|isn'?t working|won'?t|broken|denied)\b",)


def read_message(text):
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty message — a person reads it"}
    for rx in MILITARY:
        if re.search(rx, t):
            return {"label": "military_signal",
                    "why": "possible servicemember — every lien step freezes for this tenant "
                           "until a human verifies SCRA status"}
    for rx in MOVEOUT:
        if re.search(rx, t):
            return {"label": "moveout", "why": "move-out notice — admin task drafts"}
    for rx in ACCESS:
        if re.search(rx, t):
            return {"label": "gate_access", "why": "access problem — ops task now"}
    for rx in PROMISE:
        if re.search(rx, t):
            return {"label": "payment_promise", "why": "payment promise — recorded on the tenant"}
    return {"label": "human", "why": "no clean signal — a person reads it"}


# ---------------------------------------------------------------- occupancy

def occupancy():
    rows = []
    tenants = store.load("tenants")
    for f in store.load("facilities"):
        occupied = len([t for t in tenants if t.get("facility_id") == f["id"] and t.get("status") == "active"])
        if not f.get("unit_count"):
            rows.append({"facility": f["name"], **unmeasured("no unit count recorded — the "
                        "denominator is missing", field="rate"), "occupied": occupied})
            continue
        rows.append({"facility": f["name"], "units": f["unit_count"], "occupied": occupied,
                     "rate": round(occupied / f["unit_count"], 3)})
    return rows


def recovered_this_week(ref=None):
    """Counted, never asserted: delinquencies cured, SCRA verifications a human
    completed, and reminders a human sent, inside 7 days."""
    ref = ref or now()
    cured = [t for t in store.load("tenants")
             if t.get("cured_at") and (ref - (parse(t["cured_at"]) or ref)).days <= 7]
    verified = [t for t in store.load("tenants")
                if t.get("scra_verified_at")
                and (ref - (parse(t["scra_verified_at"]) or ref)).days <= 7]
    reminders = sum(1 for e in store.events(kind="draft_reminder")
                    if str(e.get("actor", "")).startswith("human:")
                    and (ref - (parse(e.get("at")) or ref)).days <= 7)
    return {"delinquencies_cured": len(cured),
            "cured_value": round(sum(t.get("balance", 0) for t in cured), 2),
            "scra_verified": len(verified), "reminders_sent": reminders,
            "note": "counted from the ledger and the event log — never asserted"}


# ---------------------------------------------------------------- eval

triage_eval = Eval("message triage",
                   costly_label="military_signal",
                   costly_note=("A MISSED DEPLOYMENT SIGNAL FOLLOWED BY AN AUCTION IS A FEDERAL "
                                "VIOLATION WITH STATUTORY DAMAGES. Freezing a ladder on a false "
                                "positive costs a few days of patience."))

EVAL_CASES = [
    {"input": "I'm deployed overseas until March, can't deal with this right now", "label": "military_signal"},
    {"input": "just got PCS orders, we're moving to Fort Cavazos", "label": "military_signal"},
    {"input": "my husband is active duty, he handles the unit", "label": "military_signal"},
    {"input": "guard unit got activated, I'm shipping out monday", "label": "military_signal"},
    {"input": "I'll pay friday I promise, just got paid late", "label": "payment_promise"},
    {"input": "moving out end of the month, unit will be empty", "label": "moveout"},
    {"input": "the gate code isn't working again", "label": "gate_access"},
    {"input": "", "label": "human"},
    {"input": "do you have any 10x20s available", "label": "human"},
    {"input": "my wife is stationed at bragg, I'm listed on her unit", "label": "military_signal"},
    {"input": "we'll be vacating unit 214 by sunday", "label": "moveout"},
    {"input": "keypad denied my code twice this morning", "label": "gate_access"},
    {"input": "I will pay when I get paid on the 15th", "label": "payment_promise"},
    {"input": "shipping out monday with my reserve unit", "label": "military_signal"},
]


def run_eval():
    return triage_eval.run(EVAL_CASES, lambda t: read_message(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_message":     {"rung": "R3", "reason": "routing only; the military bias is the point"},
    "freeze_lien_ladder": {"rung": "R2", "reason": "freezing on a military signal must not wait for a click"},
    "draft_reminder":   {"rung": "R1", "reason": "outward message about money — a human sends"},
    "lien_date_alert":  {"rung": "R2", "reason": "an internal date alert to the manager; dates, not advice"},
    "initiate_auction": {"rung": "R0", "reason": "a human runs a sale off a counsel-reviewed checklist — never software", "never_promote": True},
    "cut_lock":         {"rung": "R0", "reason": "overlocks and lock cuts are human acts with a checklist", "never_promote": True},
    "sell_contents":    {"rung": "R0", "reason": "software never sells anyone's belongings", "never_promote": True},
    "threaten_tenant":  {"rung": "R0", "reason": "a reminder never threatens", "never_promote": True},
    "verify_scra":      {"rung": "R1", "reason": "status verification is a human task with a record"},
    "draft_moveout_confirm": {"rung": "R1", "reason": "outward confirmation — a human sends; the walkthrough date locks the final bill"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Gate OS — what it computes to")
        .line("Delinquency days shortened", "cash_timing", "delinquent $ × days saved × daily cost",
              ["delinquent_total", "days_saved", "daily_cost_rate"],
              lambda g: float(g["delinquent_total"]) * float(g["days_saved"]) * float(g["daily_cost_rate"]),
              note="the delinquent total is counted; the days saved are your estimate")
        .line("Manual ladder time", "time_saved", "hrs/wk × 52 × rate",
              ["ladder_hours_wk", "manager_rate"],
              lambda g: float(g["ladder_hours_wk"]) * 52 * float(g["manager_rate"]))
        .line("Auctions avoided by earlier contact", "scenario", "auctions/yr × all-in cost",
              ["auctions_yr", "auction_cost"],
              lambda g: float(g["auctions_yr"]) * float(g["auction_cost"]),
              assumption="an exposure you weigh — avoided auctions cannot be counted")
        .line("The SCRA discipline", "scenario", "you decide what the stop is worth",
              ["scra_value"], lambda g: float(g["scra_value"]),
              assumption="never a saving — statutory damages are not our number to quote"))


def roi(given):
    rec = {}
    delinquent = [t for t in store.load("tenants") if t.get("delinquent_since")]
    rec["delinquent_total"] = round(sum(t.get("balance", 0) for t in delinquent), 2)
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("read_message", "freeze_lien_ladder", "draft_reminder", "lien_date_alert")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("tenant:",))
