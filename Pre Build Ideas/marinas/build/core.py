#!/usr/bin/env python3
"""Slip OS — domain core (marina & boat yard).

Rules live here: spill-first triage (regulator-grade verbatim), the work-
authorization gate (no clock-in without the recorded scope+rate), the storage
clamp (billing stops at the recorded departure), the slip waitlist with fit
arithmetic, the seaworthiness refusal, and the matrix.

Stdlib only. Honesty rules come from `_kit`.
"""
import math, re, sys
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent))

from _kit.moat import Eval, Gate, Matrix, Roi                       # noqa: E402
from _kit.store import (Store, automation_rate, iso, median, now,   # noqa: E402
                        parse, unmeasured)

TABLES = ("config", "slips", "vessels", "workorders", "waitlist", "messages",
          "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="SLIPOS_DATA_ROOT")

SPILL_PROTOCOL = ("Logged verbatim with a timestamp. The dockmaster is being reached NOW. "
                  "Booms deploy per the spill plan; nothing about cause or quantity is asserted "
                  "or denied by this system — a fuel-dock log entry is a USCG exhibit.")

# ---------------------------------------------------------------- triage

SPILL = (
    r"\b(fuel|diesel|gas|oil)\b.*\b(spill|sheen|in the water|overboard|leak(ing)? into)\b",
    r"\b(sheen|slick)\b.*\b(water|dock|slip)\b",
    r"\bspill(ed)?\b.*\b(fuel|diesel|pump|dock)\b",
)
WORK_REQUEST = (
    r"\b(haul|bottom paint|winteriz|shrink ?wrap|service|repair|fix|replace)\w*\b.*"
    r"\b(boat|engine|hull|prop|outdrive|vessel)\b",
    r"\b(boat|engine|hull)\b.*\b(haul|paint|service|repair|winteriz)\w*",
)
WAITLIST_ASK = (
    r"\b(slip|dock ?space|mooring)\b.*\b(available|open(ing)?|waitlist|list)\b",
    r"\b(any|a) slip\b|\bget (a|on the) (slip|list)\b",
)
BILLING = (
    r"\b(bill|invoice|charge|statement|storage fee)\b",
)


def read_message(text):
    """spill | work_request | waitlist | billing | human. Spill first."""
    t = (text or "").lower().strip()
    if not t:
        return {"label": "human", "why": "empty message — a person reads it"}
    for rx in SPILL:
        if re.search(rx, t):
            return {"label": "spill", "protocol": SPILL_PROTOCOL,
                    "why": "a fuel/oil signal on the water — the dockmaster NOW, verbatim log; "
                           "a spill entry is a USCG exhibit"}
    for rx in WORK_REQUEST:
        if re.search(rx, t):
            return {"label": "work_request",
                    "why": "yard work — a work order drafts; the clock-in gate holds until the "
                           "owner's recorded authorization exists"}
    for rx in WAITLIST_ASK:
        if re.search(rx, t):
            return {"label": "waitlist", "why": "slip inquiry — the fit arithmetic answers"}
    for rx in BILLING:
        if re.search(rx, t):
            return {"label": "billing", "why": "billing — draft at R1"}
    return {"label": "human", "why": "no clean signal — a person reads it"}


# ---------------------------------------------------------------- the authorization gate

def can_start_work(wo):
    """A work order clocks in only with the owner's recorded authorization for
    THAT scope and rate. Verbal is a note, not a gate pass."""
    auth = wo.get("authorization")
    if auth and auth.get("by") and auth.get("scope") and auth.get("rate_basis"):
        return True, (f"authorized by {auth['by']}: \"{auth['scope'][:50]}\" at "
                      f"{auth['rate_basis']}")
    if wo.get("verbal_note"):
        return False, (f"a verbal go-ahead is on file (\"{wo['verbal_note'][:40]}…\") and it is "
                       f"a note, not a gate pass. Disputed yard bills all start with 'he said "
                       f"go ahead at the fuel dock'.")
    return False, ("no recorded owner authorization for this scope and rate — the crew doesn't "
                   "clock in. The authorization is what a disputed bill reads from.")


# ---------------------------------------------------------------- the storage clamp

def storage_bill(vessel, ref=None):
    """Storage computes from recorded arrival to recorded departure (or today)
    BY CONSTRUCTION — no argument produces a day past the departure."""
    ref = ref or now()
    start = parse(vessel.get("arrived_at"))
    if not start:
        return unmeasured("no recorded arrival — storage cannot be billed", field="days")
    rate = vessel.get("storage_rate_day")
    if not rate:
        return unmeasured("no recorded storage rate — nothing can be priced", field="total")
    end = parse(vessel.get("departed_at")) or ref
    days = max(1, math.ceil((end - start).total_seconds() / 86400))
    return {"days": days, "rate": rate, "total": round(days * rate, 2),
            "ends_at": "the recorded departure" if vessel.get("departed_at") else "today (still here)"}


# ---------------------------------------------------------------- the waitlist

def slip_fit(slip, want):
    """Fit is arithmetic: length, beam, draft vs the slip's recorded dimensions."""
    problems = []
    for dim in ("length_ft", "beam_ft", "draft_ft"):
        need, have = want.get(dim), slip.get(f"max_{dim}")
        if need is None or have is None:
            return {"fit": None, "why": f"missing {dim} on the request or the slip — fit is "
                                        f"unknowable, not assumed"}
        if need > have:
            problems.append(f"{dim.replace('_ft', '')} {need}ft > slip max {have}ft")
    if problems:
        return {"fit": False, "why": "; ".join(problems)}
    return {"fit": True, "why": "fits on all three dimensions"}


def ranked_waitlist(slip):
    """Fit-checked candidates for an open slip, in recorded waitlist order —
    the shoebox, replaced by arithmetic and a first-refusal window."""
    rows, blocked = [], []
    for w in sorted(store.load("waitlist"), key=lambda x: x.get("since") or ""):
        if w.get("offered_at") or w.get("placed_at"):
            continue
        fit = slip_fit(slip, w)
        if fit["fit"] is True:
            rows.append({"waitlist": w["id"], "name": w.get("name"), "since": w.get("since"),
                         "boat": f"{w.get('length_ft')}ft"})
        else:
            blocked.append({"name": w.get("name"), "why": fit["why"]})
    return {"candidates": rows[:5], "blocked": blocked[:5],
            "note": "recorded order, fit-checked — offers go out in waves with 48h first refusal"}


def recovered_this_week(ref=None):
    """Counted: work orders authorized and started, slips filled, spills
    escalated."""
    ref = ref or now()
    started = [w for w in store.load("workorders")
               if w.get("started_at") and (ref - (parse(w["started_at"]) or ref)).days <= 7]
    placed = [w for w in store.load("waitlist")
              if w.get("placed_at") and (ref - (parse(w["placed_at"]) or ref)).days <= 7]
    spills = sum(1 for e in store.events(kind="escalate_spill")
                 if (ref - (parse(e.get("at")) or ref)).days <= 7)
    return {"workorders_started": len(started), "slips_filled": len(placed),
            "spills_escalated": spills,
            "note": "counted from the yard records and the event log — never asserted"}


# ---------------------------------------------------------------- eval

triage_eval = Eval("message triage",
                   costly_label="spill",
                   costly_note=("A SHEEN ON THE WATER HANDLED CASUALLY IS A USCG EXHIBIT WITH "
                                "THE MARINA'S NAME ON IT. Over-routing a billing note costs a "
                                "read."))

EVAL_CASES = [
    {"input": "there's diesel in the water by the fuel dock", "label": "spill"},
    {"input": "seeing a sheen around slip 40 this morning", "label": "spill"},
    {"input": "someone spilled fuel at the pump-out station", "label": "spill"},
    {"input": "oil is leaking into the water from the trawler", "label": "spill"},
    {"input": "need the boat hauled and bottom paint before june", "label": "work_request"},
    {"input": "can you winterize the engine this month", "label": "work_request"},
    {"input": "fix the outdrive on the boat before the weekend", "label": "work_request"},
    {"input": "any slip open for a 32 footer this season", "label": "waitlist"},
    {"input": "how do I get on the list for dock space", "label": "waitlist"},
    {"input": "question about my storage fee this quarter", "label": "billing"},
    {"input": "", "label": "human"},
    {"input": "the launch ramp gate code isn't working", "label": "human"},
    {"input": "shrink wrap the boat when you haul it", "label": "work_request"},
    {"input": "is there a sheen by the transient dock or is that just pollen", "label": "spill"},
]


def run_eval():
    return triage_eval.run(EVAL_CASES, lambda t: read_message(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "read_message":       {"rung": "R3", "reason": "routing only; spill-first is the point"},
    "escalate_spill":     {"rung": "R2", "reason": "the dockmaster and the verbatim log cannot wait"},
    "assert_spill_cause": {"rung": "R0", "reason": "a spill entry is a USCG exhibit — nothing asserted, nothing denied", "never_promote": True},
    "start_work_unauthorized": {"rung": "R0", "reason": "no recorded authorization, no clock-in — by construction", "never_promote": True},
    "assert_seaworthiness": {"rung": "R0", "reason": "a licensed marine surveyor's word, never software's", "never_promote": True},
    "bill_past_departure": {"rung": "R0", "reason": "the meter stops at the recorded departure — by construction", "never_promote": True},
    "draft_workorder":    {"rung": "R1", "reason": "the authorization request drafts — the owner clicks, then the crew clocks in"},
    "draft_slip_offer":   {"rung": "R1", "reason": "outward offer — a human sends, 48h first refusal"},
    "draft_billing_reply": {"rung": "R1", "reason": "outward reply — a human sends"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Slip OS — what it computes to")
        .line("Waitlist conversions", "revenue", "open slips filled × annual slip revenue",
              ["slips_filled_yr", "annual_slip"],
              lambda g: float(g["slips_filled_yr"]) * float(g["annual_slip"]))
        .line("Disputed yard bills avoided at the gate", "scenario", "disputes/yr × avg write-down",
              ["disputes_yr", "avg_writedown"],
              lambda g: float(g["disputes_yr"]) * float(g["avg_writedown"]),
              assumption="prevented disputes cannot be counted — your history, priced by you")
        .line("Office hours", "time_saved", "hrs/wk × 52 × rate",
              ["office_hours_wk", "office_rate"],
              lambda g: float(g["office_hours_wk"]) * 52 * float(g["office_rate"]))
        .line("The spill log", "scenario", "you decide what a clean USCG file is worth",
              ["spill_value"], lambda g: float(g["spill_value"]),
              assumption="never a saving — a clean file is not our number to model"))


def roi(given):
    rec = {}
    rec["open_slips"] = len([s for s in store.load("slips") if not s.get("occupied_by")])
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


MOVING = ("read_message", "escalate_spill", "draft_workorder", "draft_slip_offer",
          "draft_billing_reply")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("owner:",))
