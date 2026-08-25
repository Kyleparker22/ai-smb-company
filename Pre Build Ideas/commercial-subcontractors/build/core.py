#!/usr/bin/env python3
"""Change OS — domain core (commercial subcontractor).

Everything rule-shaped lives here: the change-event classifier and its
deliberate bias, the CO state machine with the no-directive submit refusal,
pay-app and retainage arithmetic, the per-state notice/lien rule engine, the
GC pay-speed score, and the autonomy matrix.

The thesis: a sub's margin leaks where the work was ALREADY performed — the
extra run on a superintendent's say-so that never became a CO, the retainage
that outlives the job, the notice deadline tracked in someone's head.

Stdlib only. Honesty rules come from `_kit` and are not re-implemented.
"""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent))

from _kit.moat import Eval, Gate, Matrix, Roi                       # noqa: E402
from _kit.store import (Store, automation_rate, days_until, iso,    # noqa: E402
                        median, now, parse, unmeasured)

TABLES = ("config", "projects", "gcs", "notes", "change_events", "cos",
          "pay_apps", "invitations", "approvals", "events")
store = Store(ROOT / "data", TABLES, env_var="CHANGEOS_DATA_ROOT")


# ---------------------------------------------------------------- change-event capture

# Signals that a field note describes work OUTSIDE the base contract. The bias
# is deliberate: flagging a base-scope note costs a PM thirty seconds; missing
# a change event costs the whole ticket. The costly eval class is the miss.
CHANGE_SIGNALS = (
    (r"\b(gc|super|superintendent|owner|architect)\s+(directed|told|asked|wants?|said)\b", "somebody directed work"),
    (r"\bnot (in|on) (the )?(contract|drawings|scope|plans)\b", "outside the documents"),
    (r"\b(extra|additional|added)\s+(work|run|circuit|duct|pipe|footing|pour|labor)\b", "added work named"),
    (r"\brework\b|\bre-?(ran|run|did|done|pour)\b", "rework"),
    (r"\bfield (directive|order|change)\b|\bt&m\b|\btime and material", "directive or T&M language"),
    (r"\bchanged? (the )?(spec|layout|routing|location|design)\b", "a change to the documents"),
    (r"\bdelay(ed)?\b.*\b(trade|gc|owner|weather)\b", "delay with a named cause"),
    (r"\brfi\b", "an RFI in play"),
)
BASE_SIGNALS = (
    (r"\bper (the )?(plans|drawings|spec|contract)\b", "per the documents"),
    (r"\b(installed|completed|finished|hung|set|poured|ran)\b", "base production language"),
)


def classify_note(text):
    """base_scope | change_event | ambiguous. Empty or unreadable is ambiguous —
    a note nobody can read is a note a human reads."""
    t = (text or "").lower().strip()
    if not t:
        return {"label": "ambiguous", "why": "empty note — a human reads it"}
    change = [why for rx, why in CHANGE_SIGNALS if re.search(rx, t)]
    base = [why for rx, why in BASE_SIGNALS if re.search(rx, t)]
    if change:
        return {"label": "change_event", "why": "; ".join(change[:3])}
    if base:
        return {"label": "base_scope", "why": "; ".join(base[:2])}
    return {"label": "ambiguous", "why": "no signal matched — routed to the PM, never guessed"}


# ---------------------------------------------------------------- the CO state machine

CO_STATES = ("draft", "submitted", "approved", "billed", "paid", "rejected")


def can_submit(co):
    """THE refusal this build is organised around: a CO with no recorded signed
    directive or written authorization is a dispute waiting to be mailed."""
    if co.get("directive_ref"):
        return True, "written authorization on file"
    return False, ("no signed directive or written authorization on file — a verbal CO "
                   "submitted in writing becomes a dispute, not a payment; get it signed first")


def advance_co(co, to_state):
    order = {s: i for i, s in enumerate(CO_STATES)}
    cur = co.get("state", "draft")
    if to_state == "rejected":
        return True, "rejection recorded"
    if to_state not in order or cur not in order:
        return False, f"unknown state {to_state}"
    if order[to_state] != order[cur] + 1:
        return False, f"cannot jump {cur} → {to_state}"
    if to_state == "submitted":
        ok, why = can_submit(co)
        if not ok:
            return False, why
    return True, "ok"


def unbilled_change_value(project_id=None):
    """Counted from the ledger: change events with a drafted value that have not
    reached `billed`. Never an industry percentage."""
    rows = [c for c in store.load("cos")
            if c.get("state") in ("draft", "submitted", "approved")
            and (project_id is None or c.get("project_id") == project_id)]
    return {"count": len(rows), "value": round(sum(c.get("value", 0) for c in rows), 2),
            "note": "counted from this ledger — not an industry percentage"}


# ---------------------------------------------------------------- pay apps + retainage

def project_money(p):
    """Billed / paid / retainage held, counted from pay apps. A project with no
    schedule of values refuses its % complete."""
    apps = [a for a in store.load("pay_apps") if a["project_id"] == p["id"]]
    billed = sum(a.get("billed", 0) for a in apps)
    paid = sum(a.get("paid", 0) for a in apps)
    held = sum(a.get("retainage_held", 0) for a in apps) - sum(a.get("retainage_released", 0) for a in apps)
    out = {"billed": round(billed, 2), "paid": round(paid, 2),
           "retainage_held": round(held, 2),
           "open_receivable": round(billed - paid, 2)}
    if p.get("contract_value"):
        out["pct_billed"] = round(billed / p["contract_value"], 3)
    else:
        out.update(unmeasured("no schedule of values on file — % complete unknowable", field="pct_billed"))
    return out


def retainage_aging():
    """Retainage on substantially-complete projects, aged from completion. This
    is the cash nobody owns."""
    rows = []
    for p in store.load("projects"):
        if not p.get("substantial_completion"):
            continue
        m = project_money(p)
        if m["retainage_held"] <= 0:
            continue
        age = -(days_until(p["substantial_completion"]) or 0)
        rows.append({"project": p["name"], "project_id": p["id"], "gc_id": p["gc_id"],
                     "held": m["retainage_held"], "days_since_completion": age,
                     "overdue": age > (p.get("retainage_terms_days") or 60)})
    return sorted(rows, key=lambda r: -r["held"])


# The retainage chase is a LADDER, not a drip: three steps, cooldown between
# them, and a hard stop. After the last unanswered step the row leaves the
# message lane entirely — silence is an answer, and the answer is a phone call.
RETAINAGE_LADDER = (
    {"step": 1, "days_overdue": 0,  "kind": "friendly"},
    {"step": 2, "days_overdue": 21, "kind": "specific"},
    {"step": 3, "days_overdue": 45, "kind": "final"},
)
RETAINAGE_COOLDOWN_DAYS = 10


def due_retainage_touch(row, touches, ref=None):
    """Which ladder step (if any) is due for this overdue retainage row.
    Returns the step dict, {'escalate': True} past the ladder, or None."""
    ref = ref or now()
    if not row.get("overdue"):
        return None
    done = sorted(t["step"] for t in touches)
    terms = row.get("terms_days") or 60
    overdue_days = row["days_since_completion"] - terms
    if done and (ref - parse(max(t["at"] for t in touches))).days < RETAINAGE_COOLDOWN_DAYS:
        return None
    if len(done) >= len(RETAINAGE_LADDER):
        return {"escalate": True,
                "why": (f"{len(done)} unanswered chases — silence is an answer; "
                        "this stops being a message and becomes a phone call")}
    nxt = RETAINAGE_LADDER[len(done)]
    if overdue_days >= nxt["days_overdue"]:
        return nxt
    return None


def recovered_this_week(ref=None):
    """Counted from the event log, never asserted: COs that reached submission
    (a human clicked send) and retainage releases recorded in the last 7 days."""
    ref = ref or now()
    cos_submitted = ret_released = 0.0
    n_cos = n_rel = n_chase = 0
    for e in store.events():
        at = parse(e.get("at"))
        if not at or (ref - at).days > 7:
            continue
        d = e.get("detail") or {}
        if e["kind"] == "submit_co_done":
            n_cos += 1
            cos_submitted += float(d.get("value") or 0)
        elif e["kind"] == "retainage_released":
            n_rel += 1
            ret_released += float(d.get("amount") or 0)
        elif e["kind"] == "retainage_chase_sent":
            n_chase += 1
    return {"cos_submitted": n_cos, "co_value": round(cos_submitted, 2),
            "releases": n_rel, "released_value": round(ret_released, 2),
            "chases_sent": n_chase,
            "note": "counted from the event log — a week with nothing recorded reads zero, honestly"}


def gc_pay_speed(gc_id):
    """Median days from billed to paid, counted from THIS sub's pay apps with
    that GC. Below 4 paid apps we refuse — reputation is not a number."""
    apps = [a for a in store.load("pay_apps")
            if a.get("gc_id") == gc_id and a.get("paid_at") and a.get("billed_at")]
    days = [d for d in ((parse(a["paid_at"]) - parse(a["billed_at"])).days for a in apps) if d >= 0]
    if len(days) < 4:
        return unmeasured(f"only {len(days)} paid pay-apps with this GC — need 4 to state a speed",
                          field="median_days", n=len(days))
    return {"median_days": median(days), "n": len(days), "basis": "median billed→paid, our own ledger"}


# ---------------------------------------------------------------- notice & lien calendar

# DEFAULT rules. Simplified shapes of two real regimes, and the config names
# itself replaceable — deadline law is exactly where a hardcoded default would
# eventually be wrong in the worst possible way.
DEFAULT_NOTICE_RULES = {
    "_source": ("DEFAULT rule set, simplified — replace with counsel-reviewed rules per state "
                "before go-live. Every date below is a DATE ALERT, not legal advice."),
    "TX": {"steps": [
        {"key": "monthly_notice", "label": "monthly notice", "days_after_first_furnish": 75},
        {"key": "lien_affidavit", "label": "lien affidavit", "days_after_final_furnish": 105},
    ]},
    "FL": {"steps": [
        {"key": "notice_to_owner", "label": "notice to owner", "days_after_first_furnish": 45},
        {"key": "lien_claim", "label": "claim of lien", "days_after_final_furnish": 90},
    ]},
}


def notice_rules():
    cfg = store.load("config")
    return cfg.get("notice_rules") or DEFAULT_NOTICE_RULES


def deadline_board(ref=None):
    """Every computed deadline across open projects, soonest first. A project
    with no furnishing dates cannot have a deadline computed — said, not guessed."""
    rules = notice_rules()
    ref = ref or now()
    rows, uncomputable = [], []
    for p in store.load("projects"):
        state_rules = rules.get(p.get("state_code") or "")
        if not state_rules:
            uncomputable.append({"project": p["name"],
                                 "why": f"no rule set for state {p.get('state_code')!r}"})
            continue
        done = set(p.get("notices_filed") or [])
        for s in state_rules["steps"]:
            if s["key"] in done:
                continue
            if "days_after_first_furnish" in s:
                base, base_label = p.get("first_furnish"), "first furnishing"
                offset = s["days_after_first_furnish"]
            else:
                base, base_label = p.get("final_furnish"), "final furnishing"
                offset = s["days_after_final_furnish"]
            if not base:
                uncomputable.append({"project": p["name"],
                                     "why": f"{s['label']}: no {base_label} date recorded"})
                continue
            due = parse(base)
            from datetime import timedelta
            due = due + timedelta(days=offset)
            rows.append({"project": p["name"], "project_id": p["id"], "state": p["state_code"],
                         "step": s["label"], "due": iso(due),
                         "days_left": (due - ref).days,
                         "label": "DATE ALERT — not legal advice"})
    rows.sort(key=lambda r: r["days_left"])
    return {"deadlines": rows, "uncomputable": uncomputable, "rules_source": rules["_source"]}


# ---------------------------------------------------------------- invitation triage

def invitation_score(inv):
    """Go/no-go with the reasons on the row. Pay speed comes from OUR ledger;
    an unknown GC scores on what we can see and says so."""
    reasons, score = [], 50
    gc = store.by_id("gcs", inv.get("gc_id")) or {}
    speed = gc_pay_speed(inv.get("gc_id"))
    if "_missing" in speed:
        reasons.append(f"pay speed unknown: {speed['_missing']}")
    elif speed["median_days"] <= 45:
        score += 20
        reasons.append(f"GC pays in a median {speed['median_days']:.0f} days (n={speed['n']})")
    elif speed["median_days"] > 75:
        score -= 25
        reasons.append(f"GC pays in a median {speed['median_days']:.0f} days (n={speed['n']}) — slow money")
    if inv.get("trade_fit"):
        score += 15
        reasons.append("squarely our trade")
    else:
        score -= 10
        reasons.append("edge of our trade")
    if inv.get("bond_required") and not (store.load("config").get("bonding_capacity") or 0) >= inv.get("value", 0):
        score -= 30
        reasons.append("bond required beyond recorded capacity")
    backlog = [p for p in store.load("projects") if not p.get("substantial_completion")]
    if len(backlog) >= (store.load("config").get("comfortable_backlog") or 20):
        score -= 10
        reasons.append(f"{len(backlog)} open projects — capacity is the constraint")
    return {"score": max(0, min(100, score)), "reasons": reasons,
            "gc": gc.get("name", "unknown GC")}


# ---------------------------------------------------------------- eval

change_eval = Eval("change-event capture",
                   costly_label="change_event",
                   costly_note=("A MISSED CHANGE EVENT IS MONEY NEVER BILLED. A false flag costs a "
                                "PM thirty seconds; the bias is over-flagging on purpose."))

EVAL_CASES = [
    {"input": "super directed us to add a second condensate run on L3", "label": "change_event"},
    {"input": "GC wants the duct rerouted around the new steel, not on drawings", "label": "change_event"},
    {"input": "installed VAV boxes per plans, floor 2 complete", "label": "base_scope"},
    {"input": "re-ran the feeder after the layout changed", "label": "change_event"},
    {"input": "poured footings per spec, section B", "label": "base_scope"},
    {"input": "T&M ticket signed for saturday demo work", "label": "change_event"},
    {"input": "owner asked for extra floor drain in kitchen", "label": "change_event"},
    {"input": "hung 40 sticks of pipe on L4", "label": "base_scope"},
    {"input": "waiting on RFI 114 answer before closing wall", "label": "change_event"},
    {"input": "crew on site 6am, finished rough-in east wing", "label": "base_scope"},
    {"input": "delay - electrical trade not clear of our area again", "label": "change_event"},
    {"input": "", "label": "ambiguous"},
    {"input": "misc site stuff, talked to jim", "label": "ambiguous"},
    {"input": "architect changed the routing at the stairwell, field order to follow", "label": "change_event"},
    {"input": "added circuit for owner's new kiln, super said go", "label": "change_event"},
    {"input": "set 12 fixtures per drawings, west corridor", "label": "base_scope"},
    {"input": "redid the pour after inspection failed on cover depth", "label": "change_event"},
    {"input": "finished rough-in per contract docs, passed inspection", "label": "base_scope"},
    {"input": "gc said hold this area for two days, tile trade behind", "label": "change_event"},
]


def run_eval():
    return change_eval.run(EVAL_CASES, lambda t: classify_note(t)["label"])


# ---------------------------------------------------------------- autonomy

matrix = Matrix({
    "classify_note":      {"rung": "R3", "reason": "internal classification, reversible, PM sees the queue"},
    "draft_co":           {"rung": "R2", "reason": "an internal draft moves nothing outward"},
    "submit_co":          {"rung": "R1", "reason": "outward + money — a human clicks send, and never without a directive on file"},
    "draft_retainage_chase": {"rung": "R1", "reason": "outward message to a GC — a human sends"},
    "notice_alert":       {"rung": "R2", "reason": "an internal alert to the PM; the date is an alert, not advice"},
    "file_notice":        {"rung": "R0", "reason": "the system never files a legal notice — counsel files", "never_promote": True},
    "file_lien":          {"rung": "R0", "reason": "the system never files a lien — counsel files", "never_promote": True},
    "assert_entitlement": {"rung": "R0", "reason": "claim language to a GC is a legal position — humans take legal positions", "never_promote": True},
    "score_invitation":   {"rung": "R3", "reason": "a score with reasons; the go/no-go call stays human"},
    "escalate_to_call":   {"rung": "R2", "reason": "an internal flag to the owner — silence past the ladder becomes a phone call, not a fourth email"},
})
gate = Gate(store, matrix)


# ---------------------------------------------------------------- roi

def roi_model():
    return (Roi("Change OS — what it computes to")
        .line("Unbilled change events captured", "revenue", "count × avg value (your ledger)",
              ["captured_cos", "avg_co_value"],
              lambda g: float(g["captured_cos"]) * float(g["avg_co_value"]),
              note="counted from the CO ledger, not an industry leak percentage")
        .line("Retainage brought inside terms", "cash_timing", "overdue retainage total",
              ["overdue_retainage"], lambda g: float(g["overdue_retainage"]),
              note="cash timing — this is your money arriving sooner, not new revenue")
        .line("Pay-app assembly time", "time_saved", "projects × hrs × rate",
              ["active_projects", "payapp_hours", "admin_rate"],
              lambda g: float(g["active_projects"]) * float(g["payapp_hours"]) * float(g["admin_rate"]),
              note="reported separately; never summed into revenue")
        .line("Lien-right exposure on watched deadlines", "scenario", "open receivable on projects with live deadlines",
              ["exposed_receivable"], lambda g: float(g["exposed_receivable"]),
              assumption="an exposure you weigh, never a saving we claim"))


def roi(given):
    rec = {}
    ub = unbilled_change_value()
    if ub["count"]:
        rec["captured_cos"] = ub["count"]
        rec["avg_co_value"] = round(ub["value"] / ub["count"], 2)
    overdue = [r for r in retainage_aging() if r["overdue"]]
    rec["overdue_retainage"] = round(sum(r["held"] for r in overdue), 2)
    rec["active_projects"] = len([p for p in store.load("projects") if not p.get("substantial_completion")])
    merged = dict(rec)
    merged.update({k: v for k, v in given.items() if v not in (None, "")})
    out = roi_model().render(merged)
    out["recorded"] = rec
    out["operator_supplied"] = {k: v for k, v in given.items() if k not in rec}
    return out


# ---------------------------------------------------------------- counted automation

MOVING = ("classify_note", "draft_co", "submit_co", "draft_retainage_chase", "notice_alert")


def automation():
    return automation_rate(store.events(), MOVING, exclude_actors=("gc:", "owner:"))
