#!/usr/bin/env python3
"""Pane OS — domain core (glass & glazing shops).

Rules live here: the measure-twice gate (no order releases to the fabricator
without two recorded measurements that match within the recorded tolerance),
the safety-glazing location rules ("we don't sell code violations cheaper"),
the deposit wall, the fabricator-date promise rule, break-in/board-up triage,
the remake ledger, and the matrix.

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

TABLES = ("config", "customers", "orders", "remakes", "messages", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="PANEOS_DATA_ROOT")

# ---------------------------------------------------------------- the measure-twice gate

DEFAULT_TOLERANCE = {
    "_source": ("DEFAULT measurement tolerance (1/8\"), the common fabricator spec — replace "
                "with the fabricator's actual tolerance sheet before go-live. The gate cites "
                "this number in every refusal."),
    "inches": 0.125,
}


def tolerance():
    return store.load("config").get("measurement_tolerance") or DEFAULT_TOLERANCE


def measure_check(order):
    """An order carries measurement PAIRS as recorded acts — who, when, values.
    One reading, or two that disagree beyond the recorded tolerance, refuses to
    release. There is deliberately no force path anywhere in this module."""
    tol_cfg = tolerance()
    tol = tol_cfg["inches"]
    ms = order.get("measurements") or []
    if not ms:
        return False, ("no recorded measurement at all — the gate needs two, independently "
                       "taken (who, when, values). Nothing releases to the fabricator on zero "
                       "readings.")
    if len(ms) < 2:
        m = ms[0]
        return False, (f"one recorded measurement ({m['by']}, {str(m['at'])[:10]}: "
                       f"{m['width_in']}\" × {m['height_in']}\") — the second is missing. "
                       f"Measure twice is the gate here, not a proverb: a remake starts with "
                       f"one hurried tape reading.")
    a, b = ms[0], ms[1]
    dw = round(abs(a["width_in"] - b["width_in"]), 4)
    dh = round(abs(a["height_in"] - b["height_in"]), 4)
    if dw > tol or dh > tol:
        return False, (f"the two recorded readings disagree beyond the recorded tolerance of "
                       f"{tol}\": width {a['width_in']}\" vs {b['width_in']}\" (Δ{dw}\"), "
                       f"height {a['height_in']}\" vs {b['height_in']}\" (Δ{dh}\"). Someone "
                       f"re-measures; custom glass doesn't get guessed. "
                       f"[{tol_cfg['_source'][:52]}…]")
    return True, (f"two recorded measurements match within {tol}\" — {a['by']} "
                  f"({str(a['at'])[:10]}) and {b['by']} ({str(b['at'])[:10]}); "
                  f"{b['width_in']}\" × {b['height_in']}\" goes to the fabricator")


# ---------------------------------------------------------------- the deposit wall

def deposit_check(order):
    pct = store.load("config").get("deposit_pct", 50)
    if order.get("deposit_paid_at"):
        return True, (f"deposit recorded {str(order['deposit_paid_at'])[:10]} "
                      f"(${order.get('deposit_amount', 0):,.0f})")
    return False, (f"no recorded deposit — no fabrication release. Custom glass has no second "
                   f"buyer; the {pct}% deposit is the order's commitment, and 'they'll pay "
                   f"when they see it' is how a shop fabricates someone else's maybe.")


def deposits_uncollected():
    """Counted: accepted orders sitting unfabricated with no deposit on record —
    the cash the deposit wall would already have in hand."""
    pct = store.load("config").get("deposit_pct", 50)
    rows = [o for o in store.load("orders")
            if not o.get("demo_tag") and o.get("stage") == "deposit"
            and not o.get("deposit_paid_at")]
    return {"count": len(rows),
            "value": round(sum(o.get("amount", 0) * pct / 100.0 for o in rows), 2),
            "pct": pct,
            "note": "counted from the order ledger — never asserted"}


# ---------------------------------------------------------------- safety-glazing locations

DEFAULT_SAFETY_RULES = {
    "_source": ("DEFAULT hazardous-location rule set, simplified from common code practice "
                "(IRC R308.4-shaped) — replace with the jurisdiction's adopted code before "
                "go-live. Every refusal cites the rule; this is the shop's recorded rule "
                "table, not legal advice."),
    "required": "tempered (or laminated) safety glazing",
    "rules": [
        {"location": "door", "label": "glazing in a door",
         "rule": "all glazing in doors requires safety glazing"},
        {"location": "tub_shower", "label": "tub or shower enclosure",
         "rule": "glazing in tub and shower enclosures requires safety glazing"},
        {"location": "near_floor", "label": "pane with its bottom edge within 18\" of the floor",
         "rule": "large panes near the floor require safety glazing"},
        {"location": "stairs", "label": "glazing adjacent to stairs or landings",
         "rule": "glazing next to stairways and landings requires safety glazing"},
    ],
}


def safety_rules():
    return store.load("config").get("safety_rules") or DEFAULT_SAFETY_RULES


def safety_check(location, glass_type):
    """A quote for annealed glass in a recorded hazardous location is refused
    with the rule cited. We don't sell code violations cheaper."""
    rules = safety_rules()
    rule = next((r for r in rules["rules"] if r["location"] == (location or "").lower()), None)
    if rule and (glass_type or "").lower() == "annealed":
        return {"refused": (f"{rule['label']} is a recorded hazardous location: {rule['rule']}. "
                            f"Annealed glass there is refused — we don't sell code violations "
                            f"cheaper; the quote drafts as {rules['required']}."),
                "rule": rule, "required": rules["required"],
                "rules_source": rules["_source"]}
    return {"ok": True, "location": location, "glass_type": glass_type,
            "note": ("no recorded hazardous-location rule matched" if not rule
                     else f"{rules['required']} in a {rule['label']} — the rule is satisfied")}


# ---------------------------------------------------------------- the fabricator's date

def lead_time(order):
    """A customer promise cites the fabricator's recorded promised date, or it
    refuses. A lead time from hope is a guess with a customer attached."""
    fab = store.load("config").get("fabricator", "the fabricator")
    d = (order or {}).get("fabricator_promised_at")
    if d:
        return {"date": d, "basis": f"{fab}'s recorded promised date",
                "note": ("cited from the record — install scheduling starts from this date, "
                         "not from hope")}
    return unmeasured("no recorded fabricator date on this order — a lead time promised from "
                      "hope is a guess with a customer attached; we cite the fabricator's "
                      "date or we say 'not yet'", field="date")


# ---------------------------------------------------------------- triage

BREAKIN = (
    r"\b(smashed|shattered|break[- ]?in|broke in|broken into|vandal\w*)\b",
    r"\bboard[- ]?(it )?up\b",
    r"\b(glass everywhere|open to the street)\b",
)
WARRANTY = (
    r"\b(seal (failed|failure)|foggy|fogged|fogging|condensation|moisture|cloudy)\b",
    r"\bbetween the panes\b",
)
CHANGE = (
    r"\b(change|switch|resize|instead|different size)\b",
)
STATUS = (
    r"\b(status|update)\b",
    r"\b(ready|done|finished|installed)\b",
    r"\bwhen will\b",
)
QUOTE = (
    r"\b(quote|estimate|how much|price|pricing|cost)\b",
)


def read_message(text):
    """breakin_boardup | quote_ask | status | warranty_claim | change_request |
    human. The break-in reads FIRST — an open storefront is a security event,
    and it does not wait behind shower quotes."""
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty message — a person reads it"}
    for rx in BREAKIN:
        if re.search(rx, t):
            return {"label": "breakin_boardup",
                    "why": "a break-in / board-up emergency — an open storefront is a "
                           "security event; the board-up dispatches first and the glass "
                           "order comes second"}
    for rx in WARRANTY:
        if re.search(rx, t):
            return {"label": "warranty_claim",
                    "why": "a seal-failure / warranty claim — answered from the order record "
                           "and the fabricator's warranty terms, never guessed at the counter"}
    for rx in CHANGE:
        if re.search(rx, t):
            return {"label": "change_request",
                    "why": "a change request — priced against where the order sits; a change "
                           "after the fabricator release is a new unit, said out loud"}
    for rx in STATUS:
        if re.search(rx, t):
            return {"label": "status",
                    "why": "a status ask — answered from the fabricator's recorded date, or "
                           "honestly not at all"}
    for rx in QUOTE:
        if re.search(rx, t):
            return {"label": "quote_ask",
                    "why": "a quote ask — the safety-location rules run before any price "
                           "leaves the shop"}
    return {"label": "human", "why": "no clean signal — a person reads it"}


# ---------------------------------------------------------------- the remake ledger

REMAKE_CAUSES = ("measure", "fab", "install", "customer")


def remake_rate(window_days=365, floor=30, ref=None):
    """The counted remake rate — the shop's own number, never an industry
    estimate. Below the floor of completed orders it refuses to state a rate."""
    ref = ref or now()
    cutoff = ref - timedelta(days=window_days)
    done = [o for o in store.load("orders")
            if o.get("installed_at") and (parse(o["installed_at"]) or ref) >= cutoff]
    rems = [r for r in store.load("remakes") if (parse(r.get("at")) or ref) >= cutoff]
    if len(done) < floor:
        return unmeasured(f"only {len(done)} completed orders in {window_days} days; need "
                          f"{floor} to state a rate — a remake rate off a handful of jobs is "
                          f"noise wearing a percent sign", field="rate", remakes=len(rems))
    cost = round(sum(r.get("cost", 0) for r in rems), 2)
    return {"rate": round(len(rems) / len(done), 3), "remakes": len(rems),
            "completed": len(done),
            "by_cause": {c: sum(1 for r in rems if r.get("cause") == c) for c in REMAKE_CAUSES},
            "cost": cost, "avg_cost": round(cost / len(rems), 2) if rems else None,
            "note": "the shop's own number, counted from the remake ledger — never estimated"}


# ---------------------------------------------------------------- the pipeline, counted

def pipeline():
    counts = {"quote": 0, "deposit": 0, "fabrication": 0, "install": 0, "done": 0}
    single = mismatched = awaiting_deposit = 0
    tol = tolerance()["inches"]
    for o in store.load("orders"):
        if o.get("demo_tag"):
            continue
        counts[o.get("stage", "quote")] = counts.get(o.get("stage", "quote"), 0) + 1
        if o.get("stage") != "deposit" or o.get("released_at"):
            continue
        ms = o.get("measurements") or []
        if len(ms) < 2:
            single += 1
        else:
            a, b = ms[0], ms[1]
            if abs(a["width_in"] - b["width_in"]) > tol \
               or abs(a["height_in"] - b["height_in"]) > tol:
                mismatched += 1
        if not o.get("deposit_paid_at"):
            awaiting_deposit += 1
    return {"stages": counts,
            "held_at_measure_gate": {"single": single, "mismatched": mismatched},
            "awaiting_deposit": awaiting_deposit,
            "note": "counted from the order ledger; demo fixtures excluded"}


def recovered_this_week(ref=None):
    """Counted: board-ups dispatched, deposits collected, releases a human
    approved, installs completed."""
    ref = ref or now()
    orders = store.load("orders")
    deposits = [o for o in orders if o.get("deposit_paid_at")
                and (ref - (parse(o["deposit_paid_at"]) or ref)).days <= 7]
    installs = [o for o in orders if o.get("installed_at")
                and (ref - (parse(o["installed_at"]) or ref)).days <= 7]
    boardups = sum(1 for e in store.events(kind="dispatch_board_up")
                   if (ref - (parse(e.get("at")) or ref)).days <= 7)
    releases = sum(1 for e in store.events(kind="release_to_fabricator")
                   if str(e.get("actor", "")).startswith("human:")
                   and (ref - (parse(e.get("at")) or ref)).days <= 7)
    return {"boardups_dispatched": boardups,
            "deposits_collected": round(sum(o.get("deposit_amount", 0) for o in deposits), 2),
            "deposit_count": len(deposits),
            "releases_approved": releases, "installs_done": len(installs),
            "note": "counted from the order ledger and the event log — never asserted"}


# ---------------------------------------------------------------- eval

triage_eval = Eval("message triage",
                   costly_label="breakin_boardup",
                   costly_note=("AN OPEN STOREFRONT AT NIGHT IS A SECURITY EVENT — every "
                                "unboarded hour is the store's inventory on the sidewalk, and "
                                "it never queues behind a shower quote. Over-routing a quote "
                                "ask costs a read."))

EVAL_CASES = [
    {"input": "someone smashed our storefront window, glass everywhere, we're open to the street",
     "label": "breakin_boardup"},
    {"input": "break in last night, the front door glass is shattered", "label": "breakin_boardup"},
    {"input": "vandals broke the shop window, can you board it up tonight",
     "label": "breakin_boardup"},
    {"input": "how much for a frameless shower door", "label": "quote_ask"},
    {"input": "can you give me a quote on replacing two windows", "label": "quote_ask"},
    {"input": "price for a mirror over the bathroom vanity", "label": "quote_ask"},
    {"input": "is my shower glass ready yet", "label": "status"},
    {"input": "any update on the storefront order", "label": "status"},
    {"input": "when will the glass be in for the install", "label": "status"},
    {"input": "our window is all foggy between the panes", "label": "warranty_claim"},
    {"input": "the seal failed on the picture window, there's condensation inside",
     "label": "warranty_claim"},
    {"input": "actually we want the shower door hinged on the left instead",
     "label": "change_request"},
    {"input": "can we change the glass to bronze tint before you order it",
     "label": "change_request"},
    {"input": "", "label": "human"},
    {"input": "what time do you open saturday", "label": "human"},
]


def run_eval():
    return triage_eval.run(EVAL_CASES, lambda t: read_message(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_message":        {"rung": "R3", "reason": "routing only; the board-up reads first"},
    "dispatch_board_up":   {"rung": "R2", "reason": "an open storefront is a security event — the crew moves now, the owner is told; reversible, logged"},
    "release_order_without_matching_measurements": {"rung": "R0", "reason": "two recorded measurements that match within the recorded tolerance, or nothing releases — a remake is born from one hurried reading", "never_promote": True},
    "quote_annealed_in_safety_location": {"rung": "R0", "reason": "the recorded hazardous-location rules are cited in the refusal — we don't sell code violations cheaper", "never_promote": True},
    "promise_undated_lead_time": {"rung": "R0", "reason": "promises cite the fabricator's recorded date — a lead time from hope is a guess with a customer attached", "never_promote": True},
    "release_fabrication_without_deposit": {"rung": "R0", "reason": "no deposit, no fabrication — custom glass has no second buyer", "never_promote": True},
    "release_to_fabricator": {"rung": "R1", "reason": "fabrication spend — a human clicks the release, past both structural gates"},
    "draft_boardup_reply": {"rung": "R1", "reason": "outward reply — a human sends; the dispatch itself already moved"},
    "draft_quote":         {"rung": "R1", "reason": "outward quote — a human sends, with the safety check already run"},
    "draft_status_reply":  {"rung": "R1", "reason": "outward reply — cites the fabricator's recorded date, or honestly none"},
    "draft_warranty_reply": {"rung": "R1", "reason": "outward reply — the order record and warranty terms do the talking"},
    "draft_change_reply":  {"rung": "R1", "reason": "outward reply — a change after release is a new unit, said out loud"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Pane OS — what it computes to")
        .line("Remakes avoided at the measure-twice gate", "scenario",
              "counted remakes/yr × recorded avg remake cost × your lift",
              ["remakes_12mo", "avg_remake_cost", "remake_lift"],
              lambda g: float(g["remakes_12mo"]) * float(g["avg_remake_cost"])
                        * float(g["remake_lift"]),
              assumption="prevented remakes cannot be counted — the ledger and the cost are "
                         "your own recorded numbers; the lift is your call, never ours")
        .line("Deposit float, collected before fabrication", "cash_timing",
              "uncollected deposits on accepted orders (counted)",
              ["deposits_uncollected"], lambda g: float(g["deposits_uncollected"]),
              note="cash timing — money the deposit wall would already have in hand")
        .line("Board-up work captured", "revenue",
              "board-up jobs/yr (counted) × your average ticket",
              ["board_up_jobs", "avg_boardup_ticket"],
              lambda g: float(g["board_up_jobs"]) * float(g["avg_boardup_ticket"]),
              note="the job count is counted from the order ledger; the ticket is yours")
        .line("Office hours off the phone", "time_saved", "hrs/wk × 52 × rate",
              ["office_hours_wk", "office_rate"],
              lambda g: float(g["office_hours_wk"]) * 52 * float(g["office_rate"])))


def roi(given):
    rr = remake_rate()
    rec = {"deposits_uncollected": deposits_uncollected()["value"],
           "board_up_jobs": sum(1 for o in store.load("orders")
                                if o.get("job_type") == "board_up" and not o.get("demo_tag"))}
    if not (isinstance(rr, dict) and "_missing" in rr):
        rec["remakes_12mo"] = rr["remakes"]
        rec["avg_remake_cost"] = rr["avg_cost"]
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("read_message", "dispatch_board_up", "release_to_fabricator", "draft_boardup_reply",
          "draft_quote", "draft_status_reply", "draft_warranty_reply", "draft_change_reply")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("customer:",))
