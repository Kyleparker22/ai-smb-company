#!/usr/bin/env python3
"""Bay OS — domain core (independent auto repair).

Rules live here: the declined-item classifier and its safety bias, the re-offer
ladder with the safety-item carve-out, comeback counting with its floor, intake
triage that never diagnoses by phone, and the autonomy matrix.

The thesis: the shop's next $200k is already written on its own inspection
sheets — declined and forgotten. And the fastest way to lose the shop is to
soften a brake finding into a marketing text. Recover the first, refuse the
second.

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

TABLES = ("config", "customers", "vehicles", "ros", "declined", "calls",
          "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="BAYOS_DATA_ROOT")


# ---------------------------------------------------------------- declined-item classes

# The bias is one-directional on purpose: calling a cabin filter safety-critical
# costs an awkward phone call; calling a brake line deferrable costs a family.
SAFETY = (
    (r"\bbrake|caliper|rotor(?!y)|master cylinder|brake line\b", "braking system"),
    (r"\btires?\b.*\b(cord|belt|bald|2/32|worn to|separat)", "tire at or past limit"),
    (r"\bsteering|tie rod|ball joint|rack\b", "steering component"),
    (r"\bsuspension|control arm|strut mount\b.*\b(broken|cracked|separat|loose)\b", "failed suspension part"),
    (r"\bairbag|seat ?belt|srs\b", "restraint system"),
    (r"\bfuel (line|leak)|leak(ing)? fuel\b", "fuel leak"),
    (r"\bexhaust leak\b.*\b(cabin|floor)|carbon monoxide\b", "exhaust into cabin"),
    (r"\bwheel bearing\b.*\b(loose|play|growl)", "wheel bearing with play"),
)
COSMETIC = (
    (r"\bcosmetic|scratch|trim|detail|paint\b", "cosmetic"),
    (r"\bwiper\b(?!.*(torn|split))", "wipers"),
    (r"\bcabin (air )?filter\b", "cabin filter"),
)
DEFERRABLE = (
    (r"\b(engine|air) filter\b", "filter"),
    (r"\bfluid (exchange|flush|service)|coolant service|transmission service\b", "fluid service"),
    (r"\bspark plugs?\b|\bserpentine belt\b(?!.*(crack|fray))", "tune-up item"),
    (r"\bmount\b|\bgasket seep|seep(ing)?\b", "seep / wear item"),
    (r"\balignment\b|\brotat(e|ion)\b", "alignment / rotation"),
    (r"\bbattery\b.*\b(marginal|aging)|\bbulb\b", "aging accessory"),
)


def classify_item(text):
    """safety_critical | deferrable | cosmetic | needs_review. Empty text is
    needs_review — nobody re-offers what nobody can read."""
    t = (text or "").lower().strip()
    if not t:
        return {"label": "needs_review", "why": "empty finding — a human reads the sheet"}
    for rx, why in SAFETY:
        if re.search(rx, t):
            return {"label": "safety_critical", "why": why}
    for rx, why in COSMETIC:
        if re.search(rx, t):
            return {"label": "cosmetic", "why": why}
    for rx, why in DEFERRABLE:
        if re.search(rx, t):
            return {"label": "deferrable", "why": why}
    return {"label": "needs_review", "why": "no pattern matched — the advisor classifies it"}


# ---------------------------------------------------------------- the re-offer rules

REOFFER_COOLDOWN_DAYS = 45
SAFETY_CALL_WINDOW_DAYS = 7
MAX_TOUCHES = 3

SAFETY_CONTACT_RULE = ("a safety-critical finding is a phone call from a human with the finding "
                       "verbatim — never a marketing text, never softened")


def reoffer_plan(item, ref=None):
    """What, if anything, happens to one declined item now. Safety items never
    enter the drip; they become a call task inside the window."""
    ref = ref or now()
    if item.get("recovered_at") or item.get("demo_tag"):
        return {"action": "none", "why": "recovered or demo row"}
    label = item.get("label")
    if label == "needs_review":
        return {"action": "review", "why": "unclassified — a human reads it first"}
    if label == "safety_critical":
        return {"action": "call_task", "why": SAFETY_CONTACT_RULE,
                "due": iso(ref + timedelta(days=SAFETY_CALL_WINDOW_DAYS))}
    touches = item.get("touches") or []
    if len(touches) >= MAX_TOUCHES:
        return {"action": "none", "why": f"ladder exhausted at {MAX_TOUCHES} touches — silence is an answer"}
    last = parse(touches[-1]["at"]) if touches else parse(item.get("declined_at"))
    if last and (ref - last).days < REOFFER_COOLDOWN_DAYS:
        return {"action": "none", "why": f"inside the {REOFFER_COOLDOWN_DAYS}-day cooldown"}
    return {"action": "draft_reoffer", "why": f"declined {label} item past cooldown, touch {len(touches)+1} of {MAX_TOUCHES}"}


def can_text(item):
    """THE refusal: a safety finding cannot leave as a text drip, full stop."""
    if item.get("label") == "safety_critical":
        return False, SAFETY_CONTACT_RULE
    return True, "ok"


def declined_value(only_open=True):
    rows = [d for d in store.load("declined")
            if not d.get("demo_tag") and (not only_open or not d.get("recovered_at"))]
    by_label = {}
    for d in rows:
        by_label.setdefault(d.get("label") or "needs_review", {"count": 0, "value": 0})
        by_label[d.get("label") or "needs_review"]["count"] += 1
        by_label[d.get("label") or "needs_review"]["value"] += d.get("value", 0)
    return {"count": len(rows), "value": round(sum(d.get("value", 0) for d in rows), 2),
            "by_label": {k: {"count": v["count"], "value": round(v["value"], 2)}
                         for k, v in by_label.items()},
            "note": "counted from this shop's inspection sheets"}


# ---------------------------------------------------------------- intake triage

def classify_call(text):
    t = (text or "").lower()
    if not t.strip():
        return {"label": "human", "why": "empty transcript — a person answers"}
    if re.search(r"\bwon'?t (stop|steer|brake)|brakes? (are )?(gone|to the floor)|undriveable|"
                 r"smoke|on fire|stalled (on|in) (the )?(highway|road|intersection)|accident\b", t):
        return {"label": "safety_priority", "why": "vehicle unsafe or undriveable — a human, now"}
    if re.search(r"\bwhat('?s| is) wrong|why (is|does)|is it the \w+|do you think it'?s\b", t):
        return {"label": "no_phone_diagnosis",
                "why": "a diagnosis needs an inspection — we schedule one, we never guess by phone"}
    if re.search(r"\b(appointment|book|schedule|come in|drop off|oil change|inspection)\b", t):
        return {"label": "booking", "why": "scheduling language"}
    if re.search(r"\bprice|cost|how much|quote\b", t):
        return {"label": "price_range", "why": "price question — ranges from our own history, firm price needs eyes on the car"}
    return {"label": "human", "why": "no clean signal — a person answers"}


def price_band(job_kind):
    """A band from OUR OWN closed ROs of that kind — never a national average,
    and below 6 ROs we refuse."""
    ros = [r for r in store.load("ros")
           if r.get("kind") == job_kind and r.get("total") and r.get("closed_at")]
    if len(ros) < 6:
        return unmeasured(f"only {len(ros)} closed ROs of kind {job_kind!r} — need 6 to state a band",
                          field="band", n=len(ros))
    totals = sorted(r["total"] for r in ros)
    lo, hi = totals[len(totals) // 4], totals[(3 * len(totals)) // 4]
    return {"band": [round(lo), round(hi)], "n": len(ros),
            "basis": "middle half of our own closed ROs — a firm price needs an inspection"}


def recovered_this_week(ref=None):
    """Counted, never asserted: declined items marked recovered in the last 7
    days (value from the sheet) and re-offers a human actually sent."""
    ref = ref or now()
    won = [d for d in store.load("declined")
           if d.get("recovered_at") and not d.get("demo_tag")
           and (ref - (parse(d["recovered_at"]) or ref)).days <= 7]
    sent = sum(1 for e in store.events(kind="reoffer_sent")
               if (ref - (parse(e.get("at")) or ref)).days <= 7)
    return {"items_won": len(won), "value_won": round(sum(d.get("value", 0) for d in won), 2),
            "reoffers_sent": sent,
            "note": "counted from the sheets and the event log — never asserted"}


# ---------------------------------------------------------------- comebacks

COMEBACK_WINDOW_DAYS = 30
COMEBACK_FLOOR = 50


def comeback_rate(window_days=180):
    """Repeat RO, same vehicle, same system, inside 30 days of the prior one.
    Counted; refuses below the floor."""
    cutoff = now() - timedelta(days=window_days)
    ros = sorted((r for r in store.load("ros")
                  if r.get("closed_at") and (parse(r["closed_at"]) or now()) >= cutoff),
                 key=lambda r: r["closed_at"])
    if len(ros) < COMEBACK_FLOOR:
        return unmeasured(f"only {len(ros)} closed ROs in {window_days} days — need {COMEBACK_FLOOR}",
                          field="rate", n=len(ros))
    comebacks, seen = [], {}
    for r in ros:
        key = (r.get("vehicle_id"), r.get("system"))
        prior = seen.get(key)
        if prior and (parse(r["closed_at"]) - parse(prior["closed_at"])).days <= COMEBACK_WINDOW_DAYS:
            comebacks.append({"ro": r["id"], "vehicle": r.get("vehicle_id"),
                              "system": r.get("system"), "prior": prior["id"],
                              "days_after": (parse(r["closed_at"]) - parse(prior["closed_at"])).days})
        seen[key] = r
    return {"rate": round(len(comebacks) / len(ros), 3), "comebacks": len(comebacks),
            "of": len(ros), "rows": comebacks[:20],
            "note": "same vehicle, same system, ≤30 days — counted, not asserted"}


# ---------------------------------------------------------------- eval

item_eval = Eval("declined-item classification",
                 costly_label="safety_critical",
                 costly_note=("A SAFETY ITEM CALLED DEFERRABLE IS THE FAILURE THAT ENDS A SHOP. "
                              "A cabin filter flagged for a phone call is merely awkward."))

EVAL_CASES = [
    {"input": "front brake pads 2mm, rotors scored, caliper sticking", "label": "safety_critical"},
    {"input": "inner tie rod has play, alignment off", "label": "safety_critical"},
    {"input": "both rear tires worn to 2/32, cord showing on inner edge", "label": "safety_critical"},
    {"input": "cabin air filter dirty", "label": "cosmetic"},
    {"input": "engine air filter at 70%", "label": "deferrable"},
    {"input": "coolant service due by mileage", "label": "deferrable"},
    {"input": "valve cover gasket seeping, monitor", "label": "deferrable"},
    {"input": "left front wheel bearing growl, play at 12 and 6", "label": "safety_critical"},
    {"input": "wiper blades streaking", "label": "cosmetic"},
    {"input": "serpentine belt aging", "label": "deferrable"},
    {"input": "fuel line weeping at the rail", "label": "safety_critical"},
    {"input": "battery marginal on load test", "label": "deferrable"},
    {"input": "", "label": "needs_review"},
    {"input": "customer states noise sometimes", "label": "needs_review"},
    {"input": "rear brake line rusted through, weeping at the fitting", "label": "safety_critical"},
    {"input": "outer ball joint boot torn, joint has play", "label": "safety_critical"},
    {"input": "transmission service due per interval", "label": "deferrable"},
    {"input": "paint chip on hood, offered touch-up", "label": "cosmetic"},
    {"input": "driver seat belt frayed at the retractor", "label": "safety_critical"},
    {"input": "engine mount cracked, clunk on shift", "label": "deferrable"},
]


def run_eval():
    return item_eval.run(EVAL_CASES, lambda t: classify_item(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "classify_item":      {"rung": "R3", "reason": "internal classification with a safety bias; the sheet is reviewed"},
    "classify_call":      {"rung": "R3", "reason": "routing only; anything unclear goes to a person"},
    "draft_reoffer":      {"rung": "R1", "reason": "outward message — a human sends, and never for a safety item"},
    "safety_call_task":   {"rung": "R2", "reason": "an internal task for a human caller; the call itself is human"},
    "send_safety_text":   {"rung": "R0", "reason": SAFETY_CONTACT_RULE, "never_promote": True},
    "state_vehicle_safe": {"rung": "R0", "reason": "only a technician who inspected the vehicle says 'safe'", "never_promote": True},
    "quote_firm_price":   {"rung": "R1", "reason": "a firm price needs a human and an inspected car; bands come from our own ROs", "never_promote": True},
    "phone_diagnosis":    {"rung": "R0", "reason": "we do not diagnose vehicles we have not seen", "never_promote": True},
    "draft_approval_nudge": {"rung": "R1", "reason": "outward message on a presented estimate — a human sends"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Bay OS — what it computes to")
        .line("Declined work re-offered and won", "revenue", "open declined value × your close rate",
              ["open_declined_value", "reoffer_close_rate"],
              lambda g: float(g["open_declined_value"]) * float(g["reoffer_close_rate"]),
              note="the value is counted from your sheets; the close rate is your call",
              assumption="close rate is yours to argue with — we do not invent one")
        .line("Presented estimates nudged to a yes", "revenue", "aging estimates × avg RO × lift",
              ["aging_estimates", "avg_ro", "nudge_lift"],
              lambda g: float(g["aging_estimates"]) * float(g["avg_ro"]) * float(g["nudge_lift"]))
        .line("Advisor follow-up time", "time_saved", "hrs/wk × 52 × rate",
              ["followup_hours_wk", "advisor_rate"],
              lambda g: float(g["followup_hours_wk"]) * 52 * float(g["advisor_rate"]),
              note="reported separately; never summed into revenue")
        .line("Comeback exposure made visible", "scenario", "comebacks × avg RO cost",
              ["comebacks_180d", "avg_ro"],
              lambda g: float(g["comebacks_180d"]) * float(g["avg_ro"]),
              assumption="an exposure you weigh — prevented comebacks cannot be counted"))


def roi(given):
    rec = {}
    dv = declined_value()
    rec["open_declined_value"] = dv["value"]
    ros = [r for r in store.load("ros") if r.get("total")]
    if len(ros) >= 30:
        rec["avg_ro"] = round(median([r["total"] for r in ros]), 2)
    cb = comeback_rate()
    if "_missing" not in cb:
        rec["comebacks_180d"] = cb["comebacks"]
    rec["aging_estimates"] = len([r for r in store.load("ros")
                                  if r.get("state") == "presented" and not r.get("closed_at")])
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("classify_item", "classify_call", "draft_reoffer", "safety_call_task",
          "draft_approval_nudge")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("customer:",))
